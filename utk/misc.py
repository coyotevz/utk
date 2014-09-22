# -*- coding: utf-8 -*-

"""
    utk.misc
    ~~~~~~~~

    UtkMisc widget module.

    :copyright: 2011-2012 by Utk Authors.
    :license: LGPL2 or later (see README/COPYING/LICENSE)
"""

import logging

from utk.utils import clamp, Requisition
from utk.widget import Widget
from utk.canvas import SolidCanvas

log = logging.getLogger("utk.misc")

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
        self._content_canvas = None
        self._content_size = None
        self._xalign = 0.5
        self._yalign = 0.5
        self._xpad = 0
        self._ypad = 0

    # "map" handler
    def do_map(self):
        if not self.is_realized:
            raise Warning("You must realize() a widget before call map()")
        if not self.is_mapped:
            self._mapped = True
            self._canvas.show()
            self._content_canvas.show()
            self.queue_draw()

    # "unmap" handler
    def do_unmap(self):
        if self.is_mapped:
            self._mapped = False
            self._content_canvas.hide()
            self._canvas.hide()
            self.queue_draw()

    # "size-request" handler
    def do_size_request(self):
        width, height = self.get_content_size()
        return Requisition(self.xpad*2+width, self.ypad*2+height)

    # "realize" handler
    def do_realize(self):
        assert self._canvas is None
        assert self._content_canvas is None

        req = self._requisition
        alloc = self._allocation
        left, top = self.get_left_top()
        width, height = self.get_content_size()

        canvas = SolidCanvas(' ', left=alloc.x, top=alloc.y,
                             cols=alloc.width, rows=alloc.height)
        content_canvas = self.get_content_canvas(left, top, width, height)

        canvas.add_child(content_canvas)
        canvas.set_parent_widget(self.parent)
        self._realized = True

        self._canvas = canvas
        self._content_canvas = content_canvas

    # "unrealize" handler
    def do_unrealize(self):
        self._realized = False
        self._content_canvas.unparent()
        self._canvas.unparent()
        self._canvas = self._content_canvas = None

    def get_content_size(self):
        if self._content_size is None:
            self._content_size = self.request_content_size()
        return self._content_size

    def get_left_top(self):
        alloc = self._allocation
        req = self.get_content_size()
        left = int(alloc.x+self.xpad+\
                   self.xalign*(alloc.width-2*self.xpad-req[0]))
        top = int(alloc.y+self.ypad+\
                  self.yalign*(alloc.height-2*self.ypad-req[1]))
        return (left, top)

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
