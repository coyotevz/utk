# -*- coding: utf-8 -*-

"""
    utk.utils
    ~~~~~~~~~

    Utilities for handling some of wonders of GLib and GObject. Also
    includes some usefull strucrures and functions.

    gproperty and gsignal are mostly taken from pygtkhelpers.utils

    :copyright: 2011 by Utk Authors
    :license: LGPL 2 or later (see README/COPYING/LICENSE)
"""

from collections import namedtuple
import codecs

from gulib.compat import string_type, u
from utk import escape
from utk import str_util

# bring str_util functions into our namespace
calc_text_pos = str_util.calc_text_pos
calc_width = str_util.calc_width

def clamp(value, minimum, maximum):
    value = min(value, maximum)
    value = max(value, minimum)
    return value

def isiterable(obj):
    return hasattr(obj, '__iter__')

# usefull structures
Requisition = namedtuple("Requisition", "width height")
BoxChild = namedtuple("BoxChild", "widget padding expand fill pack_type")

_Rectangle = namedtuple("Rectangle", "x y width height")
class Rectangle(_Rectangle):
    __slots__ = ()

    def __new__(cls, x=None, y=None, width=None, height=None):
        x = x if x is not None else -1
        y = y if y is not None else -1
        width = width if width is not None else 1
        height = height if height is not None else 1
        return _Rectangle.__new__(cls, x, y, width, height)

    def intersect(self, other):
        """Return True if has an intersection with other"""
        if self.intersection(other) is not None:
            return True
        return False

    def intersection(self, other):
        """Return new Rectangle with the intersection with other or None"""
        x1 = max(self.x, other.x)
        y1 = max(self.y, other.y)
        x2 = min(self.x + self.width, other.x + other.width)
        y2 = min(self.y + self.height, other.y + other.height)
        if x2 > x1 and y2 > y1:
            return Rectangle(x1, y1, x2-x1, y2-y1)
        return None

    def union(self, other):
        """
        Return new Rectangle with the union with other.

        The union of rectangles is the smallest rectangle wich
        includes both rectangles within it.
        """
        x = min(self.x, other.x)
        y = min(self.y, other.y)
        width = max(self.x+self.width, other.x+other.width) - x
        height = max(self.y+self.height, other.y+other.height) - y
        return Rectangle(x, y, width, height)

    def difference(self, other):
        """
        Return a list of rectangles that result of self substracting other.
        """
        inter = self.intersection(other)
        if inter is None or inter == self:
            return []
        res = []
        # build R1
        res.append(Rectangle(self.x, self.y, self.width, (inter.y-self.y)))
        # build R2
        res.append(Rectangle(self.x, inter.y, (inter.x-self.x), inter.height))
        # build R3
        res.append(Rectangle((inter.x+inter.width),
                             inter.y,
                             (self.width-inter.width-inter.x+self.x),
                             inter.height))
        # build R4
        res.append(Rectangle(self.x,
                             (inter.y+inter.height),
                             self.width,
                             (self.y+self.height-inter.y-inter.height)))

        return filter(None, res)

    def __nonzero__(self):
        return (self.height > 0) and (self.width > 0)

class StoppingContext(object):
    """
    Context manager that calls ``stop`` on a given object on exit. Used to make
    the ``start`` method on `MainLoop` and `BaseScreen` optionally act as
    context managers.
    """
    def __init__(self, wrapped):
        self._wrapped = wrapped

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        self._wrapped.stop()


## RLE tools
def detect_encoding():
    "Try to determine if using a supported double-byte encoding"
    import locale
    try:
        try:
            locale.setlocale(locale.LC_ALL, "")
        except locale.Error:
            pass
        return locale.getlocale()[1] or ""
    except ValueError as e:
        # with invalid LANG value python will throw ValueError
        if e.args and e.args[0].startswith("unknown locale"):
            return ""
        else:
            raise

if 'detected_encoding' not in locals():
    detected_encoding = detect_encoding()
else:
    assert 0, "It worked!"

_target_encoding = None
_use_dec_special = True


