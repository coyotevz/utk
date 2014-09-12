
from utk import str_util
from gulib.compat import b

class TestDecodeOne(object):

    def gwt(self, ch, exp_ord, exp_pos):
        ch = b(ch)
        o, pos = str_util.decode_one(ch, 0)
        assert o == exp_ord
        assert pos == exp_pos

    def test_byte_1(self):
        self.gwt("ab", ord("a"), 1)
        self.gwt("\xc0a", ord("?"), 1)

    def test_byte_2(self):
        self.gwt("\xc2", ord("?"), 1)
        self.gwt("\xc0\x80", ord("?"), 1)
        self.gwt("\xc2\x80", 0x80, 2)
        self.gwt("\xdf\xbf", 0x7ff, 2)

    def test_byte_3(self):
        self.gwt("\xe0", ord("?"), 1)
        self.gwt("\xe0\xa0", ord("?"), 1)
        self.gwt("\xe0\x90\x80", ord("?"), 1)
        self.gwt("\xe0\xa0\x80", 0x800, 3)
        self.gwt("\xef\xbf\xbf", 0xffff, 3)

    def test_byte_4(self):
        self.gwt("\xf0", ord("?"), 1)
        self.gwt("\xf0\x90", ord("?"), 1)
        self.gwt("\xf0\x90\x80", ord("?"), 1)
        self.gwt("\xf0\x80\x80\x80", ord("?"), 1)
        self.gwt("\xf0\x90\x80\x80", 0x10000, 4)
        self.gwt("\xf3\xbf\xbf\xbf", 0xfffff, 4)
