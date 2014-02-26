from collections import namedtuple
import time
from datetime import datetime

from vircu.trader.currency import BTC, GHS
from vircu.trader.state import BuyOrder, SellOrder
from vircu.threading import raw_input


class Trader(object):

    def __init__(self, tradeapi, masterplan, autoconfirm, autostart, retries, state, balance = None):
        self.tradeapi = tradeapi
        self.masterplan = masterplan
        self.autoconfirm = autoconfirm
        self.autostart = autostart
        self.retries = retries
        self.state = state

        self.bid = 0
        self.ask = 0
        self.buy_orders = []
        self.sell_orders = []

        self.masterplan.trader = self

        if not balance:
            self.real_balance = tradeapi.balance()
        else:
            self.real_balance = balance

        # TODO check all currencies, not just BTC
        if self.masterplan.assigned_balance.get(BTC, None):
            assert self.real_balance >= self.masterplan.assigned_balance[BTC]

    def log_action(self, msg, status = None):
        self.state.log_message(msg, status).flush()

    def run(self):
        if not self.autostart:
            self.confirm("run?")

        self.state.assigned_balance(self.masterplan.assigned_balance).flush()

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
        self.state.tick(self.ask, datetime.now()).flush()

        self.check_current_orders()
        self.masterplan.run()

    def place_buy_order(self, amount, price):
        apiorder = self.tradeapi.place_buy_order(amount = amount, price = price)

        order = BuyOrder(state = self.state, apiorder = apiorder)

        self.buy_orders.append(order)
        self.state.add_order(order).flush()

        return order

    def place_sell_order(self, amount, price):
        apiorder = self.tradeapi.place_sell_order(amount = amount, price = price)

        order = SellOrder(state = self.state, apiorder = apiorder)
        
        self.sell_orders.append(order)
        self.state.add_order(order).flush()
        
        return order

    def check_current_orders(self):
        open_orders = self.tradeapi.open_orders()
        open_orders_map = dict([(order.id, order) for order in open_orders])

        for orders in [list(self.buy_orders), list(self.sell_orders)]:
            for order in orders:
                # ignore orders that are already done
                if order.is_done:
                    continue

                # check if there's an open_order matching the order
                open_order = open_orders_map.get(order.id, None)
                if open_order:
                    # hotfix for when time isn't returned from the place_order API
                    if not order.time:
                        order.time = open_order.time
                    continue
                else:
                    # if there's no open_order then the order is done
                    order.is_done = True

        self.state.flush()

