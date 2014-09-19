# -*- coding: utf-8 -*-

"""
    utk.bin
    ~~~~~~~

    Bin can hold only one child.

    :copyright: 2011-2014 by Utk Authors.
    :license: LGPL2 or later (see LICENSE)
"""

from utk.container import Container

class Bin(Container):
    __type_name__ = "UtkBin"

    def __init__(self):
        super(Bin, self).__init__()
