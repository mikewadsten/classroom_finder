#!/usr/bin/env python
'''
project: classroom_finder
file: classroom_scraper.py
purpose: this script will generate a database of classrooms and their given information to use later
'''
import os
import sqlite3
from bs4 import BeautifulSoup
import datetime
today = datetime.date.today()

conn = sqlite3.connect('database.db')
db = conn.cursor()

def create_classroomstable():
    try:
        db.execute('''DROP TABLE classrooms''')
    except:
        pass
    db.execute('''CREATE TABLE classrooms
                (roomid INT, roomname STRING, capacity INT)''')

def init(source):
    ''' gather html data and generate the classroom database from it
        @param source - string of URL or FILE to grab data from
    '''
    parser = "html.parser"

    if source.endswith('.html'):
        _file = True
    if _file:
        soup = BeautifulSoup(open(source), parser)
    else:
        soup = BeautifulSoup(source)

    content = soup.find('div', {'id': 'ContentBox'})

if __name__ == '__main__':
    print "This script will generate a table in the db of classrooms from the classroom website (not the webviewer) with all the goodies (markerboard? capacity?)"
    print "tippy tip tippenein"
    #create_classroomstable()
    roomid = "3"; roomname = "BallLicker Hall Room 23"; capacity = "60";
    query = "INSERT INTO classrooms VALUES ({},\"{}\",{})".format(roomid, roomname, capacity)
    db.execute(query)
    print query