from flask import request, Response
from socketio.namespace import BaseNamespace
from socketio import socketio_manage


class TraderNamespace(BaseNamespace):
    def on_init(self):
        pass

    def recv_message(self, message):
        print "PING!!!", message


def setup_socketio(app):
    @app.route("/socket.io/<path:path>")
    def run_socketio(path):
        socketio_manage(request.environ, {'/trader': TraderNamespace})
        return Response()

