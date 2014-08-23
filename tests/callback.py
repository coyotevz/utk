# -*- coding: utf-8 -*-

class NotifyPropCallback(object):

    def __init__(self, prop):
        self.prop = prop
        self.value = None

    def __call__(self, widget, prop):
        if prop.name == self.prop:
            self.value = widget.get_property(self.prop)


class SignalEmitCallback(object):

    def __init__(self, signal=None):
        self.signal = signal
        self.called = False

    def __call__(self, widget, data=None, *args):
        self.called = True
        self.data = data
        self.args = args
        return True
