# -*- coding: utf-8 -*-

import os
import random

import utk
import gulib

if os.path.exists("/dev/pts/1"):
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
w.set_border_width(2)
label = utk.Label("this is a test\nlabel")
w.show()

def quit():
    utk.main_quit()

def add():
    w.add(label)
    label.set_padding(xpad=3, ypad=1)
    label.show()

def sett():
    label.set_text("new content")

def move():
    label.set_alignment(xalign=random.random(), yalign=random.random())

gulib.timeout_add_seconds(2, add)
gulib.timeout_add_seconds(3, move)
gulib.timeout_add_seconds(4, move)
gulib.timeout_add_seconds(5, move)
gulib.timeout_add_seconds(6, move)
gulib.timeout_add_seconds(7, move)
gulib.timeout_add_seconds(8, quit)


utk.register_palette([
    ('test', 'light red', 'light gray'),
])

utk.main()
