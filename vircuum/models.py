from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, Text, Boolean


Base = declarative_base()


class DBOrder(object):
    id = Column(Integer, primary_key = True)
    foreign_id = Column(Integer)
    amount = Column(Float)
    price  = Column(Float)
    timestamp = Column(Float)
    pending = Column(Float)
    status = Column(Integer)


class DBSellOrder(Base, DBOrder):
    __tablename__ = 'sell_order'


class DBBuyOrder(Base, DBOrder):
    __tablename__ = 'buy_order'


class DBLogMessage(Base):
    __tablename__ = 'log_message'
    id = Column(Integer, primary_key = True)
    status = Column(String)
    msg = Column(Text)

