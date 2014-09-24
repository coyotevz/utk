# -*- coding: utf-8 -*-

from collections import namedtuple

# align modes
ALIGN_LEFT = 'left'
ALIGN_CENTER = 'center'
ALIGN_RIGHT = 'right'

# wrap modes
WRAP_ANY = 'any'
WRAP_SPACE = 'space'
WRAP_CLIP = 'clip'

class StandardTextLayout(object):

    _align_modes = (ALIGN_LEFT, ALIGN_CENTER, ALIGN_RIGHT)
    _wrap_modes = (WRAP_ANY, WRAP_SPACE, WRAP_CLIP)

    def supports_align_mode(self, align):
        """
        Returns true if align mode is supported, in this case 'left', 'center',
        'right'.
        """
        return align in self._align_modes

    def supports_wrap_mode(self, wrap):
        """
        Returns true if wrap mode is supported, in this case 'any', 'space',
        'clip'.
        """
        return wrap in self._wrap_modes

    def layout(self, text, width, align, wrap):
        """
        Returns a layout structure for text.
        """
        try:
            segs = self.calculate_text_segments(text, width, wrap)
            return self.align_layout(text, width, segs, wrap, align)
        except:
            return [[]]

    def packed_size(self, width, layout):
        """
        Returns a minimal width value that would result in the same number of
        lines for layout. layout must be a layout structure returned by
        self.layout()
        """
        maxwidth = 0
        for l in layout:
            lw = line_width(l)
            if lw >= width:
                return width
            maxwidth = max(maxwidth, lw)
        return maxwidth

    def align_layout(self, text, width, segs, wrap, align):
        out = []
        for l in segs:
            sc = line_width(l)
            if sc == width or align == ALIGN_LEFT:
                out.append(l)
            elif align == ALIGN_RIGHT:
                out.append([(width-sc, None)] + l)
            elif align == ALIGN_CENTER:
                out.append([((width-sc+1) // 2, None)] + l)
            else:
                raise ValueError("Not supported align mode '%s'" % align)
        return out

    def calculate_text_segments(self, text, width, wrap):
        """
        Calculate the segments of text to display given width screen columns to
        display them.

        text - unicode text or byte string to display
        width - number of available screen columns
        wrap - wrapping mode used

        Returns a layout structure without alignment applied.
        """
        nl, nl_o, sp_o = "\n", "\n", " "
        # TODO: Handle PYTHON3 case
        b = []
        p = 0
        if wrap == WRAP_CLIP:
            # no wrapping to calculate, so it's easy.
            while p <= len(text):
                n_cr = text.find(nl, p)
                if n_cr == -1:
                    n_cr = len(text)
                sc = calc_width(text, p, n_cr)
                l = [(0, n_cr)]
                if p != n_cr:
                    l = [(sc, p, n_cr)] + l
                b.append(l)
                p = n_cr + 1
            return b

        while p <= len(text):
            # look for next elegible line break
            n_cr = text.find(nl, p)
            if n_cr == -1:
                n_cr = len(text)
            sc = calc_width(text, p, n_cr)
            if sc == 0:
                # removed character hint
                b.append([(0, n_cr)])
                p = n_cr + 1
                continue
            if sc <= width:
                # this segment fits
                b.append([(sc, p, n_cr),
                          (0, n_cr)])  # removed character hint
                p = n_cr + 1
                continue
            pos, sc = calc_text_pos(text, p, n_cr, width)
            if pos == p: # pathological width=1 double-byte case
                raise ValueError("Wide character will not fit in 1-column width")
            if wrap == "any":
                b.append([(sc, p, pos)])
                p = pos
                continue
            # wrap == 'space'
            if text[pos] == sp_o:
                # perfect space wrap
                b.append([(sc, p, pos),
                          (0, pos)])  # removed character hint
                p = pos + 1
                continue
            if is_wide_char(text, pos):
                # perfect next wide
                b.append([(sc, p, pos)])
                p = pos
                continue
            prev = pos
            while prev > p:
                prev = move_prev_char(text, p, prev)
                if text[prev] == sp_o:
                    sc = calc_width(text, p, prev)
                    l = [(0, prev)]
                    if p != prev:
                        l = [(sc, p, prev)] + l
                    b.append(l)
                    p = prev + 1
                    break
                if is_wide_char(text, prev):
                    # wrap after wide char
                    next = move_next_char(text, prev, pos)
                    sc = calc_with(text, p, next)
                    b.append([sc, p, next])
                    p = next
                    break
            else:
                # unwrap previous line space if possible to fir more text
                # (we're breaking a wird anyway)
                if b and (len(b[-1]) == 2 or (len(b[-1]) == 1 and\
                                              len(b[-1][0]) == 2)):
                    # look for removed space above
                    if len(b[-1]) == 1:
                        [(h_sc, h_off)] = b[-1]
                        p_sc = 0
                        p_off = p_end = h_off
                    else:
                        [(p_sc, p_off, p_end),
                               (h_sc, h_off)] = b[-1]
                    if (p_sc < width and h_sc == 0 and text[h_off] == sp_o):
                        # combine with previous line
                        del b[-1]
                        p = p_off
                        pos, sc = calc_text_pos(text, p, n_cr, width)
                        b.append([(sc, p, pos)])
                        # check for trailing " " or "\n"
                        p = pos
                        if p < len(text) and (text[p] in (sp_o, nl_o)):
                            # removed character hint
                            b[-1].append((0, p))
                            p += 1
                        continue

                # force any char wrap
                b.append([(sc, p, pos)])
                p = pos
        return b

# default layout
default_layout = StandardTextLayout()

_LayoutSegment = namedtuple("LayoutSegment", "text sc offs end")
class LayoutSegment(_LayoutSegment):
    """Create object from line layout segment structure"""
    __slots__ = ()

    def __new__(cls, seg):
        assert isinstance(seg, tuple), repr(seg)
        assert len(seg) in (2, 3), repr(seg)
        sc, offs = seg[:2]
        assert isinstance(sc, int), repr(sc)

        if len(seg) == 3:
            assert isinstance(offs, int), repr(offs)
            assert sc > 0, repr(seg)
            t = seg[2]
            if isinstance(t, bytes):
                text = t
                end = None
            else:
                assert isinstance(t, int), repr(t)
                text = None
                end = t
        else:
            if offs is not None:
                assert sc >= 0, repr(seg)
                assert isinstance(offs, int), repr(offs)
            text = end = None

        return _LayoutSegment.__new__(cls, text, sc, offs, end)

    def subseg(self, text, start, end):
        """
        Return a 'sub-segment' list containing segment structures that make up
        a portion of this segment.

        A list is returned to handle cases where wide characters need to be
        replaced with a space character at either edge so two or three sements
        will be returned.
        """
        if start < 0:
            start = 0
        if end > self.sc:
            end = self.sc
        if start >= end:
            return [] # completely gone
        if self.text:
            # use text stored in segment (self.text)
            spos, epos, lpad, rpad = calc_trim_text(self.text, 0,
                                                    len(self.text), start, end)
            return [(end-start, self.offs, bytes().ljust(lpad)+
                     self.text[spos:epos] + bytes().ljust(rpad))]
        elif self.end:
            # use text passed as parameter (text)
            spos, epos, lpad, rpad = calc_trim_text(text, self.offs, self.end,
                                                    start, end)
            l = []
            if lpad:
                l.append((1, spos-1))
            l.append((end-start-lpad-rpad, spos, epos))
            if rpad:
                l.append((1, epos))
            return l
        else:
            # simple padding adjustment
            return [(end-start, self.offs)]

def line_width(segs):
    """
    Returns the screen column width of one line of a text layout structure.

    This function ignores any existing shift applied to the line, represented
    by an (amount, None) tuple at the start of the line.
    """
    sc = 0
    seglist = segs
    if segs and len(segs[0]) == 2 and segs[0][1] is None:
        seglist = segs[1:]
    for s in seglist:
        sc += s[0]
    return sc


def calc_pos(text, layout, pref_col, row):
    pass

def calc_coords(text, layout, pos):
    pass

def shift_line(segs, amount):
    pass
