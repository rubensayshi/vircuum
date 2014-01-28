#! /usr/bin/env python
import sys, os
from vircuum.trader import Trader
import argparse

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

parser = argparse.ArgumentParser()
parser.add_argument("-e", "--exchange", dest="exchange", type=str, required=True, help="cexio, btce, dummy")
parser.add_argument("-t", "--threshold", dest="threshold", type=float, required=True, help="%% change required to act (0.01 = 1%%)")
parser.add_argument("-u", "--use_balance", dest="use_balance", type=float, required=True, help="amount of balance to use, (1.0 = 100%%)")
parser.add_argument("-s", "--steps", dest="steps", type=float, required=True, help="split balance into amount of 'steps'")
parser.add_argument("-y", "--autoconfirm", dest="autoconfirm", action="store_true", default=False, required=False, help="no longer require confirmation to place orders")
parser.add_argument("-yy", "--autostart", dest="autostart", action="store_true", default=False, required=False, help="no longer require confirmation to start")
parser.add_argument("-v", "--debug", dest="debug", action="store_true", default=False, required=False, help="tradeapi debug mode")
parser.add_argument("-nn", "--noncenum", dest="noncenum", type=int, default=0, required=False, help="noncenum for running multiple scripts async")
parser.add_argument("-n", "--noncemod", dest="noncemod", type=int, default=1, required=False, help="noncemod for running multiple scripts async")

args = parser.parse_args()

extra = {}

if args.exchange == 'cexio':
    from vircuum.tradeapi.cexio import TradeAPI
    tradeapi = TradeAPI(api_key="5kqjg6GJ8Omzby4LUbZXBsmOb68",
                        api_secret="QHec1J1fbWjlfaP6i4GB9ZiUs",
                        username="rubensayshi2",
                        noncenum=args.noncenum,
                        noncemod=args.noncemod,
                        debug=args.debug)

elif args.exchange == 'bitstamp':
    from vircuum.tradeapi.bitstamp import TradeAPI
    tradeapi = TradeAPI(api_key="1wuC07xlHWsNQsPT2AqZneGjJY4ozGAC",
                        api_secret="P8YLoxqErAMTYeC962tvZaQj2YPAoODP",
                        clientid="838807",
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
                steps = args.steps,
                autoconfirm = args.autoconfirm,
                autostart = args.autostart,
                **extra)

trader.run()
