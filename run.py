#! /usr/bin/env python
import sys, os
from vircuum.currency import BTC, GHS, BTCv, GHSv, GHSp, BTCp 
from vircuum.plan import MasterPlan, Plan, UpTrend, Buy, Sell, Action
from vircuum.trader import Trader
from vircuum.tester import Tester
import argparse
from sqlalchemy import create_engine
from vircuum.trader import Trader
from vircuum.models import Base

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

parser = argparse.ArgumentParser()
parser.add_argument("-e", "--exchange", dest="exchange", type=str, required=True, help="cexio, btce, dummy")
parser.add_argument("-t", "--threshold", dest="threshold", type=float, required=True, help="%% change required to act (0.01 = 1%%)")
parser.add_argument("-u", "--use-balance", dest="use_balance", type=float, default=None, help="EXACT amount of balance to use")
parser.add_argument("-r", "--retries", dest="retries", type=int, required=False, default=10, help="loop retries")
parser.add_argument("-s", "--steps", dest="steps", type=int, required=True, help="split balance into amount of 'steps'")
parser.add_argument("-y", "--autoconfirm", dest="autoconfirm", action="store_true", default=False, required=False, help="no longer require confirmation to place orders")
parser.add_argument("-yy", "--autostart", dest="autostart", action="store_true", default=False, required=False, help="no longer require confirmation to start")
parser.add_argument("-v", "--debug", dest="debug", action="store_true", default=False, required=False, help="tradeapi debug mode")
parser.add_argument("--test", dest="test", action="store_true", default=False, required=False, help="test actions")
parser.add_argument("-nn", "--noncenum", dest="noncenum", type=int, default=0, required=False, help="noncenum for running multiple scripts async")
parser.add_argument("-n", "--noncemod", dest="noncemod", type=int, default=1, required=False, help="noncemod for running multiple scripts async")
parser.add_argument("--sql", dest="sql", type=str, default=None, required=False, help="SQL connection to use for state")

args = parser.parse_args()

try:
    from config import config
except:
    raise Exception("You need to copy `config.example.py` to `config.py` and fill in your data")

if args.sql:
    engine = create_engine(args.sql, echo=False)
else:
    engine = create_engine('sqlite:///:memory:', echo=False)
    Base.metadata.create_all(engine)

from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)

extra = {}

if args.exchange == 'cexio':
    from vircuum.tradeapi.cexio import TradeAPI
    tradeapi = TradeAPI(api_key=config.get('CEXIO_API_KEY'),
                        api_secret=config.get('CEXIO_API_SECRET'),
                        username=config.get('CEXIO_USERNAME'),
                        noncenum=args.noncenum,
                        noncemod=args.noncemod,
                        debug=args.debug)

elif args.exchange == 'bitstamp':
    from vircuum.tradeapi.bitstamp import TradeAPI
    tradeapi = TradeAPI(api_key=config.get('BITSTAMP_API_KEY'),
                        api_secret=config.get('BITSTAMP_API_SECRET'),
                        clientid=config.get('BITSTAMP_CLIENTID'),
                        noncenum=args.noncenum,
                        noncemod=args.noncemod,
                        debug=args.debug)

elif args.exchange == 'dummy':
    from vircuum.tradeapi.dummy import TradeAPI
    tradeapi = TradeAPI(noncenum=args.noncenum,
                        noncemod=args.noncemod)

else:
    raise Exception("Unknown exchange [%s]" % args.exchange)


masterplan = MasterPlan(assigned_balance = [BTCv(args.use_balance), GHSv(0)])

uptrendplan = masterplan.add_child(Plan())
uptrendplan.add_condition(UpTrend())

for i in range(1, args.steps + 1):
    action   = Buy(GHS, BTC, args.threshold * i)
    reaction = action.reaction(Sell(BTC, GHS, args.threshold))

    uptrendplan.add_child(action)

# trader
cls = Trader if not args.test else Tester
trader = cls(tradeapi = tradeapi,
             masterplan = masterplan,
             autoconfirm = args.autoconfirm,
             autostart = args.autostart,
             retries = args.retries,
             sessionmaker = sessionmaker,
             **extra)

trader.run()
