from flask import Flask, request, url_for, redirect, \
             render_template, g
from datetime import datetime
import sqlite3

app = Flask(__name__)
DATABASE = 'database.db'

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

def hm_time(time):
    ''' return HH:MM time'''
    hour = time.split(' ')[1][0:2]
    minute = time.split(' ')[1][3:5]
    #t = datetime.datetime.strptime(time, "%Y-%b-%a %H:%M:%S")
    return "{}:{}".format(hour, minute)

def gap_populate():
    now = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
    query = ('''SELECT roomname,start,end,length FROM gaps 
                JOIN classrooms on (classrooms.spaceID=gaps.spaceID)
                WHERE end > '{}' AND length > 30 ORDER BY length DESC'''.format(now))
    gaps = []
    for gap in query_db(query):
        gaps.append((hm_time(gap['start']),hm_time(gap['end']),gap['length'],gap['roomname']))
    return gaps

@app.route('/')
def front_page():
    gaps = gap_populate()
    return render_template('index.html', gaps=gaps)

@app.route('/search', methods=['POST'])
def search():

    return redirect(url_for('front_page'))

if __name__ == '__main__':
    app.debug= True
    app.run()
