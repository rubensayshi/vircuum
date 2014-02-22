import copy
from vircu.util.UserDict import UserDict
from stringlike import StringLike
from werkzeug.utils import import_string
            
            

ENVIRON_VAR = 'ENVIRONMENT'
DEFAULT_ENVIRONMENT = 'development'


def dict_from_object(obj):
    """copy&paste from flask.Config class"""
    dict = {}
    
    if isinstance(obj, basestring):
        obj = import_string(obj)
    
    for key in dir(obj):
        if key.isupper():
            dict[key] = getattr(obj, key)
    
    return dict


class Environment(StringLike):
    def __init__(self, env = None):
        self._env = env
    
    @property
    def env(self):
        if self._env is None:
            import os
            self._env = os.environ.get(ENVIRON_VAR, DEFAULT_ENVIRONMENT)
        
        return self._env
    
    def __str__(self):
        return self.env


# init environment
environment = Environment()


class EnvironmentConfig(UserDict):
    """inherit from UserDict (without calling it's __init__) 
        so that we can provide our own (lazy loading) self.data - containing our config"""
    
    def __init__(self, environment = None, use_config_local = True, *args, **kwargs):
        self._environment = environment
        self._environment_class_name = None
        self._data = None
        self.use_config_local = use_config_local
    
    def __getitem__(self, attr):
        v = self.data.__getitem__(attr)
        
        if isinstance(v, LazyConfigValue):
            # overwrite the lazy config value with the generated value (based on self as config)
            self.data[attr] = v.value(self)
            # return 'normally'
            return self.data.__getitem__(attr)
        
        if isinstance(v, RequiredConfigValue):
            raise Exception('RequiredConfigValue [%s]' % attr)
        
        return v
    
    def __repr__(self):
        # loop over the data and trigger __getitem__ for each item
        return repr(dict([(k, self[k]) for k in self.data]))
    
    @property
    def environment(self):
        return str(self._environment or environment)
    
    @property
    def environment_class_name(self):
        if not self._environment_class_name:
            self._environment_class_name = "".join(map(lambda s: str(s).capitalize(), self.environment.split('_')))
        
        return self._environment_class_name
    
    @property
    def data(self):
        if self._data is None:
            self._data = {}
            
            cls = import_string('vircu.config.configs.' + self.environment_class_name + 'Config')
            
            # build config or simply create dict from object
            #  and deepcopy it to avoid object references being shared across different configs, in the edge case of having different configs in 1 codepath
            if issubclass(cls, AbstractVirCuConfig):
                self._data.update(copy.deepcopy(cls.build_config()))
            else:
                self._data.update(copy.deepcopy(dict_from_object(cls)))
            
            if self.use_config_local:
                try:
                    self._data.update(copy.deepcopy(dict_from_object('vircu.config.config_local')))
                except ImportError:
                    pass
        
        return self._data
    
    def still_required(self):
        return [k for k, v in self.data.iteritems() if isinstance(v, RequiredConfigValue)]
    
    # --------------
    # raise NotImplementedError for a bunch of methods which return values without going through __getitem__
    #  and some methods where we are uncertain how they'll function
    # if we every need one of these, just test / fix them ;-)
    def __cmp__(self, dict):
        raise NotImplementedError
    def clear(self):
        raise NotImplementedError
    def copy(self):
        raise NotImplementedError
    def items(self):
        raise NotImplementedError
    def iteritems(self):
        raise NotImplementedError
    def itervalues(self):
        raise NotImplementedError
    def values(self):
        raise NotImplementedError
    def pop(self, key, *args):
        raise NotImplementedError
    def popitem(self):
        raise NotImplementedError


# init config
config = EnvironmentConfig()


