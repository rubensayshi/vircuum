# -*- coding: utf-8 -*-
import os
import subprocess
import urllib2
import pytz
import re
import time
import ipaddr
from functools import partial, wraps
from datetime import datetime, timedelta
from unicodedata import normalize
from collections import namedtuple
import urlparse
from flask import current_app as app, request, g, url_for
import cookielib
import inspect
import hashlib
import logging
import math
from itertools import izip_longest
import locale
from vircu.config import config

DATE_INT_FORMAT = '%Y%m%d%H%M%S'
CHROME_USERAGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.97 Safari/537.11 VirCu/1.0 +http://www.vircu.me/'
UPCOMING_USERAGENT = 'VirCu/1.0 +http://www.vircu.me/'
SLUGIFY_DEFAULT_CHARS = 'abcdefghijklmnopqrstuvwxyz0123456789-_'
http_re = re.compile('''^https?:\/\/''')

PRETTY_DATE_SIMPLE    = 0
PRETTY_DATE_LOCALIZED = 1
PRETTY_DATE_RELATIVE  = 2

class HeadRequest(urllib2.Request):
    def get_method(self):
        return "HEAD"

PartialCookie = partial(cookielib.Cookie, version=0, 
                                          port=None, 
                                          port_specified=False, 
                                          domain_specified=False, 
                                          domain_initial_dot=False, 
                                          path_specified=True, 
                                          secure=False, 
                                          expires=None, 
                                          discard=True, 
                                          comment=None, 
                                          comment_url=None, 
                                          rest={'HttpOnly': None}, 
                                          rfc2109=False)

def dirty_decode(s):
    if not isinstance(s, unicode):
        try:
            s = unicode(s, 'utf-8')
        except UnicodeDecodeError:
            s = unicode(s, 'latin-1')
    return s


def as_servertime(dt):
    if not dt:
        return None
    
    return config['SERVER_TIMEZONE'].localize(dt)


def fb_dt_to_local_dt(dt):
    """
    this is horrific but until we clean up our code when storing datetime objects across the whole project this will have to suffice ...
     it strips off the +0000 because strptime can't parse that, then localizes it to UTC and then to our servertime,
     so we end up with a datetime instance in our local time
     finally it converts it back to a naive datetime object, otherwise we can't store it ..
    """
    
    dt = datetime.strptime(dt.replace('+0000', ''), "%Y-%m-%dT%H:%M:%S")
    
    dt = pytz.utc.localize(dt)
    dt = dt.astimezone(config['SERVER_TIMEZONE'])
    dt = datetime.fromtimestamp(time.mktime(dt.timetuple()))
    
    return dt


def is_pjax_request():
    return is_true(request.headers.get('X-PJAX', 0)) or is_true(request.args.get('pjax', 0))


def is_fast_connection():
    return is_true(request.headers.get('X-Fast-Connection', 0)) or is_true(request.args.get('fast', 0))

def is_frame_request():
    return is_true(request.headers.get('X-FRAME', 0)) or is_true(request.args.get('frame', 0))

def get_api_version():
    return int(request.args.get('api_version', request.headers.get('X-API-VERSION', 0)) or 0)

def is_alt_statics():
    try:
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        if ip:
            if ',' in ip:
                ip = str(str(ip).split(",")[0]).strip()
            
            ip = ipaddr.IPAddress(ip)
        
        return ip in ipaddr.IPNetwork('192.168.2.0/16') \
            or ip in ipaddr.IPNetwork('127.0.0.0/16') \
            or ip in ipaddr.IPNetwork('94.100.112.225') \
            or is_true(request.args.get('alt', 0))
    except:
        pass
    
    return False

def is_true(v):
    if isinstance(v, bool):
        return v
    else:
        try:
            if str(v).lower() == 'true':
                return True
        except:
            pass
        try:
            return bool(int(v))
        except:
            pass
    
    return False


def simple_request_url(url, data = None, timeout = None, return_response_object = False, 
                       head = False, cookiejar = None, useragent = None, disable_proxy = None,
                       internal_request = False):
    # urllib2 won't escape spaces and without doing this here some requests will fail
    url     = url.replace(' ', '%20')
    host    = None
    urlp    = None
    
    if internal_request == 'detect':
        urlp = urlp or urlparse.urlparse(url)
        internal_request = urlp.netloc == config['DEFAULT_SERVER_NAME']
    
    if internal_request:
        if disable_proxy is None:
            disable_proxy = True
        
        urlp = urlp or urlparse.urlparse(url)
        host = urlp.netloc
        url  = "http://%(host)s%(url)s" % dict(host = config['INTERNAL_SERVER_NAME'], url = urlp.path + ('?' + urlp.query if urlp.query else ''))
    
    request = HeadRequest if head else urllib2.Request 
    request = request(url)
    request.add_header('User-Agent', useragent or UPCOMING_USERAGENT)
    
    if host:
        request.add_header('Host', host)
    
    handlers = []
    if cookiejar:
        handlers.append(urllib2.HTTPCookieProcessor(cookiejar))
    if disable_proxy:
        handlers.append(urllib2.ProxyHandler({}))
    
    opener = urllib2.build_opener(*handlers)
    
    timeout = timeout or 30
    response = opener.open(request, data, timeout)
    
    return response if return_response_object else response.read()


