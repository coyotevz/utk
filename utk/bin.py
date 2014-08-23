# -*- coding: utf-8 -*-

"""
    utk.bin
    ~~~~~~~

    Bin can hold only one child.

    :copyright: 2011-2012 by Utk Authors.
    :license: LGPL2 or later (see README/COPYING/LICENSE)
"""


from utk.container import Container
from utk.utils import gproperty, Requisition


class Bin(Container):
    __gtype_name__ = "UtkBin"

    # properties
    gproperty("child", object)

    def __init__(self):
        self._child = None
        super(Bin, self).__init__()

    def get_child(self):
        return self._child

    child = property(get_child)

    # "add" signal handler
    def do_add(self, child):
        if self._child is not None:
            raise Warning("Attemping to add a widget with type %s to a %s, "
                          "but UtkBin subclass %s can only contain one widget "
                          "at a time; it already contains a widget of type %s" \
                          % (child.name, self.name, self.name, self.child.name))
        child.set_parent(self)
        self._child = child

    # "remove" signal handler
    def do_remove(self, child):
        if self._child != child:
            return
        child.unparent()
        self._child = None

    # "foreach" signal handler
    def do_foreach(self, callback, data=None, include_internals=False):
        if self._child:
            callback(self._child, data)

    # "size-request" signal handler
    def do_size_request(self):
        if self._child:
            req = self._child.size_request()
            if self.border_width:
                req = req._replace(width=req.width+self.border_width*2,
                                   height=req.height+self.border_width*2)
            return req
        return Requisition(self.border_width*2, self.border_width*2)

    # "size-allocate" signal handler
    def do_size_allocate(self, allocation):
        self._allocation = allocation
        if self._child and self._child.is_visible:
            child_alloc = allocation._replace(
                x=self.border_width,
                y=self.border_width,
                width=max(1, (allocation.width-self.border_width*2)),
                height=max(1, (allocation.height-self.border_width*2))
            )
            self._child.size_allocate(child_alloc)
        if self.is_realized:
            self.canvas.resize(allocation.width, allocation.height)

    ## get/set gproperties
    def do_get_property(self, prop):
        if prop.name == "child":
            return self._child
        else:
            return super(Bin, self).do_get_property(prop)

    def do_set_property(self, prop, value):
        if prop.name == "child":
            self.add(value)
        else:
            super(Bin, self).do_set_property(prop, value)
