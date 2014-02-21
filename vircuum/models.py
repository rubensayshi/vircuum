from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, Boolean
from sqlalchemy.dialects.mysql import DOUBLE, INTEGER
Base = declarative_base()


class DBOrder(object):
    id = Column(Integer, primary_key = True)
    foreign_id = Column(INTEGER(20))
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
    status = Column(String(20))
    msg = Column(Text)

