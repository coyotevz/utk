# -*- coding: utf-8 -*-

import utk
import gulib

class TestWidget(utk.widget.Widget):
    __type_name__ = "CustomWidget"

    def do_parent_set(self, parent):
        "Do nothing"
        pass

    def do_realize(self):
        "Do nothing"
        self._realized = True
        pass

    def do_map(self):
        "Do nothing"
        self._mapped = True
        pass

w = utk.Window()
w.show()
tw = TestWidget()
w.add(tw)
tw.show()

def quit():
    utk.main_quit()

def add():
    box = TestWidget()
    w.add(box)
    box.show()

gulib.timeout_add_seconds(3, add)
gulib.timeout_add_seconds(4, quit)


utk.register_palette([
    ('test', 'light red', 'light gray'),
])

utk.main()
