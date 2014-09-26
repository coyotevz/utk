# -*- coding: utf-8 -*-

from utk.utils import Rectangle

def diff(r1, r2):
    i = r1.intersection(r2)
    res = []
    if r1.y < i.y:
        res.append(Rectangle(r1.x, r1.y, r1.width, (r1.height+r1.y)-(i.height+i.y)))
    if r1.x < i.x:
        res.append(Rectangle(r1.x, i.y, (r1.width+r1.x)-(i.width+i.x), i.height))

    return res if res else None

class Canvas(object):

    def __init__(self, left=0, top=0, cols=1, rows=1):
        self._childs = []
        self._parent = None
        self._area = Rectangle(left, top, cols, rows)
        self._invalids = set() # areas to update
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

    def _add_invalid(self, area):
        self._invalids.add(area)
        if self._parent:
            self._parent.invalidate_area(area)

    def invalidate_area(self, area):
        self._add_invalid(area)
        self._set_dirty()

    def invalidate(self):
        self.invalidate_area(self._area)
