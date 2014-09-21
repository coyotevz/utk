# -*- coding: utf-8 -*-

"""
    utk.misc
    ~~~~~~~~

    UtkMisc widget module.

    :copyright: 2011-2012 by Utk Authors.
    :license: LGPL2 or later (see README/COPYING/LICENSE)
"""

from utk.utils import clamp
from utk.widget import Widget


class Misc(Widget):
    """
    Base class for widgets with alignments and padding

    This UtkMisc widget is an abstract widget whick is not useful itself, but
    is used to derive subclasses which have alignment and padding attributes.

    The horizontal and vertical padding attributes allows extra space to be
    added around the widget.
    """
    __type_name__ = "UtkMisc"

    def __init__(self):
        super(Misc, self).__init__()
        self._xalign = 0.5
        self._yalign = 0.5
        self._xpad = 0
        self._ypad = 0

    def get_left_top(self):
        alloc = self._allocation
        req = self._requisition
        return (int((alloc.width - req.width) * self.xalign) + alloc.x,
                int((alloc.height - req.height) * self.yalign) + alloc.y)

    def set_alignment(self, xalign=None, yalign=None):
        _changed = False
        self.freeze_notify()
        if xalign is not None:
            xalign = clamp(xalign, 0, 1)
            if xalign != self._xalign:
                self.notify("xalign")
                self._xalign = xalign
                _changed = True

        if yalign is not None:
            yalign = clamp(yalign, 0, 1)
            if yalign != self._yalign:
                self.notify("yalign")
                self._yalign = yalign
                _changed = True

        if _changed:
            self.queue_draw()

        self.thaw_notify()

    def set_padding(self, xpad=None, ypad=None):
        _changed = False
        self.freeze_notify()
        if xpad is not None:
            xpad = max(xpad, 0)
            if xpad != self._xpad:
                self.notify("xpad")
                self._xpad = xpad
                _changed = True

        if ypad is not None:
            ypad = max(ypad, 0)
            if ypad != self._ypad:
                self.notify("ypad")
                self._ypad = ypad
                _changed = True

        if _changed:
            self.queue_resize()

        self.thaw_notify()

    ## get/set gproperties
    @property
    def xalign(self):
        return self._xalign

    @xalign.setter
    def xalign(self, value):
        self.set_alignment(xalign=value)

    @property
    def yalign(self):
        return self._yalign

    @yalign.setter
    def yalign(self, value):
        self.set_alignment(yalign=value)

    @property
    def xpad(self):
        return self._xpad

    @xpad.setter
    def xpad(self, value):
        self.set_padding(xpad=value)

    @property
    def ypad(self):
        return self._ypad

    @ypad.setter
    def ypad(self, value):
        self.set_padding(ypad=value)
