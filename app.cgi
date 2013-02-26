#!/usr/bin/env python
import cgi
import sqlite3
import json
from sys import exit
from datetime import datetime, timedelta

DATABASE = 'database.db'
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

def query_db(db, query, args=(), one=False):
    cur = db.execute(query, args)
    rv = [dict((cur.description[idx][0], value)
            for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv

def hmtime(time):
    t = datetime.strptime(time, TIME_FORMAT)
    hour = t.hour
    minute = t.minute
    suffix = "am"
    if hour == 12 and minute == 0:
        return "noon"
    if hour > 12:
        hour = hour - 12
        suffix = "pm"
    return "%d:%02d%s" % (hour, minute, suffix)

def json_search(db, args):
    # delta: for debugging, introduce an added timedelta to 'now'
    delta = timedelta(hours=0)
    now = datetime.strftime(datetime.now() + delta, TIME_FORMAT)
    campus = args.get('campus', [None])[0]
    if not campus:
        campus = "east"

    search_terms = args.get('search', [None])[0]
    if not search_terms:  # None, or empty string...
        search_terms = "ORDER BY start ASC"
    else:
        search_terms = "AND roomname LIKE '%{0}%'".format(search_terms)

    query = '''
        SELECT gapID,roomname,start,end,length,{0}.spaceID FROM {0}
        JOIN classrooms ON (classrooms.spaceID={0}.spaceID)
        WHERE end > '{1}' AND length > 30
         {2}'''.format(campus, now, search_terms)
    result = query_db(db, query)
    if not result:
        result = []
    for d in result:
        if "start" in d:
            d["start"] = hmtime(d["start"])
        if "end" in d:
            d["end"] = hmtime(d["end"])
        try:
            rn = d.pop("roomname")
            import re
            reg = r'(?P<bldg>[\w\s,&-]+), Room (?P<room>[\d\w\s-]+)$'
            split = None
            try:
                split = re.search(reg, rn).groupdict()
            except Exception:
                pass
            if split is None:
                d["roomname"] = rn
                d["building"] = rn
                d["roomnum"] = "N/A"
            else:
                d["building"] = split["bldg"]
                d["roomname"] = split["room"]
                d["roomnum"] = split["room"]
        except Exception:
            pass
    #print json.dumps({"items": result})
    print json.dumps({"rooms": result})

print "Content-Type: application/json\n"
try:
    db = sqlite3.connect(DATABASE)
except Exception, e:
    print json.dumps({"error": repr(e)})
    sys.exit(1)

args = cgi.parse()  # query string parsed
#import time
#time.sleep(11)
json_search(db, args)
