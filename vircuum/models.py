from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.mysql import DOUBLE, BIGINT


Base = declarative_base()


class DBBank(Base):
    __tablename__ = 'bank'

    id = Column(Integer, primary_key = True)
    type = Column(String(20))

    balance = relationship("DBBalance")

    def __init__(self, type):
        self.type = type


class DBBalance(Base):
    __tablename__ = 'balance'

    id = Column(Integer, primary_key = True)
    bank_id = Column(Integer, ForeignKey('bank.id'))
    currency = Column(String(20))
    amount = Column(DOUBLE)

    def __init__(self, currency, amount):
        self.currency = str(currency)
        self.amount = amount


class DBPrice(Base):
    __tablename__ = 'price'

    id = Column(Integer, primary_key = True)
    timestamp = Column(Integer)
    price = Column(DOUBLE)

    def __init__(self, timestamp, price):
        self.timestamp = timestamp
        self.price = price


class DBOrder(object):
    id = Column(Integer, primary_key = True)
    foreign_id = Column(BIGINT)
    amount = Column(DOUBLE)
    price  = Column(DOUBLE)
    timestamp = Column(Integer)
    pending = Column(DOUBLE)
    status = Column(Integer)


class DBSellOrder(Base, DBOrder):
    __tablename__ = 'sell_order'


class DBBuyOrder(Base, DBOrder):
    __tablename__ = 'buy_order'


class DBLogMessage(Base):
    __tablename__ = 'log_message'

    id = Column(Integer, primary_key = True)
    timestamp = Column(Integer)
    status = Column(String(20))
    msg = Column(Text)

    def __init__(self, msg, timestamp, status = 'log'):
        self.msg = msg
        self.timestamp = timestamp
        self.status = status

