# -*- coding: utf-8 -*-

from gulib.compat import b, s

from utk.misc import Misc
from utk.canvas import TextCanvas


class Label(Misc):
    __type_name__ = "UtkLabel"

    def __init__(self, text=""):
        super(Label, self).__init__()
        self._text = None
        self.set_text(text)

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
                self._content_canvas._text = self._text.split("\n")
            self.notify("text")
            self.queue_resize()
            self.queue_draw()

    text = property(get_text, set_text)

    def request_content_size(self):
        text_lines = self.text.split("\n")
        text_width = max([len(l) for l in text_lines])
        return (text_width, len(text_lines))

    def get_content_canvas(self, left, top, cols, rows):
        text = self.text.split("\n")
        return TextCanvas(text=text, left=left, top=top, cols=cols, rows=rows)