def set_encoding( encoding ):
    """
    Set the byte encoding to assume when processing strings and the
    encoding to use when converting unicode strings.
    """
    encoding = encoding.lower()

    global _target_encoding, _use_dec_special

    if encoding in ( 'utf-8', 'utf8', 'utf' ):
        str_util.set_byte_encoding("utf8")

        _use_dec_special = False
    elif encoding in ( 'euc-jp' # JISX 0208 only
            , 'euc-kr', 'euc-cn', 'euc-tw' # CNS 11643 plain 1 only
            , 'gb2312', 'gbk', 'big5', 'cn-gb', 'uhc'
            # these shouldn't happen, should they?
            , 'eucjp', 'euckr', 'euccn', 'euctw', 'cncb' ):
        str_util.set_byte_encoding("wide")

        _use_dec_special = True
    else:
        str_util.set_byte_encoding("narrow")
        _use_dec_special = True

    # if encoding is valid for conversion from unicode, remember it
    _target_encoding = 'ascii'
    try:
        if encoding:
            u("").encode(encoding)
            _target_encoding = encoding
    except LookupError: pass


def get_encoding_mode():
    """
    Get the mode Urwid is using when processing text strings.
    Returns 'narrow' for 8-bit encodings, 'wide' for CJK encodings
    or 'utf8' for UTF-8 encodings.
    """
    return str_util.get_byte_encoding()


def apply_target_encoding(s):
    """
    Return (encoded byte string, character set rle).
    """
    if _use_dec_special and isinstance(s, string_type):
        # first convert drawing characters
        try:
            s = s.translate( escape.DEC_SPECIAL_CHARMAP )
        except NotImplementedError:
            # python < 2.4 needs to do this the hard way..
            for c, alt in zip(escape.DEC_SPECIAL_CHARS,
                    escape.ALT_DEC_SPECIAL_CHARS):
                s = s.replace( c, escape.SO+alt+escape.SI )

    if isinstance(s, string_type):
        s = s.replace(escape.SI+escape.SO, u("")) # remove redundant shifts
        s = codecs.encode(s, _target_encoding, 'replace')

    assert isinstance(s, bytes)
    SO = escape.SO.encode('ascii')
    SI = escape.SI.encode('ascii')

    sis = s.split(SO)

    assert isinstance(sis[0], bytes)

    sis0 = sis[0].replace(SI, bytes())
    sout = []
    cout = []
    if sis0:
        sout.append( sis0 )
        cout.append( (None,len(sis0)) )

    if len(sis)==1:
        return sis0, cout

    for sn in sis[1:]:
        assert isinstance(sn, bytes)
        assert isinstance(SI, bytes)
        sl = sn.split(SI, 1)
        if len(sl) == 1:
            sin = sl[0]
            assert isinstance(sin, bytes)
            sout.append(sin)
            rle_append_modify(cout, (escape.DEC_TAG.encode('ascii'), len(sin)))
            continue
        sin, son = sl
        son = son.replace(SI, bytes())
        if sin:
            sout.append(sin)
            rle_append_modify(cout, (escape.DEC_TAG, len(sin)))
        if son:
            sout.append(son)
            rle_append_modify(cout, (None, len(son)))

    outstr = bytes().join(sout)
    return outstr, cout


######################################################################
# Try to set the encoding using the one detected by the locale module
set_encoding( detected_encoding )
######################################################################


def supports_unicode():
    """
    Return True if python is able to convert non-ascii unicode strings
    to the current encoding.
    """
    return _target_encoding and _target_encoding != 'ascii'





def calc_trim_text( text, start_offs, end_offs, start_col, end_col ):
    """
    Calculate the result of trimming text.
    start_offs -- offset into text to treat as screen column 0
    end_offs -- offset into text to treat as the end of the line
    start_col -- screen column to trim at the left
    end_col -- screen column to trim at the right

    Returns (start, end, pad_left, pad_right), where:
    start -- resulting start offset
    end -- resulting end offset
    pad_left -- 0 for no pad or 1 for one space to be added
    pad_right -- 0 for no pad or 1 for one space to be added
    """
    spos = start_offs
    pad_left = pad_right = 0
    if start_col > 0:
        spos, sc = calc_text_pos( text, spos, end_offs, start_col )
        if sc < start_col:
            pad_left = 1
            spos, sc = calc_text_pos( text, start_offs,
                end_offs, start_col+1 )
    run = end_col - start_col - pad_left
    pos, sc = calc_text_pos( text, spos, end_offs, run )
    if sc < run:
        pad_right = 1
    return ( spos, pos, pad_left, pad_right )




