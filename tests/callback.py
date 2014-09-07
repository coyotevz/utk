# -*- coding: utf-8 -*-

class NotifyPropCallback(object):

    def __init__(self, prop):
        self.prop = prop
        self.value = None

    def __call__(self, widget, *args):
        self.value = widget.get_property(self.prop)


class SignalEmitCallback(object):

    order_count = 0

    def __init__(self, signal=None):
        self.signal = signal
        self.called = False

    def __call__(self, widget=None, data=None, *args):
        self.called = True
        self.data = data
        self.args = args
        self.order_count = SignalEmitCallback.order_count
        SignalEmitCallback.order_count += 1
        return True
