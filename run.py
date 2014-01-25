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
parser.add_argument("-v", "--debug", dest="debug", action="store_true", default=False, required=False, help="tradeapi debug mode")

args = parser.parse_args()

extra = {}

if args.exchange == 'cexio':
    from vircuum.tradeapi.cexio import TradeAPI
    tradeapi = TradeAPI(api_key="5kqjg6GJ8Omzby4LUbZXBsmOb68",
                        api_secret="QHec1J1fbWjlfaP6i4GB9ZiUs",
                        username="rubensayshi2",
                        debug=args.debug)

elif args.exchange == 'btce':
    from vircuum.tradeapi.btce import TradeAPI
    tradeapi = TradeAPI(api_key="Z8XZA0DU-MY93LBM6-VK3USQMY-FQ1HAPG8-UD2Z02T8",
                        api_secret="6fadd680afbe3c607571ae0385fd8be446d5bbff05d066aa40ebd1019acbaf61",
                        debug=args.debug)
    extra.update(dict(balance = 100))

elif args.exchange == 'dummy':
    from vircuum.tradeapi.dummy import TradeAPI
    tradeapi = TradeAPI()

else:
    raise Exception("Unknown exchange [%s]" % args.exchange)

# trader
trader = Trader(tradeapi = tradeapi, threshold = args.threshold, use_balance = args.use_balance, steps = args.steps, autoconfirm = args.autoconfirm, **extra)

trader.run()