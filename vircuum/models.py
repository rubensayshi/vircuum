from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, Text, Boolean


Base = declarative_base()


class Status(Base):
    __tablename__ = 'status'
    id = Column(Integer, primary_key = True)
    balance = Column(Float)
    real_balance = Column(Float)
    start_balance = Column(Float)
    max_balance = Column(Float)


class Order(object):
    id = Column(Integer, primary_key = True)
    amount = Column(Float)
    price  = Column(Float)
    timestamp = Column(Float)
    done = Column(Boolean)


class SellOrder(Base, Order):
    __tablename__ = 'sell_order'


class BuyOrder(Base, Order):
    __tablename__ = 'buy_order'


class LogMessage(Base):
    __tablename__ = 'log_message'
    id = Column(Integer, primary_key = True)
    status = Column(String)
    msg = Column(Text)


