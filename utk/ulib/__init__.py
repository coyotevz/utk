# -*- coding: utf-8 -*-

import sys

from signals import (
    SIGNAL_RUN_FIRST,
    SIGNAL_RUN_LAST,
    SignaledObject,
)

from context import (
    PRIORITY_HIGH,
    PRIORITY_DEFAULT,
    PRIORITY_HIGH_IDLE,
    PRIORITY_LOW,
    PRIORITY_DEFAULT_IDLE,
    main_context_default,
    MainContext,
)

from loop import (
    MainLoop,
)

from properties import (
    uproperty,
    PropertiedObject,
)

# some shortcuts to work with main context
def idle_add(callback, priority=PRIORITY_DEFAULT_IDLE, context=None):
    if context is None:
        context = main_context_default()
    return context.idle_add(callback, priority)

def idle_remove(handle, context=None):
    if context is None:
        context = main_context_default()
    return context.idle_remove(handle)

def timeout_add_seconds(seconds, callback, context=None):
    if context is None:
        context = main_context_default()
    return context.timeout_add_seconds(seconds, callback)

def timeout_remove(handle, context=None):
    if context is None:
        context = main_context_default()
    return context.timeout_remove(handle)

def io_add_watch(fd, callback, context=None):
    if context is None:
        context = main_context_default()
    return context.io_add_watch(fd, callback)

def io_remove_watch(handle, context=None):
    if context is None:
        context = main_context_default()
    return context.io_remove_watch(handle)

def type_name(obj):
    return obj.__type_name__

# signals utilities
def usignal(name, *args, **kwargs):
    """
    Add a UObject signal to the current object.
    """
    frame = sys._getframe(1)
    try:
        f_locals = frame.f_locals
    finally:
        del frame

    signals = f_locals.setdefault('__signals__', {})

    if args and args[0] == 'override':
        signals[name] = 'override'
    else:
        retval = kwargs.get('retval', None)
        if retval is None:
            default_flags = SIGNAL_RUN_FIRST
        else:
            default_flags = SIGNAL_RUN_LAST

        flags = kwargs.get('flags', default_flags)
        if retval is not None and flags != SIGNAL_RUN_LAST:
            raise TypeError(
                "You cannot use a return value without setting flags to "
                "ulib.SIGNAL_RUN_LAST")
        signals[name] = (flags, retval, args)


# properties utilities
_MAX_VALUES = {
    int: 0x7fffffff,
    float: float(2**1024 - 2**971),
    long: sys.maxint
}
_DEFAULT_VALUES = {
    str: '',
    float: 0.0,
    int: 0,
    long: 0L
}

from signals import SignaledMeta
from properties import PropertiedMeta

class UObjectMeta(SignaledMeta, PropertiedMeta):
    pass

# main class to inherit
class UObject(object):
    __metaclass__= UObjectMeta

# remove metaclasses from namespace
del SignaledMeta, PropertiedMeta
