import cookielib
from functools import partial
import urllib2


DEFAULT_USERAGENT = 'VirCuUM/1.0 +http://www.vircu.me/'
DEFAULT_TIMEOUT   = 30


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


def simple_request_url(url, data = None, timeout = None, return_response_object = False, head = False, cookiejar = None, useragent = None):
    # urllib2 won't escape spaces and without doing this here some requests will fail
    url     = url.replace(' ', '%20')
    host    = None
    urlp    = None

    request = HeadRequest if head else urllib2.Request
    request = request(url)
    request.add_header('User-Agent', useragent or DEFAULT_USERAGENT)

    if host:
        request.add_header('Host', host)

    handlers = []
    if cookiejar:
        handlers.append(urllib2.HTTPCookieProcessor(cookiejar))

    opener = urllib2.build_opener(*handlers)

    timeout = timeout or DEFAULT_TIMEOUT
    response = opener.open(request, data, timeout)

    if return_response_object:
        return response
    else:
        return response.read()


def isnumber(val):
    if isinstance(val, (int, long, float, complex)):
        return True
    else:
        try:
            float(val)
            return True
        except:
            return False


