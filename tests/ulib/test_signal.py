# -*- coding: utf-8 -*-

from tests.callback import SignalEmitCallback

from utk.ulib import SIGNAL_RUN_FIRST, SIGNAL_RUN_LAST
from utk.ulib.signal import _norm, _unnorm
from utk.ulib.signal import SignalBase

def test_norm():
    assert _norm('abc-def') == 'abc_def'
    assert _norm('-def') == '_def'
    assert _norm('abc-') == 'abc_'

def test_unnorm():
    assert _unnorm('abc_def') == 'abc-def'
    assert _unnorm('_def') == '-def'
    assert _unnorm('abc_') == 'abc-'

class TestSignalBase(object):

    def test_constructor(self):
        s = SignalBase('s')
        assert s.name == 's'
        assert s._default_cb is None
        assert s._flag is SIGNAL_RUN_LAST

    def test_default_callback(self):
        default_cb = lambda x, *args: x
        s = SignalBase('s', default_cb=default_cb)
        assert s._default_cb == default_cb

    def test_connect(self):
        s = SignalBase('s')
        test_emit = SignalEmitCallback('test')
        cb = lambda x, *args: x
        s.connect(cb)
        assert s._callbacks == [cb]

    def test_multi_connect(self):
        s = SignalBase('s')
        cb_1 = lambda x, *args: x
        cb_2 = lambda y, *args: y
        s.connect(cb_1)
        assert s._callbacks == [cb_1]
        s.connect(cb_2)
        assert s._callbacks == [cb_1, cb_2]

    def test_connect_after(self):
        s = SignalBase('s')
        cb_1 = lambda x, *args: x
        cb_2 = lambda y, *args: y
        s.connect_after(cb_1)
        assert s._callbacks_after == [cb_1]
        s.connect_after(cb_2)
        assert s._callbacks_after == [cb_1, cb_2]

    def test_emit_default_cb(self):
        default_cb = SignalEmitCallback('default_cb')
        s = SignalBase('s', default_cb=default_cb)
        s.emit()
        assert default_cb.called

    def test_emit_connected(self):
        s = SignalBase('s')
        emit_t1 = SignalEmitCallback('emit_t1')
        emit_t2 = SignalEmitCallback('emit_t2')
        s.connect(emit_t1)
        s.connect(emit_t2)
        s.emit()
        assert emit_t1.called
        assert emit_t2.called

    def test_emit_connected_order(self):
        default_cb = SignalEmitCallback('default_cb')
        s = SignalBase('s', default_cb=default_cb)
        emit_t1 = SignalEmitCallback('emit_t1')
        emit_t2 = SignalEmitCallback('emit_t2')
        after_t1 = SignalEmitCallback('after_t1')
        after_t2 = SignalEmitCallback('after_t1')
        s.connect(emit_t1)
        s.connect_after(after_t1)
        s.connect_after(after_t2)
        s.connect(emit_t2)
        s.emit()
        assert emit_t1.order_count < emit_t2.order_count
        assert emit_t2.order_count < default_cb.order_count
        assert default_cb.order_count < after_t1.order_count
        assert after_t1.order_count < after_t2.order_count

    def test_run_first_callback(self):
        default_cb = SignalEmitCallback('default_cb')
        s = SignalBase('s', default_cb=default_cb, flag=SIGNAL_RUN_FIRST)
        emit_t1 = SignalEmitCallback('emit_t1')
        s.connect(emit_t1)
        s.emit()
        assert default_cb.called
        assert emit_t1.called
        assert default_cb.order_count < emit_t1.order_count

    def test_stop_emission(self):
        s = SignalBase('s')
        emit_t1 = SignalEmitCallback('emit_t1')
        emit_t2 = SignalEmitCallback('emit_t2')

        def stop(*args):
            s.stop_emission()

        s.connect(emit_t1)
        s.connect(stop)
        s.connect(emit_t2)

        s.emit()

        assert emit_t1.called
        assert not emit_t2.called