PageInfo = namedtuple('PageInfo', ['page', 'page_count', 'offset', 'limit', 'start', 'end'])
def normalize_page_info(page = 0, page_count = 0):
    page   = max(int(page or 0), 1)
    limit  = page_count
    offset = (page - 1) * limit
    start  = offset
    end    = offset + limit
    
    return PageInfo(page, page_count, offset, limit, start, end)


def date_int(dt):
    return dt.strftime(DATE_INT_FORMAT)


def get_rounded_hour(dt = None):
    """get the 'nearest' hour - always rounds down 
        so 23:59:59 becomes 23:00:00"""
    dt = dt or datetime.now()
    return dt.replace(minute = 00, second = 00, microsecond = 00)


def get_rounded_minute(dt = None):
    """get the 'nearest' minute - always rounds down 
        so 23:59:59 becomes 23:59:00"""
    dt = dt or datetime.now()
    return dt.replace(second = 00, microsecond = 00)


def get_rounded_day(dt = None):
    """get the 'nearest' day - always rounds up to the last hour of the day (11pm)
        so 00:01:01 becomes 23:00:00"""
    dt = dt or datetime.now()
    return dt.replace(hour = 23, minute = 00, second = 00, microsecond = 00)


def get_start_of_day(dt = None):
    """get the 'start of the day' day - always rounds down to the first second of the day (00:00:00:00 pm)"""
    dt = dt or datetime.now()
    return dt.replace(hour = 00, minute = 00, second = 00, microsecond = 00)


def get_end_of_hour(dt = None):
    dt = dt or datetime.now()
    return dt.replace(minute = 59, second = 59, microsecond = 00)


def get_end_of_day(dt = None):
    return get_end_of_hour(get_rounded_day(dt))


def get_start_of_week(dt = None):
    """get the start the week - always rounds down to the first hour of the monday 
        so sunday 22 dec 23:59:59 becomes monday 17 dec 2012 00:00:00"""
    dt = dt or datetime.now()
    
    return datetime.strptime(dt.strftime("%Y %W 1 00 00 00"), "%Y %W %w %H %M %S")


def get_end_of_week(dt = None):
    """get the end of the week - always rounds up to the last hour of the sunday 
        so monday 17 dec 2012 00:00:00 becomes sunday 22 dec 23:59:59"""
    dt = dt or datetime.now()
    
    return datetime.strptime(dt.strftime("%Y %W 6 23 59 59"), "%Y %W %w %H %M %S") + timedelta(days=1)


def get_rounded_week(dt = None):
    return get_end_of_week(dt)


def get_start_of_month(dt = None):
    """get the start of the month - always rounds down to the first hour of the first day
        so monday 17 dec 2012 00:01:01 becomes saturday 1 dec 00:00:00"""
    dt = dt or datetime.now()
    
    return datetime.strptime(dt.strftime("%Y-%m-1 00:00:00"), "%Y-%m-%d %H:%M:%S")


def get_end_of_month(dt = None):
    """get the end of the month - always rounds up to the last hour of the last day
        so monday 17 dec 2012 00:01:01 becomes monday 31 dec 23:59:59"""
    return get_end_of_day(get_start_of_month(get_start_of_month(dt) + timedelta(weeks = 5)) - timedelta(days = 1))


def get_rounded_month(dt = None):
    return get_start_of_month(dt)


def get_last_week_of_month(dt = None):
    """get the end of the last week of the month
        so tuesday 31 okt 2013 00:01:01 becomes sunday 27 okt 23:59:59"""
    dt = get_end_of_month(dt)
    
    if get_end_of_week(dt) > dt:
        dt -= timedelta(days = 7)
    
    return get_end_of_week(dt)


MULTIPLE_VALUES_SEP = u"|$|"
def explode_multiple_values(value):
    return [val for val in value.split(MULTIPLE_VALUES_SEP) if len(unicode(val).strip()) > 0] if value else []


