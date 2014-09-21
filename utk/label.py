# -*- coding: utf-8 -*-

from gulib.compat import b, s

from utk.misc import Misc
from utk.utils import Requisition
from utk.canvas import TextCanvas


class Label(Misc):
    __type_name__ = "UtkLabel"

    def __init__(self, text=""):
        super(Label, self).__init__()
        self._text = b(text)

    def get_text(self):
        return s(self._text)

    def set_text(self, text):
        """
        Sets the text within the Label() widget. It overrides any text that
        was there before.
        """
        text = b(text)
        if text != self._text:
            self._text = text
            if self.is_realized:
                self.canvas._text = [self._text]
            self.notify("text")
            self.queue_resize()
            self.queue_draw()

    text = property(get_text, set_text)

    # "size-request" signal handler
    def do_size_request(self):
        text_lines = self.text.split('\n')
        text_width = max([len(l) for l in text_lines])
        return Requisition(self.xpad*2+text_width,
                           self.ypad*2+len(text_lines))

    # "realize" signal handler
    def do_realize(self):
        assert self._canvas is None
        self._realized = True
        self._canvas = TextCanvas(text=[self._text],
                                  left=self._allocation.x,
                                  top=self._allocation.y,
                                  cols=self._allocation.width,
                                  rows=self._allocation.height)
        self._canvas.set_parent_widget(self.parent)

    def do_unrealize(self):
        self._realized = False
        self._canvas = None
