# -*- coding: utf-8 -*-

"""
    utk.container
    ~~~~~~~~~~~~~

    Container is an abstract base class for widgets that contain other
    widgets.

    :copyright: 2011-2012 by Utk Authors
    :license: LGPL2 or later (see README/COPYING/LICENSE)
"""

import logging

from utk import ulib
from utk.ulib import usignal, uproperty
from utk.widget import Widget
from utk.canvas import SolidCanvas
from utk.constants import RESIZE_PARENT, RESIZE_QUEUE, RESIZE_IMMEDIATE, PRIORITY_RESIZE

log = logging.getLogger("utk.container")

_container_resize_queue = []

class Container(Widget):
    __type_name__ = "UtkContainer"

    # properties
    border_width = uproperty(ptype=int)

    # signals
    usignal("add")
    usignal("remove")
    usignal("foreach")
    usignal("check-resize")

    def __init__(self):
        super(Container, self).__init__()
        self._focus_child = None
        self._border_width = 0
        self._need_resize = False
        self._resize_mode = RESIZE_PARENT
        self._resize_pending = False

    def set_border_width(self, border_width):
        if self._border_width != border_width:
            self._border_width = border_width
            self.notify("border-width")
            self.queue_resize()

    def get_border_width(self):
        return self._border_width

    # container methods
    def add(self, widget):
        if widget.parent:
            raise Warning("Attemping to add a widget to a container, but the "
                          "widget is already inside a container")
        self.emit("add", widget)

    def remove(self, widget):
        self.emit("remove", widget)

    def foreach(self, callback, data=None, include_internals=False):
        self.emit("foreach", callback, data, include_internals)

    def check_resize(self):
        log.debug("%s::check_resize()" % self.name)
        self.emit("check-resize")

    # "check-resize" signal handler
    def do_check_resize(self):
        req = self.size_request()

        if (req.width > self._allocation.width) or\
           (req.height > self._allocation.height):
                if self._resize_mode == RESIZE_PARENT:
                    self.size_allocate(self._allocation)
                else:
                    self.queue_resize()
        else:
            self.resize_children()

    def resize_children(self):
        self.size_allocate(self._allocation)

    # "map" signal handler
    def do_map(self):

        def map_childrens(child, data):
            if child.is_visible and\
               child._child_visible and\
               not child.is_mapped:
                   child.map()

        self.foreach(map_childrens)
        super(Container, self).do_map()

    # "realize" signal handler
    def do_realize(self):
        assert self.canvas is None
        self._realized = True
        self.canvas = SolidCanvas('C', None,
                                  self._allocation.x, self._allocation.y,
                                  self._allocation.width, self._allocation.height)

        def realize_childrens(child, data):
            if not child.is_realized and child.is_visible:
                child.realize()

        self.foreach(realize_childrens)

    # overwrite methods
    def show_all(self):
        self.foreach(lambda w,d: w.show_all())
        self.show()

    def hide_all(self):
        self.hide()
        self.foreach(lambda w, d: w.hide_all())


    ## get/set gproperties
    def _get_property(self, prop):
        if prop == "border-width":
            return self.get_border_width()
        else:
            raise UnknowedProperty(prop)

    def _set_property(self, prop, value):
        if prop == "border-width":
            self.set_border_width(value)
        else:
            raise UnknowedProperty(prop, value)
            super(Container, self).do_set_property(prop, value)


    def get_resize_container(self):
        for widget in self.ancesor_iter():
            if widget._resize_mode != RESIZE_PARENT:
                return widget
        if self._resize_mode != RESIZE_PARENT:
            return self
        return None

    def _container_queue_resize(self):
        log.debug("%s::_container_queue_resize()" % self.name)
        resize_container = self.get_resize_container()
        widget = self
        while True:
            widget._alloc_needed = True
            widget._request_needed = True
            if (resize_container and widget == resize_container) or\
                not widget._parent:
                    break
            widget = widget._parent
        if resize_container:
            if resize_container.is_visible and\
              (resize_container.is_toplevel or resize_container.is_realized):
                  if resize_container._resize_mode == RESIZE_QUEUE:
                      if not resize_container._resize_pending:
                          resize_container._resize_pending = True
                          if not _container_resize_queue:
                              log.debug("Adding idle_sizer to loop")
                              ulib.idle_add(self._idle_sizer, priority=PRIORITY_RESIZE)
                          _container_resize_queue.append(resize_container)
                  elif resize_container._resize_mode == RESIZE_IMMEDIATE:
                      resize_container.check_resize()
                  else:
                      assert False, "Not reach this line"
            else:
                resize_container._need_resize = True

    def _idle_sizer(self):
        log.debug("%s::_idle_sizer() running", self.name)
        while _container_resize_queue:
            resize = _container_resize_queue.pop(0)
            resize._resize_pending = False
            resize.check_resize()
        # process all canvas updates
        return False
