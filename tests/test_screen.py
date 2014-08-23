# -*- coding: utf-8 -*-

import pytest
from tests.callback import SignalEmitCallback

from utk.screen import (
    _value_lookup_table, _color_desc_256, _color_desc_88,
    _parse_color_256, _parse_color_88,
    AttrSpec, AttrSpecError,
    BaseScreen,
)

def test_value_lookup_table():
    r = _value_lookup_table([0, 7, 9], 10)
    assert r == [0, 0, 0, 0, 1, 1, 1, 1, 2, 2]


def test_color_desc_256():
    c = _color_desc_256(15)
    assert c == 'h15'
    c = _color_desc_256(16)
    assert c == '#000'
    c = _color_desc_256(17)
    assert c == '#006'
    c = _color_desc_256(230)
    assert c == '#ffd'
    c = _color_desc_256(233)
    assert c == 'g7'
    c = _color_desc_256(234)
    assert c == 'g11'
    with pytest.raises(AssertionError):
        c = _color_desc_256(-1)
    with pytest.raises(AssertionError):
        c = _color_desc_256(256)


def test_color_desc_88():
    c = _color_desc_88(15)
    assert c == 'h15'
    c = _color_desc_88(16)
    assert c == '#000'
    c = _color_desc_88(17)
    assert c == '#008'
    c = _color_desc_88(78)
    assert c == '#ffc'
    c = _color_desc_88(81)
    assert c == 'g36'
    c = _color_desc_88(82)
    assert c == 'g45'
    with pytest.raises(AssertionError):
        c = _color_desc_88(-1)
    with pytest.raises(AssertionError):
        c = _color_desc_88(88)


def test_parse_color_256():
    c = _parse_color_256('h142')
    assert c == 142
    c = _parse_color_256('#f00')
    assert c == 196
    c = _parse_color_256('g100')
    assert c == 231
    c = _parse_color_256('g#80')
    assert c == 244
    c = _parse_color_256('inva')
    assert c is None


def test_parse_color_88():
    c = _parse_color_88('h142')
    assert c is None
    c = _parse_color_88('h42')
    assert c == 42
    c = _parse_color_88('#f00')
    assert c == 64
    c = _parse_color_88('g100')
    assert c == 79
    c = _parse_color_88('g#80')
    assert c == 83


def test_AttrSpec():
    a = AttrSpec('dark red', 'light gray', 16)
    assert a.foreground == 'dark red'
    assert a.background == 'light gray'
    a = AttrSpec('yellow, underline, bold', 'dark blue')
    assert a.foreground == 'yellow,bold,underline'
    assert a.background == 'dark blue'
    a = AttrSpec('#ddb', '#004', 256) # closest colors will be found
    assert a.foreground == '#dda'
    assert a.background == '#006'
    a = AttrSpec('#ddb', '#004', 88)
    assert a.foreground == '#ccc'
    assert a.background == '#000'
    assert a.colors == 88
    with pytest.raises(AttrSpecError):
        a = AttrSpec('#000', '#fff', 2)

    rgb = AttrSpec('yellow', '#ccf', colors=88).get_rgb_values()
    assert rgb == (255, 255, 0, 205, 205, 255)
    rgb = AttrSpec('default', 'g92').get_rgb_values()
    assert rgb == (None, None, None, 238, 238, 238)


class FakeBaseScreen(BaseScreen):

    def __init__(self):
        super(FakeBaseScreen, self).__init__()

    def do_start(self):
        self._started = True

    def do_stop(self):
        self._started = False

    def do_get_cols_rows(self):
        return 80, 24


class TestBaseScreen(object):

    def test_start_signal(self):
        bs = FakeBaseScreen()
        assert not bs.started
        on_start = SignalEmitCallback("start")
        bs.connect("start", on_start)
        bs.start()
        assert on_start.called
        assert bs.started
        on_start.called = False
        bs.start() # yet started
        assert not on_start.called

    def test_stop_signal(self):
        bs = FakeBaseScreen()
        on_stop = SignalEmitCallback("stop")
        bs.connect("stop", on_stop)
        bs.stop() # not yet started
        assert not on_stop.called
        bs._started = True
        bs.stop()
        assert not bs.started
        assert on_stop.called


    def test_clear_signal(self):
        bs = FakeBaseScreen()
        on_clear = SignalEmitCallback("clear")
        bs.connect("clear", on_clear)
        bs.clear()
        assert on_clear.called

    def test_get_cols_rows_signal(self):
        bs = FakeBaseScreen()
        on_get_cols_rows = SignalEmitCallback("get-cols-rows")
        bs.connect("get-cols-rows", on_get_cols_rows)
        cols, rows = bs.get_cols_rows()
        assert cols == 80 and rows == 24
        assert on_get_cols_rows.called

    def test_draw_screen_signal(self):
        bs = FakeBaseScreen()
        on_draw_screen = SignalEmitCallback("draw-screen")
        bs.connect("draw-screen", on_draw_screen)
        bs.draw_screen()
        assert on_draw_screen.called
