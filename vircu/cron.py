from datetime import datetime, timedelta
import time
import gevent


# Some utility classes / functions first
def conv_to_set(obj):
    """Converts to set allowing single integer to be provided"""
    if isinstance(obj, basestring):
        if obj == '*':
            obj = allMatch
        else:
            obj = float(obj)

    if isinstance(obj, (int, long, float)):
        return set([obj])  # Single item
    if not isinstance(obj, set):
        obj = set(obj)
    return obj


class AllMatch(set):
    """Universal set - match everything"""
    def __contains__(self, item): 
        return True


allMatch = AllMatch()


class Event(object):
    """The Actual Event Class"""

    def __init__(self, action, 
                       minute=allMatch, hour=allMatch, 
                       day=allMatch, month=allMatch, daysofweek=allMatch, 
                       args=(), kwargs={},
                       debug=None):
        self.mins = conv_to_set(minute)
        self.hours = conv_to_set(hour)
        self.days = conv_to_set(day)
        self.months = conv_to_set(month)
        self.daysofweek = conv_to_set(daysofweek)
        self.action = action
        self.args = args
        self.kwargs = kwargs
        self.debug = CronTab.DEBUG if debug is None else debug

    def matchtime(self, t1):
        """Return True if this event should trigger at the specified datetime"""
        return ((t1.minute     in self.mins) and
                (t1.hour       in self.hours) and
                (t1.day        in self.days) and
                (t1.month      in self.months) and
                (t1.weekday()  in self.daysofweek))

    def check(self, t):
        """Check and run action if needed"""

        if self.matchtime(t):
            if self.debug: print "[%s] running [%s]" % (t, self.action.__name__)
            self.action(*self.args, **self.kwargs)
            if self.debug: print "[%s] done [%s]" % (t, self.action.__name__)


class CronTab(object):
    """The crontab implementation"""

    DEBUG = True

    def __init__(self, *events, **kwargs):
        debug = kwargs.get('debug', None)

        self.events = events

        self.job       = None
        self.greenlets = []
        self.run       = 1

        self.debug = CronTab.DEBUG if debug is None else debug

    def done(self):
        return len(self.greenlets) == 0

    def _check(self):
        """Check all events in separate greenlets"""

        if not self.run:
            return

        # now rounded to minute
        now = datetime.now()
        t1 =  datetime(*now.timetuple()[:5])

        # spawn a greenlet for each event to check and run
        for event in self.events:
            self.greenlets.append(gevent.spawn(event.check, t1))

        # prepare next run (next minute)
        t2 = t1 + timedelta(minutes=1)
        s1 = (t2 - datetime.now()).seconds + 1
        if self.debug: print "[%s] Checking again in %s seconds on [%s]" % (t1, s1, t2)
        self.job = gevent.spawn_later(s1, self._check)

        # cleanup greenlets that are done
        for greenlet in self.greenlets:
            if greenlet.ready():
                self.greenlets.remove(greenlet)

    def start(self):
        """Run the cron forever"""

        # start checking
        self._check()

        # loop forever until stopped
        while self.run:
            gevent.sleep(60)

    def pause(self):
        self.run = 0

    def stop(self):
        # prevent new events
        self.pause() 

        # let the main task finish properly
        if not self.job.ready():
            self.job.start()

        # wait for any remaining tasks
        gevent.joinall(self.greenlets)

        return True
