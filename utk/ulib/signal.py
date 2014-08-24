# -*- coding: utf-8 -*-

"""
Provides mechanisms to use signal handlers in a framework

Mimics the GObject signals behavior in a pure python implementation.
"""

__all__ = ['Signal', 'SignalBase', 'install_signal', 'SignaledObjectMetaType',
           'SignaledObject', 'SIGNAL_RUN_FIRST', 'SIGNAL_RUN_LAST']

from types import ClassType, InstanceType,FunctionType, MethodType

SIGNAL_RUN_FIRST, SIGNAL_RUN_LAST = range(2)

def _norm(name):
    return name.replace('-', '_')

def _unnorm(name):
    return name.replace('_', '-')

def _bounded(method):
    if callable(method):
        if type(method) is FunctionType: # bounded
            return True
        elif type(method) is MethodType:
            im_self = getattr(method, 'im_self')
            if im_self: return True
            else: return False
        else:
            raise AttributeError("unknow callable type")
    else:
        return None

class SignalBase(object):
    """
    Signal abstaction base class
    """

    def __init__(self, name, default_cb=None, flag=SIGNAL_RUN_LAST):
        """
        @param name: signal name
        @type name: str

        @param default_cb: default callback (optional)
        @type default_cb: callable object

        @param flag: default callback run order [SIGNAL_RUN_LAST]
        @type flag: int (SIGNAL_RUN_FIRST | SIGNAL_RUN_LAST)
        """
        
        self.name = name
        self._default_cb = default_cb
        self._flag = flag
        self._default_cb_blocked = False
        self._callbacks = []
        self._callbacks_after = []
        self._blockeds = []

    def connect(self, callback):
        "Connect signal callback before SIGNAL_RUN_LAST default callback"
        assert callable(callback), "'callback' must be a callable object"
        self._callbacks.append(callback)

    def connect_after(self, callback):
        "Connect signal callback after SIGNAL_RUN_LAST defautl callback"
        assert callable(callback), "'callback' must be a callable object"
        self._callbacks_after.append(callback)

    def disconnect(self, callback):
        "Disconnect signal callback connected via connect method"
        self._callbacks.remove(callback)

    def disconnect_after(self, callback):
        "Disconnect signal callback connected via connect_after method"
        self._callbacks_after.remove(callback)

    def block(self, callback):
        "Block the given callback. To unblock call unblock(callback)"
        self._blockeds.append(callback)

    def block_default(self):
        "Block default callback, to unblock call unblock_default method"
        self._default_cb_blocked = True

    def unblock(self, callback):
        "Unblock the given callback"
        self._blockeds.remove(callback)

    def unblock_default(self):
        "Unblock default callback"
        self._default_cb_blocked = False

    def is_blocked(self, callback=None):
        "Return the given callback state or default_callback state"
        if callback:
            return callback in self._blockeds
        return self._default_cb_blocked

    def stop_emission(self):
        self._stop = True

    def emit(self, *args):
        """
        Emit signal. It run the callbacks connected with args in this order:
            - default_callback if has flaged as SIGNAL_RUN_FIRST
            - callbacks connected by connect() method
            - default_callback if has flaged as SIGNAL_RUN_LAST
            - callbacks connected by connect_after() method
        """

        self._stop = False
        retval = None

        if self._default_cb and self._flag is SIGNAL_RUN_FIRST and\
                not self._default_cb_blocked:
            stop = self._default_cb(*args)

        for cb in self._callbacks:
            if not self._stop:
                if not cb in self._blockeds:
                    retval = cb(*args)
            else:
                break

        if self._default_cb and not self._stop and self._flag is SIGNAL_RUN_LAST and\
                not self._default_cb_blocked:
            retval = self._default_cb(*args)

        for cb_after in self._callbacks_after:
            if not self._stop:
                if not cb_after in self._blockeds:
                    retval = cb_after(*args)
            else:
                break
        return retval

