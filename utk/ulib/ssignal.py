# -*- coding: utf-8 -*-

from utils import norm, unnorm

SIGNAL_RUN_FIRST, SIGNAL_RUN_LAST = range(2)


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

    def __init__(self, name, default_cb=None, flag=SIGNAL_RUN_LAST, prefix=None):
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
        self._default_cb_name = None

        if prefix:
            self._prefix = prefix

        if default_cb is False:
            assert callable(default_cb) or isinstance(default_cb, basestring),\
                    "default_cb must be a callable or str"

        if isinstance(default_cb, basestring):            
            self._default_cb_name = default_cb
            default_cb = None

        elif default_cb is False:
            #assert isinstance(namespace, dict) or \
            #       isinstance(getattr(namespace, '__dict__'), dict) or \
            #       isinstance(namespace, type), \
            #       "namespace must be a dict instance or object with __dict__"\
            #       " attribute"

            self._default_cb_name = self._prefix + norm(name)

        self._namespace = namespace

        super(Signal, self).__init__(name, default_cb=default_cb, flag=flag)

    def emit(self, owner=None, *args):
        if self._default_cb is None and self._default_cb_name:
            self._default_cb = self._get_default_cb(owner)

        return super(Signal, self).emit(*args)

    def _get_default_cb(self, owner=None):
        assert self._namespace, "i don't know where to find default callback"

        #default_cb = getattr(self._namespace, self._default_cb_name, None)
        default_cb = getattr(owner, self._default_cb_name, None)

        if default_cb is None:
            raise AttributeError("%s object has no attribute '%s'"\
                    % (self._namespace, self._default_cb_name))

        assert callable(default_cb),\
                "'%s' attribute must be callable" % self._default_cb_name

        return default_cb


def install_signal(cls, signame, default_cb=None, flag=SIGNAL_RUN_LAST,
                   override=False):
    assert isinstance(cls, type), "'cls' must be a class type"

    if isinstance(default_cb, basestring):
        default_ = getattr(cls, "%s" % default_cb, None)
        assert default_ and callable(default_), "You set '%s' as default "\
                "callback name but i can't find any callable with this name "\
                "in %s class" % (default_cb, cls.__name__)

    signals = getattr(cls, '_decl_signals', {})

    if not signals and not getattr(cls, '_signal_api', None):
        _install_signals_api(cls)

    if not override:
        assert not signals.has_key(signame), "The %s already has a signal "\
                "named '%s'" % (cls.__name__, signame)

    signals[signame] = Signal(signame, default_cb, cls, flag)

    setattr(cls, '_decl_signals', signals)


class SignaledMeta(type):

    def __init__(cls, classname, bases, ns):
        type.__init__(cls, classname, bases, ns)
        _install_signals(cls)


def _install_signals(cls):
    _signals = {}
    for base in reversed(cls.mro()):
        if hasattr(base, '__signals__'):
            _signals.update(base.__signals__)
    for signame, conf in _signals.iteritems():
        conf = _get_signal_configuration(conf)
        install_signal(cls, signame,
                       default_cb=conf['handler'],
                       flag=conf['flag'],
                       override=conf['override'])

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

    return {'flag': conf.get('flag', SIGNAL_RUN_LAST),
            'handler': conf.get('handler'),
            'override': conf.get('override', False)}


def _get_and_assert(obj, signame):
    sig = obj._decl_signals.get(signame)
    if not sig:
        raise TypeError("unknown signal name: %s" % signame)
    return sig

def _install_signals_api(cls):

    # signal api
    def emit(self, signame, *data):
        signal = _get_and_assert(self, signame)
        signal.emit(self, *data)

    def connect(self, signame, callback, *data):
        signal = _get_and_assert(self, signame)
        signal.connect(callback)

    api_methods = dict(locals())
    api = ('emit', 'connect')

    for meth in api:
        setattr(cls, meth, api_methods[meth])

class SignaledObject(object):
    __metaclass__ = SignaledMeta
