from datetime import datetime
from vircu.dt import dt_to_utc_timestamp

class TraderState(object):

    def reinit(self):
        raise NotImplementedError()

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


class InMemoryState(TraderState):

    def __init__(self):
        self.buy_orders = []
        self.sell_orders = []
        self.log_messages = []

    def reinit(self):
        return self

    def assigned_balance(self, assigned_balance):
        print "assigned_balance", assigned_balance
        return self

    def log_message(self, msg, status = None, dt = None):
        dt = dt or datetime.now()
        status = status or 'log'

        print msg, status, dt
        self.log_messages.append((msg, status, dt))
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
        if order.type == 'buy':
            return self.buy_orders
        elif order.type == 'sell':
            return self.sell_orders


class SocketState(InMemoryState):

    def __init__(self, server):
        super(SocketState, self).__init__()
        self.server = server

    def reinit(self):
        print "reinit", self.broadcast_event("reinit")
        return super(SocketState, self).reinit()

    def assigned_balance(self, assigned_balance):
        self.log_message("order reset %s" % str(assigned_balance), 'balance')
        return super(SocketState, self).assigned_balance(assigned_balance)

    def log_message(self, msg, status = None, dt = None):
        dt = dt or datetime.now()
        status = status or 'log'

        self.broadcast_event("msg", msg, status, dt_to_utc_timestamp(datetime.now()))
        return super(SocketState, self).log_message(msg, status)

    def tick(self, price, dt):
        self.broadcast_event("tick", {'value' : str(price), 'symbol' : price.symbol}, dt_to_utc_timestamp(datetime.now()))
        return super(SocketState, self).tick(price, dt)

    def add_order(self, order):
        self.broadcast_event("order", order.as_json())
        return super(SocketState, self).add_order(order)

    def order_done(self, order):
        self.broadcast_event("order", order.as_json())
        self.log_message("order done %s" % order)
        return super(SocketState, self).order_done(order)

    def order_processed(self, order):
        self.broadcast_event("order", order.as_json())
        self.log_message("order processed %s" % order)
        return super(SocketState, self).order_processed(order)

    def order_reset(self, order):
        self.broadcast_event("order", order.as_json())
        self.log_message("order reset %s" % order)
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


class Order(object):
    STATUS_OPEN      = 0
    STATUS_PARTIAL   = 1
    STATUS_DONE      = 2
    STATUS_PROCESSED = 3
    STATUS_RESET     = 99

    type = ''

    def __init__(self, apiorder, state):
        self.state    = state
        self.apiorder = apiorder

    @property
    def id(self):
        return self.apiorder.id

    @property
    def price(self):
        return self.apiorder.price

    @property
    def amount(self):
        return self.apiorder.amount

    @property
    def time(self):
        return self.apiorder.time

    @time.setter
    def time(self, value):
        self.apiorder.time = value

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

    def as_json(self):
        data = self.apiorder.as_dict()

        data['price']   = {'value' : str(data['price']),   'symbol' : data['price'].symbol}
        data['amount']  = {'value' : str(data['amount']),  'symbol' : data['amount'].symbol}
        data['pending'] = {'value' : str(data['pending']), 'symbol' : data['pending'].symbol}

        return data

    def __repr__(self):
        return str(self.apiorder)

    def __nonzero__(self):
        return not self.is_reset


class BuyOrder(Order):
    type = 'buy'


class SellOrder(Order):
    type = 'sell'


class APIOrder(object):
    def __init__(self, id, time, type, price, amount, pending):
        self.id = id
        self.time = time
        self.type = type
        self.price = price
        self.amount = amount
        self.pending = pending
        self.status = 0

    def as_dict(self):
        return dict(id = self.id,
                    time = self.time,
                    type = self.type,
                    price = self.price,
                    amount = self.amount,
                    pending = self.pending,
                    status = self.status)

    def __repr__(self):
        return str(self.as_dict())