class Signal(SignalBase):
    """
    Signal abstaction featured with default_callback get from namespace
    """
    _prefix = 'do_'

    def __init__(self, name, default_cb=None, namespace=None,
                 flag=SIGNAL_RUN_LAST, prefix=None):
        """
        @param name: name
        @type name: str

        @param default_cb: default callback or explicit False
        @type default_cb: callable object or bool or str

        @param namespace: where find a default callback
        @type namespace: object instance or dict

        @param flag: default callback run order [SIGNAL_RUN_LAST]
        @type flag: int (SIGNAL_RUN_FIRST | SIGNAL_RUN_LAST)

        @param prefix: prefix for default callback search ['do_']
        @type prefix: str

        default_cb como nombre de funcion: en ese caso hay que especificar 
            un namespace donde esta definida la funcion con el nombre que le
            pasamos, este namespace puede ser un dict como el devuelto por
            locals() o puede ser un objeto donde se defina la funcion.

        default_cb como callable: en este caso se especifica un "callable"
            (function or bound method), y no es necesario especificar un 
            namespace, en caso de hacerlo sera omitido. Si el "callable" que
            pasamos es un "unbound method" se lanza un TypeError.
            ej: self.handle_signal  <-- bound metod

        default_cb como None(default): en este caso es obligatorio especificar
            un namespace que contengla la definicion del callback con el nombre
            de la forma: do_<signal_name>, este nombre es automaticamente
            buscado por la señal armandolo en funcion del 'prefix'+'name' que
            le pasemos. El nombre es nomalizado '-' -> '_'.

        default_cb como False: este es el caso menos utilizado, namespace no
            se utiliza, no se tendrá un default_callback asociado, para que la 
            señal sea útil se tendran que conectar los callbacks con los 
            métodos connect() o connect_after().
        """
        self._namespace = None
        self._default_cb_name = None

        if prefix:
            self._prefix = prefix

        if default_cb: # true when default_cb is not (False, None)
            assert callable(default_cb) or type(default_cb) is str,\
                    "default_cb must be a callable or str"

        if type(default_cb) is str and namespace:
            assert type(namespace) is dict or \
                   type(getattr(namespace, '__dict__')) is dict, \
                   "namespace must be a dict instance or object with __dict__"\
                   "attribute"

            self._default_cb_name = default_cb
            default_cb = None

        elif default_cb is None:
            assert type(namespace) is dict or \
                   type(getattr(namespace, '__dict__')) is dict or \
                   isinstance(namespace, type), \
                   "namespace must be a dict instance or object with __dict__"\
                   " attribute"

            self._default_cb_name = self._prefix + _norm(name)

        self._namespace = namespace

        super(Signal, self).__init__(name, default_cb=default_cb, flag=flag)

    def emit(self, *args):
        if self._default_cb is None and self._default_cb_name:
            self._default_cb = self._get_default_cb()

        super(Signal, self).emit(*args)

    def _get_default_cb(self):
        assert self._namespace, "i don't know where to find default callback"

        if isinstance(self._namespace, dict):
            _getter = dict.get
        else:
            _getter = getattr

        default_cb = _getter(self._namespace, self._default_cb_name)

        if default_cb is None:
            raise AttributeError("%s object has no attribute '%s'"\
                    % (namespace.__name__, self._default_cb_name))

        assert callable(default_cb),\
                "'%s' attribute must be callable" % self._default_cb_name

#        if not _bounded(default_cb):
#            print default_cb
#            raise TypeError("%s callable must be a bound method "\
#                "(received an unbound method)" % self._default_cb_name)

        return default_cb

def _install(signal, override=False):
    sig_name = signal.name
    cls = signal._namespace

    _signals = getattr(cls, '_signals', {})

    if not override:
        assert not _signals.has_key(sig_name),\
            "The %s already has a signal named '%s'" % (cls.__name__, signame)

    _signals.update({sig_name: signal})

    setattr(cls, '_signals', _signals)

def install_signal(cls, sig_name, default_cb=None, flag=SIGNAL_RUN_LAST,\
                   override=False):
    
    assert type(cls) is ClassType or \
           isinstance(cls.__class__, type),\
            "'cls' must be a class or instance (%s received)" % type(cls)

    if isinstance(default_cb, basestring):
        default_ = getattr(cls, "%s" % default_cb, None)
        assert default_ and callable(default_), "You set '%s' as default "\
                "callback name but i can't find any callable with this name "\
                "in %s" % (default_cb, cls.__name__)

    _install(Signal(sig_name, default_cb, cls, flag), override)

def _get_signal_configuration(configuration):
    conf = dict()
    if isinstance(configuration, dict):
        conf['flag'] = configuration.get('flag', SIGNAL_RUN_LAST)
        conf['handler'] = configuration.get('handler')
        conf['override'] = configuration.get('override')
    elif isinstance(configuration, (list, tuple)):
        for elem in configuration:
            if isinstance(elem, int) and elem in range(2): # signal flag
                conf['flag'] = elem
            elif isinstance(elem, str):
                if elem == 'override':
                    conf['override'] = True
                else:
                    conf['handler'] = elem
            else:
                raise ValueError("_get_signal_configuration can't handle '%s'"
                                 % elem)

    elif isinstance(configuration, (str, int)):
        if configuration in range(2):
            conf['flag'] = configuration
        elif configuration == 'override':
            conf['override'] = True
        else:
            conf['handler'] = configuration
    elif isinstance(configuration, type(None)):
        pass # default config
    else:
        raise ValueError("_get_signal_configuration can't handle '%s'"
                         % configuration)

    conf['flag'] = conf.get('flag', SIGNAL_RUN_LAST)
    conf['handler'] = conf.get('handler')
    conf['override'] = conf.get('override', False) ## necesario False ??

    return conf

def signal_list_names(obj):

    assert isinstance(obj, SignaledObjectMetaType) or hasattr(obj,'_signals'),\
            "the argument must be a signaled object or class"

    if isinstance(obj, SignaledObjectMetaType):
        return tuple(obj.__signals__.iterkeys())
    elif hasattr(obj, '_signals'):
        return tuple(obj._signals.iterkeys())
    else:
        raise ValueError("no signaled object")

