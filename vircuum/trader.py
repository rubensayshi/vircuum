from collections import namedtuple
import time

Order = namedtuple("Order", ["price", "amount", "spent", "data"])

class Trader(object):
    RESET_THRESHOLD = 15 * 60

    def __init__(self, tradeapi, threshold, use_balance, steps, autoconfirm, autostart, balance = None):
        self.tradeapi = tradeapi
        self.threshold = threshold
        self.use_balance = use_balance
        self.steps = steps
        self.autoconfirm = autoconfirm
        self.autostart = autostart

        self.bid = 0
        self.ask = 0
        self.buy_orders = []
        self.bought_orders = []
        self.sell_orders = []
        self.sold_orders = []
        self.history = []

        if not balance:
            self.real_balance = self.tradeapi.balance()
        else:
            self.real_balance = balance

        self.start_balance = self.use_balance * self.real_balance
        self.maxbalance = self.balance = self.start_balance
        self.spend_per_step = self.balance / steps
        self.product = 0.0
        self.profit = 0.0

    def run(self):
        print "balance [%f], using [%f], perstep [%f]" % (self.real_balance, self.balance, self.spend_per_step)
        print "profit margin: [%f] = [%f%%]" % (self.threshold, self.threshold * 100)

        if not self.autostart:
            print "run?"
            self.confirm()
        else:
            print "sleeping 5 seconds before starting ..."
            time.sleep(5)

        def endofloop(t):
            tt = time.time() - t
            sleeping = 5 - tt
            print "loop took [%d], sleeping[%f]" % (tt, sleeping)
            if sleeping > 0:
                time.sleep(sleeping)

        try:
            while True:
                t = time.time()
                self.loop()
                self.maxbalance = max(self.balance, self.maxbalance)
                endofloop(t)
        finally:
            self.cancel_buy_orders()
            self.finish()

    def get_price(self):
        (bid, ask, ) = self.retry(lambda: self.tradeapi.ticker())
        return (bid, ask, )

    def retry(self, fn, tries = 3):
        for retry in range(3):
            try:
                return fn()
            except KeyboardInterrupt:
                raise
            except:
                pass
        else:
            raise
            return

    def confirm(self, allow_autoconfirm = False):
        if self.autoconfirm and allow_autoconfirm:
            return True

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

    def place_buy_orders(self):
        if self.balance < self.spend_per_step:
            return

        price = self.ask

        while self.balance >= self.spend_per_step:
            price  = float("{:3.8f}".format(price * (1 - self.threshold)))
            amount = self.spend_per_step / price 
            
            print "placing BUY order for [%f] @ [%f]" % (amount, price)
            self.confirm(allow_autoconfirm = True)

            buy_order = self.retry(lambda: self.tradeapi.place_order(type = 'buy', price = price, amount = amount))
            print "placed BUY order %s" % buy_order

            self.buy_orders.append(buy_order)

            self.balance -= (price * amount)

    def check_current_buy_orders(self, open_orders):
        for buy_order in list(self.buy_orders):
            if buy_order.id in [open_order.id for open_order in open_orders]:
                # not processed yet :-()
                continue
            else:
                # processed! \o/
                print "order BOUGHT %s" % buy_order
                self.bought_orders.append(buy_order)
                self.buy_orders.remove(buy_order)

    def place_sell_orders(self):
        for bought_order in list(self.bought_orders):
            price = float("{:3.8f}".format(bought_order.price / (1 - self.threshold)))

            print "placing SELL order for [%f] @ [%f]" % (bought_order.amount, price)
            self.confirm(allow_autoconfirm = True)

            sell_order = self.retry(lambda: self.tradeapi.place_order(type = 'sell', price = price, amount = bought_order.amount))
            print "placed SELL order %s" % sell_order

            self.sell_orders.append(sell_order)
            self.bought_orders.remove(bought_order)

    def check_current_sell_orders(self, open_orders):
        for sell_order in list(self.sell_orders):
            if sell_order.id in [open_order.id for open_order in open_orders]:
                # not processed yet :-()
                continue
            else:
                # processed! \o/
                print "order SOLD %s" % sell_order
                self.sold_orders.append(sell_order)
                self.sell_orders.remove(sell_order)

                self.balance += sell_order.price * sell_order.amount

    def cancel_buy_orders(self):
        for buy_order in list(self.buy_orders):

            print "canceling BUY order for [%f] @ [%f]" % (buy_order.amount, buy_order.price)
            canceled = self.retry(lambda: self.tradeapi.cancel_order(id = buy_order.id))
            print "canceled BUY order %s" % buy_order

            self.buy_orders.remove(buy_order)
            self.balance += buy_order.amount * buy_order.price

    def check_reset(self):
        if len(self.sell_orders) > 0:
            return

        # if our newest buy order has surpassed our threshold then we should reset
        if int(time.time() - Trader.RESET_THRESHOLD) > max([buy_order.time for buy_order in self.buy_orders]):
            print "resetting BUY orders!"
            self.cancel_buy_orders()
            print "reset BUY orders!"

    def loop(self):
            (self.bid, self.ask) = self.get_price()

            print "bid: %f" % self.bid
            print "sell: %f" % self.ask

            open_orders = self.retry(lambda: self.tradeapi.open_orders())

            self.check_current_buy_orders(open_orders)
            self.place_sell_orders()
            self.check_current_sell_orders(open_orders)
            self.place_buy_orders()

            self.check_reset()

    def finish(self):
        print "\n" *2
        print "----------------------------------------"

        netprofit = self.balance - self.start_balance
        print "start [%f]" % self.start_balance
        print "end   [%f]" % self.balance
        print "max   [%f]" % self.maxbalance
        print "diff  [%f] %f%%" % (netprofit, (netprofit / self.start_balance) * 100)

        ordersdump = []
        orderslow  = 0
        ordershigh = 0
        ordersmid  = 0

        print "----------------------------------------"
        print "sell orders left:"

        if len(self.sell_orders) == 0:
            print "NONE"
        else:

            for sell_order in sorted(self.sell_orders, key = lambda sell_order: sell_order.price, reverse = True):
                ordersdump.append(str(sell_order))

                orderslow  += sell_order.amount * self.bid
                ordershigh += sell_order.amount * sell_order.price * (1 + self.threshold)
                ordersmid  += sell_order.amount * sell_order.price
            
            print "\n".join(ordersdump)
            print "----------------------------------------"

            print "ordershigh [%f] (sell left overs against their intended price)" % ordershigh
            print "orderslow  [%f] (sell left overs against current price)" % orderslow
            print "ordersmid  [%f] (sell left overs against their bought price)" % ordersmid

            print "profithigh [%f] %f%%" % ((ordershigh + netprofit), ((ordershigh + netprofit) / self.start_balance) * 100)
            print "profitlow  [%f] %f%%" % ((orderslow + netprofit), ((orderslow + netprofit) / self.start_balance) * 100)
            print "profitmid  [%f] %f%%" % ((ordersmid + netprofit), ((ordersmid + netprofit) / self.start_balance) * 100)

        print "----------------------------------------"
        print "\n" *2

        print "CHECK IF ALL YOUR BUY ORDERS WERE PROPERLY CANCELED !!!"
        print "----------------------------------------"
        print "\n" *2
