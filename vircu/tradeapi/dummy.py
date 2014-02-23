import time
import random

from vircu.trader.currency import BTC, GHS
from vircu.trader.order import APIOrder
from vircu.tradeapi.common import isnumber


import sys, select
def raw_input(prompt):
    """non-block raw_input"""

    sys.stdout.write(prompt)
    sys.stdout.flush()

    select.select([sys.stdin], [], [])
    return sys.stdin.readline().rstrip('\n')


class TradeAPI(object):
    def __init__(self, noncemod = 1, noncenum = 0, *args, **kwargs):
        self.price = BTC.VALUE(0.04)
        self.dummy_loop = 0
        self.dummy_loop_dir = 0
        self._balance = BTC.VALUE(1)
        self.orders = []
        self.prev_nonce = None
        self.prev_ticknonce = None
        self.noncenum = noncenum
        self.noncemod = noncemod
        self.debug = True

    def ticker(self):
        self.dummy_price()
        return (self.price, self.price, )

    def balance(self):
        self.nonce()
        return self._balance

    def open_orders(self):
        self.nonce()
        return self.orders

    def place_buy_order(self, amount, price):
        return self.place_order(type = 'buy', amount = amount, price = price)

    def place_sell_order(self, amount, price):
        return self.place_order(type = 'sell', amount = amount, price = price)
    
    def place_order(self, type, amount, price):
        id = self.nonce()
        if self.debug: print "id", id
        order = APIOrder(id = id, time = time.time(), type = type, price = price, amount = amount, pending = 0.0)

        if type == 'buy':
            self._balance -= price * amount
        elif type == 'sell':
            pass
        else:
            raise Exception()

        self.orders.append(order)

        return order

    def cancel_order(self, id):
        for order in list(self.orders):
            if order.id == id:
                self.orders.remove(order)
                return True

        return False

    def process(self):
        for order in list(self.orders):
            print self.price, order
            if order.type == 'buy':
                if self.price <= order.price:
                    self.orders.remove(order)
            elif order.type == 'sell':
                if self.price >= order.price:
                    self._balance += order.price * order.amount
                    self.orders.remove(order)
            else:
                raise Exception()

    def nonce(self):
        new_nonce = lambda: int(time.time() * 1000)
        nonce = new_nonce()

        while nonce == self.prev_nonce or (nonce % self.noncemod) != self.noncenum:
            time.sleep(0.001)
            nonce = new_nonce()
        
        if self.debug: print "nonce", nonce

        self.prev_nonce = nonce

        return nonce

    def ticknonce(self):
        new_nonce = lambda: int(time.time())
        nonce = new_nonce()

        while nonce == self.prev_ticknonce or (nonce % self.noncemod) != self.noncenum:
            time.sleep(0.1)
            nonce = new_nonce()
        
        if self.debug: print "ticknonce", nonce

        self.prev_ticknonce = nonce

        return nonce

    def dummy_price(self):
        self.ticknonce()
        
        def rand(dir = None):
            if dir is None:
                dir = self.dummy_loop_dir

            if dir == 0:
                self.price *= (1 + (random.randint(-20, 20)/1000.0))
            elif dir > 0:
                self.price *= (1 + (random.randint(0, 20)/1000.0))
            elif dir < 0:
                self.price *= (1 + (random.randint(-20, 0)/1000.0))

            return self.price

        try:
            while True:
                self.price = float(self.price)
                if self.dummy_loop > 0:
                    self.dummy_loop -= 1
                    rand()
                    break

                laststr = str(raw_input("New price? \n"))
                last = laststr
                if "#" in last:
                    last = last[:last.index("#")]
                last = last.strip()

                print "[%s] -> [%s]" % (laststr, last)

                try:
                    if last == "":
                        rand(dir = 0)
                        break
                    elif last == "up":
                        rand(dir = 1)
                        break
                    elif last == "down":
                        rand(dir = -1)
                        break
                    elif last.startswith("loopup"):
                        self.dummy_loop_dir = 1
                        self.dummy_loop = int(last[6:])
                        rand()
                        break
                    elif last.startswith("loopdown"):
                        self.dummy_loop_dir = -1
                        self.dummy_loop = int(last[8:])
                        rand()
                        break
                    elif last.startswith("loop"):
                        self.dummy_loop_dir = 0
                        self.dummy_loop = int(last[4:])
                        rand()
                        break
                    elif last.startswith("*"):
                        self.price = self.price * float(last[1:])
                        break
                    elif last.startswith("/"):
                        self.price = self.price / float(last[1:])
                        break
                    elif last.startswith("+"):
                        self.price = self.price + float(last[1:])
                        break
                    elif last.startswith("-"):
                        self.price = self.price - float(last[1:])
                        break
                    elif isnumber(last):
                        self.price = float(last)
                        break
                except:
                    pass

                continue
        finally:
            self.price = BTC.VALUE(self.price)
            print "new price: ", self.price
            self.process()

