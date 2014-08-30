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

import sys
from collections import namedtuple

from utk import escape
from utk import str_util

# bring str_util functions into our namespace
calc_text_pos = str_util.calc_text_pos

_MAX_VALUES = {int: 0x7fffffff, float: float(2**1024 - 2**971), long: sys.maxint}
_DEFAULT_VALUES = {str: '', float: 0.0, int: 0, long: 0L}

#def gsignal(name, *args, **kwargs):
#    """Add a GObject signal to the current object.
#
#    It current supports the following types:
#        - str, int, float, long, object, enum
#
#    :param name: name of the signal
#    :param args: types for signal parameters,
#        if the first one is a string 'override', the signal will be
#        overriden and must therefor exists in the parent GObject.
#
#    .. note:: flags: A combination of;
#
#      - gobject.SIGNAL_RUN_FIRST
#      - gobject.SIGNAL_RUN_LAST
#      - gobject.SIGNAL_RUN_CLEANUP
#      - gobject.SIGNAL_NO_RECURSE
#      - gobject.SIGNAL_DETAILED
#      - gobject.SIGNAL_ACTION
#      - gobject.SIGNAL_NO_HOOKS
#
#    """
#
#    frame = sys._getframe(1)
#    try:
#        locals = frame.f_locals
#    finally:
#        del frame
#
#    signals = locals.setdefault('__gsignals__', {})
#
#    if args and args[0] == 'override':
#        signals[name] = 'override'
#    else:
#        retval = kwargs.get('retval', None)
#        if retval is None:
#            default_flags = gobject.SIGNAL_RUN_FIRST
#        else:
#            default_flags = gobject.SIGNAL_RUN_LAST
#
#        flags = kwargs.get('flags', default_flags)
#        if retval is not None and flags != gobject.SIGNAL_RUN_LAST:
#            raise TypeError(
#                "You cannot use a return value without setting flags to "
#                "gobject.SIGNAL_RUN_LAST")
#
#        signals[name] = (flags, retval, args)
#
#def gproperty(name, ptype, default=None, nick='', blurb='',
#              flags=gobject.PARAM_READWRITE, **kwargs):
#    """Add a GObject property to the current object.
#
#    :param name: name of property
#    :param ptype: type of property
#    :param default: default value
#    :param nick: short description
#    :param blurb: long description
#    :param flags: parameter flags, a combination of:
#      - PARAM_READABLE
#      - PARAM_READWRITE
#      - PARAM_WRITABLE
#      - PARAM_CONSTRUCT
#      - PARAM_CONSTRUCT_ONLY
#      - PARAMS_LAX_VALIDATION
#
#    Optional, only for int, float, long tpes:
#
#    :param minimum: minimum allowed value
#    :param maximum: maximum allowed value
#    """
#
#    # General type checking
#    if default is None:
#        default = _DEFAULT_VALUES.get(ptype)
#    elif not isinstance(default, ptype):
#        raise TypeError("default must be of type %s, not %r" % (
#            ptype, default))
#    if not isinstance(nick, str):
#        raise TypeError("nick for property %s must be a string, not %r" % (
#            name, nick))
#    nick = nick or name
#    if not isinstance(blurb, str):
#        raise TypeError("blurb for property %s must be a string, not %r" % (
#            name, blurb))
#
#    # Specific type checking
#    if ptype == int or ptype == float or ptype == long:
#        default = (kwargs.get('minimum', ptype(0)),
#                   kwargs.get('maximum', _MAX_VALUES[ptype]),
#                   default)
#    elif ptype == bool:
#        if (default is not True and
#            default is not False):
#            raise TypeError("default must be True or False not %r" % (
#                default))
#        default = default,
#    elif gobject.type_is_a(ptype, gobject.GEnum):
#        if default is None:
#            raise TypeError("enum properties needs a default value")
#        elif not isinstance(default, ptype):
#            raise TypeError("enum value %s must be an instance of %r" %
#                            (default, ptype))
#        default = default,
#    elif ptype == str:
#        default = default,
#    elif ptype == object:
#        if default is not None:
#            raise TypeError("object types does not have default values")
#        default = ()
#    else:
#        raise NotImplementedError("type %r" % ptype)
#
#    if flags < 0 or flags > 32:
#        raise TypeError("invalid flag value: %r" % (flags,))
#
#    frame = sys._getframe(1)
#    try:
#        locals = frame.f_locals
#        properties = locals.setdefault('__gproperties__', {})
#    finally:
#        del frame
#
#    properties[name] = (ptype, nick, blurb) + default + (flags,)


