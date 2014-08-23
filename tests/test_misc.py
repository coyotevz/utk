# -*- coding: utf-8 -*-

from tests.test_widget import TestWidget
from tests.callback import NotifyPropCallback

from utk.misc import Misc


class TestMisc(TestWidget):

    widget = Misc
    default_name = "UtkMisc"

    def test_align(self):
        m = self.widget()
        assert m.xalign == 0.5
        assert m.yalign == 0.5
        on_xalign_notify = NotifyPropCallback("xalign")
        on_yalign_notify = NotifyPropCallback("yalign")
        m.connect("notify::xalign", on_xalign_notify)
        m.connect("notify::yalign", on_yalign_notify)
        m.set_property("yalign", 0.8)
        assert m.yalign == 0.8
        assert on_yalign_notify.value == 0.8
        assert on_xalign_notify.value is None
        on_yalign_notify.value = None
        m.set_property("xalign", 0.1)
        assert m.get_property("xalign") == 0.1
        assert on_xalign_notify.value == 0.1
        assert on_yalign_notify.value is None
        on_xalign_notify.value = None
        m.set_alignment(xalign=1.5, yalign=-1.2)
        assert m.xalign == 1.0
        assert m.yalign == 0.0
        assert on_xalign_notify.value == 1.0
        assert on_yalign_notify.value == 0.0

    def test_pad(self):
        m = self.widget()
        assert m.xpad == 0
        assert m.ypad == 0
        on_xpad_notify = NotifyPropCallback("xpad")
        on_ypad_notify = NotifyPropCallback("ypad")
        m.connect("notify::xpad", on_xpad_notify)
        m.connect("notify::ypad", on_ypad_notify)
        m.set_property("ypad", 3)
        assert m.ypad == 3
        assert on_ypad_notify.value == 3
        assert on_xpad_notify.value is None
        on_ypad_notify.value = None
        m.set_property("xpad", 1)
        assert m.get_property("xpad") == 1
        assert on_xpad_notify.value == 1
        m.xpad = 0
        on_xpad_notify.value = None
        m.xpad = -5
        # there was not change so no notify
        assert on_xpad_notify.value is None
        assert on_ypad_notify.value is None
        on_xpad_notify.value = None
        m.set_padding(xpad = 8, ypad=-3)
        assert m.xpad == 8
        assert m.ypad == 0
        assert on_xpad_notify.value == 8
        assert on_ypad_notify.value == 0
