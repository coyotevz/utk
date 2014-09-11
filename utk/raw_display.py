# -*- coding: utf-8 -*-

"""
Direct terminal UI implementation
"""

import os
import logging
import struct
import sys
import signal

try:
    import fcntl
    import termios
    import tty
except ImportError:
    pass # windows

import utk
from utk.screen import BaseScreen, RealTerminal, AttrSpec
from utk import escape
from utk.utils import calc_width, calc_text_pos

log = logging.getLogger("utk.raw_display")

_trans_table = "?"*32 + "".join([chr(x) for x in range(32, 256)])


_term_files = (sys.stdout, sys.stdin)


class Screen(BaseScreen, RealTerminal):
    __type_name__ = "UtkRawScreen"

    # properties
    #uproperty("alternate-buffer", bool, default=True)

    def __init__(self):
        BaseScreen.__init__(self)
        RealTerminal.__init__(self)
        self._screen_buf = None
        self._resized = False
        self._alternate_buffer = True
        self._setup_G1_done = True
        self._rows_used = None
        self._cy = 0
        self._next_timeout = None
        self._resize = False
        self._term_output_file = _term_files[0]
        self._term_input_file = _term_files[1]
        self._resize_pipe_rd, self._resize_pipe_wr = os.pipe()
        fcntl.fcntl(self._resize_pipe_rd, fcntl.F_SETFL, os.O_NONBLOCK)

        self._pal_escape = {}

        self.colors = 16 # FIXME: detect this
        self.has_underline = True # FIXME: detect this
        self.bright_is_bold = os.environ.get('TERM', None) != "xterm"

        self.set_input_timeouts()

    def write(self, data):
        """
        Write some data to the terminal.

        You may wish to override this if you're using something other than
        regular files for input and output.
        """
        self._term_output_file.write(data)

    def flush(self):
        """
        Flush the output buffer.

        You may wish to override this if you're using something other than
        regular files for input and output.
        """
        self._term_output_file.flush()

    use_alternate_buffer = property(lambda x: x._alternate_buffer)

    def do_update_palette_entry(self, name, *attrspecs):
        # copy the attributes to a dictionary containing the escape seq.
        self._pal_escape[name] = self._attrspec_to_escape(
            attrspecs[{16: 0, 1: 1, 88: 2, 256: 3}[self.colors]]
        )

    # "start" signal handler
    def do_start(self):
        assert not self.started

        if utk._running_from_pytest:
            self._started = True
            return

        if self.use_alternate_buffer:
            self.write(escape.SWITCH_TO_ALTERNATE_BUFFER)
            self._rows_used = None
        else:
            self._rows_used = 0

        self._old_termios_settings = termios.tcgetattr(0)
        self.signal_init()
        tty.setcbreak(self._term_input_file.fileno())
        self._input_iter = self._run_input_iter()
        self._next_timeout = self.max_wait

        if not self._signal_keys_set:
            self._old_signal_keys = self.tty_signal_keys()
        self._started = True

    # "stop" signal handler
    def do_stop(self):
        self.clear()
        if not self.started:
            return
        self.signal_restore()
        termios.tcsetattr(0, termios.TCSADRAIN, self._old_termios_settings)
        move_cursor = ""
        if self.use_alternate_buffer:
            move_cursor = escape.RESTORE_NORMAL_BUFFER

        self.write(self._attrspec_to_escape(
            AttrSpec('', '')) + escape.SI + escape.MOUSE_TRACKING_OFF + \
            escape.SHOW_CURSOR + move_cursor + "\n" + escape.SHOW_CURSOR)
        self._input_iter = self._fake_input_iter()

        if self._old_signal_keys:
            self.tty_signal_keys(*self._old_signal_keys)

        self._started = False

    # "clear" signal handler
    def do_clear(self):
        self._screen_buf = None
        self.setup_G1 = True


    # "get-cols-rows" signal handler
    def do_get_cols_rows(self):
        if utk._running_from_pytest:
            return 80, 24
        buf = fcntl.ioctl(self._term_input_file.fileno(), termios.TIOCGWINSZ, ' '*4)
        y, x = struct.unpack('hh', buf)
        return x, y

    # "draw-screen" signal handler
    def do_draw_screen(self):
        assert self.started

        topcanvas = self.get_topcanvas()
        maxrow = self.get_cols_rows()[1]