class SignaledMetaType(type):
    def __init__(cls, name, bases, namespace):
        _signals_decl = namespace.get('__signals__', {})
        _signals_base = {}
        for base in reversed(bases):
            if hasattr(base, '__signals__'):
                _signals_base.update(base.__signals__)
        _signals_base.update(_signals_decl)
        setattr(cls, '__signals__', _signals_base)
        type.__init__(cls, name, bases, namespace)

    # FIXME: Verificar que no estamos haciendo algo dos veces...
    def __call__(cls, *args, **kw):
        obj = cls.__new__(cls, *args, **kw)
        _signals_decl = getattr(cls, '__signals__', {})

        if _signals_decl and isinstance(_signals_decl, dict):
            delattr(cls, '__signals__')
            for sig_name, conf in _signals_decl.iteritems():
                conf = _get_signal_configuration(conf)
                install_signal(cls=obj,
                               sig_name=sig_name,
                               default_cb=conf['handler'],
                               flag=conf['flag'],
                               override=conf['override'])
            setattr(cls, '__signals__', _signals_decl)
        elif _signals_decl:  # not dict --> malformed
            raise TypeError("__signals__ must be a dict object")

        cls.__init__(obj, *args, **kw)
        return obj

class SignaledObject(object):
    __metaclass__ = SignaledMetaType

    # Utility func
    def _get_and_assert(self, sig_name):
        sig = self._signals.get(sig_name)
        if not sig: raise TypeError("unknown signal name: %s" % sig_name)
        return sig

    # Signal API
    def emit(self, detailed_signal, *data):
        signal = self._get_and_assert(detailed_signal)
        signal.emit(*data) # FIXME: data would have to be a Event object?
                      # ans: only for event signals, like "button-press-event"
        # Implement propagation mechanisms

    def stop_emission(self, detailed_signal):
        signal = self._get_and_assert(detailed_signal)
        signal.stop_emission()

    def connect(self, detailed_signal, callback, *extra_data):
        signal = self._get_and_assert(detailed_signal)
        signal.connect(callback) # FIXME: que hacemos con extra_data ??

    def connect_after(self, detailed_signal, callback, *extra_data):
        signal = self._get_and_assert(detailed_signal)
        signal.connect_after(callback) # FIXME: idem anterior

    def disconnect(self, detailed_signal, callback):
        signal = self._get_and_assert(detailed_signal)
        signal.disconnect(callback)

    def disconnect_after(self, detailed_signal, callback):
        signal = self._get_and_assert(detailed_signal)
        signal.disconnect_after(callback)

    def handler_block(self, callback=None):
        pass

    def handler_unblock(self, callback=None):
        pass

###############################################################################

# FIXME: move this to test file
if __name__ == '__main__':
    # Test code
    import pprint
    print "Testing...\n"

    class Car(object):
        def __init__(self):
            self.start_signal = Signal("engine-started", namespace=self)
        def start(self):
            self.start_signal.emit("OK")
        def do_engine_started(self, msg):
            print "Engine started: %s, on %s" % (msg, self.__class__.__name__)

    class StandardCar(Car):
        # override handler
        def do_engine_started(self, msg):
            print "Engine started: %s, on standard %s" % (msg, \
                    self.__class__.__name__)

    class LuxuryCar(Car):
        def __init__(self):
            super(LuxuryCar, self).__init__()
            self.stop_signal = Signal("engine-stoped", namespace=self)
        def stop(self):
            self.stop_signal.emit(":-(")
        def do_engine_stoped(self, msg):
            print "Engine stoped: %s, on %s" % (msg, self.__class__.__name__)

    # ok, do things with cars
    car = Car()
    s_car = StandardCar()
    l_car = LuxuryCar()

    car.start()
    s_car.start()
    l_car.start()

    # only on luxury
    l_car.stop()

    # Meta class Test
    class SignaledObjectMetaTest(object):
        __metaclass__ = SignaledObjectMetaType
        __signals__ = {'engine-started': None}
        def dump(self): pprint.pprint(self._signals)
        def do_engine_started(self):
            print "Engine started..."

    class SignaledObjectInheritanceTest(SignaledObjectMetaTest):
        __signals__ = {'engine-stoped': None}
        def __init__(self, name):
            self.name = name
        def do_engine_stoped(self):
            print "Engine stoped..."

    class SignalTest(SignaledObjectInheritanceTest):
        __signals__ = {'show': None}
        # Esto tiene que fallar

    test1 = SignaledObjectMetaTest()
    test2 = SignaledObjectInheritanceTest("test2")
    test3 = SignalTest("test3")
    print "\nClass created:"
    print signal_list_names(SignalTest)
    print "Objects created:"
    print signal_list_names(test3)
    print
    print dir(test1)
    test1.dump()
    print
    print dir(test2)
    test2.dump()
    print
    print dir(test3)
    test3.dump()
