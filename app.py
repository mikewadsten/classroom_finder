from flask import Flask, request, url_for, redirect, \
             render_template, g
from datetime import datetime
import sqlite3
from lib.utils import int_to_month

app = Flask(__name__)
DATABASE = 'database.db'

# jinja datetime methods
def readabledate(time):
    t = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
    return "{} on {} {}, {}".format(
            hmtime(time), int_to_month(t.month), t.day, t.year)

def hmtime(time):
    ''' returns HH:MM time '''
    t = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
    return '%d:%02d'%(t.hour, t.minute)

def mins_to_hrs(minutes):
    h, m = divmod(minutes, 60)
    return '{}h {}m'.format(h,m)

def room_url(sid):
    ''' this is the individual room page. We may or may not need it'''
    return "http://wvprd.ocm.umn.edu/gpcwv/wv3_servlet/urd/run/" \
        + "wv_space.Detail?RoomID={}".format(sid)

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

#routes

@app.route('/', methods=['POST', 'GET'])
def index(gaps=None):
    now = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
    # possibly just pass the search results to index() and rerender
    if gaps:
        pass
    else:
        query = '''
                SELECT roomname, start, end, length, gaps.spaceID FROM gaps
                JOIN classrooms on (classrooms.spaceID=gaps.spaceID)
                WHERE end > '{}' AND start < '{}' AND length > 30
                '''.format(now, now)
        gaps = query_db(query)

    # Update the displayed gap length to be (gap.end - now)
    for gap in gaps:
        end = datetime.strptime(gap['end'], "%Y-%m-%d %H:%M:%S")
        avail_length = end - datetime.now()
        gap['length'] = avail_length.seconds/60
    gaps.sort(reverse=True)
    return render_template('index.html', now=now, gaps=gaps)

@app.route('/search', methods=['POST', 'GET'])
def search():
    now = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
    if request.form['building'] != '':
        query = '''
            SELECT roomname,start,end,length FROM gaps
            JOIN classrooms on (classrooms.spaceID=gaps.spaceID)
            WHERE end > '{}' AND start < '{}' AND length > 30 
            AND roomname LIKE '%{}%' '''.format(now, now, request.form['building'])
    return render_template('index.html', now=now, gaps=query_db(query))


@app.route('/spaceinfo', methods=['POST'])
def space_info():
    spaceID = request.form['spaceID']
    query = '''
        SELECT roomname,capacity,seat_type,projector,dvd,vcr,doc,chalk,marker,alc,spaceID
        FROM classrooms WHERE classrooms.spaceID='{}' '''.format(spaceID)
    try:
        info = (query_db(query))[0]
    except IndexError:
        info = query_db(query)
    return render_template('classroom_info.html', info=info)


app.jinja_env.filters['hmtime'] = hmtime
app.jinja_env.filters['room_url'] = room_url
app.jinja_env.filters['readabledate'] = readabledate
app.jinja_env.filters['m_to_h'] = mins_to_hrs

if __name__ == '__main__':
    app.debug= True
    app.run()

