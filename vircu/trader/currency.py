

class CurrencyClass(type):
    def __str__(self):
        return self.NAME


class Currency(object):
    __metaclass__ = CurrencyClass

    NAME = None

    @classmethod
    def round(cls, value):
        return float(value)

    def __init__(self):
        raise NotImplementedError()


class CurrencyV(object):
    CURRENCY = None
    def __init__(self, value):
        self.value = self.round(value)

    def round(self, value):
        return self.CURRENCY.round(value)

    @property
    def symbol(self):
        return self.CURRENCY.NAME

    def assert_same_currency(self, other):
        assert isinstance(other, self.__class__), "self[%s] other[%s]" % (self.__class__, other.__class__)

    def __add__(self, other):
        self.assert_same_currency(other)
        return self.CURRENCY.VALUE(float(self) + float(other))

    def __sub__(self, other):
        self.assert_same_currency(other)
        return self.CURRENCY.VALUE(float(self) - float(other))

    def __mul__(self, other):
        return self.CURRENCY.VALUE(float(self) * float(other))

    def __div__(self, other):
        return self.CURRENCY.VALUE(float(self) / float(other))

    def __eq__(self, other):
        return float(self) == float(other)

    def __ne__(self, other):
        self.assert_same_currency(other)
        return float(self) != float(other)

    def __lt__(self, other):
        self.assert_same_currency(other)
        return float(self) < float(other)

    def __gt__(self, other):
        self.assert_same_currency(other)
        return float(self) > float(other)

    def __le__(self, other):
        self.assert_same_currency(other)
        return float(self) <= float(other)

    def __ge__(self, other):
        self.assert_same_currency(other)
        return float(self) >= float(other)

    def __float__(self):
        return float(self.value)

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

