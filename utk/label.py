# -*- coding: utf-8 -*-

from utk.misc import Misc
from utk.utils import Requisition
from utk.canvas import TextCanvas


class Label(Misc):
    __type_name__ = "UtkLabel"

    def __init__(self, text=""):
        super(Label, self).__init__()
        self._text = text

    def get_text(self):
        return self._text

    def set_text(self, text):
        """
        Sets the text within the Label() widget. It overrides any text that
        was there before.
        """
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
        text_width = max(list(map(len, text_lines)))
        req = Requisition(text_width, len(text_lines))
        req = req._replace(width=self.xpad+req.width+self.xpad,
                           height=self.ypad+req.height+self.ypad)
        return req

    # "realize" signal handler
    def do_realize(self):
        assert self.canvas is None
        self._realized = True
        self.canvas = TextCanvas(text=[self._text],
                                 left=self._allocation.x,
                                 top=self._allocation.y,
                                 cols=self._allocation.width,
                                 rows=self._allocation.height)
