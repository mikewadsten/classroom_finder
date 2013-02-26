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

def room_url(sid):
    return "http://wvprd.ocm.umn.edu/gpcwv/wv3_servlet/urd/run/" \
        + "wv_space.Detail?RoomID={0}".format(sid)

def json_spaceinfo(db, args):
    spaceID = args.get('spaceID', [0])[0]
    query = '''
        SELECT roomname, capacity, seat_type, chalk, marker, spaceID
        FROM classrooms WHERE spaceID='{0}' '''.format(spaceID)
    try:
        results = query_db(db, query)
        info = results[0]
    except IndexError:
        info = results
    info["room_url"] = room_url(spaceID)
    print json.dumps(info)

print "Content-Type: application/json\n"
try:
    db = sqlite3.connect(DATABASE)
except Exception, e:
    print json.dumps({"error": repr(e)})
    sys.exit(1)

args = cgi.parse()  # query string parsed
#import time
#time.sleep(6)
json_spaceinfo(db, args)

