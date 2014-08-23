# -*- coding: utf-8 -*-

from utk.utils import int_scale

def test_int_scale():
    x = '%x' % int_scale(0x7, 0x10, 0x10000)
    assert x == '7777'
    x = '%x' % int_scale(0x5f, 0x100, 0x10)
    assert x == '6'
    i = int_scale(2, 6, 100)
    assert i == 40
    i = int_scale(1, 3, 4)
    assert i == 2
