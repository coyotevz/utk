# -*- coding: utf-8 -*-

from gulib.compat import b, s

from utk.misc import Misc
from utk.canvas import TextCanvas
from utk.text_layout import calc_pos, calc_coords, shift_line, default_layout

# align modes
LEFT = 'left'

# wrap modes
SPACE = 'space'

class Label(Misc):
    __type_name__ = "UtkLabel"

    def __init__(self, text="", align=LEFT, wrap=SPACE, layout=None):
        super(Label, self).__init__()
        self._text = None
        self._align_mode = None
        self._wrap_mode = None
        self._layout = None

        self.set_text(text)
        self.set_layout(align, wrap, layout)

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

    def set_layout(self, align, wrap, layout=None):
        if layout is None:
            layout = default_layout
        self._layout = layout
        self.set_align_mode(align)
        self.set_wrap_mode(wrap)

    def set_wrap_mode(self, mode):
        if not self.layout.supports_wrap_mode(mode):
            raise AttributeError("Wrap mode {} not supported.".format(mode))
        self._wrap_mode = mode
        self.queue_draw()

    def set_align_mode(self, mode):
        if not self.layout.supports_align_mode(mode):
            raise AttributeError("Align mode {} not supported.".format(mode))
        self._align_mode = mode
        self.queue_draw()

    def request_content_size(self):
        text_lines = self.text.split("\n")
        text_width = max([len(l) for l in text_lines])
        return (text_width, len(text_lines))

    def get_content_canvas(self, left, top, cols, rows):
        text = self.text.split("\n")
        return TextCanvas(text=text, left=left, top=top, cols=cols, rows=rows)
