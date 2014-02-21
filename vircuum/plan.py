import copy

from vircuum.currency import BTC, GHS


class ActionPlan(object):
    def run(self):
        raise Exception("not implemented")


class Plan(object):
    def __init__(self, parent = None):
        self.parent = parent

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

    @property
    def trader(self):
        return self.parent.trader

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

        total_req_balance = self.requested_balance()

        for child in self.children:
            child_req_balance = child.requested_balance()
            child_asigned_balance = {}

            for currency in self.assigned_balance:
                weight = child_req_balance.get(currency, 0.0)
                total  = total_req_balance.get(currency, 0)

                if not weight or not total:
                    balance = currency.VALUE(0)
                else:
                    factor  = weight / total
                    balance = self.assigned_balance[currency] * factor
                    balance = currency.VALUE(balance)
                    self.balance[currency] -= balance

                child_asigned_balance[currency] = balance

            child.assign_balance(child_asigned_balance)


class MasterPlan(Plan):
    def __init__(self, assigned_balance = None):
        super(MasterPlan, self).__init__(self)
        self.assigned_balance = dict((balance.CURRENCY, balance) for balance in assigned_balance) if assigned_balance else {}
        self._trader = None
        self.initialized = False


    @property
    def trader(self):
        return self._trader

    @trader.setter
    def trader(self, trader):
        self._trader = trader

    def init(self, price, assigned_balance = None):
        if self.initialized:
            return False

        self.initialized = True
        self.assign_balance(assigned_balance or self.assigned_balance)
        self._price = price

    def run(self):
        if not self.initialized:
            raise Exception("init first")

        super(MasterPlan, self).run()


class Action(object):
    def __init__(self, actionA, actionB, parent = None):
        self.actionA = actionA
        self.actionB = actionB
        self.parent  = parent

        self.actionA.action = self
        self.actionB.action = self

        self.balance = {}
        self._price = None

    @property
    def price(self):
        return self._price or (self.parent.price if self.parent else None)

    @price.setter
    def price(self, price):
        self._price = price

    def fixate_price(self):
        self.price = self.price

    @property
    def trader(self):
        return self.parent.trader

    def requested_balance(self):
        return {self.actionA.currency() : 1.0}

    def assign_balance(self, assigned_balance):
        self.balance = assigned_balance

    def run(self):
        return self.execute()

    def execute(self):
        self.fixate_price()

        if self.actionA.execute():
            self.actionB.price = self.actionA.price
            if self.actionB.execute():
                self.actionB.reset()
                self.actionA.reset()

                return self.execute()


class Task(object):
    def __init__(self):
        self.action  = None
        self._price  = None
        self.incurr  = None
        self.outcurr = None

    @property
    def trader(self):
        return self.action.trader

    def execute(self):
        self.fixate_price()
        return False

    def reset(self):
        self._price = None

        return True

    @property
    def price(self):
        return self._price or self.action.price

    @price.setter
    def price(self, price):
        self._price = price

    def fixate_price(self):
        self.price = self.price


class Buy(Task):
    def __init__(self, incurr, outcurr, threshold):
        super(Buy, self).__init__()

        self.incurr    = incurr
        self.outcurr   = outcurr
        self.threshold = threshold
        self.buy_order = None

    def execute(self):
        if not self.buy_order:
            self.place_buy_order()
            return False
        elif self.buy_order.status == 1:
            self.buy_order.status = 2
            self.action.balance[self.outcurr] += self.outcurr.VALUE(self.buy_order.amount)
            return True
        elif self.buy_order.status >= 2:
            return True
        else:
            return False

    def reset(self):
        self.buy_order = None

        return super(Buy, self).reset()

    def cancel_buy_order(self):
        raise Exception("not implemented")

    def place_buy_order(self):
        price  = self.price = self.price * (1 - self.threshold)
        amount = self.action.balance[self.incurr] / price

        print "place_buy_order", self.price, self.action.balance[self.incurr], amount

        self.buy_order = self.trader.place_buy_order(amount = amount, price = price)

        self.action.balance[self.incurr] -= self.incurr.VALUE(self.buy_order.price * self.buy_order.amount)


class Sell(Task):
    def __init__(self, incurr, outcurr, profit):
        super(Buy, self).__init__()

        self.incurr    = incurr
        self.outcurr   = outcurr
        self.profit    = profit
        self.buy_order = None

    def execute(self):
        if not self.sell_order:
            self.place_sell_order()
            return False
        elif self.sell_order.status == 1:
            self.sell_order.status = 2
            self.action.balance[self.outcurr] += self.outcurr.VALUE(self.sell_order.price * self.sell_order.amount)
            return True
        elif self.sell_order.status >= 2:
            return True
        else:
            return False

    def reset(self):
        self.sell_order = None

        return super(Sell, self).reset()

    def place_sell_order(self):
        price = self.price = self.price * (1 + self.profit)
        amount = self.action.balance[self.incurr]

        print "place_sell_order", self.price, self.action.balance[self.incurr], amount

        self.sell_order = self.trader.place_sell_order(amount = amount, price = price)

        self.action.balance[self.incurr] -= self.sell_order.amount


class Condition(object):
    pass


class UpTrend(Condition):
    def __nonzero__(self):
        return True


class DownTrend(Condition):
    def __nonzero__(self):
        return False

