# -*- coding: utf-8 -*-

"""
    utk.widget
    ~~~~~~~~~~

    :copyright: 2011-2014 by Utk Authors
    :license: LGPL2 or later (see LICENSE)
"""

import logging

from gulib import UObject, usignal, type_name
from utk.utils import Rectangle

log = logging.getLogger("utk.widget")


class Widget(UObject):
    """
    Base class for all Utk widgets. It provides the common set of methods and
    signals for the widgets:
        - methods to realize, map and show widgets
        - methods to manage size request and size allocation
        - methods to deal with the widget's place in the widget hierarchy
        - methods to initiate widget redraw
    """
    __type_name__ = "UtkWidget"

    # signals
    usignal("show")
    usignal("hide")
    usignal("map")
    usignal("unmap")
    usignal("realize")
    usignal("unrealize")

    usignal("size-request")
    usignal("size-allocate")

    usignal("parent-set")

    _toplevel = False

    def __init__(self):
        self._name = None
        self._requisition = None
        self._allocation = None
        self._parent = None
        self._canvas = None

        # flags
        self._visible = False
        self._mapped = False
        self._realized = False

        super(Widget, self).__init__()

    # read-only flags getters
    is_toplevel = property(lambda s: s._toplevel)
    is_visible = property(lambda s: s._visible)
    is_mapped = property(lambda s: s._mapped)
    is_realized = property(lambda s: s._realized)

    # visualizing process

    def show(self):
        """
        This method causes a widget to be displayed as soon as practical.
        """
        if not self.is_visible:
            log.debug("{}::show()".format(self.name))
            self.emit("show")
            self.notify("visible")

    def do_show(self):
        """Default 'show' implementation."""
        if not self.is_visible:
            self._visible = True
            if (self.parent and self.parent.is_mapped) or self.is_toplevel:
                self.map()

    def hide(self):
        """
        This method reverses the effect of the :meth:show() method, causing the
        widget to be hidden (removed from display) by unmapping it.
        """
        if self.is_visible:
            log.debug("{}::hide()".format(self.name))
            self.emit("hide")
            self.notify("visible")

    def do_hide(self):
        """
        Default 'hide' implementation.
        """
        if self.is_visible:
            self._visible = False
            if self.is_mapped:
                self.unmap()

    def map(self):
        """
        Maps the widget (causes it to be displayed). This method will also
        cause the widget to be realized if it is not currently realized. This
        method is usually not used by applications.
        """
        if not self.is_visible:
            return
        if not self.is_mapped:
            if not self.is_realized:
                self.realize()
            log.debug("{}::map()".format(self.name))
            self.emit("map")

    def do_map(self):
        """
        Default 'map' implementation.
        """
        if not self.is_realized:
            raise Warning("You must realize() a widget before call map()")
        if not self.is_mapped:
            self._mapped = True
            self._canvas.show()
            # Mark canvas to be redrawn

    def unmap(self):
        """
        Unmaps the widget (causes it to be removed from the display). This
        method is not usually used by applications.
        """
        if self.is_mapped:
            log.debug("{}::unmap()".format(self.name))
            self.emit("unmap")

    def do_unmap(self):
        """
        Default 'unmap' implementation.
        """
        if self.is_mapped:
            self._mapped = False
            self._canvas.hide()
            # Mark canvas to be redrawn

    def realize(self):
        """
        Creates the resources associated with a widget. For example, the widget
        canvas will be created when the widget is realized.
        Normally realization happens implicity; if you show a widget and all
        it's parent container, the the widget will be realize and mapped
        automatically.
        """
        if not self.is_realized:
            if not self.parent and not self.is_toplevel:
                raise Warning("""Calling Widget.realize() on a widget that
                isn't inside a parent wigdet, is not going to work. Widgets
                must be inside a parent before realizing them.""")
            if self.parent and not self.parent.is_realized:
                self.parent.realize()
            log.debug("{}::realize()".format(self.name))
            self.emit("realize")

    def do_realize(self):
        """
        Default 'realize' implementation, `useless`.
        """
        # Implementators:
        # - Check that self._canvas is None
        # - Mark as realized with self._realized = True
        # - Create canvas for this widget with size from self._allocation
        # - Add created canvas to parent._canvas

    def unrealize(self):
        """
        Frees all resources associated with the widget.
        """
        if self.is_mapped:
            self.unmap()
        if self.is_realized:
            log.debug("{}::unrealize()".format(self.name))
            self.emit("unrealize")

    def do_unrealize(self):
        """
        Default 'unrealize' implementation `useless`.
        """
        # Implementators:
        # - Mark as unrealized with self._realized = False
        # - Destroy created resources in do_realize().

    def get_visible(self):
        """
        Return if a widget is marked as visible
        """
        return self._visible

    def set_visible(self, visible):
        """
        Set visibility of a widget calling corresponding methods.
        """
        if visible != self._visible:
            if visible:
                self.show()
            else:
                self.hide()

    visible = property(get_visible, set_visible)

    # size negotiation

    def size_request(self):
        """
        Returns the preferred sizeof a widget as a Requisition() containing its
        required width and height.
        The size request is not necessary the size a widget will actually be
        allocated.
        """
        requisition = self.emit("size-request")
        log.debug("{}::size_request({})".format(self.name, requisition))
        self._requisition = requisition
        return requisition

    def do_size_request(self):
        """
        Default 'size-request' implementation `useless`.
        """
        # Builds and return Requisition based on widget contents

    def size_allocate(self, allocation):
        """
        Sets the size allocation for the widget using the Rectangle() specified
        by allocation.
        """
        old_alloc = self._allocation
        allocation = allocation._replace(width=max(allocation.width, 1),
                                         height=max(allocation.height, 1))

        if old_alloc:
            size_changed = (old_alloc.width != allocation.width) or \
                           (old_alloc.height != allocation.height)
            position_changed = (old_alloc.x != allocation.x) or \
                               (old_alloc.y != allocation.y)
        else:
            size_changed = position_changed = True

        if not size_changed and not position_changed:
            return

        log.debug("{}::size_allocate({})".format(self.name, tuple(allocation)))
        self.emit("size-allocate", allocation)

        if self.is_mapped:
            # Handle reallocation on canvas
            pass

    def do_size_allocate(self, allocation):
        """
        Default 'size-allocate' implementation.
        """
        self._allocation = allocation
        if self.is_realized:
            # Handle canvas move/resize
            pass

    # widget name handling

    def get_name(self):
        if self._name:
            return self._name
        return type_name(self)

    def set_name(self, name):
        self._name = name
        self.notify("name")

    name = property(get_name, set_name)

    # widget relation handlers

    def set_parent(self, parent):
        """
        This method sets the container as the parent of the widget, and takes
        care of some details such as updating the state of the child to reflect
        its new location.
        """
        if self.parent:
            raise Warning("Can't set a parent on widget wich has a parent")
        if self.is_toplevel:
            raise Warning("Can't set a parent on a toplevel widget")
        self._parent = parent
        self.emit("parent-set", None)
        self.notify("parent")

        if parent.is_realized:
            self.realize()
        if parent.is_visible and self.is_visible and parent.is_mapped:
            self.map()
            # Signal canvas to update

    def unparent(self):
        """
        Reverts the effect of :meth:set_parent() to dissocaite a child widget
        from the container.
        """
        if not self.parent:
            return

        with self.freeze_notify():
            if self.is_realized:
                self.unrealize()

            old_parent = self.parent
            self._parent = None
            self.emit("parent-set", old_parent)
            self.notify("parent")

    def do_parent_set(self, old_parent):
        """
        Default 'parent-set' implementation `useless`
        """
        pass

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value):
        if value is None:
            self.unparent()
        else:
            self.set_parent(value)

    def get_toplevel(self):
        """
        Returns the topmost widget in the container hierarchy widget is part
        of. If widget has no parent, it will be returned as the topmost widget.
        """
        widget = self
        while widget.parent:
            widget = widget.parent
        return widget

    def ancesor_iter(self):
        """
        Iterates on ancesor hierarchy of the widget.
        """
        widget = self
        while widget.parent:
            widget = widget.parent
            yield widget

    def get_path(self):
        names = [p.name for p in self.ancesor_iter()] + [self.name]
        return ".".join(names)

    # widget draw/redraw/resize routines

    def queue_draw(self):
        """
        This method is equivalent to calling the :meth:queue_draw_area() method
        for the entire area of widget.
        """
        if self.is_realized:
            self.queue_draw_area(*self._allocation)

    def queue_draw_area(self, x, y, width, height):
        """
        Invalidates the rectangular area of the widget specified by x, y, width
        and height by calling :meth:Canvas.invalidate_rect() method on the
        widget's canvas. Once the main loop becomes idle (after the current
        batch of events has been processed), the canvas will receive draw
        instruction.
        Normally you would use this method on widget implementations.
        """
        if not self.is_realized:
            return

        for ancesor in self.ancesor_iter():
            if not ancesor.is_realized:
                return

        log.debug("%s::queue_draw_area(x=%d, y=%d, width=%d, height=%d)",
                  self.name, x, y, width, height)

        self._canvas.invalidate_rect(Rectangle(x, y, width, height))

    def queue_resize(self):
        """
        Flags a widget to have its size renegotiated; should be called when a
        widget for some reason has a new size request.
        This method is only for use in widget implementation.
        """
        pass
