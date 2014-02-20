from collections import namedtuple
import time
from datetime import datetime

from vircuum.plan import BTC, GHS


class Trader(object):
    RESET_THRESHOLD = 15 * 60
    SLEEP_PER_LOOP = 0

    def __init__(self, tradeapi, masterplan, autoconfirm, autostart, retries, sessionmaker, balance = None):
        self.tradeapi = tradeapi
        self.masterplan = masterplan
        self.autoconfirm = autoconfirm
        self.autostart = autostart
        self.retries = retries
        self.sessionmaker = sessionmaker

        self.bid = 0
        self.ask = 0
        self.buy_orders = []
        self.sell_orders = []

        self.masterplan.trader = self

        if not balance:
            self.real_balance = tradeapi.balance()
        else:
            self.real_balance = balance

        if self.masterplan.assigned_balance.get(BTC, None):
            assert self.real_balance >= self.masterplan.assigned_balance[BTC].value

        self.debug_actions = []

    @property
    def session(self):
        if self._session is None:
            self._session = self.sessionmaker()

        return self._session

    @session.setter
    def session(self, session):
        self._session = session

    def debug_action(self, msg):
        self.debug_actions.append(msg)
        return msg

    def run(self):
        if not self.autostart:
            self.confirm("run?")

        (self.bid, self.ask) = self.get_price()

        self.masterplan.init(price = self.ask)

        while True:
            self.loop()

    def get_price(self):
        (bid, ask, ) = self.tradeapi.ticker()
        return (bid, ask, )

    def confirm(self, msg = None, allow_autoconfirm = False):
        if self.autoconfirm and allow_autoconfirm:
            return True

        if msg:
            print msg

        while not self.do_confirm():
            pass

    def do_confirm(self):
        while True:
            confirmedstr = str(raw_input("ok [y/N]? \n"))

            confirmed = confirmedstr
            if "#" in confirmed:
                confirmed = confirmed[:confirmed.index("#")]
            confirmed = confirmed.strip().lower()
            try:
                if confirmed == "y":
                    return True
                elif confirmed == "n":
                    return False
            except:
                pass

            continue

    def loop(self):
        (self.bid, self.ask) = self.get_price()

        self.check_current_orders()
        self.masterplan.run()

    def place_buy_order(self, amount, price):
        order = self.tradeapi.place_buy_order(amount = amount, price = price)
        self.buy_orders.append(order)
        return order

    def place_sell_order(self, amount, price):
        order = self.tradeapi.place_sell_order(amount = amount, price = price)
        self.sell_orders.append(order)
        return order

    def check_current_orders(self):
        open_orders = self.tradeapi.open_orders()

        print "open_orders", open_orders

        for buy_order in list(self.buy_orders):
            if buy_order.id in [open_order.id for open_order in open_orders]:
                # not processed yet :-()
                continue
            else:
                # processed! \o/
                print "order BOUGHT %s" % buy_order
                buy_order.status = 1

        for sell_order in list(self.sell_orders):
            if sell_order.id in [open_order.id for open_order in open_orders]:
                # not processed yet :-()
                continue
            else:
                # processed! \o/
                print "order SOLD %s" % sell_order
                sell_order.status = 1

