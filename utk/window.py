# -*- coding: utf-8 -*-

"""
    utk.window
    ~~~~~~~~~~

    Window is top level widget.

    :copyright: 2011-2012 by Utk Authors.
    :license: LGPL2 or later (see README/COPYING/LICENSE)
"""

import logging

from utk.widget import Widget
from utk.bin import Bin
from utk.utils import gsignal, Rectangle, Requisition
from utk.constants import RESIZE_QUEUE

from utk.screen import get_default_screen
from utk.canvas import SolidCanvas


log = logging.getLogger("utk.window")


class Window(Bin):
    __gtype_name__ = "UtkWindow"

    # event signals
    gsignal("event")

    _toplevel = True

    def __init__(self):
        super(Window, self).__init__()
        self._resize_mode = RESIZE_QUEUE
        self._screen = get_default_screen()
        self._screen.add_toplevel(self)

    def do_show(self):
        self._visible = True
        need_resize = self._need_resize or not self.is_realized
        self._need_resize = False

        if need_resize:
            self.size_request()
            config_request = self.compute_configure_request()
            allocation = Rectangle(0, 0, config_request.width, config_request.height)
            self.size_allocate(allocation)

            if not self.is_realized:
                self.realize()
                #self.canvas.move_resize(allocation.x, allocation.y,
                #                        allocation.width, allocation.height)

        self.check_resize()
        self.map()

    # "hide" signal handler
    def do_hide(self):
        pass

    # "map" signal handler
    def do_map(self):
        if self._child and\
           self._child.is_visible and\
           not self._child.is_mapped:
               self._child.map()
        Widget.do_map(self)

    # "realize" signal handler
    def do_realize(self):
        # ensure widget tree is properly size allocated
        if self._allocation is None:
            # FIXME: This branch is never excecuted
            # fire downwards size-request
            req = self.size_request()
            allocation = Rectangle(0, 0, 200, 200)
            if req.width or req.height:
                # non-empty window
                allocation = allocation._replace(width=req.width,
                                                 height=req.height)

            # fire downwards size-allocate
            self.size_allocate(allocation)
            self._container_queue_resize()
            if self.is_realized:
                return

        self._realized = True
        self.canvas = SolidCanvas('x', {None: 'test'},
                                  self._allocation.x, self._allocation.y,
                                  self._allocation.width, self._allocation.height)

    # "check-resize" signal handler
    def do_check_resize(self):
        if self.is_visible:
            if self._request_needed:
                log.debug("Need size request")
                self.size_request()
            if self._alloc_needed:
                log.debug("Need size allocate")
                self.size_allocate(self._allocation)
            self.queue_screen_draw()

    def compute_configure_request(self):
        log.debug("%s::compute_configure_request()", self.name)
        if not self._screen.started:
            self._screen.start()
        return Requisition(*self._screen.get_cols_rows())

    def queue_screen_draw(self):
        self._screen.queue_draw()