#        if self._screen_buf:
#            return

        self._setup_G1()

        if self._resized:
            return

        o = [escape.HIDE_CURSOR, self._attrspec_to_escape(AttrSpec('', ''))]

        def partial_display():
            # returns True if the screen is in partial display mode
            # ie. only some rows belong to the display
            return self._rows_used is not None

        if not partial_display():
            o.append(escape.CURSOR_HOME)

        if self._screen_buf:
            osb = self._screen_buf
        else:
            osb = []
        sb = []
        cy = self._cy
        y = -1

        def set_cursor_home():
            if not partial_display():
                return escape.set_cursor_position(0, 0)
            return escape.CURSOR_HOME_COL + escape.move_cursor_up(cy)

        def set_cursor_row(y):
            if not partial_display():
                return escape.set_cursor_position(0, y)
            return escape.move_cursor_down(y - cy)

        def set_cursor_position(x, y):
            if not partial_display():
                return escape.set_cursor_position(x, y)
            if cy > y:
                return ('\b' + escape.CURSOR_HOME_COL +
                        escape.move_cursor_up(cy - y) +
                        escape.move_cursor_right(x))
            return ('\b' + escape.CURSOR_HOME_COL +
                    escape.move_cursor_down(y - cy) +
                    escape.move_cursor_right(x))

        def is_blank_row(row):
            if len(row) > 1:
                return False
            if row[0][2].strip():
                return False
            return True

        def attr_to_escape(a):
            if a in self._pal_escape:
                return self._pal_escape[a]
            elif a in self._palette:
                self._pal_escape[a] = self._attrspec_to_escape(self._palette[a][0])
                return self._pal_escape[a]
            elif isinstance(a, AttrSpec):
                return self._attrspec_to_escape(a)
            # undefined attributes use default/default
            return self._attrspec_to_escape(AttrSpec('default', 'default'))

        ins = None
        o.append(set_cursor_home())
        cy = 0
        for row in topcanvas.content():
            y += 1
            if osb and osb[y] == row:
                # this row of the screen buffer matched what is
                # currently displayed, so we can skip this line
                sb.append(osb[y])
                continue

            sb.append(row)

            # leave blank lines off display when we are using
            # the default screen buffer (allows partial screen)
            if partial_display() and y > self._rows_used:
                if is_blank_row(row):
                    continue
                self._rows_used = y

            if y or partial_display():
                o.append(set_cursor_position(0, y))

            # after updating the line we will be just over the
            # edge, but terminals still treat this as being
            # on the same line
            cy = y

            if y == maxrow - 1:
                row, back, ins = _last_row(row)

            first = True
            lasta = lastcs = None
            for (a, cs, run) in row:
                if cs != 'U':
                    run = run.translate(_trans_table)

                if first or lasta != a:
                    o.append(attr_to_escape(a))
                    lasta = a
                if first or lastcs != cs:
                    assert cs in [None, "0", "U"], repr(cs)
                    if lastcs == "U":
                        o.append(escape.IBMPC_OFF)

                    if cs is None:
                        o.append(escape.SI)
                    elif cs == "U":
                        o.append(escape.IBMPC_ON)
                    else:
                        o.append(escape.SO)
                    lastcs = cs
                o.append(run)
                first = False
            if ins:
                (inserta, insertcs, inserttext) = ins
                ias = attr_to_escape(inserta)
                assert insertcs in (None, "0", "U"), repr(insertcs)
                if cs is None:
                    icss = escape.SI
                elif cs == "U":
                    icss = escape.IBMPC_ON
                else:
                    icss = escape.SO
                o += ["\x08" * back,
                      ias, icss,
                      escape.INSERT_ON, inserttext,
                      escape.INSERT_OFF]
                if cs == "U":
                    o.append(escape.IBMPC_OFF)

        if topcanvas.cursor is not None:
            x, y = topcanvas.cursor
            o += [set_cursor_position(x, y),
                  escape.SHOW_CURSOR]
            self._cy = y

        if self._resized:
            # handle resize before trying to draw screen
            return

        # Write list of commands to terminal
        try:
            k = 0
            for l in o:
                self.write(l)
                k += len(l)
                if k > 1024:
                    self.flush()
                    k = 0
            self.flush()
        except IOError as e:
            # ignore interrupted syscal
            if e.args[0] != 4:
                raise

        self._screen_buf = sb

    def set_input_timeouts(self, max_wait=None, complete_wait=0.125,
                           resize_wait=0.125):
        """Set the get_intput_timeout values. All values are in floating point
        numbers of secconds.

        max_wait -- amount of time in seconds to wait for input when there
            is not input pending, wait forever if `None`
        complete_wait -- amount of time in seconds to wait when get_input
            detects an incoplete escape sequence at the end of the available
            input
        resize_wait -- aount of time in seconds to wait for more input after
            receiving two screen resize request in a row stop Utk from consuming
            100% cpu during a gradual window resize operation
        """
        self.max_wait = max_wait
        if max_wait is not None:
            if self._next_timeout is None:
                self._next_timeout = max_wait
            else:
                self._next_timeout = min(self._next_timeout, max_wait)
        self.complete_wait = complete_wait
        self.resize_wait = resize_wait

    def _sigwinch_handler(self, sugnum, frame):
        if not self._resized:
            os.write(self._resize_pipe_wr, 'R')
        self._resized = True
        self._screen_buf = None

    def signal_init(self):
        """Called in the startup of run wrapper to set the SIGWINCH
        signal handler to self._sigwinch_handler.

        Override this function to call from main thread in threaded
        applications.
        """
        signal.signal(signal.SIGWINCH, self._sigwinch_handler)

    def signal_restore(self):
        """Called in the finally block of run wrapper to restore the
        SIGWINCH handler to the default handler

        Override this function to call from main thread in threaded
        applications.
        """
        signal.signal(signal.SIGWINCH, signal.SIG_DFL)

    def set_mouse_tracking(self):
        """Enable mouse tracking.

        After calling this method, get_input() will include mouse
        click events along with keystrokes.
        """
        self.write(escape.MOUSE_TRACKING_ON)
        self._start_gpm_tracking()

    def get_input(self, raw_keys=False):
        """Return pending input as a list.

        raw_keys -- return raw keycodes as well as translated versions

        This method will inmediately return all the input since the
        last time it was called. If there is no input pending it will
        wait before returning an empty list. The wait time may be
        configured with the set_input_timeouts() method.

        If raw_keys if False (default) this method will return a list
        of keys pressed. If raw_keys is True this method will return a
        (keys pressed, raw keycodes) tuple instead.

        Examples of keys returned
        -------------------------
        ASCII printable characters: " ", "a", "0", "A", "-", "/"
        ASCII control characters: "tab", "enter"
        Escape sequences: "up" "page up", "home", "insert", "f1"
        Key combinations: "shif f1", "meta a", "ctrl b"
        Window events: "window resize"

        When a narrow encoding is not enabled
        "Extended ASCII" characters: "\\xa1", "\\xb2", "\\xfe"

        When a wide encoding is not enabled
        Double-byte characters: "\\xa1\\xea", "\\xb2\\xd4"

        When utf8 encoding is enabled
        Unicode characters: u"\\u00a5", "\\u253c"

        Examples of mouse events returnd
        --------------------------------
        Mouse button press: ('mouse press', 1, 15, 13),
                            ('meta mouse press', 2, 17, 23)
        Mouse drag: ('mouse drag', 1, 16, 13),
                    ('mouse drag', 1, 17, 13),
                    ('ctrl mouse drag', 1, 18, 13)
        Mouse button release: ('mouse release', 0, 18, 13),
                              ('ctrl mouse release', 0, 17, 23)
        """
        assert self.started

        self._wait_for_input_ready(self._next_timeout)
        self._next_timeout, keys, raw = next(self._input_iter)

        # Avoid pagging CPU at 100% when slowly resizing
        if keys == ['window resize'] and self.prev_input_resize:
            while True:
                self._wait_for_input_ready(self.resize_wait)
                self._next_timeout, keys, raw2 = next(self._input_iter)
                raw += raw2
                if keys != ['window resize']:
                    break
            if keys[-1:] != ['window resize']:
                keys.append('window resize')

        if keys == ['window resize']:
            self.prev_input_resize = 2
        elif self.prev_input_resize == 2 and not keys:
            self.prev_input_resize = 1
        else:
            self.prev_input_resize = 0

        if raw_keys:
            return keys, raw
        return keys

    def get_input_descriptors(self):
        """Return a list of integer file descriptors that should be
        polled in external event loop to check for user input.

        Use this method if you are implementing your own event loop.
        """
        fd_list = [self._term_input_file.fileno(), self._resize_pipe_rd]
        if self.gpm_mev is not None:
            fd_list.append(self.gpm_mev.stdout.fileno())
        return fd_list

    def get_input_nonblocking(self):
        """Return a (next_input_timeout, keys_pressed, raw_keycodes)
        tuple.

        Use this method if you are implementing your own event loop.

        When there is input waiting on one of the descriptor returned
        by get_input_descriptors() this method should be called to
        read and process the input.

        This method expect to be called in next_input_timeout seconds
        (a floating point number) if there is no input waiting.
        """
        assert self.started
        return next(self._input_iter)


    def _run_input_iter(self):
        def empty_resize_pipe():
            # clean out the pipe used to signal external event loops
            # that a resize has occurred
            try:
                while True:
                    os.read(self._resize_pipe_rd, 1)
            except OSError:
                pass

        while True:
            processed = []
            codes = self._get_gpm_code() + self._get_keyboards_codes()
            original_codes = codes
            try:
                while codes:
                    run, codes = escape.process_keyqueue(codes, True)
                    processed.extend(run)
            except escape.MoreInputRequired:
                k = len(original_codes) - len(codes)
                yield (self.complete_wait, processed, original_codes[:k])
                empty_resize_pipe()
                original_codes = codes
                processed = []

                codes += self._get_keyboard_codes() + self._get_gpm_codes()
                while codes:
                    run, codes = escape.process_keyqueue(codes, False)
                    processed.extend(run)

            if self._resized:
                processed.append('window resize')
                self._resized = False

            yield (self.max_wait, processed, original_codes)
            empty_resize_pipe()

    def _fake_input_iter(self):
        """This generator is a placeholder for when the screen is stopped
        to always return that no input is available.
        """
        while True:
            yield (self.max_wait, [], [])

    def _setup_G1(self):
        """Initialize the G1 character set to graphics mode if required."""
        if self._setup_G1_done:
            return

        while True:
            try:
                self.write(escape.DESIGNATE_G1_SPECIAL)
                self.flush()
                break
            except IOError:
                pass
        self._setup_G1_done = True

    def _attrspec_to_escape(self, attrspec):
        """Convert AttrSpec instance to an escape sequence for the terminal"""
        if attrspec.foreground_high:
            fg = "38;5;%d" % attrspec.foreground_number
        elif attrspec.foreground_basic:
            if attrspec.foreground_number > 7:
                if self.bright_is_bold:
                    fg = "1;%d" % (attrspec.foreground_number - 8 + 30)
                else:
                    fg = "%d" % (attrspec.foreground_number - 8 +90)
            else:
                fg = "%d" % (attrspec.foreground_number + 30)
        else:
            fg = "39"
        st = ("1;" * attrspec.bold + "4;" * attrspec.underline + "5;" * attrspec.blink +
              "7;" * attrspec.standout)
        if attrspec.background:
            bg = "48;5;%d" % attrspec.background_number
        elif attrspec.background_basic:
            if attrspec.background_number > 7:
                # this doesn't work on most terminals
                bg = "%d" % (attrspec.background_number - 8 + 100)
            else:
                bg = "%d" % (attrspec.background_number + 40)
        else:
            bg = "49"
        return escape.ESC + "[0;%s;%s%sm" % (fg, st, bg)

    def set_terminal_properties(self, colors=None, bright_is_bold=None,
                                has_underline=None):
        """
        colors -- number of colors terminal supports (1, 16, 88, 256)
            or None to leave unchanged
        bright_is_bold -- set to True if this terminal uses the bold
            settings to create briht colors (number 8-15), set to False
            if this Terminal can create bright colors without bold or
            None to leave unchanged
        has_underline -- set to True if this terminal can use the
            underline settings, False if it cannot, or None to leave
            unchanged
        """
        if colors is None:
            colors = self.colors
        if bright_is_bold is None:
            bright_is_bold = self.bright_is_bold
        if has_underline is None:
            has_underline = self.has_underline

        if colors == self.colors and\
           bright_is_bold == self.bright_is_bold and\
           has_underline == self.has_underline:
            return

        self.colors = colors
        self.bright_is_bold = bright_is_bold
        self.has_underline = has_underline

        self.clear()
        self._pal_escape = {}
        for p, v in self._palette.items():
            self.do_update_palette_entry(p, *v)

