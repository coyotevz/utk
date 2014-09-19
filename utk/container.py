# -*- coding: utf-8 -*-

"""
    utk.container
    ~~~~~~~~~~~~~

    Container is an abstract base class for widgets that contain other widgets.

    :copyright: 2011-2014 by Utk Authors
    :license: LGPL2 or later (see LICENSE)
"""

from utk.widget import Widget

class Container(Widget):
    __type_name__ = "UtkContainer"

    def __init__(self):
        super(Container, self).__init__()
