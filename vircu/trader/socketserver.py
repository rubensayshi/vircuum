from flask import request, Response
from socketio.namespace import BaseNamespace
from socketio import socketio_manage


def setup_socketio(app, state):
    class TraderNamespace(BaseNamespace):
        def on_init(self):
            for order in state.buy_orders:
                self.emit("order", order.as_json())
            for order in state.sell_orders:
                self.emit("order", order.as_json())

        def recv_message(self, message):
            print "PING!!!", message

    @app.route("/socket.io/<path:path>")
    def run_socketio(path):
        socketio_manage(request.environ, {'/trader': TraderNamespace})
        return Response()

