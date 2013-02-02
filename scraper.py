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

from lib.campus import constructURL

today = datetime.date.today()

'''We no longer want to rebuild the database each time as the classrooms table will
now hold more permanent data (populated by a separate script, classroom_scraper.py
Instead, init_db() now drops and recreates the gaps table'''

conn = sqlite3.connect('database.db')
db = conn.cursor()

def init_db():
    db.execute('''DROP TABLE IF EXISTS gaps''')
    db.execute('''CREATE TABLE gaps (start DATE, end DATE, length INTEGER)''')

#def insert_gaps(query_list):
#    db.executemany()

def insert_gap(start, end, length):
    query = "INSERT INTO gaps (start,end,length) VALUES (\"{}\", \"{}\", {})".format(start,end,length)
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
        soup = BeautifulSoup(open("EastBank.html"), parser)

    content = soup.find('div', {'id': 'ContentBox'})
    if content is None:
        print "No content found..."
        return {}
    eventList = []
    for tr in content.table.findAll('tr'):
        if (tr.find_all('td', {'class': 'ListText'})):
            # this is where it grabs the 4 ListText elements
            # makes a list of lists 
            # [[building1, start, end, event],[building2, start, end, event] ... etc]
            eventList.append(tr.findAll('td'))

    events = {}
    for event in eventList:
        room = event[0].find('a', {'class': 'ListText'}).string
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
            #events dict, key=room, value=[start time, end time]
            times.append((s_time, e_time))
        events[room] = times

    for room in events:
        insert_gap_times(events[room])
    return events


def insert_gap_times(times):
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
            # insert gap data into db
            insert_gap(prev_event[1], event[0], _gap(prev_event[1], event[0]))
            prev_event = event
    gap_times.append( (prev_event[1], build_close[0]) )

def _gap(_from, _to):
    ''' returns gap in minutes '''
    return (_to - _from).seconds/60

if __name__ == '__main__':
    init()

