from collections import namedtuple
import time
import copy
from datetime import datetime

Order = namedtuple("Order", ["price", "amount", "spent", "data"])

# {col1head:<{col1len}}
# {myfloat:15.8f}
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#|  TIME:   YYYY-MM-DD HH:II:SS  |  PROFIT:  1475.495025 (9999999)       |
#|  START:  1475.495025          |  BALANCE: 1475.495025                 |
#=========================================================================
#|  BID:  1475.495025 | 10min MIN: 1475.495025 | 30min MIN: 1475.495025  |
#|  SELL: 1475.495025 | 10min MAX: 1475.495025 | 30min MAX: 1475.495025  |
#=========================================================================
#| placing BUY order for [0.007712] @ [0.043310]
#| placed BUY order {'amount': 0.00771152, 'type': u'buy', 'price': 0.04331025, 'id': u'253419312'}
#| placing BUY order for [0.007719] @ [0.043267]
#| placed BUY order {'amount': 0.00771924, 'type': u'buy', 'price': 0.04326694, 'id': u'253419328'}
#| placing BUY order for [0.007727] @ [0.043224]
#| placed BUY order {'amount': 0.00772697, 'type': u'buy', 'price': 0.04322367, 'id': u'253419343'}
#=========================================================================
#|  ---------- BUY ORDERS ---------  |  --------- SELL ORDERS ---------  |
#|       amount        price    age  |       amount        price    age  |
#|     0.007712     0.043310  9999s  |     0.007712     0.043310  9999s  |
#|     0.007712     0.043310  9999s  |     0.007712     0.043310  9999s  | 
#|     0.007712     0.043310  9999s  |     0.007712     0.043310  9999s  |
#|     0.007712     0.043310  9999s  |     0.007712     0.043310  9999s  |
#|  1199.007712  1475.495025  9999s  |  1199.007712  1475.495025  9999s  |
#-------------------------------------------------------------------------
#|       amount          sum         |       amount          sum         |
#|  1199.007712  1199.007712         |  1199.007712  1199.007712         |
#=========================================================================
#|  PROFIT CUR:  1475.495025         |  1475.495025%                     |
#|  PROFIT LOW:  1475.495025         |  1475.495025%                     |
#|  PROFIT MID:  1475.495025         |  1475.495025%                     |
#|  PROFIT HIGH: 1475.495025         |  1475.495025%                     |
#=========================================================================
#| loop took [3], sleeping[1.072918]
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
ACTION_TEMPLATE = """| {action}"""

SHORT_TEMPLATE = "{:11.6f}"
LONG_TEMPLATE = SHORT_TEMPLATE
BALANCE_TEMPLATE = LONG_TEMPLATE
PRICE_TEMPLATE = SHORT_TEMPLATE
AMOUNT_TEMPLATE = SHORT_TEMPLATE
ORDER_TEMPLATE = """{amount:>11}  {price:>11}  {age:>4}{ageunit:>1}"""

STATUS_TEMPLATE = """
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
|  TIME:   {dt:>19}  |  PROFIT:  {cur_profit:>11} ({sold_cnt:>7})       |
|  START:  {start_balance:>11}          |  BALANCE: {balance:>11}                 |
=========================================================================
|  BID:  {bid:>11} | 10min MIN:    0.000000 | 30min MIN:    0.000000  |
|  SELL: {ask:>11} | 10min MAX:    0.000000 | 30min MAX:    0.000000  |
=========================================================================
{actionsbefore}
=========================================================================
|  ---------- BUY ORDERS ---------  |  --------- SELL ORDERS ---------  |
|       amount        price    age  |       amount        price    age  |
{orders}
-------------------------------------------------------------------------
|       amount          sum         |       amount          sum         |
|  {buy_amount:>11}  {buy_sum:>11}         |  {sell_amount:>11}  {sell_sum:>11}         |
=========================================================================
|  PROFIT CUR:  {cur_profit:>11}         |  {cur_profit_p:>11}%                     |
|  PROFIT LOW:  {low_profit:>11}         |  {low_profit_p:>11}%                     |
|  PROFIT HIGH: {high_profit:>11}         |  {high_profit_p:>11}%                     |
=========================================================================
{actionsafter}
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
"""


class ActionPlan(object):
    def run(self):
        raise Exception("not implemented")


