# -*- coding: utf-8 -*-

import pytest
from tests.test_container import TestContainer

from utk.widget import Widget
from utk.bin import Bin


class TestBin(TestContainer):

    widget = Bin
    default_name = "UtkBin"

    def test_get_child(self):
        b = self.widget()
        w = Widget()
        assert b.child is None
        b.emit("add", w)
        assert b.get_child() is w

    def test_get_set_child_property(self):
        b = self.widget()
        w = Widget()
        b.set_property("child", w)
        assert b.get_property("child") is w
        assert w.parent is b

    def test_add(self):
        b = self.widget()
        w1 = Widget()
        w2 = Widget()
        b.add(w1)
        assert b.child is w1
        with pytest.raises(Warning):
            b.do_add(w2) # Needs to raise
        assert b.child is w1
        assert w1.parent is b

    def test_add_with_parent(self):
        b1 = self.widget()
        b2 = self.widget()
        w = Widget()
        b1.add(w)
        assert w.parent is b1
        with pytest.raises(Warning):
            b2.add(w)

    def test_remove(self):
        b = self.widget()
        w = Widget()
        b.add(w)
        assert b.child is w
        assert w.parent is b
        b.remove(w)
        assert b.child is None
        assert w.parent is None
        b.remove(w)

    def test_foreach(self):
        b = self.widget()
        w = Widget()
        b.add(w)
        def cb(child, data):
            assert child is w
        b.foreach(cb)
