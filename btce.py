#! /usr/bin/env python
from collections import namedtuple
import time
from vircuum.tradeapi.btce import TradeAPI
# from vircuum.tradeapi.cexio import TradeAPI
# from vircuum.tradeapi.dummy import TradeAPI

Order = namedtuple("Order", ["price", "amount", "spent", "data"])

THRESHOLD = 0.02
USE_BALANCE = 1
STEPS = 10

# tradeapi = TradeAPI(api_key="UwqnvISKJGhs285xubyS6f6f6rc", api_secret="mOSZ3kHeTzYoZLfXMw89Tk9KOtE", username="rubensayshi")
tradeapi = TradeAPI(api_key="Z8XZA0DU-MY93LBM6-VK3USQMY-FQ1HAPG8-UD2Z02T8", 
                    api_secret="6fadd680afbe3c607571ae0385fd8be446d5bbff05d066aa40ebd1019acbaf61")

orders = []
history = []

real_balance = float(tradeapi.balance())
start_balance = USE_BALANCE * real_balance
start_balance = 100
balance = start_balance
spend_per_step = balance / STEPS
profit = 0

print "balance [%f], using [%f], perstep [%f]" % (real_balance, balance, spend_per_step)

try:
    while True:
        t = time.time()

        def sleep(t):
            tt = time.time() - t
            sleeping = TradeAPI.TIME_PER_LOOP - tt

            print "loop took [%d], sleeping [%d] ..." % (tt, sleeping)
            if sleeping > 0:
                time.sleep(sleeping)

        price = None
        retry = 1
        for retry in range(3):
            try:
                (price, ) = tradeapi.ticker()
                break
            except KeyboardInterrupt:
                raise
            except:
                pass

        if not price:
            sleep(t)

        print "price [%f]" % price
        print "balance [%f]" % balance

        for order in sorted(orders, key = lambda order: order.price, reverse = True):
            print "%f  |  %f  " % (order.price, order.amount)

        # track price
        history.append(price)

        # check if we want to buy

        # highest price we've measured
        roof = max(history)

        # we don't want to buy above our own orders that still need to sell
        ordersdesc = sorted(orders, key = lambda order: order.price, reverse = True)
        if len(ordersdesc) > 0:
            roof = min(roof, ordersdesc[-1].price)

        diff = (price - roof)
        diffperc = diff / price

        print "price change [%f] -> [%f] = %f (%f%%)" % (roof, price, diff, diffperc * 100)

        # if the price dropped more than our THRESHOLD
        if (diffperc * -1) >= THRESHOLD:
            print "goodtobuy! "

            if not balance > spend_per_step:
                print "not enough balance to buy"
            else:
                print "buying!"
                orders.append(Order(price, spend_per_step / price, spend_per_step, {}))
                balance -= spend_per_step

        # check if we want to sell
        for order in orders:
            diff = (price - order.price)
            diffperc = diff / order.price
            # if the price went up by at least our THRESHOLD
            if diffperc >= THRESHOLD:
                if order.amount != 0.0:
                    print "selling! [%f] -> [%f] = %f (%f%%)" % (order.price, price, diff, diffperc * 100)
                orders.remove(order)
                balance += price * order.amount

        sleep(t)
finally:
    netprofit = balance - start_balance
    print "start [%f]" % start_balance
    print "end   [%f]" % balance
    print "diff  [%f] %f%%" % (netprofit, (netprofit / start_balance) * 100)

    ordersdump = []
    orderslow  = 0
    ordershigh = 0
    ordersmid  = 0
    for order in sorted(orders, key = lambda order: order.price, reverse = True):
        ordersdump.append("%f  |  %f  " % (order.price, order.amount))

        orderslow  += order.amount * price
        ordershigh += order.amount * order.price * (1 + THRESHOLD)
        ordersmid  += order.amount * order.price

    print "ordershigh [%f]" % ordershigh
    print "orderslow  [%f]" % orderslow
    print "ordersmid  [%f]" % ordersmid

    print "profithigh [%f] %f%%" % ((ordershigh + netprofit), ((ordershigh + netprofit) / start_balance) * 100)
    print "profitlow  [%f] %f%%" % ((orderslow + netprofit), ((orderslow + netprofit) / start_balance) * 100)
    print "profitmid  [%f] %f%%" % ((ordersmid + netprofit), ((ordersmid + netprofit) / start_balance) * 100)




    print "\n".join(ordersdump)

