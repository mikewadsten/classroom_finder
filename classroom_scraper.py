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
    db.execute('''CREATE TABLE classrooms
        (spaceID INT, roomname STRING, capacity INT, seat_type STRING,
        projector STRING, dvd STRING, vcr STRING, doc STRING, chalk STRING,
        marker STRING, alc STRING)''')

def insert_classroom(spaceID,name,capacity,seat_type,proj,dvd,vcr,doc,chalk,marker,alc):
    query = '''INSERT INTO classrooms VALUES
        ("{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}")'''.format(
        spaceID, name, capacity, seat_type, proj, dvd, vcr, doc, chalk, marker, alc)
    db.execute(query)

def init():
    ''' gather html data and generate the classroom database from it
    '''

    init_db()

    parser = "html.parser"
    if os.environ.get("DEBUG"):
        soup = BeautifulSoup(open("test/dump_classrooms.html"), parser)
    else:
        usock = urllib2.urlopen(url)
        source = usock.read()
        usock.close()
        soup = BeautifulSoup(source)

    rows = soup.table.tbody.findAll('tr', class_=re.compile("even_row|odd_row"))
    for row in rows:
        try:
            url_search = row.find('a', {'class', 'roomInfo'})
            classroom_id = re.search('(?<=RoomID=)\w+', url_search.get('href')).group(0)
            features = row.find_all('td')
        #TODO get correct exceptions and raise
        except:
            raise ScrapeError("search for html data failed")

        _name = features[0].get_text()
        _capacity = features[1].get_text()
        _seat_type = features[2].get_text()
        # bools
        _proj = hasFeature(features[3])
        _dvd = hasFeature(features[4])
        _vcr = hasFeature(features[6])
        _doc = hasFeature(features[7])
        _chalk = hasFeature(features[8])
        _marker = hasFeature(features[9])
        _alc = hasFeature(features[10])

        insert_classroom( classroom_id, _name, _capacity,
                _seat_type, _proj, _dvd, _vcr,
                _doc, _chalk, _marker, _alc )
    conn.commit()

class ScrapeError(Exception):
    pass

def hasFeature(feature):
    if feature.get('class')[0]=='checkmark':
        return "yes"
    return "no"


if __name__ == '__main__':
    init()