class Version(StringLike):
    def __init__(self, version_name):
        self.version_name = version_name
        self._version     = None
    
    @property
    def is_dev(self):
        from vircu import constants
        return config['ENV'] == constants.ENV_DEV
    
    @property
    def version(self):
        from time import time
        
        if self._version is None:
            self._version = self.get_version()
        
        return self._version if self._version else str(int(time()))
    
    def get_version(self):
        import os
        
        if not self.is_dev:
            return self._get_version()
        else:
            if config['VERSION_ON_DEV'] and isinstance(config['VERSION_ON_DEV'], basestring):
                # version needs to be VERSION_STRING_LENGTH long for some of our sanity checks
                return str(config['VERSION_ON_DEV']).rjust(config['VERSION_STRING_LENGTH'], "_")
            elif config['VERSION_ON_DEV']:
                return self._get_version()
            else:
                return None
    
    def _get_version(self):
        import os
        version_file = os.path.join(config['ROOT_DIR'], "VERSION")
        
        if not os.path.exists(version_file):
            raise Exception("VERSION file not found")
        
        try:
            f = open(version_file, "r")
            data = f.read().split("\n")
            
            for line in data:
                line = str(line).split("=")
                if len(line) == 2:
                    if line[0] == self.version_name:
                        return line[1]
        except:
            raise Exception("Failed to parse VERSION file")
        
        raise Exception("Failed to find version [%s] in VERSION file" % self.version_name)
    
    def __str__(self):
        return self.version


# init versions
MAIN_VERSION   = Version("MAIN_VERSION")
STATIC_VERSION = Version("STATIC_VERSION")


class LazyConfigValue(object):
    """LazyConfigValue provides a way to do lazy string replacements.
        this allows us to overload the values that are used in the replacement in our env specific classes.
        
        instead of doing a lot of fancy (and not perfectly bullet proof) things with extending string or trying to behave like a string
         we're instead just letting the EnvironmentConfig use our .value method
        
        for example: 
            class Config(object): 
                REDIS_SERVER=  'localhost'; 
                REDIS_URL = LazyConfigString('redis://%(REDIS_SERVER)s:9999/1')
            
            class DevConfig(Config):
                REDIS_SERVER = 'redis1.dev'
        
            print DevConfig()['REDIS_URL'] # redis://redis1.dev:9999/1
    """
    
    def __init__(self, pattern, type = str):
        self._type    = type
        self._pattern = pattern
        self._value   = None
    
    @property
    def pattern(self):
        return self._pattern
    
    @property
    def global_config(self):
        """use the self._config bound to this or otherwise fallback to the global active 'config'"""
        return config
    
    def value(self, config = None):
        config = config or self.global_config
        
        # generate the value if we haven't already
        if self._value is None:
            if self.pattern in config:
                self._value = config[self.pattern]
            elif callable(self.pattern):
                self._value = self.pattern(config)
            else:
                self._value = self.pattern % config
            
            self._value = self._type(self._value)
        
        return self._value
    
    def __repr__(self):
        return "<LazyConfigValue %s>" % self.pattern


class RequiredConfigValue(object):
    """RequiredConfigValue provides a way to do specify a config value that needs to be overwritten by any config inhereting it."""
    pass


class AbstractVirCuConfig(object):
    @classmethod
    def build_config(cls):
        config = {}
        
        for key in dir(cls):
            if key.isupper():
                config[key] = getattr(cls, key)
        
        return config


class VirCuMixinConfig(AbstractVirCuConfig):
    pass


class VirCuBaseConfig(AbstractVirCuConfig):
    pass


class VirCuServerConfig(AbstractVirCuConfig):
    pass


class VirCuEnvConfig(AbstractVirCuConfig):
    @classmethod
    def build_config(cls):
        config = {}
        
        parents = [('BASE_CONFIG',     VirCuBaseConfig), 
                   ('SERVER_CONFIG',   VirCuServerConfig)]
        
        for parent_attr, parent_class in parents:
            if not hasattr(cls, parent_attr):
                raise Exception("VirCuEnvConfig.%s needs to be defined" % parent_attr)
            
            parent = getattr(cls, parent_attr)
            
            if not issubclass(parent, parent_class):
                raise Exception("%s is set to %s, which is not a subclass of %s" % (parent_attr, parent, parent_class))
        
        base_config     = cls.BASE_CONFIG.build_config()
        server_config   = cls.SERVER_CONFIG.build_config()
        
        config.update(base_config)
        config.update(server_config)
        
        for key in dir(cls):
            if key.isupper() and key not in [k for k, c in parents]:
                config[key] = getattr(cls, key)
        
        return config

