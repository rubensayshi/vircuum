from flask import request, url_for, g
from functools import partial
from flask.globals import _lookup_object
from werkzeug.local import LocalProxy
import urllib

WILDCARD_VIEW_ARG = '**'

menu_state = LocalProxy(lambda: g.menu_state)

class MenuManager(object):
    def __init__(self, app):
        self.app = app
        
        self.app.before_request(self.bind_stat_to_request)
    
    def bind_stat_to_request(self):
        if not hasattr(g, 'menu_state'):
            g.menu_state = MenuRequestState()


class MenuRequestState(object):
    def __init__(self):
        pass
    
    @property
    def endpoint(self):
        return  self._endpoint if hasattr(self, '_endpoint') else request.endpoint
    
    @endpoint.setter
    def endpoint(self, endpoint):
        self._endpoint = endpoint
        
    @property
    def view_args(self):
        return self._view_args if hasattr(self, '_view_args') else request.view_args
    
    @view_args.setter
    def view_args(self, view_args):
        self._view_args = view_args


class Menu(object):   
    """Menu is a container for MenuItem instances"""
    
    def __init__(self, items = None):
        self._items = items or []
        self.is_build = False
    
    @property
    def is_item(self):
        return False
    
    @property
    def is_section(self):
        return False
    
    @property
    def has_children(self):
        return len(filter(lambda item: item.visible, self.items)) > 0
    
    def add(self, item):
        self._items.append(item)
        
        return item

    @property
    def items(self):
        if not self.is_build:
            self.is_build = True
            self.build_items()
        
        return self._items
    
    def build_items(self):
        pass
    
    def __iter__(self):                
        for item in self.sorted():
            if item.visible:
                yield item
    
    def sorted(self):
        return sorted(self.items, key=lambda item: item.weight if item.weight is not None else MenuItem.DEFAULT_WEIGHT)


class MenuItem(Menu):
    """MenuItem represents an actual item in the menu
    extends Menu so that it can contain a child menu"""
    
    DEFAULT_WEIGHT=100
    def __init__(self, title, faicon=None, icon=None, visible=True, endpoint=None, view_args=None, href=None, weight=None, requires_perm=None, show_self=True, extra='', submenu=None, open_in_new = False, *args, **kwargs):
        self._title = title
        self._visible = visible        
        self.icon = icon       
        self.faicon = faicon
        self._href = href
        self.endpoint = endpoint
        self._view_args = view_args
        self.weight = weight
        self.requires_perm = requires_perm
        self.show_self = show_self
        self.extra = extra
        self.submenu = submenu
        self.open_in_new = open_in_new
        
        super(MenuItem, self).__init__(*args, **kwargs)
    
    @property
    def is_item(self):
        return True
    
    @property
    def href(self):
        return self.get_href()
    
    @property
    def view_args(self):
        return self._view_args or {}
    
    @property
    def title(self):
        if callable(self._title):
            return self._title()
        else:
            return self._title
    
    @property
    def external_href(self):
        return self.get_href(_external = True)
    
    def get_href(self, _external = False):
        if self._href:
            if callable(self._href):
                return self._href(_external = _external)
            else:
                return self._href
        elif self.endpoint:
            return url_for(self.endpoint, _external = _external, **dict([(k, v) for k, v in self.view_args.iteritems() if v != WILDCARD_VIEW_ARG]))
        else:
            raise Exception("MenuItem without href nor endpoint")
        
    @property
    def visible(self):
        if not self._visible:
            return False
        
        if self.requires_perm is not None:
            if isinstance(self.requires_perm, list):
                for perm in self.requires_perm:
                    if perm.can():
                        return True
                return False
            else:
                return self.requires_perm.can()
            
        return True
    
    @property
    def has_children(self):
        return any([item.visible for item in self.items])
    
    @property
    def active_path(self):
        if self.active:
            return True
        else:
            for item in self.items:
                if item.active_path:
                    return True

        return False
    
    @property
    def active(self):
        if self._href:
            return request.path == self._href
        elif self.endpoint:
            if str(self.current_endpoint) == str(self.endpoint):
                # cast both keys and values to str to compare the dicts properly
                sview_args = []
                rview_args = []
                
                for k in self.view_args:
                    v = str(self.view_args[k])
                    
                    if v != WILDCARD_VIEW_ARG:
                        sview_args.append((k, v))
                
                for k in (self.current_view_args or {}):
                    v = str(self.current_view_args[k])
                    if not k in self.view_args or self.view_args[k] != WILDCARD_VIEW_ARG:
                        rview_args.append((k, v))
                
                return (self._view_args is None) or sview_args == rview_args
            else:
                return False
        else:
            raise Exception("MenuItem without href nor endpoint")
    
    @property
    def current_endpoint(self):
        return menu_state.endpoint
    
    @property
    def current_view_args(self):
        return menu_state.view_args


class SectionMenuItem(MenuItem):
    def __init__(self, *args, **kwargs):
        super(SectionMenuItem, self).__init__(*args, **kwargs)

    @property
    def is_item(self):
        return False
    
    @property
    def is_section(self):
        return True


class MailtoMenuItem(MenuItem):
    def __init__(self, title, mailto, subject, body = None, *args, **kwargs):
        self._mailto  = mailto
        self._subject = subject
        self._body    = body
        
        super(MailtoMenuItem, self).__init__(title, *args, **kwargs)

    @property
    def body(self):
        if callable(self._body):
            return self._body()
        else:
            return self._body
    
    @property
    def subject(self):
        if callable(self._subject):
            return self._subject()
        else:
            return self._subject
    
    @property
    def mailto(self):
        if callable(self._mailto):
            return self._mailto()
        else:
            return self._mailto

    def get_href(self, _external = False):
        mailto = self.mailto
        mailto = mailto() if callable(mailto) else mailto
        
        return u"mailto:%(mailto)s?subject=%(subject)s&body=%(body)s" % dict(mailto  = mailto, 
                                                                             subject = urllib.quote(self.subject), 
                                                                             body    = urllib.quote(self.body.encode('utf-8')))
    
    @property
    def active(self):
        return False


class PlaceholderMenuItem(MenuItem):
    """PlaceholderMenuItem is just to fake an active_path to highlight it's parents"""
    
    def __init__(self, *args, **kwargs):
        kwargs['visible'] = False        
        super(PlaceholderMenuItem, self).__init__(*args, **kwargs)
        
    