from flask import request, Response
from socketio.namespace import BaseNamespace
from socketio import socketio_manage
from vircu.dt import dt_to_utc_timestamp


def setup_socketio(app, state):
    class TraderNamespace(BaseNamespace):
        def on_request_init(self):
            for order in state.buy_orders:
                self.emit("order", order.as_json())
            for order in state.sell_orders:
                self.emit("order", order.as_json())
            for msg, status, dt in state.log_messages:
                self.emit("msg", msg, status, dt_to_utc_timestamp(dt))

        def recv_message(self, message):
            print "PING!!!", message

    @app.route("/socket.io/<path:path>")
    def run_socketio(path):
        socketio_manage(request.environ, {'/trader': TraderNamespace})
        return Response()

