#! /usr/bin/env python
import sys, os
import argparse
import sqlalchemy
from vircuum.models import Base

parser = argparse.ArgumentParser()
parser.add_argument("--reset", dest="reset", action='store_true', default=False, help="reset current data")

args = parser.parse_args()

try:
    from config import config
except:
    raise Exception("You need to copy `config.example.py` to `config.py` and fill in your data")

engine = sqlalchemy.create_engine(config['MYSQL_CONNECT'], echo=False)

if args.reset:
    for tbl in reversed(Base.metadata.sorted_tables):
        if tbl.exists(engine):
            tbl.drop(engine)

Base.metadata.create_all(engine)

