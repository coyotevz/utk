# -*- coding: utf-8 -*-

import time
import select
import heapq

PRIORITY_HIGH         = -100
PRIORITY_DEFAULT      =    0
PRIORITY_HIGH_IDLE    =  100
PRIORITY_DEFAULT_IDLE =  200
PRIORITY_LOW          =  300

class MainContext(object):

    def __init__(self):
        self._alarms = []
        self._watch_files = {}
        self._idle_callbacks = []
        self._did_something = False

    def iteration(self):
        """
        A single context iteration
        """
        fds = self._watch_files.keys()
        if self._alarms or self._did_something:
            if self._alarms:
                tm = self._alarms[0][0]
                timeout = max(0, tm-time.time())
            if self._did_something and (not self._alarms or timeout > 0):
                timeout = 0
                tm = 'idle'
            ready, w, err = select.select(fds, [], fds, timeout)
        else:
            tm = None
            ready, w, err = select.select(fds, [], fds)

        if not ready:
            if tm == 'idle':
                self._did_something = False
                self._dispatch_idle()
            elif tm is not None:
                # must gave been a timeout
                tm, alarm_callback = self._alarms.pop(0)
                alarm_callback()
                self._did_something = True

        for fd in ready:
            self._watch_files[fd]()
            self._did_something = True

    def _dispatch_idle(self):
        """
        Call top most priority registered idle callback.
        """
        if self._idle_callbacks:
            priority, idle_callback = self._idle_callbacks.pop(0)
            idle_callback()
            self._did_something = True

    def idle_add(self, callback, priority=PRIORITY_DEFAULT_IDLE):
        """
        Add a callback for idle.

        Returns a handle that may be passed to :meth:`idle_remove`
        """
        heapq.heappush(self._idle_callbacks, (priority, callback))
        return (priority, callback)

    def idle_remove(self, handle):
        """
        Remove an idle callback.

        Returns ``True`` if the handle was removed.
        """
        try:
            self._idle_callbacks.remove(handle)
            heapq.heapify(self._idle_callbacks)
            return True
        except ValueError:
            return False

    def timeout_add_seconds(self, seconds, callback):
        """
        Call callback() given time from now. No parameters are passed to
        callback.

        Returns a handle that may be passed to :`timeout_remove`
        """
        tm = time.time() + seconds
        heapq.heappush(self._alarms, (tm, callback))
        return (tm, callback)

    def timeout_remove(self, handle):
        """
        Remove a timeout callback added with :meth:`timeout_add_seconds`
        method.

        Return ``True`` if the handle was removed.
        """
        try:
            self._alarms.remove(handle)
            heapq.heapify(self._alarms)
            return True
        except ValueError:
            return False

    def io_add_watch(self, fd, callback):
        """
        Call callback() when fd has some data to read. No parameters are passed
        to callback.

        Returns a handle that may be passed to :meth:`io_remove_watch`.
        """
        # FIXME: This only support one callback per file
        self._watch_files[fd] = callback
        return fd, callback

    def io_remove_watch(self, handle):
        """
        Remove an input file watcher.

        Returns ``True`` if the handle was removed.
        """
        if handle in self._watch_files:
            del self._wathc_files[handle]
            return True
        return False

    def pending(self):
        """
        Checks if any sources have pending event for the given context.
        """
        fds = self._watch_files.keys()
        timeout = -1
        if self._alarms:
            tm = self._alarms[0][0]
            timeout = max(0, tm-time.time())
        ready, w, err = select.select(fds, [], fds, 0)
        return bool(ready or timeout) or self._did_something


_default_main_context = None

def main_context_default():
    """
    Returns the global default main context. This is the main context used for
    main loop functions when a main loop is not explicity specified, and
    corresponds to the "main" main loop.
    """
    global _default_main_context
    if not _default_main_context:
        _default_main_context = MainContext()
    return _default_main_context
