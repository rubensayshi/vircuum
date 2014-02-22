from vircu import constants
from vircu.config import LazyConfigValue, RequiredConfigValue, VirCuBaseConfig, VirCuEnvConfig, VirCuServerConfig, VirCuMixinConfig
import locale
import logging
import os
import pytz


__REQUIRED__ = RequiredConfigValue()


class BaseConfig(VirCuBaseConfig):
    """base config which defines all the config values our application needs
    
       values should either be a proper default value which we can use 'blindly' anywhere, unless we really want something different for a specific env
        or they should be set to __REQUIRED__ so that they need to be specified by server, language or env specific configs! 
    """
    
    ENV             = __REQUIRED__ # constants.ENV_*
    ENVIRONMENT     = __REQUIRED__ # the env name that should result in using this config
    
    SERVER_TIMEZONE = pytz.timezone('Europe/Amsterdam')
    LOCALE_DEFAULT  = 'en_US'
    
    LOCALE = {
       locale.LC_TIME     : 'en_US.UTF-8', 
       locale.LC_NUMERIC  : 'en_US.UTF-8', 
       locale.LC_MONETARY : 'en_US.UTF-8',
    }
    
    SITE_NAME       = 'VirCu'
    BASE_SERVER_NAME    = __REQUIRED__ # upcoming.nl
    DEFAULT_SERVER_NAME = __REQUIRED__ # www.upcoming.nl
    INTERNAL_SERVER_NAME= __REQUIRED__ # localhost, loadbalancer IP or web.lb    # used to go around our proxy
    
    BASIC_LOG_LEVEL = logging.WARNING
    LOGGING_LEVEL   = logging.WARNING
    EMAIL_LOGGING   = False
    NEWRELIC        = True
    
    VERSION_ON_DEV = False
    MAIN_VERSION   = None
    STATIC_VERSION = None
    VERSION_STRING_LENGTH = 10

    DEBUG = False
    
    SECRET_KEY          = '63fe3db58d1e3aa76432b6badbcafaeb'
    SESSION_COOKIE_NAME = "c_ses"
    PERMANENT_SESSION_LIFETIME = 86400 * 60 # 60 days
    SESSION_IN_MEMORY_OK = False
    
    CSRF_ENABLED     = True
    CSRF_SESSION_KEY = LazyConfigValue('%(SECRET_KEY)s')

    STATIC_NR_DOMAINS      = 2
    STATIC_VARNISH_SERVERS = None
    USE_STATIC_HOST = False # True
    STATIC_HOST     = None # LazyConfigValue('%%d.static.%(BASE_SERVER_NAME)s')
    USE_MINIFIED_ASSETS = True

    BASE_APP_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    ROOT_DIR     = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    TMP_DIR      = os.path.join(ROOT_DIR, "tmp")
    STATIC_DIR   = os.path.join(BASE_APP_DIR, "static")
    
    SQLALCHEMY_DATABASE_URI = __REQUIRED__
    SQLALCHEMY_POOL_RECYCLE = 600
    DATABASE_CONNECT_OPTIONS = {}
    
    SHOW_BRAND = True
    
    TICKER_SILENT = __REQUIRED__
    OLD_THRESHOLD = 5 * 60

    GOOGLE_ANALYTICS = 'UA-46778032-1'


class DevServerConfig(VirCuServerConfig):
    """dev server config"""
    
    ENV = constants.ENV_DEV
    
    SQLALCHEMY_DATABASE     = 'vircu'
    SQLALCHEMY_DATABASE_URI = LazyConfigValue('mysql://root:Letmein1@localhost/%(SQLALCHEMY_DATABASE)s?charset=utf8')
    
    SQLALCHEMY_POOL_RECYCLE = 59
    
    USE_MINIFIED_ASSETS = False
    
    TICKER_SILENT = False


class LiveServerConfig(VirCuServerConfig):
    """live server config"""
    
    ENV = constants.ENV_LIVE
    
    SQLALCHEMY_DATABASE     = 'vircu'
    SQLALCHEMY_DATABASE_URI = LazyConfigValue('mysql://root:root@localhost/%(SQLALCHEMY_DATABASE)s?charset=utf8')

    SQLALCHEMY_POOL_RECYCLE = 59
    
    TICKER_SILENT = True


class DevelopmentConfig(VirCuEnvConfig):
    """basic development env config"""
    
    ENVIRONMENT = 'development'
    
    BASE_CONFIG     = BaseConfig
    SERVER_CONFIG   = DevServerConfig
    
    BASIC_LOG_LEVEL     = logging.DEBUG
    LOGGING_LEVEL       = logging.DEBUG
    DEBUG               = True
    
    BASE_SERVER_NAME    = 'localhost:5000'
    DEFAULT_SERVER_NAME = 'localhost:5000'
    INTERNAL_SERVER_NAME= 'localhost:5000'


class LiveConfig(VirCuEnvConfig):
    """basic development env config"""
    
    ENVIRONMENT = 'live'
    
    BASE_CONFIG     = BaseConfig
    SERVER_CONFIG   = LiveServerConfig
    
    BASIC_LOG_LEVEL     = logging.WARNING
    LOGGING_LEVEL       = logging.WARNING
    DEBUG               = False
    
    BASE_SERVER_NAME    = 'vircu-demo.rubensayshi.com:5000'
    DEFAULT_SERVER_NAME = 'vircu-demo.rubensayshi.com:5000'
    INTERNAL_SERVER_NAME= 'vircu-demo.rubensayshi.com:5000'

