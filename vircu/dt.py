from datetime import datetime
import pytz
import time
from vircu.config import config

def dt_as_naive_utc(dt, asume_timezone = None):
    """convert `datetime` instance to a naive `datetime` instance with it's time in UTC"""
    
    if not dt.tzinfo:
        # we can either hope and asume it's in UTC
        if not asume_timezone:
            dt = pytz.utc.localize(dt)
        # or we can asume it's supposed to be a local time but just wasn't localized yet?
        else:
            dt = asume_timezone.localize(dt)
    
    # otherwise convert to UTC and make it naive
    return dt.astimezone(pytz.utc).replace(tzinfo=None)


def dt_naive_utc_as_timezone(dt, timezone):
    """localized a naive `datetime` instance with it's time in UTC to specified timezone"""
    
    return pytz.utc.localize(dt).astimezone(timezone)


def dt_server_timezone_as_naive_utc(dt):
    """convert `datetime` instance which is in our servertime to a naive `datetime` instance with it's time in UTC"""
    
    return dt_as_naive_utc(dt, asume_timezone = config['SERVER_TIMEZONE'])


def dt_as_server_timezone(dt, asume_utc = False):
    """convert `datetime` instance to a `datetime` instance in our server timezone"""
    
    if not dt.tzinfo:
        if asume_utc:
            dt = pytz.utc.localize(dt)
        else:
            return config['SERVER_TIMEZONE'].localize(dt)
        
    return dt.astimezone(config['SERVER_TIMEZONE'])


def dt_as_utc(dt, asume_utc = False):
    if not dt.tzinfo:
        if asume_utc:
            dt = pytz.utc.localize(dt)
        else:
            dt = config['SERVER_TIMEZONE'].localize(dt)
        
    return dt.astimezone(pytz.utc)


def dt_now():
    """get a `datetime` instance for NOW() in our server timezone"""
    
    return dt_as_server_timezone(datetime.now())


def dt_from_timestamp(ts):
    """get a `datetime` instance based off a timestamp (which should always be in UTC)"""
    
    dt = datetime.utcfromtimestamp(ts)
    return dt_as_server_timezone(dt, asume_utc = True)


def utc_mktime(utc_tuple):
    """Returns number of seconds elapsed since epoch

    Note that no timezone are taken into consideration.

    utc tuple must be: (year, month, day, hour, minute, second)

    """

    if len(utc_tuple) == 6:
        utc_tuple += (0, 0, 0)
    return time.mktime(utc_tuple) - time.mktime((1970, 1, 1, 0, 0, 0, 0, 0, 0))


def dt_to_utc_timestamp(dt):
    """Converts a datetime object to UTC timestamp"""
    
    # localize it as UTC first
    dt = dt_as_utc(dt)

    return int(utc_mktime(dt.timetuple()))

