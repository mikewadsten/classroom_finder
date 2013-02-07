#!/usr/bin/env python
'''
project: classroom_finder
file: classroom_scraper.py
'''
from bs4 import BeautifulSoup
import sqlite3
import datetime
import urllib2
import os
import re

today = datetime.date.today()
url = "http://www.classroom.umn.edu/roomsearch/results.php?building=&room_number="\
        "&seating_capacity=&seat_type=&campus=&pagesize=9999&Submit1=Search"


conn = sqlite3.connect('database.db')
db = conn.cursor()

def init_db():
    db.execute('''DROP TABLE IF EXISTS classrooms''')
    db.execute('''CREATE TABLE classrooms (spaceID INT, roomname STRING, capacity INT)''')

def insert_classroom(spaceID,name,capacity):
    query = "INSERT INTO classrooms VALUES ({},\"{}\",{})".format(
            spaceID, name, capacity)
    db.execute(query)

def init():
    ''' gather html data and generate the classroom database from it
        @param source - string of URL or FILE to grab data from
    '''
    parser = "html.parser"
    if os.environ.get("SCRAPER_ENV") == 'production':
        #TODO url for data source
        usock = urllib2.urlopen(url)
        source = usock.read()
        usock.close()
        soup = BeautifulSoup(source)
    else:
        soup = BeautifulSoup(open("classroom_dump.html"), parser)

    rows = soup.table.tbody.findAll('tr')
    # dirty hack, we seem to get a duplicate final row
    # I'm so sorry for this.
    for row in rows[:-1]:
        #for column in row:
            #print "~~~~~~~~~~~~~~~COLUMN INFO~~~~~~~~~~~~~~~"
            #print column
        print "~~~~~~~~~~~~~~~ROW~~~~~~~~~~~~~~~~~~~~~`"
        classroom_search = row.find('a', {'class', 'roomInfo'})
        if classroom_search:
            classroom_name = classroom_search.get_text()
        url_search = row.find('a', {'class', 'roomInfo'})
        if url_search:
            classroom_id = re.search('(?<=RoomID=)\w+', url_search.get('href')).group(0)
        print classroom_name
        print classroom_id

def construct_url(sid):
    ''' this is the individual room page. We may or may not need it'''
    return "http://wvprd.ocm.umn.edu/gpcwv/wv3_servlet/urd/run/" \
        + "wv_space.Detail?RoomID={}".format(sid)

if __name__ == '__main__':
    init()
