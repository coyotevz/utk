# -*- coding: utf-8 -*-

import pytest

from utk import text_layout as tl
from utk.text_layout import StandardTextLayout

class TestStandardTextLayout(object):

    def test_supports_align_mode(self):
        l = StandardTextLayout()
        assert l.supports_align_mode(tl.ALIGN_LEFT)
        assert l.supports_align_mode(tl.ALIGN_CENTER)
        assert l.supports_align_mode(tl.ALIGN_RIGHT)
        assert l.supports_align_mode("no-align") == False

    def test_supports_wrap_mode(self):
        l = StandardTextLayout()
        assert l.supports_wrap_mode(tl.WRAP_ANY)
        assert l.supports_wrap_mode(tl.WRAP_SPACE)
        assert l.supports_wrap_mode(tl.WRAP_CLIP)
        assert l.supports_wrap_mode("no-wrap") == False


class TestLayoutSegment(object):

    def test_padding(self):
        s = tl.LayoutSegment((10, None))
        assert s.subseg("", 0, 8) == [(8, None)]