class Plan(object):
    def __init__(self, parent = None):
        self.parent  = parent

        self.balance = []
        self.children = []
        self.conditions = []

        self._price = None

    @property
    def price(self):
        return self._price or (self.parent.price if self.parent else None)

    @price.setter
    def price(self, price):
        self._price = price

    def add_condition(self, condition):
        self.conditions.append(condition)
        return condition

    def add_child(self, child):
        self.children.append(child)
        child.parent = self
        return child

    def validate(self):
        return all([bool(condition) for condition in self.conditions])

    def run(self):
        if self.validate():
            self.execute()

    def execute(self):
        for child in self.children:
            child.run()

    def requested_balance(self):
        grp = {}

        for child in self.children:
            for currency, weight in child.requested_balance().items():
                grp.setdefault(currency, 0.0)
                grp[currency] += float(weight)

        return grp

    def assign_balance(self, assigned_balance):
        self.assigned_balance = assigned_balance
        self.balance = copy.deepcopy(self.assigned_balance)
        
        requested_balance = self.requested_balance()

        for child in self.children:
            for currency, weight in child.requested_balance().items():
                factor  = weight / requested_balance[currency]
                balance = factor * self.assigned_balance[currency].value
                balance = currency.VALUE(balance)

                self.balance[currency] -= balance
                child.assign_balance({currency : balance})


class MasterPlan(Plan):
    def __init__(self, assigned_balance = None):
        super(MasterPlan, self).__init__(self)
        self.assigned_balance = dict((balance.CURRENCY, balance) for balance in assigned_balance)
        self.initialized = False

    def init(self, price):
        if self.initialized:
            return False

        self.assign_balance(self.assigned_balance)
        self._price = price

    def run(self, price):
        self.init(price)

        super(MasterPlan, self).run()


class Action(object):
    def __init__(self, actionA, actionB, parent = None):
        self.actionA = actionA
        self.actionB = actionB
        self.parent  = parent

        self.actionA.action = self
        self.actionB.action = self

        self.assigned_balance = {}
        self._price = None

    @property
    def price(self):
        return self._price or (self.parent.price if self.parent else None)

    @price.setter
    def price(self, price):
        self._price = price

    def requested_balance(self):
        return {self.actionA.currency() : 1.0}

    def assign_balance(self, assigned_balance):
        self.assigned_balance = assigned_balance

    def run(self):
        return self.execute()

    def execute(self):
        # fixate the price
        if not self._price:
            self._price = self.price

        if self.actionA.execute() and self.actionB.execute():
            self.actionB.reset()
            self.actionA.reset()

            return self.execute()


class Currency(object):
    NAME = None

    @classmethod
    def round(cls, value):
        return float(value)


class CurrencyV(object):
    CURRENCY = None
    def __init__(self, value):
        self.value = self.round(value)

    def round(self, value):
        return self.CURRENCY.round(value)

    def __add__(self, other):
        return self.CURRENCY.VALUE(other.value + self.value)

    def __sub__(self, other):
        return self.CURRENCY.VALUE(other.value - self.value)

    def __mul__(self, other):
        return self.CURRENCY.VALUE(other.value * self.value)

    def __div__(self, other):
        return self.CURRENCY.VALUE(other.value / self.value)

    def __repr__(self):
        return str(self.value)


class CurrencyP(object):
    CURRENCY = None
    def __init__(self, percentage):
        self.percentage = percentage


class GHS(Currency):
    NAME = 'GHS'

    @classmethod
    def VALUE(cls, value):
        return GHSv(value)


class BTC(Currency):
    NAME = 'BTC'

    @classmethod
    def VALUE(cls, value):
        return BTCv(value)


class GHSv(CurrencyV):
    CURRENCY = GHS


class BTCv(CurrencyV):
    CURRENCY = BTC


class GHSp(CurrencyP):
    CURRENCY = GHS

    def __repr__(self):
        return repr(self.CURRENCY)


class BTCp(CurrencyP):
    CURRENCY = BTC

    def __repr__(self):
        return repr(self.CURRENCY)


class Task(object):
    def __init__(self):
        self.action = None
        self._price = None

    def execute(self):
        return False

    def reset(self):
        pass

    def currency(self):
        raise Exception("not implemented")

    @property
    def price(self):
        return self._price or self.action.price

    @price.setter
    def price(self, price):
        self._price = price

    def place_order(self, type, price, amount):
        print "place order [%s] [%s] @ [%s]" % (type, amount, price)


class Buy(Task):
    def __init__(self, buy, curr):
        super(Buy, self).__init__()

        self.buy = buy
        self.curr = curr
        self.buy_order = None

    def currency(self):
        return self.curr

    def execute(self):
        if not self.buy_order:
            self.place_buy_order()
            return False
        elif not self.buy_order.bought:
            return False
        else:
            return True

    def reset(self):
        if not self.buy_order.bought:
            self.cancel_buy_order()

        self.buy_order = None

        return True

    def cancel_buy_order(self):
        pass

    def place_buy_order(self):
        price  = self.price * (1 - self.buy.percentage)
        amount = self.action.assigned_balance[self.currency()].value / price
        self.place_order('buy', price, amount)


