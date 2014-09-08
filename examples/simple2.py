# -*- coding: utf-8 -*-

from functools import partial

import utk
import gulib

# create window and label widgets
window = utk.Window()
window.set_border_width(1)

vbox = utk.VBox()
vbox.set_border_width(1)

l1 = utk.Label("label-1")
l2 = utk.Label("label-2")

vbox.pack_start(l1)
vbox.pack_start(l2)

# set label as child of window
window.add(vbox)

window.show_all()

def hide_widget(widget):
    widget.hide()

def show_widget(widget):
    widget.show()

def add_label():
    l3 = utk.Label("label-3")
    vbox.pack_start(l3)
    l3.show()

gulib.timeout_add_seconds(2, add_label)
gulib.timeout_add_seconds(3, partial(hide_widget, vbox))
gulib.timeout_add_seconds(4, partial(show_widget, vbox))
gulib.timeout_add_seconds(5, partial(hide_widget, l2))
gulib.timeout_add_seconds(6, partial(hide_widget, l1))
gulib.timeout_add_seconds(7, lambda *x: vbox.show_all())
gulib.timeout_add_seconds(8, utk.main_quit)

# run main loop
utk.main()
