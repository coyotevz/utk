# -*- coding: utf-8 -*-

import utk
import gulib

utk.configure_logging("/dev/pts/1")

class TestWidget(utk.widget.Widget):
    __type_name__ = "CustomWidget"

    def do_parent_set(self, parent):
        "Do nothing"
        pass

    def do_realize(self):
        "Do nothing"
        self._realized = True

    def do_unrealize(self):
        "Do nothing"
        self._realized = False

    def do_map(self):
        "Do nothing"
        self._mapped = True

    def do_unmap(self):
        "Do nothing"
        self._mapped = False

    def do_size_request(self):
        "Do nothing"
        return (0, 0)

w = utk.Window()
label = utk.Label("test")
w.show()

def quit():
    utk.main_quit()

def add():
    w.add(label)
    label.show()

gulib.timeout_add_seconds(3, add)
gulib.timeout_add_seconds(4, quit)


utk.register_palette([
    ('test', 'light red', 'light gray'),
])

utk.main()
