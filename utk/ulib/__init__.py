# -*- coding: utf-8 -*-

from signals import (
    SIGNAL_RUN_FIRST,
    SIGNAL_RUN_LAST,
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
