from vircuum.tradeapi.common import isnumber
import time
import random

autoinc = 0

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
    TIME_PER_LOOP = 1

    def __init__(self, *args, **kwargs):
        self.price = 500
        self.dummy_loop = 0
        self.dummy_loop_dir = 0
        self._balance = 250
        self.orders = []

    def ticker(self):
        return (self.dummy_price(), )

    def balance(self):
        return self._balance

    def open_orders(self):
        return self.orders

    def place_order(self, type, amount, price):
        global autoinc
        autoinc += 1

        order = Order(id = autoinc, time = time.time(), type = type, price = price, amount = amount, pending = False)

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
            if order.type == 'buy':
                if self.price <= order.price:
                    self.orders.remove(order)
            elif order.type == 'sell':
                if self.price >= order.price:
                    self._balance += order.price * order.amount
                    self.orders.remove(order)
            else:
                raise Exception()

    def dummy_price(self):

        def rand(dir = None):
            if dir is None:
                dir = self.dummy_loop_dir

            if dir == 0:
                self.price += float(random.randint(-50, 50)) * 1
            elif dir > 0:
                self.price += float(random.randint(0, 100)) * 1
            elif dir < 0:
                self.price += float(random.randint(-100, 0)) * 1

            return self.price

        try:
            while True:
                if self.dummy_loop > 0:
                    self.dummy_loop -= 1
                    return rand()

                laststr = str(raw_input("New price? \n"))
                last = laststr
                if "#" in last:
                    last = last[:last.index("#")]
                last = last.strip()

                print "%s -> %s" % (laststr, last)
                try:
                    if last == "":
                        return rand(dir = 0)
                    elif last.startswith("loopup"):
                        self.dummy_loop_dir = 1
                        self.dummy_loop = int(last[6:])
                        return rand()
                    elif last.startswith("loopdown"):
                        self.dummy_loop_dir = -1
                        self.dummy_loop = int(last[8:])
                        return rand()
                    elif last.startswith("loop"):
                        self.dummy_loop_dir = 0
                        self.dummy_loop = int(last[4:])
                        return rand()
                    elif last.startswith("*"):
                        self.price = self.price * float(last[1:])
                    elif last.startswith("*"):
                        self.price = self.price * float(last[1:])
                        return self.price
                    elif last.startswith("/"):
                        self.price = self.price / float(last[1:])
                        return self.price
                    elif last.startswith("+"):
                        self.price = self.price + float(last[1:])
                        return self.price
                    elif last.startswith("-"):
                        self.price = self.price - float(last[1:])
                        return self.price
                    elif isnumber(last):
                        self.price = float(last)
                        return self.price
                except:
                    pass

                continue
        finally:
            print "new price: ", self.price
            self.process()

