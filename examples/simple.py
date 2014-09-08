# -*- coding: utf-8 -*-

import utk
import gulib

# create window and label widgets
window = utk.Window()
label = utk.Label("Very simple sample")

# set label as child of window
window.add(label)

window.show_all()

def modify_text():
    label.set_text(label.get_text() + ". Bye!")

gulib.timeout_add_seconds(4, modify_text)
gulib.timeout_add_seconds(5, utk.main_quit)

# run main loop
utk.main()
