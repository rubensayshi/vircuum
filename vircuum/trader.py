from collections import namedtuple
import time
from datetime import datetime

from vircuum.currency import BTC, GHS
from vircuum.order import BuyOrder, SellOrder
from vircuum.models import DBLogMessage, DBBank, DBBalance


class Trader(object):
    RESET_THRESHOLD = 15 * 60
    SLEEP_PER_LOOP = 0

    def __init__(self, tradeapi, masterplan, autoconfirm, autostart, retries, Session, balance = None):
        self.tradeapi = tradeapi
        self.masterplan = masterplan
        self.autoconfirm = autoconfirm
        self.autostart = autostart
        self.retries = retries
        self.Session = Session

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
            assert self.real_balance >= self.masterplan.assigned_balance[BTC]

        self.start_balance = DBBank('start_balance')
        self.session.add(self.start_balance)

        for currency, amount in self.masterplan.assigned_balance.items():
            self.start_balance.balance.append(DBBalance(currency = currency,
                                                        amount   = amount))
        
        self.current_balance = DBBank('current_balance')
        self.session.add(self.current_balance)

        self.session.commit()
        
    @property
    def session(self):
        if not hasattr(self, '_session'):
            self._session = self.Session()

        return self._session

    @session.setter
    def session(self, session):
        self._session = session

    def log_action(self, msg, status = 'log'):
        self.session.add(DBLogMessage(msg, timestamp = int(time.time()), status = status))
        print "[%s] %s" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), msg)
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
        apiorder = self.tradeapi.place_buy_order(amount = amount, price = price)

        order = BuyOrder(trader = self, apiorder = apiorder)
        self.session.commit()

        self.buy_orders.append(order)

        return order

    def place_sell_order(self, amount, price):
        apiorder = self.tradeapi.place_sell_order(amount = amount, price = price)

        order = SellOrder(trader = self, apiorder = apiorder)
        self.session.commit()

        self.sell_orders.append(order)
        
        return order

    def check_current_orders(self):
        open_orders = self.tradeapi.open_orders()

        for order in list(self.buy_orders):
            if order.is_done or order.apiorder.id in [open_order.id for open_order in open_orders]:
                continue
            else:
                self.log_action("order_bought %s @ %s" % (order.amount, order.price))
                order.is_done = True


        for order in list(self.sell_orders):
            if order.is_done or order.apiorder.id in [open_order.id for open_order in open_orders]:
                continue
            else:
                self.log_action("order_sold %s @ %s" % (order.amount, order.price))
                order.is_done = True

        self.session.commit()

