# -*- coding: utf-8 -*-

"""
    utk.widget
    ~~~~~~~~~~

    Widget objects.

    :copyright: 2011-2012 by Utk Authors
    :license: LGPL2 or later (see README/COPYING/LICENSE)
"""

import logging

from gobject import GObject, type_name
from gobject import SIGNAL_RUN_FIRST

import utk
from utk.constants import STATE_NORMAL
from utk.utils import gproperty, gsignal
from utk.utils import Rectangle, Requisition
from utk.canvas import SolidCanvas


log = logging.getLogger("utk.widget")


class Widget(GObject):
    """
    Base class for all Utk widgets. It provides the common set of methods and
    signals for the widgets including:
        - methods to realize, map and show widgets
        - methods to manage size allocation and requests
        - methods to initiate widget redrawing
        - methods to deal with the widget's place in the widget hierarchy
        - event management methods
    """
    __gtype_name__ = "UtkWidget"

    #properties
    gproperty("name", str)
    gproperty("parent", object)
    gproperty("visible", bool, default=False)

    #signals
    gsignal("show")
    gsignal("hide")
    gsignal("map")
    gsignal("unmap")
    gsignal("realize")
    gsignal("unrealize")
    gsignal("size-request", retval=object)
    gsignal("size-allocate", object, flags=SIGNAL_RUN_FIRST)

    gsignal("parent-set", object)

    _toplevel = False

    def __init__(self):
        self._state = STATE_NORMAL
        self._saved_state = STATE_NORMAL
        self._name = None
        self._requisition = None
        self._allocation = Rectangle()
        #self._allocation = None
        self._parent = None
        self.canvas = None

        # flags
        self._visible = False
        self._mapped = False
        self._realized = False

        # private flags
        self._child_visible = True
        self._redraw_on_alloc = True
        self._request_needed = True
        self._alloc_needed = True


        super(Widget, self).__init__()

    def set_name(self, name):
        """
        Sets the 'name' property of the widget to the string specified by name.
        Wigets can be named, which allows you to refer to them in a Utk Style
        File.
        """
        self._name = name
        self.notify("name")

    def get_name(self):
        if self._name:
            return self._name
        return type_name(self)

    name = property(get_name, set_name)

    def show(self):
        """
        This method causes a widget to be displayed as soon as practial. Any
        widget that isn0t shown will not appear on the screen. If you want to
        show all the widgets in a container, it's easier to call :meth:show_all()
        on the container.
        """
        if not self.is_visible:
            log.debug("%s::show()" % self.name)
            if self.is_toplevel:
                self.queue_resize()
            self.emit("show")
            self.notify("visible")

    def do_show(self):
        """Default 'show' handler implementation."""
        if not self.is_visible:
            self._visible = True
            if (self.parent and
                self.parent.is_mapped and
                self._child_visible and
                not self.is_mapped):
                    self.map()

    def hide(self):
        """
        This method reverses the effects of the :meth:show() method, causing
        the widget to be hidden (removed from display) by unmapping it.
        """
        if self.is_visible:
            log.debug("%s::hide()" % self.name)
            self.emit("hide")
            self.notify("visible")

    def do_hide(self):
        """Default 'hide' signal handler."""
        if self.is_visible:
            self._visible = False
            if self.is_mapped:
                self.unmap()

    def show_all(self):
        """
        Recursively shows the widget, and any child widget (if the wiget is
        a container).
        """
        self.show()

    def hide_all(self):
        """
        Recursively hides the widget and its child wigdets (if any).
        """
        self.hide()

    def map(self):
        """
        Maps the widget (causes it to be displayed). This method will also
        cause the widget to be realized if it is not currently realized. This
        method is usually not used by applications.
        """
        if not self.is_visible or not self._child_visible:
            return
        if not self.is_mapped:
            if self._alloc_needed and self.parent:
                print "%s needs allocation" % self
                self.parent._alloc_needed = True
                self.parent.check_resize()
                print "%s allocation %r" % (self, self._allocation)
            if not self.is_realized:
                self.realize()
            log.debug("%s::map()" % self.name)
            self.emit("map")

    def do_map(self):
        assert self.is_realized
        if not self.is_mapped:
            self._mapped = True
            self.canvas.show()
            self.queue_draw()

    def unmap(self):
        """
        Unmaps the widget (causes it to be removed from the display). This
        method is not usually used by applications.
        """
        if self.is_mapped:
            log.debug("%s::unmap()" % self.name)
            self.emit("unmap")

    def do_unmap(self):
        if self.is_mapped:
            self._mapped = False
            self.canvas.hide()
            self.queue_draw()

    def realize(self):
        """
        Creates the resources associated with a widget. For example, the widget
        Canvas will be created when the widget is realized.
        Normally realization happens implicitly; if you show a widget and all
        its parent containers, then the wigdet will be realized and mapped
        automatically.
        Realizing a widget requires all the widget's parent widget to be
        realized; calling the :meth:`realize` method realizes the widget's
        parents in addition to the widget itself.
        This method is primarily used in widget implementations, and not in
        applications.
        """
        if not self.is_realized:
            if not utk._running_from_pytest:
                assert self._allocation is not None
            if not self.parent and not self.is_toplevel:
                raise Warning("Calling Widget.realize() on a widget that isn't"
                              " inside a parent widget, is not going to work "
                              "very well. Widgets must be inside a parent "
                              "widget before realizing them.")
            if self.parent and not self.parent.is_realized:
                self.parent.realize()
            log.debug("%s::realize()", self.name)
            self.emit("realize")
            if self.parent:
                self.parent.canvas.add_child(self.canvas)

    def do_realize(self):
        """Default 'realize' handler implementation `useless`."""
        assert self.canvas is None
        self._realized = True
        # Only for test
        import random
        self.canvas = SolidCanvas('%d' % random.randint(0, 9), None,
                                  self._allocation.x, self._allocation.y,
                                  self._allocation.width, self._allocation.height)

    def unrealize(self):
        """
        Frees all resources associated with the widget, such as the Canvas()
        """
        if self.is_mapped:
            self.unmap()
        if self.is_realized:
            log.debug("%s::unrealize()", self.name)
            self.emit("unrealize")

    def do_unrealize(self):
        """Default 'unrealize' handler implementation `useless`."""
        self._realized = False
        self.canvas = None

    def size_request(self):
        """
        Returns the preferred sizeof a widget as a Requisition() containing
        its required width and height. This method is typically used when
        implementing a :class:utk.Container() subclass to arrange the container's
        child wigdet and decide what size allocations to give them.
        Remember that the size request is not necessarily the size a wiget will
        actually be allocated.
        """
        requisition = self.emit("size-request")
        log.debug("%s(%x)::size_request(%r)", self.name, id(self), requisition)
        self._requisition = requisition
        return requisition

    def do_size_request(self):
        """Default 'size-request' handler implementation `useless`."""
        self._requisition = Requisition(0, 0)
        return self._requisition

    def size_allocate(self, allocation):
        """
        Sets the size allocation for the widget using the Rectangle() specified
        by allocation. This method is only used by :class:utk.Container() sub-
        classes, to assing a size and position to their child widgets.
        """
        alloc_needed = self._alloc_needed
        if self._request_needed: # Preserve request/allocate ordering
            self._alloc_needed = False

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

        if not alloc_needed and not size_changed and not position_changed:
            return

        log.debug("%s::size_allocate%r", self.name, tuple(allocation))
        self.emit("size-allocate", allocation)

        if self.is_mapped and self._redraw_on_alloc:
            invalidate = Rectangle(*self._allocation).union(old_alloc)
            if position_changed:
                self.canvas.move_to(self._allocation.x, self._allocation.y)
            if size_changed:
                self.canvas.resize(self._allocation.width, self._allocation.height)

    def do_size_allocate(self, allocation):
        """Default 'size-allocate' handler"""
        self._allocation = allocation
        if self.is_realized:
            self.canvas.move_resize(allocation.x, allocation.y,
                                    allocation.width, allocation.height)
            if self.is_toplevel:
                self.queue_screen_draw()

    def set_parent(self, parent):
        """
        This method is useful only when implementing subclasses of
        :class:utk.Container(). This methods sets the container as the parent
        of the wigdet, and takes care of some details such as updating the
        state of the child to refect its new location.
        """
        if self.parent:
            raise Warning("Can't set a parent on widget wich has a parent")
        if self.is_toplevel:
            raise Warning("Can't set a parent on a toplevel widget")
        self._parent = parent
        self.emit("parent-set", None)
        self.notify("parent")

        # Enforce realized/mapped invariants
        if parent.is_realized:
            self.realize()
        if parent.is_visible and self.is_visible:
            if self._child_visible and parent.is_mapped:
                self.map()
            self.queue_resize()

    def unparent(self):
        """
        Revert the effect of :meth:set_parent() to dissociate a child wigdet
        from the container.
        """
        if not self.parent:
            return
        self.freeze_notify()

        if self.is_realized:
            self.unrealize()
        self._child_visible = True

        old_parent = self.parent
        self._parent = None
        self.emit("parent-set", old_parent)
        self.notify("parent")
        self.thaw_notify()

    def set_visible(self, value):
        """Sets the visibility state of @widget. Note that settings this to
        %True doesn't mean the widget is actually viewable.

        This method simply calls @widget.show() or @wiget.hide() but is
        nicer to use when the visibility of the @widget depends on some
        condition.
        """
        if visible != self._visible:
            if visible:
                self.show()
            else:
                self.hide()

    def set_child_visible(self, is_visible):
        """
        This method is only useful for container implementations and never
        should be called by an application.
        """
        if self.is_toplevel:
            return
        if is_visible:
            self._child_visible = True
        else:
            self._child_visible = False

        if self.parent and self.parent.is_realized:
            if self.parent.is_mapped and\
               self._child_visible and\
               self.is_visible:
                   self.map()
            else:
                self.unmap()

    def get_toplevel(self):
        """
        Returns the topmost widget in the container hierarchy @widget is
        a part of. If @widget has no parent widgets, it will be returned
        as the topmost widget.
        """
        widget = self
        while widget._parent:
            widget = widget._parent
        return widget

    def ancesor_iter(self):
        """
        Iterates on ancesor hierarchy of the widget.
        """
        widget = self
        while widget._parent:
            widget = widget._parent
            yield widget

    @property
    def parent(self):
        return self._parent

    @property
    def is_toplevel(self):
        return self._toplevel

    @property
    def is_visible(self):
        return self._visible

    @property
    def is_mapped(self):
        return self._mapped

    @property
    def is_realized(self):
        return self._realized

    def path(self):
        names = [p.get_name() for p in self.ancesor_iter()] + [self.get_name()]
        return ".".join(names)

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
        widget's canvas and all its child canvas. Once the main loop becomes
        idle (after the current batch of events has been processed, roughly),
        the canvas will receive expose events for the union of all regions
        that have been invalidated.
        Normally you would use this method in wigdet implementations.
        """
        if not self.is_realized:
            return

        for ancesor in self.ancesor_iter():
            if not ancesor.is_realized:
                return

        log.debug("%s::queue_draw_area(x=%d, y=%d, width=%d, height=%d)",
                  self.name, x, y, width, height)

        if self.parent:
            self.parent.canvas.invalidate_area(Rectangle(x, y, width, height))
            # Translate widget relative to canvas-relative
            # Invalidate canvas region
            # Queue redraw screen
            pass

        toplevel = self.get_toplevel()
        if toplevel.is_toplevel:
            toplevel.queue_screen_draw()

    def queue_resize(self):
        """
        This method is only for use in widget implementations.
        Flags a widget to have its size renegotiated; should 
        be called when a widget for some reason has a new size request.
        For example, when you change the text in :class:utk.Label(),
        a resize is queued to ensure there's enough space for the new text.
        """
        if self.is_realized:
            log.debug("%s::queue_resize()" % self.name)
            self._alloc_needed = True
            self._request_needed = True
            if self.parent:
                self.parent._container_queue_resize()
            elif self.is_toplevel:
                self._container_queue_resize()
            else:
                assert False, "Not reach this line"

    ## get/set gproperties
    def do_get_property(self, prop):
        if prop.name == "name":
            return self.get_name()
        elif prop.name == "parent":
            return self._parent
        elif prop.name == "visible":
            return self._visible
        else:
            raise AttributeError("unknown property %s" % prop.name) # pragma: no cover

    def do_set_property(self, prop, value):
        if prop.name == "name":
            self.set_name(value)
        elif prop.name == "parent":
            if value is None:
                self.unparent()
            else:
                self.set_parent(value)
        elif prop.name == "visible":
            self.set_visible(value)
        else:
            raise AttributeError("unknown property %s" % prop.name) # pragma: no cover
