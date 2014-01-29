#! /usr/bin/env python
import sys, os
from vircuum.trader import Trader
import argparse

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

parser = argparse.ArgumentParser()
parser.add_argument("-e", "--exchange", dest="exchange", type=str, required=True, help="cexio, btce, dummy")
parser.add_argument("-t", "--threshold", dest="threshold", type=float, required=True, help="%% change required to act (0.01 = 1%%)")
parser.add_argument("-u", "--use-balance", dest="use_balance", type=float, required=False, default=None, help="PERCENTAGE amount of balance to use, (1.0 = 100%%)")
parser.add_argument("-ue", "--use-balance-exact", dest="use_balance_exact", type=float, required=False, default=None, help="EXACT amount of balance to use,")
parser.add_argument("-r", "--retries", dest="retries", type=int, required=False, default=3, help="loop retries")
parser.add_argument("-s", "--steps", dest="steps", type=float, required=True, help="split balance into amount of 'steps'")
parser.add_argument("-y", "--autoconfirm", dest="autoconfirm", action="store_true", default=False, required=False, help="no longer require confirmation to place orders")
parser.add_argument("-yy", "--autostart", dest="autostart", action="store_true", default=False, required=False, help="no longer require confirmation to start")
parser.add_argument("-v", "--debug", dest="debug", action="store_true", default=False, required=False, help="tradeapi debug mode")
parser.add_argument("-nn", "--noncenum", dest="noncenum", type=int, default=0, required=False, help="noncenum for running multiple scripts async")
parser.add_argument("-n", "--noncemod", dest="noncemod", type=int, default=1, required=False, help="noncemod for running multiple scripts async")

args = parser.parse_args()

assert args.use_balance is not None or args.use_balance_exact is not None
assert args.use_balance is None or args.use_balance_exact is None

try:
    from config import config
except:
    raise Exception("You need to copy `config.example.py` to `config.py` and fill in your data")

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

# trader
trader = Trader(tradeapi = tradeapi,
                threshold = args.threshold,
                use_balance = args.use_balance,
                use_balance_exact = args.use_balance_exact,
                steps = args.steps,
                autoconfirm = args.autoconfirm,
                autostart = args.autostart,
                retries = args.retries,
                **extra)

trader.run()
