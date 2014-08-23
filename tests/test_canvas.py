# -*- coding: utf-8 -*-

from utk.canvas import Canvas
from utk.canvas import CanvasView
from utk.canvas import Shard
from utk.canvas import ShardBody
from utk.canvas import ShardTail

from utk.canvas import shard_body, shard_body_row, shard_body_tail
from utk.canvas import shards_trim_top, shards_trim_rows
from utk.canvas import shards_trim_sides, shards_join


class TestCanvasView(object):

    def cview(self):
        return CanvasView(5, 3, 25, 10, None, Canvas())

    def test_trim_rows(self):
        cv = self.cview()
        cv = cv.trim_rows(3)
        assert cv.rows == 3

    def test_trim_top(self):
        cv = self.cview()
        cv2 = cv.trim_top(5)
        assert cv2.top == 5+cv.top
        assert cv2.rows == cv.rows-5

    def test_trim_left(self):
        cv = self.cview()
        cv2 = cv.trim_left(10)
        assert cv2.left == 10+cv.left
        assert cv2.cols == cv.cols-10

    def test_trim_cols(self):
        cv = self.cview()
        cv = cv.trim_cols(1)
        assert cv.cols == 1


class TestCanvas(object):

    def sample_canvas(self):
        return [Canvas(0, 0, 80, 24),
                Canvas(1, 1, 10, 5),
                Canvas(40, 12, 10, 5)]

    def test_constructor(self):
        c = Canvas(10, 7, 8, 12)
        assert c.is_dirty
        assert c._area == (10, 7, 8, 12)
        assert c._update == [(10, 7, 8, 12)]
        assert not c._childs
        assert not c._parent


    def test_add_child(self):
        p, c1, c2 = self.sample_canvas()
        #p._dirty = False
        p.add_child(c1)
        assert p.is_dirty
        assert p._childs == [c1]
        assert p._update == [(0, 0, 80, 24),
                             (1, 1, 10, 5)]
        assert c1._parent is p
        p.add_child(c2)
        assert p._childs == [c1, c2]
        assert c2._parent is p
        assert p._update == [(0, 0, 80, 24),
                             (1, 1, 10, 5),
                             (40, 12, 10, 5)]

    def test_remove_child(self):
        p, c1, c2 = self.sample_canvas()
        p.add_child(c1)
        p.add_child(c2)
        p._dirty = False
        p._update = []

        p.remove_child(c1)
        assert p.is_dirty
        assert c1._parent is None
        assert p._childs == [c2]
        assert p._update == [(1, 1, 10, 5)]
        p.remove_child(c2)
        assert c2._parent == None
        assert not p._childs
        assert p._update == [(1, 1, 10, 5),
                             (40, 12, 10, 5)]
        p._update = []
        p._dirty = False
        p.remove_child(c1)

    def test_set_parent(self):
        p1, c1, c2 = self.sample_canvas()
        p2 = Canvas(10, 10, 20, 20)
        c1.set_parent(p1)
        c2.set_parent(p2)
        assert p1._childs == [c1]
        assert p2._childs == [c2]
        p1._update = []
        p2._update = []
        c2.set_parent(p1)
        assert c2._parent is p1
        assert not p2._childs
        assert p1._update == [(40, 12, 10, 5)]
        assert p2._update == [(40, 12, 10, 5)]
        p2.set_parent(p1)
        assert p1._update == [(40, 12, 10, 5),
                              (10, 10, 20, 20)]

    def test_unparent(self):
        p, c1, c2 = self.sample_canvas()
        p.add_child(c1)
        p.add_child(c2)
        assert c1._parent is p
        assert c2._parent is p
        p._update = []
        c1.unparent()
        assert c1._parent is None
        assert p._childs == [c2]
        assert p._update == [(1, 1, 10, 5)]
        c1.unparent()
        assert c1._parent is None
        assert p._update == [(1, 1, 10, 5)]

    def test_move_to(self):
        p, c1, c2 = self.sample_canvas()
        p.add_child(c1)
        p.add_child(c2)
        p._update = []
        c1.move_to()
        assert not p._update
        c1.move_to(1, 1)
        assert not p._update
        olda1 = c1._area
        c1.move_to(0, 0)
        newa1 = c1._area
        assert p._update == [olda1, newa1]
        olda2 = c2._area
        c2.move_to(1, 1)
        newa2 = c2._area
        assert p._update == [olda1, newa1, olda2, newa2]

    def test_move(self):
        p, c1, c2 = self.sample_canvas()
        p.add_child(c1)
        p.add_child(c2)
        p._update = []
        c1.move(0, 0)
        assert not p._update
        olda1 = c1._area
        c1.move(3, 5)
        newa1 = c1._area
        assert p._update == [olda1, newa1]
        olda2 = c2._area
        c2.move(-10, 2)
        newa2 = c2._area
        assert p._update == [olda1, newa1, olda2, newa2]

    def test_invalidate(self):
        c = self.sample_canvas()[1]
        c._dirty = None
        c._update = []
        c.invalidate()
        assert c.is_dirty
        assert c._update == [c._area]

    def test_invalidate_area(self):
        p, c1 = self.sample_canvas()[0:2]
        p.add_child(c1)
        p._dirty = False
        p._update = []
        c1._dirty = False
        c1._update = []
        c1.invalidate_area((0, 0, 5, 5))
        assert c1.is_dirty
        assert p.is_dirty
        assert c1._update == [(0, 0, 5, 5)]


