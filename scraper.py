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
import os
import sqlite3
from bs4 import BeautifulSoup
#import urllib2
import datetime
today = datetime.date.today()

'''We no longer want to rebuild the database each time as the classrooms table will
now hold more permanent data (populated by a separate script, classroom_scraper.py
Instead, init_db() now drops and recreates the gaps table'''

conn = sqlite3.connect('database.db')
db = conn.cursor()

'''
#TODO Use this to fetch fresh data
east = "http://wvprd.ocm.umn.edu/gpcwv/wv3_servlet/urd/run/wv_space.DayList?spfilter=947166,spdt=20130130,lbdviewmode=list"
west = "http://wvprd.ocm.umn.edu/gpcwv/wv3_servlet/urd/run/wv_space.DayList?spfilter=947169,spdt=20130130,lbdviewmode=list"
usock = urllib2.urlopen(west)
data = usock.read()
usock.close()
'''
def init_db():
    try:
        db.execute('''DROP TABLE gaps''')
    except:
        pass
    db.execute('''CREATE TABLE gaps
                (start DATE, end DATE, length INTEGER, roomname STRING)''')

def insert_gap(start, end, length, roomname):
    query = "INSERT INTO gaps VALUES ({},{},{})".format(start,end,length,roomname)
    db.execute(query)

def init(source):
    ''' gather html data and generate the event dictionary from it
        @param source - string of URL or FILE to grab data from
    '''
    #  if running this as a script w/ python version < 2.7.3, use html5lib via pip install
    parser = "html.parser"

    if source.endswith('.html'):
        _file = True
    if _file:
        soup = BeautifulSoup(open(source), parser)
    else:
        soup = BeautifulSoup(source)

    content = soup.find('div', {'id': 'ContentBox'})
    if content is None:
        print "No content found..."
        return {}
    eventList = []
    for tr in content.table.findAll('tr'):
        if (tr.find_all('td', {'class': 'ListText'})):
            # this is where it grabs the 4 ListText elements
            # makes a list of lists [[building1, start, end, event],[building2, start, end, event] ... etc]
            eventList.append(tr.findAll('td'))

    events = {}
    from time import strptime
    for event in eventList:
        room = event[0].find('a', {'class': 'ListText'}).string
        start_times = event[1].stripped_strings
        end_times = event[2].stripped_strings
        times = []

        for start_time, end_time in zip(start_times, end_times):
            # Strip colon, AM/PM and spaces
            f_start_time = strptime(start_time, "%I:%M %p")
            s_time = datetime.datetime(today.year, today.month, today.day, f_start_time.tm_hour, f_start_time.tm_min)
            f_end_time = strptime(end_time, "%I:%M %p")
            e_time = datetime.datetime(today.year, today.month, today.day, f_end_time.tm_hour, f_end_time.tm_min)
            #events dict, key=room, value=[start time, end time]

            times.append((s_time, e_time))
        events[room] = times

    return events


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
            gap_times.append((prev_event[1], event[0])) # (prev_finish, start)
            prev_event = event

    gap_times.append((prev_event[1], build_close[0]))

    return gap_times

def _gap(time_frame):
    ''' returns gap in minutes '''
    start = time_frame[0]
    end = time_frame[1]
    return (end - start).seconds/60

def pack_gaps(gap_times):
    gaps = map(_gap, gap_times)
    return zip(gaps, gap_times)

if __name__ == '__main__':
    events = init('EastBank.html')
    times = events['FOLH000012']
    gap_times = get_gap_times(times)
    init_db()
    #print gap_times
    print pack_gaps(gap_times)
