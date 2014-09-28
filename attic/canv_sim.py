# -*- coding: utf-8 -*-

from collections import namedtuple

from utk.utils import Rectangle

class CanvasView(namedtuple("CanvasView", "left top cols rows canvas")):
    __slots__ = ()

    def content(self):
        return self.canvas.body_content(self.left, self.top,
                                        self.cols, self.rows)

    def trim_left(self, trim):
        return self._replace(left=self.left+trim,
                             cols=self.cols-trim)

    def trim_top(self, trim):
        return self._replace(top=self.top+trim,
                             rows=self.rows-trim)

    def trim_cols(self, cols):
        return self._replace(cols=cols)

    def trim_rows(self, rows):
        return self._replace(rows=rows)


# Shard structure is composed of number of rows that this shard have, and a
# list of CanvasView that generates the contents of shard rows
Shard = namedtuple("Shard", "rows views")


class Canvas(object):

    def __init__(self, left=0, top=0, cols=1, rows=1):
        self._childs = []
        self._parent = None
        self._area = Rectangle(left, top, cols, rows)
        self._invalids = set() # areas to update
        self._shards = None
        self.invalidate()

    # shortcuts
    left = property(lambda s: s._area.x)
    top = property(lambda s: s._area.y)
    cols = property(lambda s: s._area.width)
    rows = property(lambda s: s._area.height)

    is_dirty = property(lambda s: bool(len(s._invalids)))

    def invalidate_area(self, area):
        self._invalids.add(area)
        if self._parent:
            self._parent.invalidate_area(area)

    def invalidate(self):
        self.invalidate_area(self._area)

    @property
    def shards(self):
        if not self.is_dirty:
            return self._shards

        shard = Shard(self.rows,
                      [CanvasView(0, 0, self.cols, self.rows, self)])

        self._shards = [shard]
        self._invalids.clear()
        return self._shards
