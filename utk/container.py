# -*- coding: utf-8 -*-

"""
    utk.container
    ~~~~~~~~~~~~~

    Container is an abstract base class for widgets that contain other widgets.

    :copyright: 2011-2014 by Utk Authors
    :license: LGPL2 or later (see LICENSE)
"""

from gulib import usignal

from utk.widget import Widget

class Container(Widget):
    __type_name__ = "UtkContainer"

    # signals
    usignal("add")
    usignal("remove")
    usignal("foreach")

    def __init__(self):
        super(Container, self).__init__()
        self._border_width = 0

    def get_border_width(self):
        return self._border_width

    def set_border_width(self, border_width):
        if self._border_width != border_width:
            self._border_width = border_width
            self.notify("border-width")
            #TODO: call queue resize

    border_width = property(get_border_width, set_border_width)

    # "map" handler
    def do_map(self):

        def map_childrens(child, data):
            if child.is_visible and not child.is_mapped:
                child.map()
        self.foreach(map_childrens)
        super(Container, self).do_map()

    # "unmap" handler
    def do_unmap(self):
        super(Container, self).do_unmap()
        self.foreach(lambda w, d: w.unmap())

    def add(self, widget):
        if widget.parent:
            raise Warning("Attemping to add a widget to a container, but the "
                          "widget is already inside a container")
        self.emit("add", widget)

    def remove(self, widget):
        self.emit("remove", widget)

    def foreach(self, callback, data=None, include_internals=False):
        self.emit("foreach", callback, data, include_internals)
