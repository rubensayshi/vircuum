from datetime import datetime

def get_start_of_hour(dt = None):
    """get the 'nearest' hour - always rounds down 
        so 23:59:59 becomes 23:00:00"""
    dt = dt or datetime.now()
    return dt.replace(minute = 00, second = 00, microsecond = 00)


def get_start_of_minute(dt = None):
    """get the 'nearest' hour - always rounds down 
        so 23:59:59 becomes 23:00:00"""
    dt = dt or datetime.now()
    return dt.replace(second = 00, microsecond = 00)


def get_start_of_day(dt = None):
    """get the 'start of the day' day - always rounds down to the first second of the day (00:00:00:00 pm)"""
    dt = dt or datetime.now()
    return dt.replace(hour = 00, minute = 00, second = 00, microsecond = 00)


def get_end_of_hour(dt = None):
    dt = dt or datetime.now()
    return dt.replace(minute = 59, second = 59, microsecond = 00)


def get_end_of_day(dt = None):
    return get_end_of_hour(get_start_of_day(dt))


def get_start_of_week(dt = None):
    """get the start the week - always rounds down to the first hour of the monday 
        so sunday 22 dec 23:59:59 becomes monday 17 dec 2012 00:00:00"""
    dt = dt or datetime.now()
    
    return datetime.strptime(dt.strftime("%Y %W 1 00 00 00"), "%Y %W %w %H %M %S")


def get_end_of_week(dt = None):
    """get the end of the week - always rounds up to the last hour of the sunday 
        so monday 17 dec 2012 00:00:00 becomes sunday 22 dec 23:59:59"""
    dt = dt or datetime.now()
    
    return datetime.strptime(dt.strftime("%Y %W 6 23 59 59"), "%Y %W %w %H %M %S") + timedelta(days=1)


def get_start_of_month(dt = None):
    """get the start of the month - always rounds down to the first hour of the first day
        so monday 17 dec 2012 00:01:01 becomes saturday 1 dec 00:00:00"""
    dt = dt or datetime.now()
    
    return datetime.strptime(dt.strftime("%Y-%m-1 00:00:00"), "%Y-%m-%d %H:%M:%S")


def get_end_of_month(dt = None):
    """get the end of the month - always rounds up to the last hour of the last day
        so monday 17 dec 2012 00:01:01 becomes monday 31 dec 23:59:59"""
    return get_end_of_day(get_start_of_month(get_start_of_month(dt) + timedelta(weeks = 5)) - timedelta(days = 1))


def get_last_week_of_month(dt = None):
    """get the end of the last week of the month
        so tuesday 31 okt 2013 00:01:01 becomes sunday 27 okt 23:59:59"""
    dt = get_end_of_month(dt)
    
    if get_end_of_week(dt) > dt:
        dt -= timedelta(days = 7)
    
    return get_end_of_week(dt)

