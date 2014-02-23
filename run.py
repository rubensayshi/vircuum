#! /usr/bin/env python
import sys, os
import argparse
import sqlalchemy
import gevent

from gevent import monkey; monkey.patch_all()

from vircu.trader.currency import BTC, GHS, BTCv, GHSv, GHSp, BTCp 
from vircu.trader.plan import MasterPlan, Plan, UpTrend, Buy, Sell
from vircu.trader.trader import Trader
from vircu.trader.tester import Tester

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

args = parser.parse_args()

try:
    from config import config
except:
    raise Exception("You need to copy `config.example.py` to `config.py` and fill in your data")

extra = {}

if args.exchange == 'cexio':
    from vircu.tradeapi.cexio import TradeAPI
    tradeapi = TradeAPI(api_key=config.get('CEXIO_API_KEY'),
                        api_secret=config.get('CEXIO_API_SECRET'),
                        username=config.get('CEXIO_USERNAME'),
                        noncenum=args.noncenum,
                        noncemod=args.noncemod,
                        debug=args.debug)

elif args.exchange == 'bitstamp':
    from vircu.tradeapi.bitstamp import TradeAPI
    tradeapi = TradeAPI(api_key=config.get('BITSTAMP_API_KEY'),
                        api_secret=config.get('BITSTAMP_API_SECRET'),
                        clientid=config.get('BITSTAMP_CLIENTID'),
                        noncenum=args.noncenum,
                        noncemod=args.noncemod,
                        debug=args.debug)

elif args.exchange == 'dummy':
    from vircu.tradeapi.dummy import TradeAPI
    tradeapi = TradeAPI(noncenum=args.noncenum,
                        noncemod=args.noncemod)

else:
    raise Exception("Unknown exchange [%s]" % args.exchange)


masterplan = MasterPlan(assigned_balance = [BTCv(args.use_balance), GHSv(0)])

uptrendplan = masterplan.add_child(Plan())
uptrendplan.add_condition(UpTrend())

for i in range(1, args.steps + 1):
    action   = Buy(GHS, BTC, args.threshold * i)
    reaction = action.reaction = Sell(BTC, GHS, args.threshold)

    uptrendplan.add_child(action)


from vircu_app import app
from socketio import socketio_manage
from socketio.namespace import BaseNamespace
from socketio.mixins import BroadcastMixin
from flask import request, Response
from vircu.trader.state import SocketState


class TraderNamespace(BaseNamespace, BroadcastMixin):
    def on_init(self):
        self.broadcast_event('msg', 'TEST')

    def recv_message(self, message):
        print "PING!!!", message


@app.route("/socket.io/<path:path>")
def run_socketio(path):
    socketio_manage(request.environ, {'/trader': TraderNamespace})
    return Response()


from socketio.server import SocketIOServer
server = SocketIOServer(('0.0.0.0', 5000), app, resource="socket.io")
state  = SocketState(server)

# trader
cls = Trader if not args.test else Tester
trader = cls(tradeapi = tradeapi,
             masterplan = masterplan,
             autoconfirm = args.autoconfirm,
             autostart = args.autostart,
             retries = args.retries,
             state = state,
             **extra)


gevent.spawn(server.serve_forever)
gevent.spawn(trader.run)

while True:
    gevent.sleep(1)

