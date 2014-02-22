import signal, gevent
from functools import wraps
from flask.ext.script import Command, Option, Manager
from vircu.cron import CronTab, Event
from vircu.app import app


manager = Manager()


class Cron(Command):
    """
    """

    def __init__(self):
        self.cron = CronTab()

    def with_app_context(self, fn):
        @wraps(fn)
        def _fn(*args, **kwargs):
            with app.app_context():
                with app.cli_request_context():
                    return fn(*args, **kwargs)

        return _fn

    def onexit(self, *args, **kwargs):
        if self.cron.stop():
            import sys
            sys.exit(0)

    def run(self):
        gevent.signal(signal.SIGTERM, self.onexit)
        gevent.signal(signal.SIGINT, self.onexit)
 
        try:
            self.cron.start()
        except KeyboardInterrupt:
            self.cron.stop()


manager = Cron()
