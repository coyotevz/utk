
from utk import str_util

class TestDecodeOne(object):

    def gwt(self, ch, exp_ord, exp_pos):
        ch = ch
        o, pos = str_util.decode_one(ch, 0)
        assert o == exp_ord
        assert pos == exp_pos

    def test_byte_1(self):
        self.gwt("ab", ord("a"), 1)
        self.gwt("\xc0a", ord("?"), 1)
