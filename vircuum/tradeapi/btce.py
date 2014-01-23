from functools import partial
import hashlib
import hmac
import json
import time
import urllib
from vircuum.tradeapi.common import simple_request_url

simple_request_url = partial(simple_request_url, timeout = 6)


class TradeAPI(object):
    TIME_PER_LOOP = 90

    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret

    def ticker(self):
        data = simple_request_url("https://btc-e.com/api/2/btc_usd/ticker", timeout = 5)
        data = json.loads(data)

        return (float(data['ticker']['buy']), )

    def balance(self):
        args = urllib.urlencode({'method': 'getInfo', 'nonce' : str(int(time.time()))})
        headers = self.auth_headers(args)
        data = simple_request_url("https://btc-e.com/tapi", data=args, headers=headers)
        data = json.loads(data)

        print data

        return float(data['return']['funds']['usd'])

    def auth_headers(self, args):
        H = hmac.new(self.api_secret, digestmod=hashlib.sha512)
        H.update(args)
        sign = H.hexdigest()
        
        return dict(Key = self.api_key, Sign = sign)