def test_shard_body_row():
    sbody = [ShardBody(0, None, CanvasView(0, 0, 10, 5, None, "foo")),
             ShardBody(0, None, CanvasView(0, 0, 5, 5, None, "bar")),
             ShardBody(3, None, CanvasView(0, 0, 5, 8, None, "baz"))]
    result = shard_body_row(sbody)
    assert result == [20]

    sbody = [ShardBody(0, iter("foo"), CanvasView(0, 0, 10, 5, None, "foo")),
             ShardBody(0, iter("bar"), CanvasView(0, 0, 5, 5, None, "bar")),
             ShardBody(3, iter("zzz"), CanvasView(0, 0, 5, 8, None, "baz"))]
    result = shard_body_row(sbody)
    assert result == ["f", "b", "z"]

def test_shard_body_tail():
    sbody = [ShardBody(0, None, CanvasView(0, 0, 10, 5, None, "foo")),
             ShardBody(0, None, CanvasView(0, 0, 5, 5, None, "bar")),
             ShardBody(3, None, CanvasView(0, 0, 5, 8, None, "baz"))]
    result = shard_body_tail(5, sbody)
    assert result == []
    result = shard_body_tail(3, sbody)
    assert result == [(0, 3, None, (0, 0, 10, 5, None, "foo")),
                      (0, 3, None, (0, 0, 5, 5, None, "bar")),
                      (0, 6, None, (0, 0, 5, 8, None, "baz"))]

    sbody = [ShardBody(0, None, CanvasView(0, 0, 10, 3, None, "foo")),
             ShardBody(0, None, CanvasView(0, 0, 5, 5, None, "bar")),
             ShardBody(3, None, CanvasView(0, 0, 5, 9, None, "baz"))]
    result = shard_body_tail(3, sbody)
    assert result == [(10, 3, None, (0, 0, 5, 5, None, "bar")),
                      (0, 6, None, (0, 0, 5, 9, None, "baz"))]


def test_shard_body():
    cviews = [CanvasView(0, 0, 10, 5, None, "foo"),
              CanvasView(0, 0, 5, 5, None, "bar")]
    result = shard_body(cviews, [], False)
    assert result == [(0, None, cviews[0]),
                      (0, None, cviews[1])]
    bazcv = CanvasView(0, 0, 5, 8, None, "baz")
    stail = [ShardTail(0, 3, None, bazcv)]
    result = shard_body(cviews, stail, False)
    assert result == [(3, None, bazcv),
                      (0, None, cviews[0]),
                      (0, None, cviews[1])]
    stail = [ShardTail(10, 3, None, bazcv)]
    result = shard_body(cviews, stail, False)
    assert result == [(0, None, cviews[0]),
                      (3, None, bazcv),
                      (0, None, cviews[1])]
    stail = [ShardTail(15, 3, None, bazcv)]
    result = shard_body(cviews, stail, False)
    assert result == [(0, None, cviews[0]),
                      (0, None, cviews[1]),
                      (3, None, bazcv)]