class Sell(Task):
    def __init__(self, sell, curr):
        super(Sell, self).__init__()

        self.sell = sell
        self.curr = curr
        self.sell_order = None

    def currency(self):
        return self.curr

    def execute(self):
        if not self.sell_order:
            self.place_sell_order()
            return False
        elif not self.sell_order.sold:
            return False
        else:
            return True

    def reset(self):
        if not self.sell_order.sold:
            return False

        self.sell_order = None

        return True

    def place_sell_order(self):
        price = self.price * (1 + self.sell.percentage)
        amount = price / self.action.assigned_balance[self.currency()]
        self.place_order('sell', price, amount)


class Condition(object):
    pass


class UpTrend(Condition):
    def __nonzero__(self):
        return True


class DownTrend(Condition):
    def __nonzero__(self):
        return False


masterplan = MasterPlan(assigned_balance = [BTCv(2), GHSv(5)])


uptrendplan = masterplan.add_child(Plan())
uptrendplan.add_condition(UpTrend())

uptrendplan.add_child(Action(Buy(GHSp(0.01), BTC), Sell(BTCp(0.01), GHS)))
uptrendplan.add_child(Action(Buy(GHSp(0.02), BTC), Sell(BTCp(0.01), GHS)))
uptrendplan.add_child(Action(Buy(GHSp(0.05), BTC), Sell(BTCp(0.03), GHS)))

if False:
    downtrendplan = masterplan.add_child(Plan())
    downtrendplan.add_condition(DownTrend())

    downtrendplan.add_child(Action(Sell(GHSp(0.01), BTC), Buy(BTCp(0.01), GHS)))
    downtrendplan.add_child(Action(Sell(GHSp(0.02), BTC), Buy(BTCp(0.01), GHS)))
    downtrendplan.add_child(Action(Sell(GHSp(0.05), BTC), Buy(BTCp(0.03), GHS)))


masterplan.run(price = 0.3)


while True:
    import time
    time.sleep(10)

