from flask import Flask, request, url_for, redirect, \
             render_template, g
from datetime import datetime
import sqlite3

now = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")

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


@app.route('/')
def front_page():
    now = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
    return render_template('index.html', now=now, 
        gaps=query_db('''
            SELECT roomname,start,end,length FROM gaps 
            JOIN classrooms on (classrooms.spaceID=gaps.spaceID)
            WHERE end > '{}' AND length > 30 ORDER BY length DESC'''.format(now) )
        )

@app.route('/search', methods=['POST'])
def search():
    # This could be a redirect to front_page, however
    # not sure how to pass a new set of gaps
    if request.form['building']:
        query = ''' 
            SELECT roomname,start,end,length FROM gaps
            JOIN classrooms on (classrooms.spaceID=gaps.spaceID)
            WHERE roomname LIKE '%{}%' '''.format(request.form['building'])
    return render_template('index.html', now=now,  gaps=query_db(query))

def readabledate(time):
    pass
    #t = datetime.strptime(time, "%Y-%b-%a %H:%M:%S")
    #return "{} {}, {} - {} {}".format(t.month, t.day, t.year, t.hour, t.minute)

def hmtime(time):
    ''' returns HH:MM time '''
    hour = time.split(' ')[1][0:2]
    minute = time.split(' ')[1][3:5]
    #TODO get this to recognize format..
    #t = datetime.strptime(time, "%Y-%b-%a %H:%M:%S")
    return "{}:{}".format(hour, minute)

def mins_to_hrs(minutes):
    h, m = divmod(minutes, 60)
    return '{}h {}m'.format(h,m)

app.jinja_env.filters['hmtime'] = hmtime
app.jinja_env.filters['readabledate'] = readabledate
app.jinja_env.filters['m_to_h'] = mins_to_hrs

if __name__ == '__main__':
    app.debug= True
    app.run()

