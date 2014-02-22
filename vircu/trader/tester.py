from collections import namedtuple
import time
from datetime import datetime

from vircu.trader.trader import *

class Tester(Trader):

    def debug_action(self, msg):
        print msg
        return msg

    def run(self):
        print "TESTER"
        print "TESTER"
        print "TESTER"
        print "TESTER"

        print "\n\nbalance"
        self.real_balance = self.tradeapi.balance()
        self.balance = self.real_balance * 0.1 # keep some margin for transaction costs
        print self.real_balance, self.balance
        
        print "\n\nticker"
        (self.bid, self.ask) = self.get_price()
        print self.bid, self.ask

        print "\n\nopen_orders", self.tradeapi.open_orders()

        print "\n\nplace ultra low order at 10% of current bid"
        price  = self.price_format(self.bid * 0.1)
        amount = self.amount_format(self.balance / price)
        
        print "placing BUY order for [%f] @ [%f]" % (amount, price)
        self.confirm(allow_autoconfirm = False)

        buy_order = self.tradeapi.place_buy_order(price = price, amount = amount)
        print "placed BUY order %s" % buy_order

        self.buy_orders.append(buy_order)

        print "\n\nopen_orders", self.tradeapi.open_orders()

        print "\n\ncancel buy orders", self.retry(lambda: self.cancel_buy_orders(), tries = 10, wait = 1)
        