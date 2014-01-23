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

    def __init__(self, api_key, api_secret, username):
        self.api_key = api_key
        self.api_secret = api_secret
        self.username = username

    def ticker(self):
        data = simple_request_url("https://cex.io/api/ticker/GHS/BTC")
        data = json.loads(data)

        return (float(data['last']), )

    def balance(self):
        args = self.auth_args()
        data = simple_request_url("https://cex.io/api/balance/", data=urllib.urlencode(args))
        data = json.loads(data)

        return data

    def auth_args(self):
        nonce = str(int(time.time()))
        message = nonce + self.username + self.api_key
        signature = hmac.new(self.api_secret, msg=message, digestmod=hashlib.sha256).hexdigest().upper()

        return dict(key = self.api_key, signature = signature, nonce = nonce)
