# -*- coding: utf-8 -*-

"""
    utk.bin
    ~~~~~~~

    Bin can hold only one child.

    :copyright: 2011-2014 by Utk Authors.
    :license: LGPL2 or later (see LICENSE)
"""

from utk.container import Container
from utk.utils import Requisition

class Bin(Container):
    __type_name__ = "UtkBin"

    def __init__(self):
        self._child = None
        super(Bin, self).__init__()

    def get_child(self):
        return self._child

    def set_child(self, child):
        self.add(child)

    child = property(get_child, set_child)

    # "size-request" handler
    def do_size_request(self):
        if self._child:
            req = self._child.size_request()
            if self.border_width:
                req = Requisition(req.width+self.border_width*2,
                                  req.height+self.border_width*2)
            return req
        return Requisition(self.border_width*2, self.border_width*2)

    # "size-allocate" handler
    def do_size_allocate(self, allocation):
        self._allocation = allocation
        if self._child and self._child.is_visible:
            child_alloc = allocation._replace(
                x=self.border_width,
                y=self.border_width,
                width=max(1, (allocation.width-self.border_width*2))
                height=max(1, (allocation.height-self.border_width*2))
            )
            self._child.size_allocate(child_alloc)
        if self.is_realized:
            self._canvas.resize(allocation.width, allocation.height)

    # "add" handler
    def do_add(self, child):
        if self._child is not None:
            raise Warning("Attemping to add a widget with type %s to a %s, "
                          "but UtkBin subclass %s can only contain one widget "
                          "at a time; it already contains a widget of type %s"\
                          % (child.name, self.name, self.name, self.child.name))
        child.set_parent(self)
        self._child = child

    # "remove" handler
    def do_remove(self, child):
        pass

    # "foreach" handler
    def do_foreach(self, callback, data=None, include_internals=False):
        if self._child:
            callback(self._child, data)
