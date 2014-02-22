# -*- coding: utf-8 -*-
import urllib2
from flask import url_for, current_app as app
from vircu.common import get_relative_url


def static_hostname_for_path(rel_path, force = False):
    if app.config['STATIC_HOST'] and app.config['STATIC_NR_DOMAINS'] and (force or app.config['USE_STATIC_HOST']):
        return app.config['STATIC_HOST'] % (hash(rel_path) % app.config['STATIC_NR_DOMAINS'])
    else:
        return None


def static_url(path, force = False):
    # ensure we have a relative url as base
    static_path = get_relative_url(path)
    
    # ensure there's a / at the start
    if not static_path.startswith('/'):
        static_path = '/' + static_path

    # check if there should be a static hostname used 
    static_hostname = static_hostname_for_path(static_path, force = force)
    if static_hostname:
        return 'http://%s%s' % (static_hostname, static_path)
    
    # return the original
    return path

