import time
import datetime
import urllib
import json
from functools import partial
from uuid import uuid4
from flask import g, url_for, request
from jinja2 import nodes
from jinja2.ext import Extension
from jinja2.utils import Markup
from vircu.common import get_domain, simple_request_url, get_pretty_url, get_end_of_hour, pretty_date, is_dev,\
    appcache_enabled, feature_enabled, get_relative_url, strip_trailing_slash, get_base_url, get_canonical_url,\
    chunks, trim_whitespace, PRETTY_DATE_SIMPLE, PRETTY_DATE_RELATIVE, get_locale_ctx
from vircu.util.statics_cache import static_url
from vircu.util import clean_html
import pytz
from vircu.view.utils import pretty_sizeof, url_for_static_page
from werkzeug.local import LocalProxy
from vircu.dt import dt_to_utc_timestamp, dt_as_utc
import vircu.chart
import vircu.constants
import math
import locale

def setup_jinja_helpers(app):
    # expose constants
    app.jinja_env.globals['config'] = app.config
    app.jinja_env.globals['constants'] = vircu.constants
    app.jinja_env.globals['chart_constants'] = vircu.chart
    
    app.jinja_env.globals['uuid4'] = uuid4
    app.jinja_env.globals['nbsp'] = Markup('&nbsp')
    app.jinja_env.filters['pretty_sizeof'] = pretty_sizeof
    
    app.jinja_env.globals['static_url'] = static_url
    
    def url_for_static(filename, version = None, minify = None, alt = None):
        min = '.min' if (minify is None and app.config['USE_MINIFIED_ASSETS']) or minify else ''
        alt = '' # '-alt' if (alt is None and cache_context.is_alt_statics) or alt else ''
        
        filename = filename % dict(min = min, alt = alt)
        version  = version or app.config['STATIC_VERSION'][0:app.config['VERSION_STRING_LENGTH']]
        version  = str(version).rjust(app.config['VERSION_STRING_LENGTH'], "_")
        
        return static_url(url_for('static', version = version, filename = filename))
    
    app.jinja_env.globals['url_for_static'] = url_for_static   
    app.jinja_env.globals['url_for_static_page'] = url_for_static_page
    
    def strip_html_filter(v, *args, **kwargs):
        # returning Markup means jinja2 will consider it as safe 
        return Markup(clean_html.strip(v, *args, **kwargs))
    
    def clean_html_filter(v, *args, **kwargs):
        # returning Markup means jinja2 will consider it as safe 
        return Markup(clean_html.clean(v, *args, **kwargs))
    
    def very_clean_html_filter(v, *args, **kwargs):
        kwargs['level'] = clean_html.CLEAN_LEVEL_HIGH if 'level' not in kwargs else kwargs['level']
        # returning Markup means jinja2 will consider it as safe 
        return Markup(clean_html.clean(v, *args, **kwargs))
    
    app.jinja_env.filters['clean_html'] = clean_html_filter
    app.jinja_env.filters['very_clean_html'] = very_clean_html_filter
    app.jinja_env.filters['strip_html'] = strip_html_filter
    app.jinja_env.globals['feature_enabled'] = feature_enabled
    
    def first_char(s):
        return s[0]
    
    app.jinja_env.filters['first_char'] = first_char
    app.jinja_env.globals['min'] = min
    app.jinja_env.globals['max'] = max
    
    # expose datetime format
    def datetimeformat(value, format='%d %b %Y %H:%M'):
        if not value:
            return ''
        
        if isinstance(value, (float, int, long)):
            value = datetime.datetime.fromtimestamp(value)
        return value.strftime(format)
    
    def as_utctime(dt):
        return pytz.utc.localize(dt)
    
    def datetime_to_timestamp(dt):
        return time.mktime(dt.timetuple())

    app.jinja_env.filters['datetimeformat'] = datetimeformat
    app.jinja_env.filters['pretty_date'] = pretty_date
    app.jinja_env.filters['simple_pretty_date'] = partial(pretty_date, text_mode = PRETTY_DATE_SIMPLE)
    app.jinja_env.filters['relative_pretty_date'] = partial(pretty_date, text_mode = PRETTY_DATE_RELATIVE)
    app.jinja_env.filters['chunks'] = chunks
    
    def nl2br(s):
        return unicode(s).replace('\n', '<br />')

    app.jinja_env.filters['nl2br'] = nl2br
    
    def trim_whitespace(s):
        return unicode(s).strip()
    
    app.jinja_env.filters['trim'] = trim_whitespace
    
    def intersect(l1, l2):
        return filter(lambda x: x in l2, l1)
    
    app.jinja_env.globals['intersect'] = intersect
    
    # expose number_format format
    def number_format(value, grouping = True, monetary = False, rounding = None):
        try:
            value = float(value)
        except:
            return ""

        if rounding is not None:
            format = '%.{0}f'.format(str(rounding))
        else:
            format = '%.2f'

        with get_locale_ctx(locale.LC_NUMERIC):
            return locale.format(format, value, grouping = grouping, monetary = monetary)
    
    def money_format(value, grouping = True, symbol = True):
        try:
            value = float(value)
        except:
            return ""

        with get_locale_ctx(locale.LC_MONETARY):
            return locale.currency(value, grouping = grouping, symbol = symbol)
    
    app.jinja_env.filters['number_format'] = number_format
    app.jinja_env.filters['money_format']  = money_format
    
    # expose timestamp
    def timestamp(value, format='%Y-%m-%d %H:%M:%S'):
        if not value:
            return ''
        
        if not isinstance(value, datetime.datetime):
            value = datetime.strptime(value, format)

        return dt_to_utc_timestamp(dt_as_utc(value, asume_utc = True))
        
    app.jinja_env.filters['timestamp'] = timestamp
    app.jinja_env.globals['now'] = datetime.datetime.now
    
    # expose urlencode
    def urlencode_filter(s, plus = False):
        if type(s) == 'Markup':
            s = s.unescape()
        s = s.encode('utf8')
        s = urllib.quote_plus(s) if plus else urllib.quote(s)
        return Markup(s)
    
    app.jinja_env.filters['urlencode'] = urlencode_filter
    app.jinja_env.filters['domain'] = get_domain
    app.jinja_env.filters['pretty_url'] = get_pretty_url
    
    app.jinja_env.globals['base_url'] = get_base_url
    app.jinja_env.filters['relative_url'] = get_relative_url
    app.jinja_env.filters['strip_trailing_slash'] = strip_trailing_slash
    app.jinja_env.filters['canonical_url'] = get_canonical_url
    
    def smart_len(l):
        if isinstance(l, BaseQuery):
            return len(list(l))
        return len(l)
    
    app.jinja_env.filters['count'] = smart_len
           
    # expose menus
    app.jinja_env.globals['main_menu'] = app.main_menu
    _base_js_escapes = (
        ('\\', r'\u005C'),
        ('\'', r'\u0027'),
        ('"', r'\u0022'),
        ('>', r'\u003E'),
        ('<', r'\u003C'),
        ('&', r'\u0026'),
        ('=', r'\u003D'),
        ('-', r'\u002D'),
        (';', r'\u003B'),
        (u'\u2028', r'\u2028'),
        (u'\u2029', r'\u2029')
    )
    
    # Escape every ASCII character with a value less than 32.
    _js_escapes = (_base_js_escapes +
                   tuple([('%c' % z, '\\u%04X' % z) for z in range(32)]))
    
    # escapejs from Django: https://www.djangoproject.com/
    def escapejs(value):
        """Hex encodes characters for use in JavaScript strings."""
        if not isinstance(value, basestring):
            value = str(value)
    
        for bad, good in _js_escapes:
            value = value.replace(bad, good)
    
        return value
    
    app.jinja_env.filters['escapejs'] = escapejs

    class OnDomReadyExtension(Extension):
        """provides a ondomready/endondomready block to contain javascript code from anywhere
        which gets printed in 1 go by the printondomready block at the bottom of the page
        """
        
        # a set of names that trigger the extension.
        tags = set(['ondomready', 'printondomready'])
    
        def __init__(self, environment):
            super(OnDomReadyExtension, self).__init__(environment)
    
        def parse(self, parser):
            # grab the name token
            token = parser.stream.next()
            
            # check the value of the name token
            if token.value == 'ondomready':
                
                # check if the name token is followed by a string
                unique = parser.stream.next_if('string')
                # create a constant from the string or None
                args = [nodes.Const(unique.value if unique else None)]
                
                # parse the body up to the end tag
                body = parser.parse_statements(['name:endondomready'], drop_needle=True)
    
                # return a new node (which will be empty)
                return nodes.CallBlock(self.call_method('_store_ondomready', args), [], [], body).set_lineno(token.lineno)
            elif token.value == 'printondomready':
                # return a node with the stashed js code
                return nodes.CallBlock(self.call_method('_print_ondomready'), [], [], []).set_lineno(token.lineno)
    
        def _store_ondomready(self, unique, caller):
            # check if we're to late
            if hasattr(g, 'domreadyprinted') and g.domreadyprinted:
                raise Exception("Atempt to add to ondomready after it has already been output.")
            
            # init the requestglobal var
            if not hasattr(g, 'ondomready'):
                g.ondomready_unique = []
                g.ondomready = []
                
               
            # if we have a unique identifier then make sure we don't add it twice 
            if unique:
                if unique in g.ondomready_unique:
                    return ""
                else:
                    g.ondomready_unique.append(unique)
            
            # add to the requestglobal var
            g.ondomready.append(caller())
    
            # return emptiness
            return ""
    
        def _print_ondomready(self, caller):
            # mark the requestglobal that we can't add more js to it
            g.domreadyprinted = True
            
            # return the stashed js code or emptiness
            return "\n".join(g.ondomready) if hasattr(g, 'ondomready') else ""
        
    # register the OnDomReady extension
    app.jinja_env.add_extension(extension=OnDomReadyExtension)


