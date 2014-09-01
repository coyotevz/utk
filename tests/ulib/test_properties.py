# -*- coding: utf-8 -*-

import pytest

from utk.ulib.properties import uproperty, PropertiedObject, UnknowedProperty


class Exc1(Exception): pass
class Exc2(Exception): pass
class Exc3(Exception): pass
class Exc4(Exception): pass


class TestPropertiedObject(object):

    def test_constructor(self):
        class T(PropertiedObject):
            prop1 = uproperty()

        t = T()

        assert hasattr(T, 'notify')
        assert hasattr(t, 'notify')

    def test_inheritance(self):
        class Base(PropertiedObject):
            base_prop1 = uproperty()
            base_prop2 = uproperty()

        class Inherit(Base):
            inherit_prop1 = uproperty()
            inherit_prop2 = uproperty()

        assert hasattr(Base, '_decl_properties')
        assert 'base-prop1' in Base._decl_properties
        assert 'base-prop2' in Base._decl_properties
        assert 'inherit-prop1' not in Base._decl_properties
        assert 'inherit-prop2' not in Base._decl_properties
        assert hasattr(Inherit, '_decl_properties')
        assert 'base-prop1' in Inherit._decl_properties
        assert 'base-prop2' in Inherit._decl_properties
        assert 'inherit-prop1' in Inherit._decl_properties
        assert 'inherit-prop2' in Inherit._decl_properties

    def test_set_get_propery(self):
        class Base(PropertiedObject):
            base_prop1 = uproperty()
            base_prop2 = uproperty()

            def _get_property(self, prop):
                if prop == 'base-prop1':
                    raise Exc1(prop)
                elif prop == 'base-prop2':
                    raise Exc2(prop)
                else:
                    UnknowedProperty(prop)

            def _set_property(self, prop, value):
                if prop == 'base-prop1':
                    raise Exc1(prop, value)
                elif prop == 'base-prop2':
                    raise Exc2(prop, value)
                else:
                    UnknowedProperty(prop, value)

        b = Base()
        with pytest.raises(Exc1):
            b.get_property('base-prop1')
        with pytest.raises(Exc1):
            b.base_prop1
        with pytest.raises(Exc2):
            b.get_property('base-prop2')
        with pytest.raises(Exc2):
            b.base_prop2
        with pytest.raises(Exc1):
            b.set_property('base-prop1', None)
        with pytest.raises(Exc1):
            b.base_prop1 = None
        with pytest.raises(Exc2):
            b.set_property('base-prop2', None)
        with pytest.raises(Exc2):
            b.base_prop2 = None
        with pytest.raises(ValueError):
            b.get_property('non-property')
        with pytest.raises(ValueError):
            b.set_property('non-property', None)

    def test_set_get_inheritance(self):
        class Base(PropertiedObject):
            base_prop1 = uproperty()
            base_prop2 = uproperty()

            def _get_property(self, prop):
                if prop == 'base-prop1':
                    raise Exc1(prop)
                elif prop == 'base-prop2':
                    raise Exc2(prop)
                else:
                    UnknowedProperty(prop)

            def _set_property(self, prop, value):
                if prop == 'base-prop1':
                    raise Exc1(prop, value)
                elif prop == 'base-prop2':
                    raise Exc2(prop, value)
                else:
                    UnknowedProperty(prop, value)

        class Inherit(Base):
            i_prop1 = uproperty()
            i_prop2 = uproperty()

            def _get_property(self, prop):
                if prop == 'i-prop1':
                    raise Exc3(prop)
                elif prop == 'i-prop2':
                    raise Exc4(prop)
                else:
                    raise UnknowedProperty(prop)

            def _set_property(self, prop, value):
                if prop == 'i-prop1':
                    raise Exc3(prop, value)
                elif prop == 'i-prop2':
                    raise Exc4(prop, value)
                else:
                    raise UnknowedProperty(prop, value)

        i = Inherit()
        with pytest.raises(Exc1):
            i.get_property('base-prop1')
        with pytest.raises(Exc1):
            i.base_prop1
        with pytest.raises(Exc2):
            i.get_property('base-prop2')
        with pytest.raises(Exc2):
            i.base_prop2
        with pytest.raises(Exc1):
            i.set_property('base-prop1', None)
        with pytest.raises(Exc1):
            i.base_prop1 = None
        with pytest.raises(Exc2):
            i.set_property('base-prop2', None)
        with pytest.raises(Exc2):
            i.base_prop2 = None
        with pytest.raises(ValueError):
            i.get_property('non-property')
        with pytest.raises(ValueError):
            i.set_property('non-property', None)
        with pytest.raises(Exc3):
            i.get_property('i-prop1')
        with pytest.raises(Exc3):
            i.i_prop1
        with pytest.raises(Exc4):
            i.get_property('i-prop2')
        with pytest.raises(Exc4):
            i.i_prop2
