# -*- coding: utf-8 -*-

# align modes
ALIGN_LEFT = 'left'
ALIGN_CENTER = 'center'
ALIGN_RIGHT = 'right'

# wrap modes
WRAP_ANY = 'any'
WRAP_SPACE = 'space'
WRAP_CLIP = 'clip'

class StandardTextLayout(object):

    _align_modes = (ALIGN_LEFT, ALIGN_CENTER, ALIGN_RIGHT)
    _wrap_modes = (WRAP_ANY, WRAP_SPACE, WRAP_CLIP)

    def supports_align_mode(self, align):
        """
        Returns true if align mode is supported, in this case 'left', 'center',
        'right'.
        """
        return align in self._align_modes

    def supports_wrap_mode(self, wrap):
        """
        Returns true if wrap mode is supported, in this case 'any', 'space',
        'clip'.
        """
        return wrap in self._wrap_modes

    def layout(self, text, width, align, wrap):
        """
        Returns a layout structure for text.
        """
        try:
            segs = self.calculate_text_segments(text, width, wrap)
            return self.align_layout(text, width, segs, wrap, align)
        except:
            return [[]]

# default layout
default_layout = StandardTextLayout()