def trim_text_attr_cs( text, attr, cs, start_col, end_col ):
    """
    Return ( trimmed text, trimmed attr, trimmed cs ).
    """
    spos, epos, pad_left, pad_right = calc_trim_text(
        text, 0, len(text), start_col, end_col )
    attrtr = rle_subseg( attr, spos, epos )
    cstr = rle_subseg( cs, spos, epos )
    if pad_left:
        al = rle_get_at( attr, spos-1 )
        rle_append_beginning_modify( attrtr, (al, 1) )
        rle_append_beginning_modify( cstr, (None, 1) )
    if pad_right:
        al = rle_get_at( attr, epos )
        rle_append_modify( attrtr, (al, 1) )
        rle_append_modify( cstr, (None, 1) )

    return (bytes().rjust(pad_left) + text[spos:epos] +
        bytes().rjust(pad_right), attrtr, cstr)


def rle_get_at(rle, pos):
    """
    Return the attribute at offset pos.
    """
    x = 0
    if pos < 0:
        return None
    for a, run in rle:
        if x+run > pos:
            return a
        x += run
    return None


def rle_subseg(rle, start, end):
    """Return a sub segment of an rle list."""
    l = []
    x = 0
    for a, run in rle:
        if start:
            if start >= run:
                start -= run
                x += run
                continue
            x += start
            run -= start
            start = 0
        if x >= end:
            break
        if x+run > end:
            run = end-x
        x += run
        l.append( (a, run) )
    return l


def rle_len(rle):
    """
    Return the number of characters covered by a run length
    encoded attribute list.
    """

    run = 0
    for v in rle:
        assert type(v) == tuple, repr(rle)
        a, r = v
        run += r
    return run

def rle_append_beginning_modify(rle, a_r):
    """
    Append (a, r) (unpacked from *a_r*) to BEGINNING of rle.
    Merge with first run when possible

    MODIFIES rle parameter contents. Returns None.
    """
    a, r = a_r
    if not rle:
        rle[:] = [(a, r)]
    else:
        al, run = rle[0]
        if a == al:
            rle[0] = (a,run+r)
        else:
            rle[0:0] = [(al, r)]


def rle_append_modify(rle, a_r):
    """
    Append (a, r) (unpacked from *a_r*) to the rle list rle.
    Merge with last run when possible.

    MODIFIES rle parameter contents. Returns None.
    """
    a, r = a_r
    if not rle or rle[-1][0] != a:
        rle.append( (a,r) )
        return
    la,lr = rle[-1]
    rle[-1] = (a, lr+r)

def rle_join_modify(rle, rle2):
    """
    Append attribute list rle2 to rle.
    Merge last run of rle with first run of rle2 when possible.

    MODIFIES attr parameter contents. Returns None.
    """
    if not rle2:
        return
    rle_append_modify(rle, rle2[0])
    rle += rle2[1:]

def rle_product(rle1, rle2):
    """
    Merge the runs of rle1 and rle2 like this:
    eg.
    rle1 = [ ("a", 10), ("b", 5) ]
    rle2 = [ ("Q", 5), ("P", 10) ]
    rle_product: [ (("a","Q"), 5), (("a","P"), 5), (("b","P"), 5) ]

    rle1 and rle2 are assumed to cover the same total run.
    """
    i1 = i2 = 1 # rle1, rle2 indexes
    if not rle1 or not rle2: return []
    a1, r1 = rle1[0]
    a2, r2 = rle2[0]

    l = []
    while r1 and r2:
        r = min(r1, r2)
        rle_append_modify( l, ((a1,a2),r) )
        r1 -= r
        if r1 == 0 and i1< len(rle1):
            a1, r1 = rle1[i1]
            i1 += 1
        r2 -= r
        if r2 == 0 and i2< len(rle2):
            a2, r2 = rle2[i2]
            i2 += 1
    return l


def rle_factor(rle):
    """
    Inverse of rle_product.
    """
    rle1 = []
    rle2 = []
    for (a1, a2), r in rle:
        rle_append_modify( rle1, (a1, r) )
        rle_append_modify( rle2, (a2, r) )
    return rle1, rle2


def int_scale(val, val_range, out_range):
    """
    Scale val in the range [0, val_range-1] to an integer in the range
    [0, out_range-1].  This implementation uses the "round-half-up" rounding
    method.
    """
    num = int(val * (out_range-1) * 2 + (val_range-1))
    dem = ((val_range-1) * 2)
    # if num % dem == 0 then we are exactly half-way and have rounded up.
    return num // dem
