# -*- coding: utf-8 -*-

import utk
import glib

# create window and label widgets
window = utk.Window()
label = utk.Label("Very simple sample")

# set label as child of window
window.add(label)

window.show_all()

glib.timeout_add_seconds(5, utk.main_quit)

# run main loop
utk.main()
