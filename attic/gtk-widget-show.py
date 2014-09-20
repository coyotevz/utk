# -*- coding: utf-8 -*-

from functools import partial
import gtk

def _sig(signame, w, *args):
    print("%s::%s()" % (w.get_name(), signame))

signames = ["show", "map", "realize",
            "hide", "unmap", "unrealize",
            "size-request", "size-allocate"]

def connect_signals(w):
    for s in signames:
        w.connect(s, partial(_sig, s))

t = gtk.Window()
t.set_name("toplevel")
connect_signals(t)
w1 = gtk.VBox()
w1.set_name("w1")
connect_signals(w1)
w2 = gtk.HBox()
w2.set_name("w2")
connect_signals(w2)
w3 = gtk.Label("label-1")
w3.set_name("w3")
connect_signals(w3)

t.add(w1)
w1.add(w2)
