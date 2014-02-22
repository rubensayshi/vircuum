from functools import partial
import datetime
import hashlib
import hmac
import json
import time
import urllib
from vircu.tradeapi.common import simple_request_url


simple_request_url = partial(simple_request_url, timeout = 20)


class Order(object):
    def __init__(self, id, time, type, price, amount):
        self.id = id
        self.time = time
        self.type = type
        self.price = price
        self.amount = amount

    def __repr__(self):
        return str(dict(id = self.id, type = self.type, price = self.price, amount = self.amount))


class TradeAPI(object):
    PRICE_FORMAT  = "{:11.2f}"
    AMOUNT_FORMAT = "{:11.8f}"

    def __init__(self, api_key, api_secret, clientid, noncemod = 1, noncenum = 0, debug = False):
        self.api_key = api_key
        self.api_secret = api_secret
        self.clientid = clientid
        self.debug = debug
        self.noncenum = noncenum
        self.noncemod = noncemod
        self.prev_nonce = None

    def ticker(self):
        nonce = self.nonce() # fetch a nonce just to avoid the rate limit
        data = simple_request_url("https://www.bitstamp.net/api/ticker/")
        data = json.loads(data)

        return (float(data['bid']), float(data['ask']), )

    def balance(self):
        args = self.auth_args()
        data = simple_request_url("https://www.bitstamp.net/api/balance/", data=urllib.urlencode(args))
        if self.debug: print data
        data = json.loads(data)

        return float(data['usd_available'])

    def open_orders(self):
        args = self.auth_args()
        data = simple_request_url("https://www.bitstamp.net/api/open_orders/", data=urllib.urlencode(args))
        if self.debug: print data
        data = json.loads(data)

        if not isinstance(data, list):
            raise Exception("API Request failed: \n\n %s" % data)

        return [Order(int(row['id']), self._parse_dt(row['datetime']), str(row['type']), float(row['price']), float(row['amount'])) 
                for row in data]

    def place_buy_order(self, amount, price):
        return self.place_order(type = 'buy', amount = amount, price = price)

    def place_sell_order(self, amount, price):
        return self.place_order(type = 'sell', amount = amount, price = price)

    def place_order(self, type, amount, price):
        args = dict(amount = amount, price = price)
        if self.debug: print "place_order", args
        args.update(self.auth_args())
        data = simple_request_url("https://www.bitstamp.net/api/%s/" % type, data=urllib.urlencode(args))
        if self.debug: print data
        data = json.loads(data)

        if not isinstance(data, dict) or 'id' not in data:
            raise Exception("API Request failed: \n\n %s" % data)

        return Order(int(data['id']), self._parse_dt(data['datetime']), str(data['type']), float(data['price']), float(data['amount']))

    def cancel_order(self, id):
        args = dict(id = id)
        if self.debug: print "cancel_order", args
        args.update(self.auth_args())
        data = simple_request_url("https://www.bitstamp.net/api/cancel_order/", data=urllib.urlencode(args))
        if self.debug: print data

        if data != 'true':
            raise Exception("Cancel Order failed: \n\n %s " % data)

        return True

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
        message = nonce + self.clientid + self.api_key
        signature = hmac.new(self.api_secret, msg=message, digestmod=hashlib.sha256).hexdigest().upper()

        return dict(key = self.api_key, signature = signature, nonce = nonce)

    def _parse_dt(self, dt):
        dt = str(dt).split('.')[0]
        dt = datetime.datetime.strptime(dt, '%Y-%m-%d %H:%M:%S') # 2014-02-14 16:15:00
        ts = time.mktime(dt.timetuple()) + 3600 # nasty way of correcting the fact that our server is GMT+1

        return int(ts)

