from vircuum.models import DBBuyOrder, DBSellOrder


class Order(object):
    STATUS_OPEN      = 0
    STATUS_PARTIAL   = 1
    STATUS_DONE      = 2
    STATUS_PROCESSED = 3
    STATUS_RESET     = 99

    def __init__(self, trader, apiorder = None, dborder = None):
        self.trader   = trader
        self.dborder  = dborder
        self.apiorder = apiorder

        assert self.dborder or self.apiorder

        if not self.dborder:
            self.dborder = self.dborder_from_apiorder(self.apiorder)
            self.updatedb()
        if not self.apiorder:
            raise NotImplementedError()

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
            self.dborder.status  = self.STATUS_DONE
            self.apiorder.status = self.STATUS_DONE
            self.updatedb()
        else:
            raise Exception()

    @property
    def is_processed(self):
        return self.apiorder.status >= self.STATUS_PROCESSED

    @is_processed.setter
    def is_processed(self, is_processed):
        if is_processed:
            self.dborder.status  = self.STATUS_PROCESSED
            self.apiorder.status = self.STATUS_PROCESSED
            self.updatedb()
        else:
            raise Exception()

    @property
    def is_reset(self):
        return self.apiorder.status >= self.STATUS_RESET

    @is_reset.setter
    def is_reset(self, is_reset):
        if is_reset:
            self.dborder.status  = self.STATUS_RESET
            self.apiorder.status = self.STATUS_RESET
            self.updatedb()
        else:
            raise Exception()

    def reset(self):
        self.is_reset = True

    def updatedb(self):
        self.trader.session.add(self.dborder)

    def __repr__(self):
        return str(self.apiorder)

    def __nonzero__(self):
        return not self.is_reset

    @classmethod
    def dborder_from_apiorder(cls, apiorder):
        dborder = cls.DBCLASS()
        dborder.foreign_id = apiorder.id
        dborder.timestamp  = apiorder.time
        dborder.price      = apiorder.price
        dborder.amount     = apiorder.amount
        dborder.pending    = apiorder.pending
        dborder.status     = cls.STATUS_OPEN

        return dborder


class BuyOrder(Order):
    DBCLASS = DBBuyOrder


class SellOrder(Order):
    DBCLASS = DBSellOrder


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