def get_domain(url, subdomain = True):
    url = url or ''
    
    if not http_re.match(url):
        url = 'http://' + url
    
    url = urlparse.urlparse(url)
    domain = str(url.netloc).replace('www.', '')
    
    extract = app.tldextract(domain)
    result = filter(None, [extract.subdomain if subdomain else None, extract.domain, extract.tld])
    
    return ".".join(result)


def get_pretty_url(url):
    url = urlparse.urlparse(url)
    
    host = str(url.netloc).replace('www.', '')
    path = str(url.path)
    
    if path == '/':
        path = None
    
    host = host or ''
    path = path or ''
    
    return host + path


def parse_sizes(sizes):
    if isinstance(sizes, tuple):
        sizes = {'width' : sizes[0] or None, 'height' : sizes[1] or None}
    elif isinstance(sizes, str):
        sizes = sizes.split("x")
        sizes = {'width' : sizes[0] or None, 'height' : sizes[1] or None}
    elif isinstance(sizes, dict):
        pass
    else:
        sizes = {'width' : None, 'height' : None}
    
    return sizes


def create_dir(dir_path):
    try:
        os.makedirs(dir_path)
    except OSError:
        if os.path.isdir(dir_path):
            # This means that the directory already existed, we can continue
            pass
        else:
            # Otherwise, raise an exception
            raise


def less_to_css(src_path, dst_path, include_path = []):
    if not os.path.isfile(dst_path):
        dst_mtime = -1
        create_dir(os.path.dirname(dst_path))
        open(dst_path, 'w').close()
    else:
        dst_mtime = os.path.getmtime(dst_path)
    
    src_mtime = os.path.getmtime(src_path)
    if src_mtime >= dst_mtime:
        print("Compiling .less file: " + src_path)
        include_path = ":".join(include_path)
        return_code = subprocess.call(['lessc', src_path, dst_path, "--include-path=%s" % include_path], shell=False)
        if return_code == 0:
            print("lessc done with: " + src_path)
        else:
            print("lessc failed on: " + src_path)
            os.remove(dst_path)


def slugify(text, encoding = None, lower = True, permitted_chars = None):
    permitted_chars = permitted_chars or SLUGIFY_DEFAULT_CHARS
    
    if text is None:
        text = ''
    if isinstance(text, str):
        text = text.decode(encoding or 'ascii')
    clean_text = text.strip() \
                     .replace(' ', '-') \
                     .replace('+', '-') \
                     .replace('.', '_')
    
    if lower:
        clean_text = clean_text.lower()
    else:
        permitted_chars += permitted_chars.upper()
    
    ascii_text = normalize('NFKD', clean_text).encode('ascii', 'ignore')
    strict_text = map(lambda x: x if x in permitted_chars else '', ascii_text)
    
    slug = ''.join(strict_text)

    while '--' in slug:
        slug = slug.replace('--', '-')
    while '__' in slug:
        slug = slug.replace('__', '_')
    while slug.startswith(('_', '-')):
        slug = slug[1:]
    while slug.endswith(('_', '-')):
        slug = slug[:-1]
        
    return slug


def pretty_date(original_date, now = None, text_mode = PRETTY_DATE_LOCALIZED):
    """
    From a datetime return a pretty string like 'an hour ago', 'just now', etc
    by setting :text_mode to PRETTY_DATE_SIMPLE you can force not using our (localized) texts but instead use shorter hardcoded texts
    by setting :text_mode to PRETTY_DATE_RELATIVE you can force not using our (localized) texts but instead use hardcoded texts that present comparing 2 dates better
    """
    now  = now or datetime.now()
    diff = now - original_date
    minute_diff = int(diff.seconds / 60)
    hour_diff = int(minute_diff / 60)
    day_diff = diff.days

    if text_mode == PRETTY_DATE_LOCALIZED:
        pretty_date_texts = {
            'NOW'         : texts.texts.get('PRETTY_DATE_NOW'),
            'MINUTES_AGO' : texts.texts.get('PRETTY_DATE_MINUTES_AGO'),
            'HOURS_AGO'   : texts.texts.get('PRETTY_DATE_HOURS_AGO'),
            'DAYS_AGO'    : texts.texts.get('PRETTY_DATE_DAYS_AGO'),
        }
    elif text_mode == PRETTY_DATE_SIMPLE:
        pretty_date_texts = {
            'NOW'         : 'just now',
            'MINUTES_AGO' : '{0} min(s) ago',
            'HOURS_AGO'   : '{0} hr(s) ago',
            'DAYS_AGO'    : '{0} day(s) ago',
        }
    elif text_mode == PRETTY_DATE_RELATIVE:
        pretty_date_texts = {
            'NOW'         : 'shortly after',
            'MINUTES_AGO' : '{0} min(s) after',
            'HOURS_AGO'   : '{0} hr(s) after',
            'DAYS_AGO'    : '{0} day(s) after',
        }
    
    # If it's in the future, ignore
    if day_diff < 0:
        return ''

    if day_diff == 0:
        if minute_diff < 15:
            return format_text(pretty_date_texts['NOW'])
        elif minute_diff < 60:
            return format_text(pretty_date_texts['MINUTES_AGO'], str(minute_diff), minute_diff)
        else:
            return format_text(pretty_date_texts['HOURS_AGO'], str(hour_diff), hour_diff)
    else:
        return format_text(pretty_date_texts['DAYS_AGO'], str(day_diff), day_diff)


