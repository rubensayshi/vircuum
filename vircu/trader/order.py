

class Order(object):
    STATUS_OPEN      = 0
    STATUS_PARTIAL   = 1
    STATUS_DONE      = 2
    STATUS_PROCESSED = 3
    STATUS_RESET     = 99

    def __init__(self, apiorder, state):
        self.state    = state
        self.apiorder = apiorder

    @property
    def price(self):
        return self.apiorder.price

    @property
    def amount(self):
        return self.apiorder.amount

    @property
    def is_open(self):
        return self.apiorder.status <= self.STATUS_PARTIAL

    @property
    def is_done(self):
        return self.apiorder.status >= self.STATUS_DONE

    @is_done.setter
    def is_done(self, is_done):
        if is_done:
            self.apiorder.status = self.STATUS_DONE
            self.state.order_done(self)
        else:
            raise Exception()

    @property
    def is_processed(self):
        return self.apiorder.status >= self.STATUS_PROCESSED

    @is_processed.setter
    def is_processed(self, is_processed):
        if is_processed:
            self.apiorder.status = self.STATUS_PROCESSED
            self.state.order_processed(self)
        else:
            raise Exception()

    @property
    def is_reset(self):
        return self.apiorder.status >= self.STATUS_RESET

    @is_reset.setter
    def is_reset(self, is_reset):
        if is_reset:
            self.apiorder.status = self.STATUS_RESET
            self.state.order_reset(self)
        else:
            raise Exception()

    def reset(self):
        self.is_reset = True

    def __repr__(self):
        return str(self.apiorder)

    def __nonzero__(self):
        return not self.is_reset


class BuyOrder(Order):
    pass


class SellOrder(Order):
    pass


class APIOrder(object):
    def __init__(self, id, time, type, price, amount, pending):
        self.id = id
        self.time = time
        self.type = type
        self.price = price
        self.amount = amount
        self.pending = pending
        self.status = 0

    def __repr__(self):
        return str(dict(id = self.id, type = self.type, price = self.price, amount = self.amount, pending = self.pending, status = self.status))

