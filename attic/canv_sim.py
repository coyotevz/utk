# -*- coding: utf-8 -*-

from utk.utils import Rectangle

class Canvas(object):

    def __init__(self, left=0, top=0, cols=1, rows=1):
        self._childs = []
        self._parent = None
        self._area = Rectangle(left, top, cols, rows)
        self._update= set() # areas to update
        self.invalidate()

    # shortcuts
    left = property(lambda s: s._area.x)
    top = property(lambda s: s._area.y)
    cols = property(lambda s: s._area.width)
    rows = property(lambda s: s._area.height)

    def _set_dirty(self):
        self._dirty = True
        if self._parent:
            self._parent._set_dirty()

    def _unset_dirty(self):
        self._dirty = False

    def invalidate_area(self, area):
        if self._parent:
            self._parent.invalidate_area(area)
        self._update.add(area)
        self._set_dirty()

    def invalidate(self):
        self.invalidate_area(self._area)
