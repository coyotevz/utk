# -*- coding: utf-8 -*-

from tests.test_widget import TestWidget
from tests.callback import SignalEmitCallback

from utk.widget import Widget
from utk.container import Container


class TestContainer(TestWidget):

    widget = Container
    default_name = "UtkContainer"

    def test_add_signal(self):
        c = self.widget()
        w = Widget()
        on_add = SignalEmitCallback("add")
        c.connect("add", on_add)
        c.add(w)
        assert on_add.called
        assert on_add.data is w

    def test_remove_signal(self):
        c = self.widget()
        w = Widget()
        c.add(w)
        on_remove = SignalEmitCallback("remove")
        c.connect("remove", on_remove)
        c.remove(w)
        assert on_remove.called
        assert on_remove.data is w

    def test_foreach_signal(self):
        cb = lambda *a: None
        w1 = self.widget()
        w2 = Widget()
        w1.add(w2)
        on_foreach = SignalEmitCallback("foreach")
        w1.connect("foreach", on_foreach)
        w1.foreach(cb, "data")
        assert on_foreach.called
        assert on_foreach.data == cb
        assert on_foreach.args == ("data", False)
