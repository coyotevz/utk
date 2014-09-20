# -*- coding: utf-8 -*-

"""
Sintesis del proceso de visualizacion de un widget.

show() -> map() -> realize()

Algunas condiciones:
~~~~~~~~~~~~~~~~~~~~
- Un widget no puede estar `mapped` si antes no esta `realized`
- Un widget no puede estar `realized` si no lo esta antes su padre.
- Un widget no puede estar `mapped` si antes no lo esta su padre.
- El método `show()` en un widget trata de `mapear` el widget, en caso que no
  pueda solo lo marca para se sea mostrado en cuando su padre sea `mapeado`.
- Un widget que es `realized` o `mapped` debe corroborar que sus hijos visibles
  sean también `realized` o `mapped`.
- Cuando a un widget se le asigna un padre debe verificar si se tiene que
  `realize` o `map`.
"""


class Widget(object):

    _toplevel = False

    def __init__(self, name=None):
        self.name = name
        self._visible = False
        self._mapped = False
        self._realized = False

        self._requisition = None
        self._allocation = None
        self._needs_request = True
        self._needs_alloc = True

        self._parent = None
        self._child = None

    is_visible = property(lambda s: s._visible)
    is_mapped = property(lambda s: s._mapped)
    is_realized = property(lambda s: s._realized)
    is_toplevel = property(lambda s: s._toplevel)

    needs_request = property(lambda s: s._needs_request)
    needs_alloc = property(lambda s: s._needs_alloc)

    def show(self):
        """
        Este metodo muestra el widget lo más pronto que sea posible.
        Este metodo debería basicamente llamar al metodo map que es quien pone
        este widget en la pantalla para que sea mostrado siempre y cuando el
        contenedor de este widget esté ya mapeado, si no marca este widget como
        candidato a ser mapeado por su contenedor.
        """
        if not self.is_visible:
            self._visible = True
            print("%s::show()" % self.name)
            if (self.parent and self.parent.is_mapped) or self.is_toplevel:
                self.map()


    def hide(self):
        if self.is_visible:
            if self.is_mapped:
                self.unmap()
            self._visible = False
            print("%s::hide()" % self.name)

    def map(self):
        """
        Este metodo marca al widget como mapeado que significa que su canvas es
        visible y participa del proceso de refresco de pantalla.
        En caso que este widget no tenga canvas (no esta realized) llama al
        metodo realize que es el encargado de generar el canvas
        correspondiente.
        Luego llama al metodo show del canvas y encola el widget en el proceso
        de dibujo de pantalla.
        """
        if not self.is_mapped:
            if not self.is_realized:
                self.realize()
            self._mapped = True
            print("%s::map()" % self.name)
            if self._child and self._child.is_visible:
                self._child.map()

    def unmap(self):
        if self.is_mapped:
            if self._child and self._child.is_mapped:
                self._child.unmap()
            self._mapped = False
            print("%s::unmap()" % self.name)

    def realize(self):
        """
        Este metodo es el encargado de crear los recursos asociados a este
        widget, más especificamente el canvas para este widget.
        En caso que el contenedor de este widget no este realizado todavia
        llama a la realización del mismo, condicion necesaria para poder
        agregar el canvas al canvas del contenedor.
        """
        if not self.is_realized:
            if not self.parent and not self.is_toplevel:
                raise Warning("Calling Widget.realize() on a widget with no "\
                              "parent")
            if self.parent and not self.parent.is_realized:
                self.parent.realize()
            self.check_resize()

            self._realized = True
            print("%s::realize()" % self.name)

            if self._child and self._child.is_visible and\
                    not self._child.is_realized:
                self._child.realize()

    def unrealize(self):
        if self.is_mapped:
            self.unmap()
        if self.is_realized:
            if self._child and self._child.is_realized:
                self._child.unrealize()
            self._realized = False
            print("%s::unrealize()" % self.name)

    # methods for size negotiation
    def size_request(self):
        if not self.needs_request and self._requisition:
            return self._requisition
        if self._child and self._child.is_visible:
            child_req = self._child.size_request()
        print("%s::size_request()" % self.name)
        self._requisition = (100, 100)
        self._needs_request = False
        return self._requisition

    def size_allocate(self, allocation):
        if not self.needs_alloc and self._allocation:
            return
        print("%s::size_allocation()" % self.name)
        self._allocation = allocation
        self._needs_alloc = False
        if self._child and self._child.is_visible:
            self._child.size_allocate(allocation)

    def check_resize(self):
        if self.parent:
            self.parent._needs_request = self.needs_request
            self.parent._needs_alloc = self.needs_alloc
            self.parent.check_resize()
        elif self.is_toplevel:
            # real check resize
            req = self.size_request()
            self.size_allocate(req)

    # methods for handle containers relations
    def add(self, widget):
        self._child = widget
        widget.set_parent(self)

    def set_parent(self, parent):
        if self.parent:
            raise Warning("Can't set a parent on widget wich has a parent")
        if self.is_toplevel:
            raise Warning("Can't set a parent on a toplevel widget")
        self._parent = parent

        if self.is_visible:
            # check realized/mapped invariants
            if parent.is_realized:
                self.realize()
            if parent.is_mapped:
                self.map()

    def unparent(self):
        if not self.parent:
            return

        if self.is_realized:
            self.unrealize()
        self._parent._child = None
        self._parent = None

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value):
        if value is None:
            self.unparent()
        else:
            self.set_parent(value)

    def set_visible(self, visible):
        if visible != self._visible:
            if visible:
                self.show()
            else:
                self.hide()

    visible = property(lambda s: s._visible, set_visible)

    def destroy(self):
        if self.is_realized:
            self.unrealize()

    def __repr__(self):
        return "<%s '%s'>" % (self.__class__.__name__, self.name)


class Toplevel(Widget):

    _toplevel = True

    def realize(self):
        if not self._requisition:
            req = self.size_request()
        if not self._allocation:
            self.size_allocate(self._requisition)
        super(Toplevel, self).realize()

    def queue_draw(self):
        print("%s::queue_draw()" % self.name)


t = Toplevel('toplevel')
w1 = Widget('w1')
w2 = Widget('w2')
w3 = Widget('w3')

# Basic example
t.add(w1)
w1.add(w2)

# Do some test things and then
# w2.add(w3)
