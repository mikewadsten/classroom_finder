import sqlite3

from flask import Flask, request, g, render_template
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

def gap_populate():
    query = ('select * from gaps')
    gaps = []
    for gap in query_db(query):
        gaps.append((gap['start'],gap['end'],gap['length'],gap['room']))
    return gaps


@app.route('/')
def front_page():
    gaps = gap_populate()
    return render_template('index.html', gaps=gaps)

if __name__ == '__main__':
    app.debug= True
    app.run()
