# -*- coding: utf-8 -*-

from tests.test_misc import TestMisc
from tests.callback import NotifyPropCallback

from utk.label import Label

class TestLabel(TestMisc):

    widget = Label
    default_name = "UtkLabel"

    def test_constructor(self):
        l = self.widget()
        assert not l.text
        l = self.widget("test")
        assert l.text == "test"

    def test_text_property(self):
        l = self.widget()
        on_text_notify = NotifyPropCallback("text")
        l.connect("notify::text", on_text_notify)
        l.set_property("text", "test-2")
        assert on_text_notify.value == "test-2"
        l.text = "test-3"
        assert on_text_notify.value == "test-3"
        assert l.text == "test-3"

    def test_set_text(self):
        l = self.widget("t")
        on_text_notify = NotifyPropCallback("text")
        l.connect("notify::text", on_text_notify)
        l.set_text(l.get_text() + " t")
        assert l.text == "t t"
        assert on_text_notify.value == "t t"
