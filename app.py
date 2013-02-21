#!/usr/bin/env python
from flask import Flask, request, render_template, g, send_from_directory
                #url_for, redirect
from datetime import datetime, timedelta
import sqlite3
import os

from lib.utils import int_to_month

# configuration -> app.config['DATABASE'] => 'database.db'
DEBUG=(True if os.environ.get('DEBUG') in ['1', 'True'] else False)
PORT=int(os.environ.get('PORT', 5000))
DATABASE = 'database.db'
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# initialize the app
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('APP_SETTINGS', silent=True)

# Database
def connect_db():
    return sqlite3.connect(DATABASE)

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()

def get_connection():
    db = getattr(g, '_db', None)
    if db is None:
        db = g._db = connect_db()
    return db

def query_db(query, args=(), one=False):
    cur = g.db.execute(query, args)
    rv = [dict((cur.description[idx][0], value)
               for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv

# jinja datetime methods
def readabledate(time):
    t = datetime.strptime(time, TIME_FORMAT)
    return "{} on {} {}, {}".format(
            hmtime(time), int_to_month(t.month), t.day, t.year)

def hmtime(time):
    ''' returns HH:MM time '''
    t = datetime.strptime(time, TIME_FORMAT)
    return '%d:%02d'%(t.hour, t.minute)

def mins_to_hrs(minutes):
    h, m = divmod(minutes, 60)
    return '{}h {}m'.format(h,m)

def room_url(sid):
    ''' this is for the individual room page.'''
    return "http://wvprd.ocm.umn.edu/gpcwv/wv3_servlet/urd/run/" \
        + "wv_space.Detail?RoomID={}".format(sid)

#routes
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')

@app.route('/', methods=['GET'])
def index():
    now = datetime.strftime(datetime.now(), TIME_FORMAT)
    try:
        campus = request.args['campus']
    except KeyError:
        campus = 'east'

    query = '''
            SELECT roomname, start, end, length, {0}.spaceID FROM {0}
            JOIN classrooms on (classrooms.spaceID={0}.spaceID)
            WHERE end > '{1}' AND length > 30
            ORDER BY start ASC
            '''.format(campus,now)
    gaps = query_db(query)

    # Update the displayed gap length to be (gap.end - now)
    return render_template('index.html', now=now, gaps=gaps)

@app.route('/now', methods=['GET'])
def available_now():
    now = datetime.strftime(datetime.now(), TIME_FORMAT)
    try:
        campus = request.args['campus']
    except KeyError:
        campus = 'east'

    query = '''
            SELECT roomname, start, end, length, {0}.spaceID FROM {0}
            JOIN classrooms on (classrooms.spaceID={0}.spaceID)
            WHERE end > '{1}' AND start < '{1}' AND length > 30
            '''.format(campus, now)
    gaps = query_db(query)

    # Update the displayed gap length to be (gap.end - now)
    for gap in gaps:
        end = datetime.strptime(gap['end'], TIME_FORMAT)
        avail_length = end - datetime.now()
        gap['length'] = avail_length.seconds/60
    gaps.sort(reverse=True)
    return render_template('index.html', now=now, gaps=gaps)

@app.route('/search.json', methods=['GET'])
def search_json():
    # delta: for debugging, introduce an added timedelta to 'now'
    delta = timedelta(hours=0)
    now = datetime.strftime(datetime.now() + delta, TIME_FORMAT)
    args = request.args.to_dict(flat=True)
    campus = args.get('campus', None)
    if not campus:  # None, or empty string...
        campus = "east"

    search_terms = args.get('search', None)
    if not search_terms:  # None, or empty string...
        search_terms = "ORDER BY start ASC"
    else:
        search_terms = "AND roomname LIKE '%{0}%'".format(search_terms)

    query = '''
        SELECT roomname,start,end,length,{0}.spaceID FROM {0}
        JOIN classrooms ON (classrooms.spaceID={0}.spaceID)
        WHERE end > '{1}' AND length > 30
         {2}'''.format(campus, now, search_terms)
    result = query_db(query)
    return render_template('json_results.html', now=now, gaps=result)

@app.route('/search', methods=['GET'])
def search():
    now = datetime.strftime(datetime.now(), TIME_FORMAT)
    args = request.args
    campus = args.get('campus', None)
    if not campus:  # None, or empty string...
        campus = "east"
    search_terms = args.get('search', None)
    if not search_terms:  # None, or empty string...
        search_terms = "ORDER BY start ASC"
    else:
        search_terms = "AND roomname LIKE '%{0}%'".format(search_terms)

    query = '''
        SELECT roomname,start,end,length,{0}.spaceID FROM {0}
        JOIN classrooms ON (classrooms.spaceID={0}.spaceID)
        WHERE end > '{1}' AND length > 30
         {2}'''.format(campus, now, search_terms)
    result = query_db(query)
    return render_template('results.html', now=now, gaps=result)

@app.route('/spaceinfo.json', methods=['GET'])
def json_space_info():
    spaceID = request.args.get('spaceID', 0)
    query = '''
        SELECT roomname, capacity, seat_type, chalk, marker, spaceID
        FROM classrooms WHERE spaceID='{}' '''.format(spaceID)
    try:
        results = query_db(query)
        info = results[0]
    except IndexError:
        info = results
    return render_template('json_classroom_info.html', info=info)

@app.route('/spaceinfo', methods=['GET'])
def space_info():
    spaceID = request.args['spaceID']
    query = '''
        SELECT roomname, capacity, seat_type, chalk, marker, spaceID
        FROM classrooms WHERE classrooms.spaceID='{}' '''.format(spaceID)
    try:
        results = query_db(query)
        info = results[0]
    except IndexError:
        info = results
    return render_template('classroom_info.html', info=info)


app.jinja_env.filters['hmtime'] = hmtime
app.jinja_env.filters['room_url'] = room_url
app.jinja_env.filters['readabledate'] = readabledate
app.jinja_env.filters['m_to_h'] = mins_to_hrs

if __name__ == '__main__':
    app.run(port=app.config['PORT'])

