# -*- coding: utf-8 -*-
"""
Accepts a server log file and adds two columns - session and visit

'session' is the session id
For the same ip and user agent, we assume the same session for some time
If the time between two visits exceeds 30 minutes we assume a new session

'visit' is the number of visit within the session. 
The first visit within the session will be 1.
The second visit will be 2 and so on
"""

import pandas as pd
from datetime import datetime, timedelta
import pytz

INPUT_FILE = 'in.txt'
OUTPUT_FILE = 'out.txt'
MAX_DURATION_MINUTES = 30

def parse_str(x):
    """
    Returns the string delimited by two characters.

    Example:
        `>>> parse_str('[my string]')`
        `'my string'`
    """
    try:
        return x[1:-1]
    except:
        return ''

def parse_datetime(x):
    '''
    Parses datetime with timezone formatted as:
        `[day/month/year:hour:minute:second zone]`

    Example:
        `>>> parse_datetime('13/Nov/2015:11:45:42 +0000')`
        `datetime.datetime(2015, 11, 3, 11, 45, 4, tzinfo=<UTC>)`

    Due to problems parsing the timezone (`%z`) with `datetime.strptime`, the 
    timezone will be obtained using the `pytz` library.
    '''    
    try:
        dt = datetime.strptime(x[1:-7], '%d/%b/%Y:%H:%M:%S')
        dt_tz = int(x[-6:-3])*60+int(x[-3:-1])    
        return dt.replace(tzinfo=pytz.FixedOffset(dt_tz))
    except:
        return datetime(1, 1, 1, 0, 0, 0, tzinfo=pytz.utc)

def parse_int(x):
    try:
        return int(x)
    except:
        return 0


df = pd.read_csv(
    INPUT_FILE, 
    sep=r'\s(?=(?:[^"]*"[^"]*")*[^"]*$)(?![^\[]*\])', 
    engine='python', 
    na_values='-', 
    header=None,
    error_bad_lines=False,
    usecols=[0, 3, 4, 5, 6, 7, 8],
    names=['ip', 'time', 'request', 'status', 'size', 'referer', 'user_agent'],
    converters={'time': parse_datetime,
                'request': parse_str,
                'status': parse_int,
                'size': parse_int,
                'referer': parse_str,
                'user_agent': parse_str})

df = df.sort_values(['ip', 'user_agent', 'time'])
df['session'] = (
        (df.ip != df.ip.shift()) | 
        (df.user_agent != df.user_agent.shift()) | 
        (((df.time - df.time.shift())/timedelta(minutes=1)) > MAX_DURATION_MINUTES)
        ).astype(int).cumsum()
df['visit'] = df.groupby('session')['session'].transform(lambda x: range(1, len(x) + 1))

df = df.sort_index()
df.to_csv(OUTPUT_FILE, index=False)