def clamp(value, minimum, maximum):
    value = min(value, maximum)
    value = max(value, minimum)
    return value


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


## RLE tools
def rle_get_at(rle, pos):
    "Return the attribute at offset pos"
    x = 0
    if pos < 0:
        return None
    for a, run in rle:
        if x+run > pos:
            return a
        x += run
    return None


def rle_subseg(rle, start, end):
    "Return a sub segmet of an rle list"
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
            run = end - x
        x += run
        l.append((a, run))
    return l


def rle_len(rle):
    """Return the number of characters covered by a run length encoded
    attribute list"""
    run = 0
    for v in rle:
        assert isinstance(v, tuple), repr(rle)
        a, r = v
        run += r
    return run


def rle_append_beginning_modify(rle, (a, r)):
    """Append (a, r) to BEGINNING of rle.
    Merge with first run when possible

    MODIFIES rle parameter contents. Returns None.
    """
    if not rle:
        rle[:] = [(a, r)]
    else:
        al, run = rle[0]
        if a == al:
            rle[0] = (a, run+r)
        else:
            rle[0:0] = [(al, r)]


def rle_append_modify(rle, (a, r)):
    """Append (a, r) to the rle list.
    Merge with last run when possible

    MODIFIES rle parameter contents. Returns None.
    """
    if not rle or rle[-1][0] != a:
        rle.append((a, r))
        return
    la, lr = rle[-1]
    rle[-1] = (a, lr+r)


def rle_join_modify(rle, rle2):
    """Append attribute list rle2 to rle.
    Merge last run of rle with first run of rle2 when possible.

    MODIFIES attr parameter contents. Returns None.
    """
    if not rle2:
        return
    rle_append_modify(rle, rle2[0])
    rle += rle2[1:]


def rle_product(rle1, rle2):
    """Merge the runs of rle1 and rle2 like this:
    eg.
    rle1 = [("a", 10), ("b", 5)]
    rle2 = [("Q", 5), ("P", 10)]
    rle_product: [(("a", "Q"), 5), (("a", "P"), 5), (("b", "P"), 5)]

    rle1 and rle2 are assumed to cover the same total run.
    """
    i1 = i2 = 1 # rle1, rle2 indexes
    if not rle1 or not rle2:
        return []
    a1, r1 = rle1[0]
    a2, r2 = rle2[0]

    l = []
    while r1 and r2:
        r = min(r1, r2)
        rle_append_modify(l, ((a1, a2), r))
        r1 -= r
        if r1 == 0 and i1 < len(rle1):
            a1, r1 = rle1[i1]
            i1 += 1
        r2 -= r
        if r2 == 0 and i2 < len(rle2):
            a2, r2 = rle2[i2]
            i2 += 1
    return l


def rle_factor(rle):
    "Inverse of rle_product"
    rle1 = []
    rle2 = []
    for (a1, a2), r in rle:
        rle_append_modify(rle1, (a1, r))
        rle_append_modify(rle2, (a2, r))
    return rle1, rle2


def int_scale(val, val_range, out_range):
    """Scale val in the range [0, val_range-1] to an integer int the range
    [0, out_range-1]. This implementation uses the "round-half-up" rounding
    method.
    """
    num = int(val * (out_range - 1) * 2 + (val_range - 1))
    dem = ((val_range - 1) * 2)
    # if num % dem == 0 then we are exactly half-way and have rounded up.
    return num / dem

isiterable = lambda x: hasattr(x, '__iter__')


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

# FIXME: Quick&Dirty
from utk.rle_util import *
