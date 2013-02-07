#!/usr/bin/env python
'''
project: classroom_finder
file: scraper.py

This is the terrible structure that they use. (I think..)
div.ContentBox
    tr
        td.ListText
            a.ListText title=Location
                Location
        td.ListText
            Start
        td.ListText
            End
        td.ListText
            Event

'''
from bs4 import BeautifulSoup
from time import strptime
import datetime
import sqlite3
import urllib2
import os

from lib.utils import constructURL, get_space_id

today = datetime.date.today()
SHORTEST_GAP_TIME = 15

'''We no longer want to rebuild the database each time as the classrooms table will
now hold more permanent data (populated by a separate script, classroom_scraper.py
Instead, init_db() now drops and recreates the gaps table'''

conn = sqlite3.connect('database.db')
db = conn.cursor()

def init_db():
    db.execute('''DROP TABLE IF EXISTS gaps''')
    db.execute('''CREATE TABLE gaps (room STRING, start DATE, end DATE, length INTEGER)''')

#def insert_gaps(query_list):
#    db.executemany()

def insert_gap(spaceID, start, end, length):
    query = "INSERT INTO gaps (spaceID,start,end,length) VALUES ('{}', '{}', '{}', {})".format(spaceID,start,end,length)
    db.execute(query)
    # how do we commit at the end instead of after every insert
    #conn.commit()

#TODO grab all sources, right now it only does EastBank from the url provided in lib/campus.py
def init():
    ''' gather html data and generate the event dictionary from it
        @param campus - which campus to initialize
    '''

    init_db()

    #  if running this as a script w/ python version < 2.7.3, use html5lib via pip install
    parser = "html.parser"

    # run with SCRAPER_ENV=production if you want fresh data
    if os.environ.get("SCRAPER_ENV") == "production":
        usock = urllib2.urlopen(constructURL(today, "east"))
        source = usock.read()
        usock.close()
        soup = BeautifulSoup(source)
    # Debug mode
    else:
        soup = BeautifulSoup(open("test/EastBank.html"), parser)

    content = soup.find('div', {'id': 'ContentBox'})
    if content is None:
        exit("No content found...")
    eventList = []
    for tr in content.table.findAll('tr'):
        if (tr.find_all('td', {'class': 'ListText'})):
            # this is where it grabs the 4 ListText elements
            # [[building1, start, end, event],[building2, start, end, event] ... etc]
            eventList.append(tr.findAll('td'))

    events = {}
    for event in eventList:
        #TODO rewrite regex to grab space id from the first href
        href = event[0].find('a', {'class', 'ListText'}).get('href')
        sid = get_space_id(href)
        start_times = event[1].stripped_strings
        end_times = event[2].stripped_strings
        times = []
        for start_time, end_time in zip(start_times, end_times):
            # Strip colon, AM/PM and spaces
            f_start_time = strptime(start_time, "%I:%M %p")
            s_time = datetime.datetime(today.year, today.month, today.day, \
                    f_start_time.tm_hour, f_start_time.tm_min)
            f_end_time = strptime(end_time, "%I:%M %p")
            e_time = datetime.datetime(today.year, today.month, today.day, \
                    f_end_time.tm_hour, f_end_time.tm_min)
            #events dict, key=spaceID, value=[start time, end time]
            times.append((s_time, e_time))
        events[sid] = times

    # insert gaps
    for sid, times in events.items():
        print "Inserting " + sid
        gap_times = get_gap_times(times)
        for s_time, e_time in gap_times:
            gap_length = _gap(s_time, e_time)
            if (gap_length > SHORTEST_GAP_TIME):
                insert_gap(sid, s_time, e_time, gap_length)
    conn.commit()


def get_gap_times(times):
    ''' return gaps ((start.hour, start.minute)(end.hour, end.minute)). 
        This will be called on a per room basis
        @param times - a list of time tuples [((start.hour, start.minute)(end.hour, end.minute))...] 
    '''
    # buidings open at 8:00 and close at 10:00
    prev_event = (None, datetime.datetime(today.year, today.month, today.day, 8, 0))
    build_close = (datetime.datetime(today.year, today.month, today.day, 22, 0), None)

    gap_times = []
    for event in times:
        # ignore duplicates
        if prev_event[1] < event[0]:
            gap_times.append( (prev_event[1], event[0]) ) # (prev_finish, start)
            prev_event = event
    gap_times.append( (prev_event[1], build_close[0]) )
    return gap_times

def _gap(_from, _to):
    ''' returns gap in minutes '''
    return (_to - _from).seconds/60

if __name__ == '__main__':
    init()

