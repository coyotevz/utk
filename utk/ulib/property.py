# -*- coding: utf-8 -*-


class uproperty(object):

    def __init__(self, value):
        self._value = value
        self._name = None

    def __get__(self, obj, objtype=None):
        print obj, objtype
        return self._value

    def __set__(self, obj, value):
        print obj, value
        self._value = value


class PropertiedMeta(type):

    def __init__(cls, classname, bases, ns):
        type.__init__(cls, classname, bases, ns)


class PropertiedClass(object):
    __metaclass__ = PropertiedMeta

    def get_property(self, pname):
        pass

    def set_property(self, pname, value):
        pass

    def get_properties(self, props):
        pass

    def set_properties(self, pdict):
        pass

    def notify(self, pname):
        pass

    def freeze(self, pname):
        # return context manager
        pass

    def thaw(self, pname):
        pass


class Sample(PropertiedClass):

    width = uproperty()
    height = uproperty(int, min=0, max=100)
    border_width = uproperty(int, min=0, blurb="Border width")
    visible = uproperty(bool, default=True, blurb="Widget is visible")

    def do_get_property(self, pname):
        pass

    def do_set_property(self, pname, pvalue):
        pass
