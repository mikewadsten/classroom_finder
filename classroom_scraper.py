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

classrooms = {}
feature_headers = ['proj','dvd','vcr','doc','chalk','marker','alc']

conn = sqlite3.connect('database.db')
db = conn.cursor()

def init_db():
    db.execute('''DROP TABLE IF EXISTS classrooms''')
    db.execute('''CREATE TABLE classrooms (spaceID INT, roomname STRING, capacity INT, seat_type STRING, projector STRING, dvd STRING, vcr STRING, doc STRING, chalk STRING, marker STRING, alc STRING)''')

def insert_classroom(spaceID,name,capacity,seat_type,proj,dvd,vcr,doc,chalk,marker,alc):
    query = "INSERT INTO classrooms VALUES (\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\")".format(spaceID,name,capacity,seat_type,proj,dvd,vcr,doc,chalk,marker,alc)
    db.execute(query)

def init():
    ''' gather html data and generate the classroom database from it
    '''

    init_db()

    parser = "html.parser"
    if os.environ.get("SCRAPER_ENV") == 'production':
        #TODO url for data source
        usock = urllib2.urlopen(url)
        source = usock.read()
        usock.close()
        soup = BeautifulSoup(source)
    else:
        soup = BeautifulSoup(open("test/dump_classrooms.html"), parser)

    rows = soup.table.tbody.findAll('tr', class_=re.compile("even_row|odd_row"))
    for row in rows:
        print "~~~~~~~~~~~~~~~~ NEW CLASSROOM ~~~~~~~~~~~~~~~~"
        try:
            url_search = row.find('a', {'class', 'roomInfo'})
            classroom_id = re.search('(?<=RoomID=)\w+', url_search.get('href')).group(0)
            features = row.find_all('td')
        #TODO get correct exceptions and raise
        except:
            raise ScrapeError("search for html data failed")

        classroom_name = features[0].get_text()
        classroom_capacity = features[1].get_text()
        classroom_seat_type = features[2].get_text()
        classroom_proj = hasFeature(features[3])
        classroom_dvd = hasFeature(features[4])
        classroom_vcr = hasFeature(features[5])
        classroom_doc = hasFeature(features[6])
        classroom_chalk = hasFeature(features[7])
        classroom_marker = hasFeature(features[8])
        classroom_alc = hasFeature(features[9])


        insert_classroom(classroom_id, classroom_name, classroom_capacity, classroom_seat_type, classroom_proj, classroom_dvd, classroom_vcr, classroom_doc, classroom_chalk, classroom_marker, classroom_alc)
    conn.commit()

class ScrapeError(Exception):
    pass

def hasFeature(feature):
    print feature
    if feature.get('class')[0]=='checkmark':
        return "yes"
    return "no"

def construct_url(sid):
    ''' this is the individual room page. We may or may not need it'''
    return "http://wvprd.ocm.umn.edu/gpcwv/wv3_servlet/urd/run/" \
        + "wv_space.Detail?RoomID={}".format(sid)

if __name__ == '__main__':
    init()
