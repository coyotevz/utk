# -*- coding: utf-8 -*-

import pytest
from tests.callback import NotifyPropCallback, SignalEmitCallback

from utk.widget import Widget
from utk.bin import Bin
from utk.window import Window

from utk.utils import Requisition, Rectangle


class BaseTest(object):

    def test_default_name(self):
        w = self.widget()
        assert w.name == self.default_name

class TestWidget(BaseTest):

    widget = Widget
    default_name = "UtkWidget"

    def test_set_get_name(self):
        w = self.widget()
        w.set_property("name", "WidgetName")
        assert w.get_name() == "WidgetName"
        w.set_name("TestWidget")
        assert w.get_property("name") == "TestWidget"

    def test_name_notify(self):
        on_notify_name = NotifyPropCallback('name')

        w = self.widget()
        w.connect("notify::name", on_notify_name)
        w.set_name("test-name")
        assert w.name == "test-name"
        assert on_notify_name.value == "test-name"
        w.name = "test-name-2"
        assert on_notify_name.value == "test-name-2"

    def test_unknown_property(self):
        w = self.widget()
        with pytest.raises(TypeError):
            w.set_property("unknown", None)
        with pytest.raises(TypeError):
            w.get_property("unknown-too")

    def test_initial_not_realized(self):
        w = self.widget()
        assert not w.is_realized

    def test_realize_no_parent(self):
        w = self.widget()
        with pytest.raises(Warning):
            w.realize()

    def test_realize_signal(self):
        w = self.widget()
        on_realize = SignalEmitCallback("realize")
        w.connect("realize", on_realize)
        if not w.is_toplevel:
            win = Window()
            win.add(w)
        w.realize()
        assert on_realize.called

    def test_realize_with_parent(self):
        w = self.widget()
        if not w.is_toplevel:
            win = Window()
            win.add(w)
        w.realize()
        assert w.is_realized
        w.unrealize()
        assert not w.is_realized

    def test_unrealize_signal(self):
        w = self.widget()
        on_unrealize = SignalEmitCallback("unrealize")
        w.connect("unrealize", on_unrealize)
        w.unrealize()
        assert not on_unrealize.called
        if not w.is_toplevel:
            win = Window()
            win.add(w)
        w.realize()
        w.unrealize()
        assert on_unrealize.called

    def test_unrealize(self):
        w = self.widget()
        if not w.is_toplevel:
            win = Window()
            win.add(w)
        w.realize()
        assert w.is_realized
        w.unrealize()
        assert not w.is_realized

    def test_size_request_signal(self):
        w = self.widget()
        on_size_request = SignalEmitCallback("size-request")
        w.connect("size-request", on_size_request)
        assert w._requisition is None
        w.size_request()
        assert on_size_request.called

    def test_size_request(self):
        w = self.widget()
        assert w._requisition is None
        req = w.size_request()
        assert isinstance(req, Requisition)
        assert w._requisition is req

    def test_size_allocate_signal(self):
        w = self.widget()
        on_size_allocate = SignalEmitCallback("size-allocate")
        w.connect("size-allocate", on_size_allocate)
        assert w._allocation == Rectangle()
        a = Rectangle(0, 0, 10, 10)
        w.size_allocate(a)
        assert on_size_allocate.called
        assert (on_size_allocate.data == a)

    def test_size_allocate(self):
        w = self.widget()
        assert w._allocation == Rectangle()
        a = Rectangle(0, 0, 10, 10)
        w.size_allocate(a)
        assert (w._allocation == a)

    def test_set_parent(self):
        w = self.widget()
        win = Window()
        w.set_parent(win)
        assert w.parent is win

    def test_set_parent_with_parent(self):
        w = self.widget()
        if w.is_toplevel:
            pytest.skip()
        win1 = Window()
        win2 = Window()
        w.set_parent(win1)
        with pytest.raises(Warning):
            w.set_parent(win2)
        assert w.parent is win1

    def test_set_parent_signal(self):
        w = self.widget()
        if w.is_toplevel:
            pytest.skip()
        win = Window()
        on_parent_set = SignalEmitCallback("parent-set")
        w.connect("parent-set", on_parent_set)
        w.set_parent(win)
        assert on_parent_set.called
        assert on_parent_set.data is None

    def test_unparent_with_parent(self):
        w = self.widget()
        if w.is_toplevel:
            pytest.skip()
        win = Window()
        w.set_property("parent", win)
        assert w.parent is not None
        w._realized = True
        w.unparent()
        assert w.parent is None
        w.unparent()

    def test_unparent_signal(self):
        w = self.widget()
        if w.is_toplevel:
            pytest.skip()
        win = Window()
        w.set_parent(win)
        on_parent_set = SignalEmitCallback("parent-set")
        w.connect("parent-set", on_parent_set)
        w.unparent()
        assert on_parent_set.called
        assert on_parent_set.data is win

    def test_parent_notify(self):
        w = self.widget()
        if w.is_toplevel:
            pytest.skip()
        win = Window()
        on_notify_parent = NotifyPropCallback("parent")
        w.connect("notify::parent", on_notify_parent)
        w.set_parent(win)
        assert on_notify_parent.value is win
        w.unparent()
        assert on_notify_parent.value is None

    def test_get_toplevel(self):
        w = self.widget()
        tl = w.get_toplevel()
        assert tl is w
        if not w.is_toplevel:
            b = Bin()
            win = Window()
            win.add(b)
            b.add(w)
            tl = w.get_toplevel()
            assert tl is win

    def test_is_toplevel(self):
        w = self.widget()
        assert not w.is_toplevel

    def test_ancesor_iter(self):
        w = self.widget()
        if w.is_toplevel:
            pytest.skip()
        b = Bin()
        win = Window()

        win.add(b)
        b.add(w)
        ancesors = list(w.ancesor_iter())
        assert ancesors == [b, win]
