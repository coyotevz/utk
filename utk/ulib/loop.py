# -*- coding: utf-8 -*-

from context import main_context_default

class MainLoop(object):

    def __init__(self, context=None):
        if context is None:
            context = main_context_default()
        self._context = context
        self._stopped = True

    def get_context(self):
        """
        Returns the :class:`MainContext` of loop.
        """
        return self._context

    def run(self):
        """
        Start the loop. Exit the loop when any callback call :meth:`quit`.
        """
        self._stopped = False
        self._context._did_something = True
        while not self._stopped:
            self._context.iteration()

    def quit(self):
        """
        Stops a :class:`MainLoop` loop.
        """
        self._stopped = True

    def is_running(self):
        """
        Checks to see if the main loop is currently being run via :meth:`run`.
        """
        return not self._stopped
