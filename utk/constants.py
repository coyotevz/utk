# -*- coding: utf-8 -*-

"""
    utk.constants
    ~~~~~~~~~~~~~

    Utk Constants

    :copyright: 2011-2012 by Utk Authors
    :license: LGPL2 or later (see README/COPYING/LICENSE)
"""

import glib

# Priorities for redrawing and resizing...
PRIORITY_HIGH = glib.PRIORITY_HIGH            # -100
PRIORITY_DEFAULT = glib.PRIORITY_DEFAULT      #    0
PRIORITY_HIGH_IDLE = glib.PRIORITY_HIGH_IDLE  #  100
PRIORITY_IDLE = glib.PRIORITY_DEFAULT_IDLE    #  200

PRIORITY_EVENTS = PRIORITY_DEFAULT
PRIORITY_RESIZE = PRIORITY_HIGH_IDLE + 10
PRIORITY_REDRAW = PRIORITY_HIGH_IDLE + 20

# Widget states
STATE_NORMAL = "state-normal"
STATE_ACTIVE = "state-active"
STATE_SELECTED = "state-selected"
STATE_INSENSITIVE = "state-insensitive"

# Resize Mode Constants
RESIZE_PARENT = "resize-parent"
RESIZE_QUEUE = "resize-queue"
RESIZE_IMMEDIATE = "reisze-immediate"

# Orientation Constants
ORIENTATION_HORIZONTAL = "orientation-horizontal"
ORIENTATION_VERTICAL = "orientation-vertical"

# Pack Type Constants
PACK_START = "pack-start"
PACK_END = "pack-end"
