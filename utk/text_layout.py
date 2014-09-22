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

# default layout
default_layout = StandardTextLayout()

_LayoutSegment = namedtuple("LayoutSegment", "text sc offs end")
class LayoutSegment(_LayoutSegment):
    """Create object from line layout segment structure"""
    __slots__ = ()

    def __new__(cls, seg):
        assert type(seg) == tuple, repr(seg)
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
