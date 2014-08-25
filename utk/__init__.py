# -*- coding: utf-8 -*-

"""
    utk
    ~~~

    Utk Toolkit

    :copyright: 2011-2012 by Utk Authors
    :license: LGPL 2 or later (see README/COPYING/LICENSE)
"""

import logging

import glib
from utk.label import Label
from utk.box import VBox, HBox
from utk.window import Window
from utk.screen import get_default_screen

# version information
__version__ = '0.0.1'

_running_from_pytest = False

main_loops = []

def main():
    loop = glib.MainLoop()
    main_loops.append(loop)

    loop.run()

    if not main_loops:
        screen = get_default_screen()
        if screen.started:
            screen.stop()

def main_quit(*args):

    assert len(main_loops), "There is no running loop"

    loop = main_loops.pop()
    loop.quit()


def register_palette(palette):
    get_default_screen().register_palette(palette)

def set_terminal_file(fname):
    try:
        from utk import raw_display
    except ImportError:
        return

    try:
        outfile, infile = open(fname, "w"), open(fname, "r")
    except:
        return

    raw_display._term_files = (outfile, infile)


# Configure logging facilities
def _setup_null_handler_logging():
    h = logging.NullHandler()
    logging.getLogger("utk").addHandler(h)

def configure_logging(outfilename, level=logging.DEBUG):
    fh = logging.FileHandler(outfilename, delay=True)
    #formatter = logging.Formatter("%(msecs)-13s %(levelname)s %(name)s: %(message)s")
    formatter = logging.Formatter("%(levelname)s %(name)s: %(message)s")
    fh.setFormatter(formatter)
    logger = logging.getLogger("utk")
    logger.addHandler(fh)
    logger.setLevel(level)

_setup_null_handler_logging()
