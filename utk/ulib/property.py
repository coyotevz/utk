# -*- coding: utf-8 -*-

"""
    utk.ulib.property
    ~~~~~~~~~~~~~~~~~
"""

from signals import install_signal


class uproperty(object):

    def __init__(self, name=None, type=None, default=None, min=None, max=None,
                 blurb=None):
        self.name = name

    def __get__(self, obj, objtype=None):
        return self.get(obj)

    def __set__(self, obj, value):
        return self.set(obj, value)

    def get(self, obj):
        try:
            return obj._get_property(self.name)
        except UnknowedProperty:
            return super(obj.__class__, obj)._get_property(self.name)

    def set(self, obj, value):
        try:
            return obj._set_property(self.name, value)
        except UnknowedProperty:
            return super(obj.__class__, obj)._set_property(self.name, value)


class UnknowedProperty(Exception):
    pass


def install_property(cls, uprop):
    if not hasattr(cls, '_decl_properties'):
        cls._decl_properties = {}
    cls._decl_properties[uprop.name] = uprop
    signame = "notify::%s" % uprop.name
    print 'signame:', signame
    install_signal(cls, signame, default_cb=False)

def _install_properties(cls):

    attrs = dict(cls.__dict__)

    for attrname, attrvalue in attrs.iteritems():
        if isinstance(attrvalue, uproperty):
            if not attrvalue.name:
                attrvalue.name = attrname
            install_property(cls, attrvalue)

class PropertiedMeta(type):

    def __init__(cls, classname, bases, ns):
        type.__init__(cls, classname, bases, ns)
        _install_properties(cls)


class PropertiedClass(object):
    __metaclass__ = PropertiedMeta

    _freezed = False
    _thaw = set()

    def get_property(self, pname):
        if pname in self._decl_properties:
            return self._decl_properties[pname].get(self)
        raise ValueError("this object don't have a property with name '%s'" \
                         % pname)

    def set_property(self, pname, value):
        if pname in self._decl_properties:
            return self._decl_properties[pname].set(self, value)
        raise ValueError("this object don't have a property with name '%s'" \
                         % pname)

    def notify(self, pname):
        if self._freezed:
            self._thaw.add(pname)
        else:
            self.emit("notify::%s" % pname)

    def freeze_notify(self):
        self._freezed = True
        return FreezedContext(self)

    def thaw_notify(self):
        self._freezed = False
        for pname in self._thaw:
            self.emit("notify::%s" % pname)
        self._thaw.clear()


class FreezedContext(object):
    """
    Context manager that calls ``thaw_notify`` on a given object on exit. Used
    to make the ``freeze_notify`` method on `PropertiedClass`.
    """

    def __init__(self, obj):
        self._obj = obj

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        self._obj.thaw_notify()


class SampleBase(PropertiedClass):
    _name = None
    _age = 0

    name = uproperty()
    age = uproperty(type=int, min=18, max=99)

    def _get_property(self, pname):
        if pname == 'name':
            return self._name
        elif pname == 'age':
            return self._age
        else:
            raise UnknowedProperty()

    def _set_property(self, pname, value):
        if pname == 'name':
            self._name = value
        elif pname == 'age':
            self._age = value


class Sample(SampleBase):

    width = uproperty()
    height = uproperty(type=int, min=0, max=100)
    border_width = uproperty('border-width', type=int, min=0, blurb="Border width")
    visible = uproperty(type=bool, default=True, blurb="Widget is visible")

    def __init__(self):
        self._width = 0
        self._height = 0
        self._border = 0
        self._hidden = True

    def set_border_width(self, value):
        self.set_property('border-width', value)

    def get_border_width(self):
        self.get_property('border-width')

    def _get_property(self, pname):
        if pname == "width":
            return self._width
        elif pname == "height":
            return self._height
        elif pname == "border-width":
            return self._border
        elif pname == "visible":
            return not self._hidden
        else:
            raise UnknowedProperty(self, pname)

    def _set_property(self, pname, value):
        if pname == "width":
            self._width = value
            print "new with: %s" % value
        elif pname == "height":
            self._height = value
            print "new height: %s" % value
        elif pname == "border-width":
            self._border = value
            print "we need redraw"
        elif pname == "visible":
            self._hidden = not value
            if value:
                print "showing!"
            else:
                print "hidding!"
        else:
            raise UnknowedProperty(self, pname, value)
