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

        return float(data['BTC']['available'])

    def open_orders(self):
        args = self.auth_args()
        data = simple_request_url("https://cex.io/api/open_orders/GHS/BTC", data=urllib.urlencode(args))
        data = json.loads(data)

        return [Order(row['id'], row['time'], row['type'], row['price'], row['amount'], row['pending']) for row in data]

    def place_order(self, type, amount, price):
        args = self.auth_args()
        args.update(dict(type = type, amount = amount, price = price))
        data = simple_request_url("https://cex.io/api/place_order/GHS/BTC", data=urllib.urlencode(args))
        data = json.loads(data)

        return Order(row['id'], row['time'], row['type'], row['price'], row['amount'], row['pending'])

    def cancel_order(self, id):
        args = self.auth_args()
        args.update(dict(id = id))
        data = simple_request_url("https://cex.io/api/cancel_order", data=urllib.urlencode(args))
        
        return len(data) > 0

    def auth_args(self):
        nonce = str(int(time.time()))
        message = nonce + self.username + self.api_key
        signature = hmac.new(self.api_secret, msg=message, digestmod=hashlib.sha256).hexdigest().upper()

        return dict(key = self.api_key, signature = signature, nonce = nonce)
