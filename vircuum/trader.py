from collections import namedtuple
import time

Order = namedtuple("Order", ["price", "amount", "spent", "data"])

class Trader(object):
    def __init__(self, tradeapi, threshold, use_balance, steps, balance = None):
        self.tradeapi = tradeapi
        self.threshold = threshold
        self.use_balance = use_balance
        self.steps = steps

        self.price = 0
        self.orders = []
        self.history = []

        if not balance:
            self.real_balance = self.tradeapi.balance()
        else:
            self.real_balance = balance

        self.start_balance = self.use_balance * self.real_balance
        self.maxbalance = self.balance = self.start_balance
        self.spend_per_step = self.balance / steps
        self.profit = 0

    def run(self):
        print "balance [%f], using [%f], perstep [%f]" % (self.real_balance, self.balance, self.spend_per_step)

        def sleep(t):
            tt = time.time() - t
            sleeping = self.tradeapi.TIME_PER_LOOP - tt

            print "loop took [%d], sleeping [%d] ..." % (tt, sleeping)
            if sleeping > 0:
                time.sleep(sleeping)

        try:
            while True:
                t = time.time()
                self.loop()
                self.maxbalance = max(self.balance, self.maxbalance)
                sleep(t)
                yield
        finally:
            self.finish()

    def loop(self):
            for retry in range(3):
                try:
                    (self.price, ) = self.tradeapi.ticker()
                    break
                except KeyboardInterrupt:
                    raise
                except:
                    pass
            else:
                return

            print "price [%f]" % self.price
            print "balance [%f]" % self.balance

            for order in sorted(self.orders, key = lambda order: order.price, reverse = True):
                print "%f  |  %f  " % (order.price, order.amount)

            # track price
            self.history.append(self.price)

            # check if we want to buy

            # highest price we've measured
            roof = max(self.history)

            # we don't want to buy above our own orders that still need to sell
            ordersdesc = sorted(self.orders, key = lambda order: order.price, reverse = True)
            if len(ordersdesc) > 0:
                roof = min(roof, ordersdesc[-1].price)

            diff = (self.price - roof)
            diffperc = diff / self.price

            print "price roof[%f] -> price[%f] = %f (%f%%)" % (roof, self.price, diff, diffperc * 100)

            # if the price dropped more than our THRESHOLD
            if (diffperc * -1) >= self.threshold:
                print "goodtobuy! "

                if not self.balance > self.spend_per_step:
                    print "not enough balance to buy"
                else:
                    print "buying!"
                    self.orders.append(Order(self.price, self.spend_per_step / self.price, self.spend_per_step, {}))
                    self.balance -= self.spend_per_step

            # check if we want to sell
            for order in self.orders:
                diff = (self.price - order.price)
                diffperc = diff / order.price
                # if the price went up by at least our THRESHOLD
                if diffperc >= self.threshold:
                    if order.amount != 0.0:
                        print "selling! [%f] -> [%f] = %f (%f%%)" % (order.price, self.price, diff, diffperc * 100)
                    self.orders.remove(order)
                    self.balance += self.price * order.amount

    def finish(self):
        netprofit = self.balance - self.start_balance
        print "start [%f]" % self.start_balance
        print "end   [%f]" % self.balance
        print "max   [%f]" % self.maxbalance
        print "diff  [%f] %f%%" % (netprofit, (netprofit / self.start_balance) * 100)

        ordersdump = []
        orderslow  = 0
        ordershigh = 0
        ordersmid  = 0
        for order in sorted(self.orders, key = lambda order: order.price, reverse = True):
            ordersdump.append("%f  |  %f  " % (order.price, order.amount))

            orderslow  += order.amount * self.price
            ordershigh += order.amount * order.price * (1 + self.threshold)
            ordersmid  += order.amount * order.price

        print "ordershigh [%f]" % ordershigh
        print "orderslow  [%f]" % orderslow
        print "ordersmid  [%f]" % ordersmid

        print "profithigh [%f] %f%%" % ((ordershigh + netprofit), ((ordershigh + netprofit) / self.start_balance) * 100)
        print "profitlow  [%f] %f%%" % ((orderslow + netprofit), ((orderslow + netprofit) / self.start_balance) * 100)
        print "profitmid  [%f] %f%%" % ((ordersmid + netprofit), ((ordersmid + netprofit) / self.start_balance) * 100)

        print "\n".join(ordersdump)