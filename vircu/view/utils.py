import colorsys
from functools import partial
from flask import url_for, current_app as app


def custom_url_for_list(endpoint=None, **kwargs):
    """
    decorator for a wrapper around url_for to maintain context
    this way we can call the result callable(page=1) and still maintain our current endpoint plus status parameters
    """
    def custom_url_for(**values):
        for key in  kwargs:
            if key not in values:
                values[key] = kwargs[key]
        return url_for(endpoint, **values)

    return custom_url_for


def pretty_sizeof(num):
    num = float(num)
    for x in ['bytes','KB','MB','GB']:
        if num < 1024.0 and num > -1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0
    return "%3.1f%s" % (num, 'TB')


class HsvColor(object):
    """
    Hue Saturation Value color
    
    Hue, Saturation and Value should range from 0.0 and 1.0
    
    """
    
    def __init__(self, h, s, v):
        self.h     = h
        self.s     = s
        self.v     = v
    
    @property
    def hsv(self):
        return (self.h, self.s, self.v)
    
    @property
    def rgb(self):
        return colorsys.hsv_to_rgb(*self.hsv)
    
    def new_color(self, **kwargs):
        kwargs.setdefault('h', self.h)
        kwargs.setdefault('s', self.s)
        kwargs.setdefault('v', self.v)
        
        return HsvColor(**kwargs)
    
    @property
    def hex(self):
        hex = map(lambda x: int(x * 255), self.rgb)
        hex = map(lambda y: chr(y).encode('hex'), hex)
        
        return "".join(hex)
    
    def get_palleteNXH(self, x):
        return partial(HsvColorNXH, s = self.s, v = self.v, x = x)
    
    def get_palleteNXS(self, x):
        return partial(HsvColorNXS, h = self.h, v = self.v, x = x)
    
    def get_palleteNXV(self, x):
        return partial(HsvColorNXV, h = self.h, s = self.s, x = x)


class HsvColorNXH(HsvColor):
    """
    Hue Saturation Value color, with Hue based on N with a color range of X
    
    This class can be used to generate a range of X colors with their Hue spread equally - which results in a 'distinctive' colors.
     and get the N'th color.
    You can configure the Saturation and Value (can range from 0.0 to 1.0).
    
    N = 1.0 == N = 0.0 so it doesn't matter if N is a 0based or 1based index
    """
    
    def __init__(self, n, x, s, v):
        self.n     = n
        self.x     = x
        self.s     = s
        self.v     = v
    
    @property
    def h(self):
        return self.n * (1.0 / self.x)


class HsvColorNXS(HsvColor):
    """
    Hue Saturation Value color, with Saturation based on N with a color range of X
    
    This class can be used to generate a range of X colors with their Saturation spread equally - which results in a similair colors.
     and get the N'th color.
    You can configure the Hue and Value (can range from 0.0 to 1.0).
    
    N = 1.0 == N = 0.0 so it doesn't matter if N is a 0based or 1based index
    """
    
    def __init__(self, n, x, h, v):
        self.n     = n
        self.x     = x
        self.h     = h
        self.v     = v
    
    @property
    def s(self):
        return self.n * (1.0 / self.x)



class HsvColorNXV(HsvColor):
    """
    Hue Saturation Value color, with Value based on N with a color range of X
    
    This class can be used to generate a range of X colors with their Value spread equally - which results in a similair colors.
     and get the N'th color.
    You can configure the Hue and Saturation (can range from 0.0 to 1.0).
    
    N = 1.0 == N = 0.0 so it doesn't matter if N is a 0based or 1based index
    """
    
    def __init__(self, n, x, h, s):
        self.n     = n
        self.x     = x
        self.h     = h
        self.s     = s
    
    @property
    def v(self):
        return self.n * (1.0 / self.x)


# used for article age format (1d5h12m)
def days_hours_minutes(td):
    return (str(td.days) + 'd' if td.days > 0 else '') + \
           (str(td.seconds//3600) + 'h' if td.seconds//3600 > 0 else '') + \
           (str((td.seconds//60)%60) + 'm' if td.days == 0 else '')

