# -*- coding: utf-8 -*-

import pytest
from tests.callback import NotifyPropCallback
from tests.test_container import TestContainer

from utk.widget import Widget
from utk.box import Box, ORIENTATION_HORIZONTAL, ORIENTATION_VERTICAL
from utk.box import HBox, VBox


class TestBox(TestContainer):

    widget = Box
    default_name = "UtkBox"
    initial_orientation = ORIENTATION_HORIZONTAL

    def test_get_set_orientation(self):
        b = self.widget()
        assert b.get_property("orientation") == self.initial_orientation
        b.set_property("orientation", ORIENTATION_VERTICAL)
        assert b._orientation == ORIENTATION_VERTICAL

    def test_orientation_notify(self):
        on_orientation_notify = NotifyPropCallback('orientation')

        w = self.widget()
        w.connect("notify::orientation", on_orientation_notify)
        w.set_orientation(ORIENTATION_VERTICAL)
        assert w.orientation == ORIENTATION_VERTICAL
        assert on_orientation_notify.value == ORIENTATION_VERTICAL
        w.orientation = ORIENTATION_HORIZONTAL
        assert on_orientation_notify.value == ORIENTATION_HORIZONTAL

    def test_add(self):
        b = self.widget()
        w1 = Widget()
        w2 = Widget()
        w3 = Widget()

        b.add(w1)
        b.add(w2)
        b.add(w3)

        assert [c.widget for c in b._childs] == [w1, w2, w3]
        assert list(b.get_children()) == [w1, w2, w3]

    def test_add_with_parent(self):
        b1 = self.widget()
        b2 = self.widget()
        w = Widget()
        b1.add(w)
        assert w.parent is b1
        with pytest.raises(Warning):
            b2.add(w)


    def test_pack_start_end(self):
        b = self.widget()
        w1 = Widget()
        w2 = Widget()
        w3 = Widget()
        w4 = Widget()

        b.pack_end(w4)
        b.pack_start(w1)
        b.pack_end(w3)
        b.pack_start(w2)

        assert [c.widget for c in b._childs] == [w4, w1, w3, w2]
        assert list(b.get_children()) == [w1, w2, w3, w4]

    def test_remove(self):
        b = self.widget()
        w1 = Widget()
        w2 = Widget()
        w3 = Widget()

        b.pack_start(w1)
        b.pack_start(w2)

        assert w1.parent is b
        assert w2.parent is b

        b.remove(w2)

        assert w2 not in list(b.get_children())
        assert w2.parent is None

        b.remove(w3)
        b.remove(w1)

        assert not b._childs

    def test_foreach(self):
        b = self.widget()
        w1 = Widget()
        w2 = Widget()
        w3 = Widget()
        w4 = Widget()

        b.pack_end(w4)
        b.pack_start(w1)
        b.pack_end(w3)
        b.pack_start(w2)

        wl = []
        def cb(child, d=None):
            wl.append(child)

        b.foreach(cb)
        assert wl == [w1, w2, w3, w4]

    def test_hbox(self):
        hb = HBox()
        assert hb.get_orientation() == ORIENTATION_HORIZONTAL

    def test_vbox(self):
        vb = VBox()
        assert vb.get_orientation() == ORIENTATION_VERTICAL
