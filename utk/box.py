# -*- coding: utf-8 -*-

"""
    utk.box
    ~~~~~~~

    A vertical/horizontal container box

    UtkHBox is a container that organizes childs into a single row.
    UtkVBox is a container that organizes childs into a single column.

    :copyright: 2011-2012 by Utk Authors
    :license: LGPL2 or later (see README/COPYING/LICENSE)
"""

import logging

from utk.container import Container
from utk.utils import BoxChild, Requisition, Rectangle
from utk.constants import ORIENTATION_HORIZONTAL, ORIENTATION_VERTICAL
from utk.constants import PACK_START, PACK_END
from utk.canvas import SolidCanvas

log = logging.getLogger("utk.box")

class Box(Container):
    __type_name__ = "UtkBox"

    def __init__(self, spacing=0, homogeneous=False,
                 orientation=ORIENTATION_HORIZONTAL):
        super(Box, self).__init__()
        self._childs = []
        self._orientation = orientation
        self._spacing = spacing
        self._homogeneous = homogeneous

    def get_orientation(self):
        return self._orientation

    def set_orientation(self, orientation):
        assert orientation in (ORIENTATION_HORIZONTAL, ORIENTATION_VERTICAL)
        self._orientation = orientation
        self.notify("orientation")

    orientation = property(get_orientation, set_orientation)

    def get_spacing(self):
        return self._spacing

    def set_spacing(self, spacing):
        """Sets the 'spacing' property of @box, which is the
        number of chars to place between children of @box.
        """
        if self._spacing != spacing:
            self._spacing = spacing
            self.notify("spacing")
            self.queue_resize()

    spacing = property(get_spacing, set_spacing,
                       doc="The amount of space between childrens")

    def get_homogeneous(self):
        return self._homogeneous

    def set_homogeneous(self, homogeneous):
        if self._homogeneous != homogeneous:
            self._homogeneous = homogeneous
            self.notify("homogeneous")
            self.queue_resize()

    homogeneous = property(get_homogeneous, set_homogeneous,
            doc="Whether the children should be all the same size")

    def _pack(self, widget, expand, fill, padding, pack_type):
        child = BoxChild(widget, padding, expand, fill, pack_type)
        self._childs.append(child)
        widget.set_parent(self)

    def pack_start(self, child, expand=True, fill=True, padding=0):
        """Adds @child to @box, packed with reference to the start of @box.

        The @child is packed after any other child packed whith reference to
        the start of @box.

        :expand: if True the new @child is given extra space allocated to @box.
                 The extra space will be divided evenly between all @children
                 of the @box that use this option.
        :fill: if True space given to @child by the @expand option is actually
               allocated to @child, rather than just padding it. This parameter
               has no effect if @expand is set to False.
        :padding: extra space to put between this child and its neighbors, over
                  and above the global amount specified by "spacing" property.
        """

        self._pack(child, expand, fill, padding, PACK_START)

    def pack_end(self, child, expand=True, fill=True, padding=0):
        """Adds @child to @box, packed with reference to the end of @box

        The @child is packed after (away from end of) any other child
        packed whith reference to the end of @box.

        :expand: if True the new @child is given extra space allocated to @box.
                 The extra space will be divided evenly between all @children
                 of the @box that use this option.
        :fill: if True space given to @child by the @expand option is actually
               allocated to @child, rather than just padding it. This parameter
               has no effect if @expand is set to False.
        :padding: extra space to put between this child and its neighbors, over
                  and above the global amount specified by "spacing" property.
        """
        self._pack(child, expand, fill, padding, PACK_END)

    def get_children(self):
        for child in self._childs:
            if child.pack_type == PACK_START:
                yield child.widget
        for child in reversed(self._childs):
            if child.pack_type == PACK_END:
                yield child.widget

    # "add" signal handler
    def do_add(self, widget):
        self.pack_start(widget)

    # "remove" signal handler
    def do_remove(self, widget):
        for child in self._childs:
            if child.widget == widget:
                widget.unparent()
                self._childs.remove(child)

    # "foreach" signal handler
    def do_foreach(self, callback, data=None, include_internals=None):
        for child in self._childs:
            if child.pack_type == PACK_START:
                callback(child.widget, data)
        for child in reversed(self._childs):
            if child.pack_type == PACK_END:
                callback(child.widget, data)

    # "size-request" signal handler
    def do_size_request(self):
        req = Requisition(0, 0)
        visible_childs = 0
        for child in self._childs:
            if child.widget.is_visible:
                child_req = child.widget.size_request()
                if self.homogeneous:
                    width = child_req.width + child.padding * 2
                    height = child_req.height + child.padding * 2
                    if self.orientation == ORIENTATION_HORIZONTAL:
                        req = req._replace(width=max(req.width, width))
                    else:
                        req = req._replace(height=max(req.height, height))
                else:
                    if self.orientation == ORIENTATION_HORIZONTAL:
                        req = req._replace(width=req.width + child_req.width + child.padding*2)
                    else:
                        req = req._replace(height=req.height + child_req.height + child.padding*2)
                if self.orientation == ORIENTATION_HORIZONTAL:
                    req = req._replace(height=max(req.height, child_req.height))
                else:
                    req = req._replace(width=max(req.width, child_req.width))
                visible_childs += 1
        if visible_childs > 0:
            if self.homogeneous:
                if self.orientation == ORIENTATION_HORIZONTAL:
                    req = req._replace(width=req.width * visible_childs)
                else:
                    req = req._replace(height=req.height * visible_childs)
            if self.orientation == ORIENTATION_HORIZONTAL:
                req = req._replace(width=req.width + (visible_childs-1) * self.spacing)
            else:
                req = req._replace(height=req.height + (visible_childs-1) * self.spacing)

        req = req._replace(width=req.width+self.border_width*2,
                           height=req.height+self.border_width*2)

        return req

    # "size-allocate" signal handler
    def do_size_allocate(self, allocation):
        self._allocation = allocation
        if self.is_realized:
            self.canvas.move_resize(allocation.x, allocation.y,
                                    allocation.width, allocation.height)
        visible_childs = len(filter(lambda c: c.widget.is_visible, self._childs))
        expanded_childs = len(filter(lambda c: c.expand, self._childs))
        log.debug("UtkBox::visible_childs: %d", visible_childs)
        log.debug("UtkBox::expanded_childs: %d", expanded_childs)
        if visible_childs < 1:
            return

        child_alloc = Rectangle()
        x = allocation.x + self.border_width
        y = allocation.y + self.border_width
        width = (allocation.width - self.border_width*2)
        height = (allocation.height - self.border_width*2)

        if self.homogeneous:
            if self.orientation == ORIENTATION_HORIZONTAL:
                width = (allocation.width - self.border_width*2 -
                         (visible_childs-1) * self.spacing)
                extra = width / visible_childs
            else:
                height = (allocation.height - self.border_width*2 -
                          (visible_childs-1) * self.spacing)
                extra = height / visible_childs
        elif expanded_childs > 0:
            if self.orientation == ORIENTATION_HORIZONTAL:
                width = allocation.width - self._requisition.width
                extra = width / expanded_childs
            else:
                height = allocation.height - self._requisition.height
                extra = height / expanded_childs

        if self.orientation == ORIENTATION_HORIZONTAL:
            child_alloc = child_alloc._replace(y=(allocation.y + self.border_width),
                                               height=max(1, allocation.height - self.border_width*2))
        else:
            child_alloc = child_alloc._replace(x=(allocation.x + self.border_width),
                                               width=max(1, allocation.width - self.border_width*2))

        for child in self._childs:
            if child.pack_type == PACK_START and child.widget.is_visible:
                if self.homogeneous:
                    if visible_childs == 1:
                        child_width = width
                        child_height = height
                    else:
                        child_width = extra
                        child_height = extra
                    visible_childs -= 1
                    width -= extra
                    height -= extra
                else:
                    child_req = child.widget._requisition
                    child_width = child_req.width + child.padding * 2
                    child_height = child_req.height + child.padding * 2
                    if child.expand:
                        if expanded_childs == 1:
                            child_width += width
                            child_height += height
                        else:
                            child_width += extra
                            child_height += extra
                    expanded_childs -= 1
                    width -= extra
                    height -= extra

                if child.fill:
                    if self.orientation == ORIENTATION_HORIZONTAL:
                        child_alloc = child_alloc._replace(x=(x+child.padding),
                                                           width=max(1, child_width - child.padding*2))
                    else:
                        child_alloc = child_alloc._replace(y=(y+child.padding),
                                                           height=max(1, child_height - child.padding*2))
                else:
                    child_req = child.widget._requisition
                    if self.orientation == ORIENTATION_HORIZONTAL:
                        child_alloc = child_alloc._replace(x=x+(child_width-child_alloc.width)/2,
                                                           width=child_req.width)
                    else:
                        child_alloc = child_alloc._replace(y=y+(child_height-child_alloc.height)/2,
                                                           height=child_req.height)

                child.widget.size_allocate(child_alloc)
                x += child_width + self.spacing
                y += child_height + self.spacing

        x = allocation.x + allocation.width - self.border_width
        y = allocation.y + allocation.height - self.border_width

        for child in self._childs:
            if child.pack_type == PACK_END and child.widget.is_visible:
                child_req = child.widget._requisition
                if self.homogeneous:
                    if visible_childs == 1:
                        child_width = width
                        child_height = height
                    else:
                        child_width = extra
                        child_height = extra
                    visible_childs -= 1
                    width -= extra
                    height -= extra
                else:
                    child_width = child_req.width + child.padding*2
                    child_height = child_req.height + child.padding*2
                    if child.expand:
                        if expanded_childs == 1:
                            child_width += width
                            child_height += height
                        else:
                            child_width += extra
                            child_height += height
                        expanded_childs -= 1
                        width -= extra
                        height -= extra
                if child.fill:
                    if self.orientation == ORIENTATION_HORIZONTAL:
                        child_alloc = child_alloc._replace(x=x+child.padding-child_width,
                                                           width=max(1, child_width-child.padding*2))
                    else:
                        child_alloc = child_alloc._replace(y=y+child.padding-child_height,
                                                           height=max(1, child_height-child.padding*2))
                else:
                    if self.orientation == ORIENTATION_HORIZONTAL:
                        child_alloc = child_alloc._replace(x=x+(child_width-child_alloc.width)/2-child_width,
                                                           width=child_req.width)
                    else:
                        child_alloc = child_alloc._replace(y=y+(child_height-child_alloc.height)/2-child_height,
                                                           height=child_req.height)

                child.widget.size_allocate(child_alloc)
                x -= (child_width + self.spacing)
                y -= (child_height + self.spacing)

class HBox(Box):
    """
    Container that organizes childs widgets into a single row.

    Use the UtkHBox packing interface to determine the arrangement,
    spacing, width, and alignment of children.

    All children are allocated the same height.
    """
    __type_name__ = "UtkHBox"

    def __init__(self, spacing=0, homogeneous=False):
        super(HBox, self).__init__(spacing, homogeneous, ORIENTATION_HORIZONTAL)

    def do_realize(self):
        assert self.canvas is None
        self._realized = True
        self.canvas = SolidCanvas('H', None,
                                  self._allocation.x, self._allocation.y,
                                  self._allocation.width, self._allocation.height)


class VBox(Box):
    """
    Container that orginizes childs widgets into a single column.

    Use the UtkVBox packing interface to deterine the arrangement,
    spacing, height, and alignment of children.

    All children are allocated the same width.
    """
    __type_name__ = "UtkVBox"

    def __init__(self, spacing=0, homogeneous=False):
        super(VBox, self).__init__(spacing, homogeneous, ORIENTATION_VERTICAL)

    def do_realize(self):
        assert self.canvas is None
        self._realized = True
        self.canvas = SolidCanvas('V', None,
                                  self._allocation.x, self._allocation.y,
                                  self._allocation.width, self._allocation.height)
