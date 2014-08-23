# -*- coding: utf-8 -*-

from tests.callback import SignalEmitCallback

from utk.ulib import SIGNAL_RUN_FIRST, SIGNAL_RUN_LAST
from utk.ulib.signal import SignalBase

class TestSignalBase(object):

    def test_constructor(self):
        s = SignalBase('s')
        assert s.name == 's'
        assert s._default_cb is None
        assert s._flag is SIGNAL_RUN_LAST

    def test_callback(self):
        s = SignalBase('s')
        test_emit = SignalEmitCallback('test')
        s.connect(test_emit)
        s.emit()
        assert test_emit.called