def csrf_disabled_form_class(form):
    def get_form(*args, **kwargs):
        kwargs['csrf_enabled'] = False
                
        return form(*args, **kwargs)
    
    return get_form


def floor_date(dt, round_by = 'day'):
    # when rounding by week the day is defined by week / dayoftheweek
    # while otherwise the day is defined by month / day
    if round_by == 'week':
        units = [('year',   '%Y', None), 
                 ('week',   '%W', '1'),  
                 ('day',    '%w', '0'), 
                 ('hour',   '%H', '00'), 
                 ('minute', '%M', '00'), 
                 ('second', '%S', '00')]
    else:
        units = [('year',   '%Y', None), 
                 ('month',  '%m', '1'), 
                 ('day',    '%d', '1'), 
                 ('hour',   '%H', '00'), 
                 ('minute', '%M', '00'), 
                 ('second', '%S', '00')]

    # loop over the units,
    # while we haven't found our round_by yet we user the real data
    # and once we have found our round_by we keep using the default 
    found = False
    src  = ''
    dest = ''
    for unit, mod, default in units:
        if not found:
            src += ' ' + mod
        else:
            src += ' ' + default
        
        # always use the mod for the dest
        dest += ' ' + mod
        
        # check if found
        found = found or unit == round_by
    
    # examples:
    # round_by='month' -> datetime.strptime(dt.strftime("%Y %m 01 00 00 00"), "%Y %m %d %H %M %S")
    # round_by='hour'  -> datetime.strptime(dt.strftime("%Y %m %d %H 00 00"), "%Y %m %d %H %M %S")
    
    return datetime.strptime(dt.strftime(src), dest)


def lineno():
    """Returns the current line number in our program."""
    return inspect.currentframe().f_back.f_lineno


def called_from():
    """Returns the line number and filename from where our function was called in our program."""
    frame = inspect.currentframe().f_back.f_back

    lineno = frame.f_lineno
    filename = frame.f_globals["__file__"]
    return (filename, lineno)


def isnumber(val):
    if isinstance(val, (int, long, float, complex)):
        return True
    else:
        try:
            float(val)
            return True
        except:
            return False


def is_dev():
    return app.config['MAIN_VERSION'].is_dev


telegraaf_re  = re.compile('''(www\.?)telegraaf\.nl/(.+)/(?P<id>\d+)/(?P<title>.+?)(\.html)?$''')
spitsnieuw_re = re.compile('''(www\.?)spitsnieuws\.nl/archives/(?P<spitsurl>.+)$''')
adnl_re = re.compile('''(www\.?)(?P<base>(ad|volkskrant|trouw)\.nl/.+)/nl/(?P<rest>.+)$''') # covers ad.nl, volkskrant.nl, trouw.nl
def link_to_mobile(link):
    link = telegraaf_re.sub('telegraaf.mobi/article/\g<id>/\g<title>', link)
    link = spitsnieuw_re.sub('m.spitsnieuws.nl/pl/svt/po/opnl/si/tmg_spits/pa/alles-article-web?spitsurl=/\g<spitsurl>', link)
    link = adnl_re.sub('m.\g<base>/m/nl/\g<rest>', link)
    
    return link


def appcache_enabled():
    return app.config['APP_CACHE_ON_DEV'] or not app.config['MAIN_VERSION'].is_dev


def feature_enabled(feature):
    """check if `feature.upper()`_ENABLED is True in the config or if '?no_cache=1&`feature`_enabled=1' is in the URL"""
    feature = str(feature).lower() + '_enabled'
    
    if feature in request.args and is_true(request.args.get('no_cache', False)):
        return is_true(request.args.get(feature, False))
    
    if app.config[feature.upper()]:
        return True
    
    return False