def _last_row(row):
    """
    On the last row we need to slide the bottom right character
    into place. Calculate the new line, attr and an insert sequence
    to do that.

    eg. last row:
    XXXXXXXXXXXXXXXXXXXXXYZ

    Y will be draw after Z, shifting Z into position.
    """

    new_row = row[:-1]
    z_attr, z_cs, last_text = row[-1]
    last_cols = calc_width(last_text, 0, len(last_text))
    last_offs, z_col = calc_text_pos(last_text, 0, len(last_text), last_cols-1)
    if last_offs == 0:
        z_text = last_text
        del new_row[-1]
        # we need another segment
        y_attr, y_cs, nlast_text = row[-2]
        nlast_cols = calc_width(nlast_text, 0, len(nlast_text))
        z_col += nlast_cols
        nlast_offs, y_col = calc_text_pos(nlast_text, 0, len(nlast_text), nlast_cols-1)
        y_text = nlast_text[nlast_offs:]
        if nlast_offs:
            new_row.append((y_attr, y_cs, nlast_text[:nlast_offs]))
    else:
        z_text = last_text[last_offs:]
        y_attr, y_cs = z_attr, z_cs
        nlast_cols = calc_width(last_text, 0, last_offs)
        nlast_offs, y_col = calc_text_pos(last_text, 0, last_offs, nlast_cols-1)
        y_text = last_text[nlast_offs:last_offs]
        if nlast_offs:
            new_row.append((y_attr, y_cs, last_text[:nlast_offs]))

    new_row.append((z_attr, z_cs, z_text))
    return new_row, z_col-y_col, (y_attr, y_cs, y_text)
