# -*- coding: utf-8 -*-

import utk

def pytest_configure(config):
    utk._running_from_pytest = True

def pytest_unconfigure(config):
    utk._running_from_pytest = False