def test_shards_trim_top():
    cviews = [CanvasView(0, 0, 10, 5, None, "foo"),
              CanvasView(0, 0, 5, 5, None, "bar")]
    shards = [Shard(5, cviews)]
    result = shards_trim_top(shards, 2)
    assert result == [(3, [(0, 2, 10, 3, None, "foo"),
                           (0, 2, 5, 3, None, "bar")])]
    cviews = [CanvasView(0, 0, 10, 5, None, "foo"),
              CanvasView(0, 0, 10, 3, None, "bar")]
    shards = [Shard(5, [cviews[0]]), Shard(3, [cviews[1]])]
    result = shards_trim_top(shards, 2)
    assert result == [(3, [(0, 2, 10, 3, None, "foo")]),
                      (3, [(0, 0, 10, 3, None, "bar")])]
    result = shards_trim_top(shards, 5)
    assert result == [(3, [(0, 0, 10, 3, None, "bar")])]
    result = shards_trim_top(shards, 7)
    assert result == [(1, [(0, 2, 10, 1, None, "bar")])]
    cviews = [CanvasView(0, 0, 10, 5, None, "foo"),
              CanvasView(0, 0, 5, 8, None, "baz")]
    shards = [Shard(5, cviews),
              Shard(3, [CanvasView(0, 0, 10, 3, None, "bar")])]
    result = shards_trim_top(shards, 2)
    assert result == [(3, [(0, 2, 10, 3, None, "foo"),
                           (0, 2, 5, 6, None, "baz")]),
                      (3, [(0, 0, 10, 3, None, "bar")])]
    result = shards_trim_top(shards, 5)
    assert result == [(3, [(0, 0, 10, 3, None, "bar"),
                           (0, 5, 5, 3, None, "baz")])]
    result = shards_trim_top(shards, 7)
    assert result == [(1, [(0, 2, 10, 1, None, "bar"),
                           (0, 7, 5, 1, None, "baz")])]

def test_shards_trim_rows():
    cviews = [CanvasView(0, 0, 10, 5, None, "foo"),
              CanvasView(0, 0, 5, 5, None, "bar")]
    shards = [Shard(5, cviews)]
    result = shards_trim_rows(shards, 2)
    assert result == [(2, [(0, 0, 10, 2, None, "foo"),
                           (0, 0, 5, 2, None, "bar")])]
    cviews = [CanvasView(0, 0, 10, 5, None, "foo"),
              CanvasView(0, 0, 10, 3, None, "bar")]
    shards = [Shard(5, [cviews[0]]), Shard(3, [cviews[1]])]
    result = shards_trim_rows(shards, 7)
    assert result == [(5, [(0, 0, 10, 5, None, "foo")]),
                      (2, [(0, 0, 10, 2, None, "bar")])]
    result = shards_trim_rows(shards, 5)
    assert result == [(5, [(0, 0, 10, 5, None, "foo")])]
    result = shards_trim_rows(shards, 4)
    assert result == [(4, [(0, 0, 10, 4, None, "foo")])]
    cviews = [CanvasView(0, 0, 10, 5, None, "foo"),
              CanvasView(0, 0, 5, 8, None, "baz")]
    shards = [Shard(5, cviews),
              Shard(3, [CanvasView(0, 0, 10, 3, None, "bar")])]
    result = shards_trim_rows(shards, 7)
    assert result == [(5, [(0, 0, 10, 5, None, "foo"),
                           (0, 0, 5, 7, None, "baz")]),
                      (2, [(0, 0, 10, 2, None, "bar")])]
    result = shards_trim_rows(shards, 5)
    assert result == [(5, [(0, 0, 10, 5, None, "foo"),
                           (0, 0, 5, 5, None, "baz")])]
    result = shards_trim_rows(shards, 4)
    assert result == [(4, [(0, 0, 10, 4, None, "foo"),
                           (0, 0, 5, 4, None, "baz")])]

