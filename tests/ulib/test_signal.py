# -*- coding: utf-8 -*-

import pytest
from tests.callback import SignalEmitCallback

from utk.ulib import SIGNAL_RUN_FIRST, SIGNAL_RUN_LAST
from utk.ulib.utils import norm, unnorm
from utk.ulib.ssignal import SignalBase, Signal, SignaledObject, install_signal

def test_norm():
    assert norm('abc-def') == 'abc_def'
    assert norm('-def') == '_def'
    assert norm('abc-') == 'abc_'

def test_unnorm():
    assert unnorm('abc_def') == 'abc-def'
    assert unnorm('_def') == '-def'
    assert unnorm('abc_') == 'abc-'

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

    def test_disconnect(self):
        s = SignalBase('s')
        cb_1 = lambda x, *args: x
        cb_2 = lambda y, *args: y
        s.connect(cb_1)
        s.connect(cb_2)
        assert s._callbacks == [cb_1, cb_2]
        s.disconnect(cb_1)
        assert s._callbacks == [cb_2]
        s.disconnect(cb_2)
        assert s._callbacks == []

    def test_disconnect_after(self):
        s = SignalBase('s')
        cb_1 = lambda x, *args: x
        cb_2 = lambda y, *args: y
        s.connect_after(cb_1)
        s.connect_after(cb_2)
        assert s._callbacks_after == [cb_1, cb_2]
        s.disconnect_after(cb_1)
        assert s._callbacks_after == [cb_2]
        s.disconnect_after(cb_2)
        assert s._callbacks_after == []

    def test_connect_disconnect(self):
        s = SignalBase('s')
        cb_1 = lambda x, *args: x
        cb_2 = lambda y, *args: y
        s.connect(cb_1)
        s.connect_after(cb_2)
        with pytest.raises(ValueError):
            s.disconnect(cb_2)
        with pytest.raises(ValueError):
            s.disconnect_after(cb_1)

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

    def test_block_unblock(self):
        s = SignalBase('s')
        emit_t1 = SignalEmitCallback('emit_t1')
        emit_t2 = SignalEmitCallback('emit_t2')
        emit_t3 = SignalEmitCallback('emit_t3')
        handlers = [emit_t1, emit_t2, emit_t3]
        for h in handlers:
            s.connect(h)
        assert s._callbacks == handlers
        s.block(emit_t2)
        s.emit()
        assert emit_t1.called == True
        assert emit_t2.called == False
        assert emit_t3.called == True
        for h in handlers:
            h.called = False
        s.unblock(emit_t2)
        s.emit()
        for h in handlers:
            assert h.called == True

    def test_block_unblock_after(self):
        s = SignalBase('s')
        emit_t1 = SignalEmitCallback('emit_t1')
        emit_t2 = SignalEmitCallback('emit_t2')
        emit_t3 = SignalEmitCallback('emit_t3')
        handlers = [emit_t1, emit_t2, emit_t3]
        for h in handlers:
            s.connect_after(h)
        assert s._callbacks_after == handlers
        s.block(emit_t2)
        s.emit()
        assert emit_t1.called == True
        assert emit_t2.called == False
        assert emit_t3.called == True
        for h in handlers:
            h.called = False
        s.unblock(emit_t2)
        s.emit()
        for h in handlers:
            assert h.called == True

    def test_block_unblock_default(self):
        default_cb = SignalEmitCallback('default_cb')
        emit_t1 = SignalEmitCallback('emit_t1')
        emit_t2 = SignalEmitCallback('emit_t2')
        s = SignalBase('s', default_cb=default_cb)
        s.connect(emit_t1)
        s.connect_after(emit_t2)
        s.block_default()
        s.emit()
        assert emit_t1.called == True
        assert emit_t2.called == True
        assert default_cb.called == False
        s.unblock_default()
        for h in emit_t1, emit_t2, default_cb:
            h.called = False
        s.emit()
        assert emit_t1.called == True
        assert emit_t2.called == True
        assert default_cb.called == True

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


class TestSignal(object):

    def test_signal_named(self):
        class T(object):
            def __init__(self):
                self.custom_called = False
                self.test_signal = Signal("test-signal", "custom_handler", namespace=self)
            def custom_handler(self, *args):
                self.custom_called = True
        class R(T):
            def custom_handler(self, *args):
                self.custom_called = 'called'
        t = T()
        t.test_signal.emit()
        assert t.custom_called == True
        r = R()
        r.test_signal.emit()
        assert r.custom_called == 'called'

    def test_signal_default_prefix(self):
        class T(object):
            def __init__(self):
                self.called = False
                self.test_signal = Signal("test-signal", namespace=self)
            def do_test_signal(self, *args):
                self.called = True
        class R(T):
            def do_test_signal(self, *args):
                self.called = 'called'
        t = T()
        t.test_signal.emit()
        assert t.called == True
        r = R()
        r.test_signal.emit()
        assert r.called == 'called'

    def test_signal_custom_prefix(self):
        class T(object):
            def __init__(self):
                self.called = False
                self.test_signal = Signal("test-signal", namespace=self, prefix='on_')
            def on_test_signal(self, *args):
                self.called = True
        class R(T):
            def on_test_signal(self, *args):
                self.called = 'called'
        t = T()
        t.test_signal.emit()
        assert t.called == True
        r = R()
        r.test_signal.emit()
        assert r.called == 'called'


class TestSignaledObject(object):

    def test_signal_decl(self):
        class T(SignaledObject):
            __signals__ = { 'test-signal': None }
        t = T()
        assert hasattr(t, '_decl_signals')
        assert 'test-signal' in t._decl_signals

    def test_signal_wo_cb_raises(self):
        class T(SignaledObject):
            __signals__ = { 'test-signal': None }
        t = T()
        with pytest.raises(AttributeError):
            t.emit('test-signal')
        cb_1 = lambda x:x
        t.connect('test-signal', cb_1)
        with pytest.raises(AttributeError):
            t.emit('test-signal')

    def test_signal_emission(self):
        class T(SignaledObject):
            __signals__ = { 'test-signal': None }
            called = False
            def do_test_signal(self, *args):
                self.called = True
        t = T()
        cb_1 = SignalEmitCallback('cb_1')
        t.connect('test-signal', cb_1)
        t.emit('test-signal')
        assert t.called == True
        assert cb_1.called == True

    def test_individual_signals(self):
        class T(SignaledObject):
            __signals__ = {'test-signal': None}
            called = False
            def do_test_signal(self, *args):
                self.called = True
        t1 = T()
        t2 = T()
        cb_1 = SignalEmitCallback('cb_1')
        cb_2 = SignalEmitCallback('cb_2')
        t1.connect('test-signal', cb_1)
        t2.connect('test-signal', cb_2)
        t1.emit('test-signal')
        assert t1.called == True
        assert cb_1.called == True
        assert t2.called == False
        assert cb_2.called == False
        t1.called = False
        cb_1.called = False
        t2.emit('test-signal')
        assert t1.called == False
        assert cb_1.called == False
        assert t2.called == True
        assert cb_2.called == True
