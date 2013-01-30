'''
project: classroom_finder
file: scraper.py

This is the terrible structure that they use. (I think..)
ContentBox
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
import urllib2

'''
#TODO Use this to fetch fresh data
east = "http://wvprd.ocm.umn.edu/gpcwv/wv3_servlet/urd/run/wv_space.DayList?spfilter=947166,spdt=20130130,lbdviewmode=list"
west = "http://wvprd.ocm.umn.edu/gpcwv/wv3_servlet/urd/run/wv_space.DayList?spfilter=947169,spdt=20130130,lbdviewmode=list"
usock = urllib2.urlopen(west)
data = usock.read()
usock.close()
'''

soup = BeautifulSoup(open('WestBank.html'))
content = soup.find('div', {'id': 'ContentBox'})
eventList = []
for tr in content.table.find_all('tr'):
    if (tr.find_all('td', {'class': 'ListText'}) ):
        # this is where it grabs the 4 ListText elements
        # makes a list of lists [[building1, start, end, event],[building2, start, end, event] ... etc]
        eventList.append(tr.findAll('td'))

events = {}
for event in eventList:
    print event[0]
    print
    #events['building'] = event[0].title
    #events['start'] = 
    #events['end'] = 

