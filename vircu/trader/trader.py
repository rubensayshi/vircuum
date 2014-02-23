from collections import namedtuple
import time
from datetime import datetime

from vircu.trader.currency import BTC, GHS
from vircu.trader.order import BuyOrder, SellOrder
from vircu.trader.models import DBLogMessage, DBBank, DBBalance, DBPrice


class TraderState(object):

    def assigned_balance(self, assigned_balance):
        raise NotImplementedError()

    def log_message(self, msg, status = None, dt = None):
        raise NotImplementedError()

    def tick(self, price, dt):
        raise NotImplementedError()

    def add_order(self, order):
        raise NotImplementedError()

    def order_done(self, order):
        raise NotImplementedError()

    def order_processed(self, order):
        raise NotImplementedError()

    def order_reset(self, order):
        raise NotImplementedError()

    def flush(self):
        raise NotImplementedError()


class CLIState(TraderState):

    def __init__(self):
        self.buy_orders = []
        self.sell_orders = []

    def assigned_balance(self, assigned_balance):
        print "assigned_balance", assigned_balance
        return self

    def log_message(self, msg, status = None, dt = None):
        dt = dt or datetime.now()
        status = status or 'log'

        print msg, status, dt
        return self

    def tick(self, price, dt):
        print "price", str(price)
        return self

    def add_order(self, order):
        print "new order %s" % order
        self.order_container(order).append(order)
        return self

    def order_done(self, order):
        print "order done %s" % order
        return self

    def order_processed(self, order):
        print "order processed %s" % order
        return self

    def order_reset(self, order):
        print "order processed %s" % order
        return self

    def flush(self):
        return self

    def order_container(self, order):
        if isinstance(order, BuyOrder):
            return self.buy_orders
        elif isinstance(order, SellOrder):
            return self.sell_orders


class SocketState(CLIState):

    def __init__(self, server):
        super(SocketState, self).__init__()
        self.server = server

    def assigned_balance(self, assigned_balance):
        self.broadcast_event("msg", str(assigned_balance))
        return super(SocketState, self).assigned_balance(assigned_balance)

    def log_message(self, msg, status = None, dt = None):
        dt = dt or datetime.now()
        status = status or 'log'

        self.broadcast_event("msg", msg, status, str(dt))
        return super(SocketState, self).log_message(msg, status)

    def tick(self, price, dt):
        self.broadcast_event("msg", "price", str(price), str(dt))
        return super(SocketState, self).tick(price, dt)

    def add_order(self, order):
        self.broadcast_event("msg", "new order %s" % order)
        return super(SocketState, self).add_order(order)

    def order_done(self, order):
        self.broadcast_event("msg", "order done %s" % order)
        return super(SocketState, self).order_done(order)

    def order_processed(self, order):
        self.broadcast_event("msg", "order processed %s" % order)
        return super(SocketState, self).order_processed(order)

    def order_reset(self, order):
        self.broadcast_event("msg", "order reset %s" % order)
        return super(SocketState, self).order_reset(order)

    def flush(self):
        return super(SocketState, self).flush()

    def broadcast_event(self, event, *args):
        """
        This is sent to all in the sockets in this particular Namespace,
        including itself.
        """
        pkt = dict(type="event",
                   name=event,
                   args=args,
                   endpoint="/trader")

        for sessid, socket in self.server.sockets.iteritems():
            socket.send_packet(pkt)


class Trader(object):
    RESET_THRESHOLD = 15 * 60
    SLEEP_PER_LOOP = 0

    def __init__(self, tradeapi, masterplan, autoconfirm, autostart, retries, Session, state, balance = None):
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

        self.state.assigned_balance(self.masterplan.assigned_balance).flush()

    def log_action(self, msg, status = None):
        self.state.log_message(msg, status).flush()

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

        for order in list(self.buy_orders):
            if order.is_done or order.apiorder.id in [open_order.id for open_order in open_orders]:
                continue
            else:
                order.is_done = True


        for order in list(self.sell_orders):
            if order.is_done or order.apiorder.id in [open_order.id for open_order in open_orders]:
                continue
            else:
                order.is_done = True

        self.state.flush()

