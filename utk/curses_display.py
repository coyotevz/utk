# -*- coding: utf-8 -*-

"""
Curses-based UI implementation
"""

import logging
import curses
import _curses

import utk
from utk.screen import BaseScreen, RealTerminal, AttrSpec, \
    UNPRINTABLE_TRANS_TABLE
from utk.compat import bytes, PYTHON3

log = logging.getLogger("utk.curses_display")

KEY_RESIZE = 410 # curses.KEY_RESIZE (sometimes not defined)
KEY_MOUSE = 409 # curses.KEY_MOUSE

_curses_colours = {
    'default':        (-1,                    0),
    'black':          (curses.COLOR_BLACK,    0),
    'dark red':       (curses.COLOR_RED,      0),
    'dark green':     (curses.COLOR_GREEN,    0),
    'brown':          (curses.COLOR_YELLOW,   0),
    'dark blue':      (curses.COLOR_BLUE,     0),
    'dark magenta':   (curses.COLOR_MAGENTA,  0),
    'dark cyan':      (curses.COLOR_CYAN,     0),
    'light gray':     (curses.COLOR_WHITE,    0),
    'dark gray':      (curses.COLOR_BLACK,    1),
    'light red':      (curses.COLOR_RED,      1),
    'light green':    (curses.COLOR_GREEN,    1),
    'yellow':         (curses.COLOR_YELLOW,   1),
    'light blue':     (curses.COLOR_BLUE,     1),
    'light magenta':  (curses.COLOR_MAGENTA,  1),
    'light cyan':     (curses.COLOR_CYAN,     1),
    'white':          (curses.COLOR_WHITE,    1),
}


class Screen(BaseScreen, RealTerminal):
    __type_name__ = "UtkCursesScreen"

    def __init__(self):
        BaseScreen.__init__(self)
        RealTerminal.__init__(self)
        self.has_colors = False


    # "start" signal handler
    def do_start(self):

        assert not self.started

        if utk._running_from_pytest:
            self._started = True
            return

        self.s = curses.initscr()
        self.has_color = curses.has_colors()
        if self.has_color:
            curses.start_color()
            if curses.COLORS < 8:
                # not colourful enough
                self.has_color = False
        if self.has_color:
            try:
                curses.use_default_colors()
                self.has_default_colors = True
            except _curses.error:
                self.has_default_colors = False

        curses.noecho()
        curses.meta(1)
        curses.halfdelay(10) # use set_input_timeouts to adjust
        self.s.keypad(0)

        self._started = True

    # "stop" signal handler
    def do_stop(self):
        assert self.started

        curses.echo()
        try:
            curses.endwin()
        except _curses.error:
            pass # don't block original error with curses error

        self._started = False

    # "clear" signal handler
    def do_clear(self):
        self.s.clear()

    # "get-cols-rows" signal handler
    def do_get_cols_rows(self):
        if utk._running_from_pytest:
            return 80, 24
        rows, cols = self.s.getmaxyx()
        return cols, rows
