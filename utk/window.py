# -*- coding: utf-8 -*-

"""
    utk.window
    ~~~~~~~~~~

    Window is top level widget.

    :copyright: 2011-2014 by Utk Authors.
    :license: LGPL2 or later (see LICENSE)
"""

from utk.bin import Bin
from utk.utils import Rectangle

from utk.screen import get_default_screen
from utk.canvas import SolidCanvas

class Window(Bin):
    __type_name__ = "UtkWindow"

    _toplevel = True

    def __init__(self):
        super(Window, self).__init__()
        self._screen = get_default_screen()
        self._screen.add_toplevel(self)

    def do_show(self):
        if not self.is_visible:
            self._visible = True
            self.map()

    def do_realize(self):
        assert self._canvas is None
        alloc = self._allocation
        self._realized = True
        self._canvas = SolidCanvas('x', {None: 'test'},
                                   alloc.x, alloc.y, alloc.width, alloc.height)
        self.queue_screen_draw()

    def do_unrealize(self):
        self._realized = False
        self._canvas = None
        self.foreach(lambda w, d: w.unrealize())
        self.queue_screen_draw()

    def compute_allocation(self):
        if not self._screen.started:
            self._screen.start()
        return Rectangle(0, 0, *self._screen.get_cols_rows())

    def check_resize(self):
        # ensure widget tree is properly size allocated
        # fire downward size-request
        req = self.size_request()
        allocation = self.compute_allocation()
        # fire downward size-allocate
        self.size_allocate(allocation)

    def queue_screen_draw(self):
        self._screen.queue_draw()