def test_shards_trim_sides():
    cviews = [CanvasView(0, 0, 10, 5, None, "foo"),
              CanvasView(0, 0, 5, 5, None, "bar")]
    shards = [Shard(5, cviews)]
    result = shards_trim_sides(shards, 0, 15)
    assert result == [(5, [(0, 0, 10, 5, None, "foo"),
                           (0, 0, 5, 5, None, "bar")])]
    result = shards_trim_sides(shards, 6, 9)
    assert result == [(5, [(6, 0, 4, 5, None, "foo"),
                           (0, 0, 5, 5, None, "bar")])]
    result = shards_trim_sides(shards, 6, 6)
    assert result == [(5, [(6, 0, 4, 5, None, "foo"),
                           (0, 0, 2, 5, None, "bar")])]
    result = shards_trim_sides(shards, 0, 10)
    assert result == [(5, [(0, 0, 10, 5, None, "foo")])]
    result = shards_trim_sides(shards, 10, 5)
    assert result == [(5, [(0, 0, 5, 5, None, "bar")])]
    result = shards_trim_sides(shards, 1, 7)
    assert result == [(5, [(1, 0, 7, 5, None, "foo")])]

    cviews = [CanvasView(0, 0, 10, 5, None, "foo"),
              CanvasView(0, 0, 5, 8, None, "baz")]
    shards = [Shard(5, cviews),
              Shard(3, [CanvasView(0, 0, 10, 3, None, "bar")])]
    result = shards_trim_sides(shards, 0, 15)
    assert result == [(5, [(0, 0, 10, 5, None, "foo"),
                           (0, 0, 5, 8, None, "baz")]),
                      (3, [(0, 0, 10, 3, None, "bar")])]
    result = shards_trim_sides(shards, 2, 13)
    assert result == [(5, [(2, 0, 8, 5, None, "foo"),
                           (0, 0, 5, 8, None, "baz")]),
                      (3, [(2, 0, 8, 3, None, "bar")])]
    result = shards_trim_sides(shards, 2, 10)
    assert result == [(5, [(2, 0, 8, 5, None, "foo"),
                           (0, 0, 2, 8, None, "baz")]),
                      (3, [(2, 0, 8, 3, None, "bar")])]
    result = shards_trim_sides(shards, 2, 8)
    assert result == [(5, [(2, 0, 8, 5, None, "foo")]),
                      (3, [(2, 0, 8, 3, None, "bar")])]
    result = shards_trim_sides(shards, 2, 6)
    assert result == [(5, [(2, 0, 6, 5, None, "foo")]),
                      (3, [(2, 0, 6, 3, None, "bar")])]
    result = shards_trim_sides(shards, 10, 5)
    assert result == [(8, [(0, 0, 5, 8, None, "baz")])]
    result = shards_trim_sides(shards, 11, 3)
    assert result == [(8, [(1, 0, 3, 8, None, "baz")])]

def test_shards_join():
    shards1 = [Shard(5, [CanvasView(0, 0, 10, 5, None, "foo"),
                         CanvasView(0, 0, 5, 8, None, "baz")]),
               Shard(3, [CanvasView(0, 0, 10, 3, None, "bar")])]
    shards2 = [Shard(3, [CanvasView(0, 0, 10, 3, None, "aaa")]),
               Shard(5, [CanvasView(0, 0, 10, 5, None, "bbb")])]
    shards3 = [Shard(3, [CanvasView(0, 0, 10, 3, None, "111")]),
               Shard(2, [CanvasView(0, 0, 10, 3, None, "222")]),
               Shard(3, [CanvasView(0, 0, 10, 3, None, "333")])]

    result = shards_join([shards1])
    assert result == shards1
    result = shards_join([shards1, shards2])
    assert result == [(3, [(0, 0, 10, 5, None, "foo"),
                           (0, 0, 5, 8, None, "baz"),
                           (0, 0, 10, 3, None, "aaa")]),
                      (2, [(0, 0, 10, 5, None, "bbb")]),
                      (3, [(0, 0, 10, 3, None, "bar")])]
    result = shards_join([shards1, shards3])
    assert result == [(3, [(0, 0, 10, 5, None, "foo"),
                           (0, 0, 5, 8, None, "baz"),
                           (0, 0, 10, 3, None, "111")]),
                      (2, [(0, 0, 10, 3, None, "222")]),
                      (3, [(0, 0, 10, 3, None, "bar"),
                           (0, 0, 10, 3, None, "333")])]
    result = shards_join([shards1, shards2, shards3])
    assert result == [(3, [(0, 0, 10, 5, None, "foo"),
                           (0, 0, 5, 8, None, "baz"),
                           (0, 0, 10, 3, None, "aaa"),
                           (0, 0, 10, 3, None, "111")]),
                      (2, [(0, 0, 10, 5, None, "bbb"),
                           (0, 0, 10, 3, None, "222")]),
                      (3, [(0, 0, 10, 3, None, "bar"),
                           (0, 0, 10, 3, None, "333")])]

