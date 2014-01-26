from functools import partial
import hashlib
import hmac
import json
import time
import urllib
from vircuum.tradeapi.common import simple_request_url

simple_request_url = partial(simple_request_url, timeout = 6)


class Order(object):
    def __init__(self, id, time, type, price, amount, pending):
        self.id = id
        self.time = time
        self.type = type
        self.price = price
        self.amount = amount
        self.pending = pending

    def __repr__(self):
        return str(dict(id = self.id, type = self.type, price = self.price, amount = self.amount))


class TradeAPI(object):
    def __init__(self, api_key, api_secret, username, noncemod = 1, noncenum = 0, debug = False):
        self.api_key = api_key
        self.api_secret = api_secret
        self.username = username
        self.debug = debug
        self.noncenum = noncenum
        self.noncemod = noncemod
        self.prev_nonce = None

    def ticker(self):
        nonce = self.nonce() # fetch a nonce just to avoid the rate limit
        data = simple_request_url("https://cex.io/api/ticker/GHS/BTC")
        data = json.loads(data)

        return (float(data['bid']), float(data['ask']), )

    def balance(self):
        args = self.auth_args()
        data = simple_request_url("https://cex.io/api/balance/", data=urllib.urlencode(args))
        if self.debug: print data
        data = json.loads(data)

        return float(data['BTC']['available'])

    def open_orders(self):
        args = self.auth_args()
        data = simple_request_url("https://cex.io/api/open_orders/GHS/BTC", data=urllib.urlencode(args))
        if self.debug: print data
        data = json.loads(data)

        if not isinstance(data, list):
            raise Exception("API Request failed: \n\n %s" % data)

        return [Order(int(row['id']), int(int(row['time']) / 1000), str(row['type']), float(row['price']), float(row['amount']), float(row['pending'])) for row in data]

    def place_order(self, type, amount, price):
        args = dict(type = type, amount = amount, price = price)
        if self.debug: print "place_order", args
        args.update(self.auth_args())
        data = simple_request_url("https://cex.io/api/place_order/GHS/BTC", data=urllib.urlencode(args))
        if self.debug: print data
        data = json.loads(data)

        if not isinstance(data, dict) or 'id' not in data:
            raise Exception("API Request failed: \n\n %s" % data)

        return Order(int(data['id']), int(int(data['time']) / 1000), str(data['type']), float(data['price']), float(data['amount']), float(data['pending']))

    def cancel_order(self, id):
        args = dict(id = id)
        if self.debug: print "cancel_order", args
        args.update(self.auth_args())
        data = simple_request_url("https://cex.io/api/cancel_order/", data=urllib.urlencode(args))
        if self.debug: print data

        return len(data) > 0

    def nonce(self):
        # nonce needs to be increasing, and this also ensures we don't break the 1 req/sec rate limit
        nonce = int(time.time())
        while nonce == self.prev_nonce or (nonce % self.noncemod) != self.noncenum:
            nonce = int(time.time())
            time.sleep(0.01)
        
        if self.debug: print "nonce", nonce

        self.prev_nonce = nonce

        return str(nonce)

    def auth_args(self):
        nonce = self.nonce()
        message = nonce + self.username + self.api_key
        signature = hmac.new(self.api_secret, msg=message, digestmod=hashlib.sha256).hexdigest().upper()

        return dict(key = self.api_key, signature = signature, nonce = nonce)
