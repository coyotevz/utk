# -*- coding: utf-8 -*-

"""
    utk.misc
    ~~~~~~~~

    UtkMisc widget module.

    :copyright: 2011-2012 by Utk Authors.
    :license: LGPL2 or later (see README/COPYING/LICENSE)
"""

from utk.utils import gproperty, clamp
from utk.widget import Widget


class Misc(Widget):
    """
    Base class for widgets with alignments and padding

    This UtkMisc widget is an abstract widget whick is not useful itself, but
    is used to derive subclasses which have alignment and padding attributes.

    The horizontal and vertical padding attributes allows extra space to be
    added around the widget.
    """
    __gtype_name__ = "UtkMisc"

    # properties
    gproperty("xalign", float)
    gproperty("yalign", float)
    gproperty("xpad", int)
    gproperty("ypad", int)

    def __init__(self):
        super(Misc, self).__init__()
        self._xalign = 0.5
        self._yalign = 0.5
        self._xpad = 0
        self._ypad = 0

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


    xalign = property(lambda x: x._xalign,
                      lambda x,v: x.set_alignment(xalign=v))
    yalign = property(lambda x: x._yalign,
                      lambda x,v: x.set_alignment(yalign=v))
    xpad = property(lambda x: x._xpad,
                    lambda x,v: x.set_padding(xpad=v))
    ypad = property(lambda x: x._ypad,
                    lambda x,v: x.set_padding(ypad=v))

    ## get/set gproperties
    def do_get_property(self, prop):
        if prop.name == "xalign":
            return self._xalign
        elif prop.name == "yalign":
            return self._yalign
        elif prop.name == "xpad":
            return self._xpad
        elif prop.name == "ypad":
            return self._ypad
        else:
            return super(Misc, self).do_get_property(prop)

    def do_set_property(self, prop, value):
        if prop.name == "xalign":
            self.set_alignment(xalign=value)
        elif prop.name == "yalign":
            self.set_alignment(yalign=value)
        elif prop.name == "xpad":
            self.set_padding(xpad=value)
        elif prop.name == "ypad":
            self.set_padding(ypad=value)
        else:
            super(Misc, self).do_set_property(prop, value)
