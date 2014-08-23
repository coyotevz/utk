# -*- coding: utf-8 -*-

import pytest
from tests.test_bin import TestBin

from utk.window import Window

class TestWindow(TestBin):

    widget = Window
    default_name = "UtkWindow"

    def test_is_toplevel(self):
        w = self.widget()
        assert w.is_toplevel

    def test_set_parent(self):
        w = self.widget()
        win = Window()
        with pytest.raises(Warning):
            w.set_parent(win)

    def test_realize_no_parent(self):
        w = self.widget()
        w.realize()
        assert w.is_realized
