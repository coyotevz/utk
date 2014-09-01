# -*- coding: utf-8 -*-

"""
    utk.ulib.property
    ~~~~~~~~~~~~~~~~~
"""

from signals import install_signal
from utils import unnorm


class uproperty(object):

    def __init__(self, name=None, ptype=None, default=None, min=None, max=None,
                 blurb=None):
        self.name = name

    def __get__(self, obj, objtype=None):
        return self.get(obj)

    def __set__(self, obj, value):
        return self.set(obj, value)

    def get(self, obj):
        cls = obj.__class__
        while hasattr(cls, '_decl_properties'):
            try:
                return cls._get_property(obj, self.name)
            except UnknowedProperty:
                cls = cls.__base__
        raise ValueError(self.name)

    def set(self, obj, value):
        cls = obj.__class__
        while hasattr(cls, '_decl_properties'):
            try:
                return cls._set_property(obj, self.name, value)
            except UnknowedProperty:
                cls = cls.__base__
        raise ValueError(self.name, value)


class UnknowedProperty(Exception):
    pass


def install_property(cls, uprop):
    # copy to avoid overwrite super _decl_properties
    props = dict(getattr(cls, '_decl_properties', {}))
    props[uprop.name] = uprop
    install_signal(cls, "notify::%s" % uprop.name, default_cb=False)
    setattr(cls, '_decl_properties', props)
    _install_properties_api(cls)

def _install_properties(cls):

    attrs = dict(cls.__dict__)

    for attrname, attrvalue in attrs.iteritems():
        if isinstance(attrvalue, uproperty):
            if not attrvalue.name:
                attrvalue.name = unnorm(attrname)
            install_property(cls, attrvalue)

class PropertiedMeta(type):

    def __init__(cls, classname, bases, ns):
        type.__init__(cls, classname, bases, ns)
        _install_properties(cls)


class PropertiedObject(object):
    __metaclass__ = PropertiedMeta

def _install_properties_api(cls):

    if hasattr(cls, '_properties_api'):
        return

    _freezed = False
    _thaw = set()

    def _get_property(self, pname):
        raise ValueError("don't have %s property" % pname)

    def _set_property(self, pname, value):
        raise ValueError("don't have %s property" % pname)

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

    api_attrs = dict(locals())
    api = ('_freezed', '_thaw', 'get_property', 'set_property', 'notify',
           'freeze_notify', 'thaw_notify')

    for attr in api:
        setattr(cls, attr, api_attrs[attr])

    cls._properties_api = True


class FreezedContext(object):
    """
    Context manager that calls ``thaw_notify`` on a given object on exit. Used
    to make the ``freeze_notify`` method on `PropertiedObject`.
    """

    def __init__(self, obj):
        self._obj = obj

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        self._obj.thaw_notify()


class SampleBase(PropertiedObject):
    _name = None
    _age = 0

    name = uproperty()
    age = uproperty(ptype=int, min=18, max=99)

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
    height = uproperty(ptype=int, min=0, max=100)
    border_width = uproperty(ptype=int, min=0, blurb="Border width")
    visible = uproperty('visible', ptype=bool, default=True,
                        blurb="Widget is visible")

    def __init__(self):
        self._width = 0
        self._height = 0
        self._border = 0
        self._hidden = True

    def set_border_width(self, value):
        self.set_property('border-width', value)
        self.notify('border-width')

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