class Trader(object):
    RESET_THRESHOLD = 15 * 60
    SLEEP_PER_LOOP = 0

    def __init__(self, tradeapi, threshold, use_balance, use_balance_exact, steps, autoconfirm, autostart, retries, sessionmaker, balance = None):
        self.tradeapi = tradeapi
        self.threshold = threshold
        self.use_balance = use_balance
        self.use_balance_exact = use_balance_exact
        self.steps = steps
        self.autoconfirm = autoconfirm
        self.autostart = autostart
        self.retries = retries
        self.sessionmaker = sessionmaker

        self.bid = 0
        self.ask = 0
        self.buy_orders = []
        self.bought_orders = []
        self.sell_orders = []
        self.sold_orders = []
        self.history = []

        if not balance:
            self.real_balance = self.retry(lambda: tradeapi.balance())
        else:
            self.real_balance = balance

        if self.use_balance_exact:
            assert self.real_balance >= self.use_balance_exact
            self.start_balance = self.use_balance_exact
        else:
            self.start_balance = self.use_balance * self.real_balance

        self.maxbalance = self.balance = self.start_balance
        self.spend_per_step = self.balance / steps
        self.product = 0.0
        self.profit = 0.0
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
        print "balance [%f], using [%f], perstep [%f]" % (self.real_balance, self.balance, self.spend_per_step)
        print "profit margin: [%f] = [%f%%]" % (self.threshold, self.threshold * 100)

        if not self.autostart:
            self.confirm("run?")
        else:
            print "sleeping 5 seconds before starting ..."
            time.sleep(5)

        def endofloop(t):
            tt = time.time() - t
            sleeping = max(Trader.SLEEP_PER_LOOP - tt, 0)

            return ("loop took [%f], sleeping[%f]" % (tt, sleeping), sleeping)

        try:
            fails = 0

            while True:
                try:
                    t = time.time()
                    self.debug_actions = []

                    self.loop()

                    self.maxbalance = max(self.balance, self.maxbalance)
                    endmsg, sleeping = endofloop(t)

                    self.print_status(actionsbefore = self.debug_actions, actionsafter = [endmsg])

                    if sleeping > 0:
                        time.sleep(sleeping)

                    fails = 0
                except KeyboardInterrupt:
                    raise
                except:
                    print """
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!                   LOOP FAILED [%d], RETRYING ...                   !!!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
""" % fails
                    fails += 1

                    if fails >= self.retries:
                        raise
                    else:
                        pass # time.sleep(60)
        finally:
            try:
                self.print_status(actionsbefore = self.debug_actions, actionsafter = ["FINALLY, state before canceling buy orders ---^"])

                self.retry(lambda: self.cancel_buy_orders(), wait = 10)

                self.print_status(actionsbefore = self.debug_actions, actionsafter = ["FINALLY, state after canceling buy orders ---^"])
                self.finish()
            except Exception, e:
                # supress this, we want to see the original error!!
                print e


    def price_format(self, price):
        return float(self.tradeapi.PRICE_FORMAT.format(price))

    def amount_format(self, amount):
        return float(self.tradeapi.AMOUNT_FORMAT.format(amount))

    def get_price(self):
        (bid, ask, ) = self.retry(lambda: self.tradeapi.ticker())
        return (bid, ask, )

    def retry(self, fn, tries = 5, wait = 1.0):
        for retry in range(max(tries, 1)):
            t = time.time()
            try:
                return fn()
            except KeyboardInterrupt:
                raise
            except:
                pass

            sleeping = (wait * float(tries)) - (time.time() - t)
            if sleeping > 0.0:
                time.sleep(sleeping)
        else:
            raise
            return

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

    def place_buy_orders(self):
        if self.balance < self.spend_per_step:
            return

        price = self.ask

        while self.balance >= self.spend_per_step:
            price  = self.price_format(price * (1 - self.threshold))
            amount = self.amount_format(self.spend_per_step / price) 
            
            self.confirm(self.debug_action("placing BUY order for [%f] @ [%f]" % (amount, price)), 
                         allow_autoconfirm = True)

            buy_order = self.retry(lambda: self.tradeapi.place_buy_order(price = price, amount = amount))
            self.debug_action("placed BUY order %s" % buy_order)

            self.buy_orders.append(buy_order)

            self.balance -= self.price_format(price * amount)

    def check_current_buy_orders(self, open_orders = None):
        if not open_orders:
            open_orders = self.retry(lambda: self.tradeapi.open_orders())

        for buy_order in list(self.buy_orders):
            if buy_order.id in [open_order.id for open_order in open_orders]:
                # not processed yet :-()
                continue
            else:
                # processed! \o/
                self.debug_action("order BOUGHT %s" % buy_order)
                self.bought_orders.append(buy_order)
                self.buy_orders.remove(buy_order)

        self.cancel_unknown_buy_orders(open_orders = open_orders)

    def place_sell_orders(self):
        for bought_order in list(self.bought_orders):
            price = self.price_format(bought_order.price / (1 - self.threshold))

            self.confirm(self.debug_action("placing SELL order for [%f] @ [%f]" % (bought_order.amount, price)), 
                         allow_autoconfirm = True)

            sell_order = self.retry(lambda: self.tradeapi.place_sell_order(price = price, amount = bought_order.amount))
            self.debug_action("placed SELL order %s" % sell_order)

            self.sell_orders.append(sell_order)
            self.bought_orders.remove(bought_order)

    def check_current_sell_orders(self, open_orders = None):
        if not open_orders:
            open_orders = self.retry(lambda: self.tradeapi.open_orders())

        for sell_order in list(self.sell_orders):
            if sell_order.id in [open_order.id for open_order in open_orders]:
                # not processed yet :-()
                continue
            else:
                # processed! \o/
                self.debug_action("order SOLD %s" % sell_order)
                self.sold_orders.append(sell_order)
                self.sell_orders.remove(sell_order)

                self.balance += sell_order.price * sell_order.amount

    def cancel_unknown_buy_orders(self, open_orders = None):
        if not open_orders:
            open_orders = self.retry(lambda: self.tradeapi.open_orders())

        for open_order in list(open_orders):
            if open_order.type == 'buy':
                if open_order.id not in [buy_order.id for buy_order in self.buy_orders]:
                    self.debug_action("!! CANCELING UNKNOWN BUY ORDER %s !!" % open_order)
                    self.tradeapi.cancel_order(id = open_order.id)


    def cancel_buy_orders(self):
        for buy_order in list(self.buy_orders):

            self.debug_action("canceling BUY order for [%f] @ [%f]" % (buy_order.amount, buy_order.price))
            canceled = self.retry(lambda: self.tradeapi.cancel_order(id = buy_order.id))

            if canceled:
                self.debug_action("canceled BUY order %s" % buy_order)
                self.buy_orders.remove(buy_order)
                self.balance += buy_order.amount * buy_order.price
            else:
                self.debug_action("FAILED to cancel BUY order %s" % buy_order)

        if len(self.buy_orders) > 0:
            raise Exception("Failed to cancel all buy orders")

    def check_reset(self):
        if len(self.sell_orders) > 0:
            return

        # if our newest buy order has surpassed our threshold then we should reset
        if int(time.time() - Trader.RESET_THRESHOLD) > max([buy_order.time for buy_order in self.buy_orders]):
            self.debug_action("resetting BUY orders!")
            self.retry(lambda: self.cancel_buy_orders(), wait = 10)
            self.debug_action("reset BUY orders!")

    def print_status(self, actionsbefore, actionsafter):
        dt = datetime.now()

        null_order = ORDER_TEMPLATE.format(price = "", amount = "", age = "", ageunit = "")

        def format_order(order):
            age = int(time.time() - order.time)
            ageunit = "s"
            if (age > 3600 * 2):
                age /= 3600
                ageunit = "h"
            elif (age > 60 * 10):
                age /= 60
                ageunit = "m"

            return ORDER_TEMPLATE.format(price = PRICE_TEMPLATE.format(order.price),
                                         amount = AMOUNT_TEMPLATE.format(order.amount),
                                         age = age, 
                                         ageunit = ageunit)


        actionsbefore = "\n".join(actionsbefore)
        actionsafter = "\n".join(actionsafter)

        buy_orders  = sorted(self.buy_orders, key = lambda o: o.price, reverse = True)
        sell_orders = sorted(self.sell_orders, key = lambda o: o.price, reverse = False)

        orders = []
        for x in range(max(len(buy_orders), len(sell_orders))):
            buy_order  = buy_orders[x]  if len(buy_orders) > x  else None
            sell_order = sell_orders[x] if len(sell_orders) > x else None
            buy_order  = format_order(buy_order)  if buy_order else null_order
            sell_order = format_order(sell_order) if sell_order else null_order

            orders.append("|  %s  |  %s  |" % (buy_order, sell_order))
        orders = "\n".join(orders)

        args = dict(
            bid = self.bid, ask = self.ask,
            balance = BALANCE_TEMPLATE.format(self.balance), start_balance = BALANCE_TEMPLATE.format(self.start_balance),
            dt = dt.strftime('%Y-%m-%d %H:%M:%S'),
            orders = orders,
            actionsbefore = actionsbefore, actionsafter = actionsafter
        )
        args.update(self.profit_data())

        print STATUS_TEMPLATE.format(**args)


    def loop(self):
        (self.bid, self.ask) = self.get_price()

        self.check_current_buy_orders()
        self.place_sell_orders()
        self.check_current_sell_orders()
        self.place_buy_orders()
        self.check_reset()

    def profit_data(self):
        data = {
            'cur_profit'      : 0,
            'cur_profit_p'    : 0,
            'low_profit'      : 0,
            'low_profit_p'    : 0,
            'high_profit'     : 0,
            'high_profit_p'   : 0,

            'buy_amount'      : 0,
            'buy_sum'         : 0,
            'buy_cnt'         : 0,
            'sell_amount'     : 0,
            'sell_sum'        : 0,
            'sell_cnt'        : 0,
            'bought_amount'   : 0,
            'bought_sum'      : 0,
            'bought_cnt'      : 0,
            'sold_amount'     : 0,
            'sold_sum'        : 0,
            'sold_cnt'        : 0,
        }


        for k, fn in [
            ('cur',  None),
            ('low',  lambda o: max(self.bid, (o.price / (1 + self.threshold)))),
            ('high', lambda o: o.price),
        ]:
            balance = self.balance
            balance += sum((o.amount * o.price) for o in self.buy_orders)

            if fn:
                balance += sum(o.amount * fn(o) for o in self.sell_orders)

            profit = balance - self.start_balance

            data['%s_profit' % k]   = BALANCE_TEMPLATE.format(profit)
            data['%s_profit_p' % k] = PRICE_TEMPLATE.format(profit / self.start_balance * 100)

        for k in ['buy', 'sell', 'sold']:
            orders = getattr(self, '%s_orders' % k)

            data['%s_amount' % k] = AMOUNT_TEMPLATE.format((sum(o.amount for o in orders)))
            data['%s_sum' % k]    = PRICE_TEMPLATE.format((sum(o.price * o.amount for o in orders)))
            data['%s_cnt' % k]    = int(len(orders))

        return data

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