def referrer_is_self(referrer, request_host = None):
    if request_host and get_domain(referrer, subdomain = False) == get_domain(request_host, subdomain = False):
        return True
    elif get_domain(referrer, subdomain = False) == get_domain(app.config['SERVER_NAME'], subdomain = False):
        return True
    
    return False


def kwargs_to_args(f, *args, **kwargs):
    """latest version of flask-cache memoize_kwargs_to_args method"""
    
    #: Inspect the arguments to the function
    #: This allows the memoization to be the same
    #: whether the function was called with
    #: 1, b=2 is equivilant to a=1, b=2, etc.
    new_args = []
    arg_num = 0
    argspec = inspect.getargspec(f)

    args_len = len(argspec.args)
    for i in range(args_len):
        if i == 0 and argspec.args[i] in ('self', 'cls'):
            #: use the repr of the class instance
            #: this supports instance methods for
            #: the memoized functions, giving more
            #: flexibility to developers
            arg = repr(args[0])
            arg_num += 1
        elif argspec.args[i] in kwargs:
            arg = kwargs[argspec.args[i]]
        elif arg_num < len(args):
            arg = args[arg_num]
            arg_num += 1
        elif abs(i-args_len) <= len(argspec.defaults):
            arg = argspec.defaults[i-args_len]
            arg_num += 1
        else:
            arg = None
            arg_num += 1

        new_args.append(arg)
    
    return tuple(new_args), {}


def make_func_cache_key(func, key = None, args_in_key = False, *args, **kwargs):
    base_key = func.__name__ if key is None else key
    
    if args_in_key:
        cache_key = hashlib.md5()

        if callable(func):
            args, kwargs = kwargs_to_args(func, *args, **kwargs)

        try:
            updated = "{0}{1}{2}".format(base_key, args, kwargs)
        except AttributeError:
            updated = "%s%s%s" % (base_key, args, kwargs)

        cache_key.update(updated)
        cache_key = cache_key.digest().encode('base64')[:16]
    else:
        cache_key = base_key
    
    return "only_one_lock:{}".format(cache_key)

def only_one(key = None, args_in_key = False, expires = None):
    """
    Ensures that a given task in executed by only 1 worker or machine at any given moment
    :param str   key:          Key to identify the task. If a key is not given the func name will be used.
    :param bool  args_in_key:  When True the args and kwargs of the func are included in the lock key.
    :param int   expires:      The a expires value if the task runs for too long
    """
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with app.cli_request_context():
                cache_key = make_func_cache_key(func, key, args_in_key, *args, **kwargs)
                
                if app.cache.get(cache_key):
                    logging.info("[ONLYONE] Task {} already running, aborting!".format(cache_key))
                    return
                try:
                    app.cache.set(cache_key, str(datetime.now()), expires)
                    logging.info("[ONLYONE] Task {} started".format(cache_key))
                    return func(*args, **kwargs)
                finally:
                    logging.info("[ONLYONE] Task {} done".format(cache_key))
                    app.cache.delete(cache_key)
        return wrapper
    return decorator

def get_base_url():
    if 'BASE_URL' not in app.config:
        app.config['BASE_URL'] = ('%s://%s' % (request.scheme, app.config['DEFAULT_SERVER_NAME']))

    return app.config['BASE_URL']

def get_relative_url(url):
    try:
        return urlparse.urlparse(url).path + ('?' + urlparse.urlparse(url).query if urlparse.urlparse(url).query else '')
    except:
        return None

def get_canonical_url(url):
    return get_base_url() + get_relative_url(url)

def strip_trailing_slash(url):
    if url[-1:] == '/':
        url = url[:-1]
    return url

def chunks(l, n):
    n = int(math.ceil(len(l) / float(n)))
    
    if n > 0:
        for i in xrange(0, len(l), n):
            yield l[i:i+n]

def trim_whitespace(s):
    return unicode(s).strip()

def grouper(n, iterable, fillvalue=None):
    "grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return izip_longest(fillvalue=fillvalue, *args)


class LocaleCtx(object):
    def __init__(self, *args):
        self.old = {}
        self.new = {}
        
        for c, l in grouper(2, args):
            self.old[c] = locale.getlocale(c)
            self.new[c] = l
    
    def __enter__(self):
        for c, l in self.new.iteritems():
            locale.setlocale(c, l)
    
    def __exit__(self, type, value, traceback):
        for c, l in self.old.iteritems():
            locale.setlocale(c, l)


def get_locale_ctx(c):
    return LocaleCtx(c, config['LOCALE'].get(c, None))


def get_local_static_page_path(page_path):
    return 'static/' + config['LANGUAGE_PREFIX'] + '/' + page_path
