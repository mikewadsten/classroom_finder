'''
project: classroom_finder
file: scraper.py

This is the terrible structure that they use.
ContentBox
    tr
        td.ListText
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
stuff = []
for tr in content.table.find_all('tr'):
    if (tr.find_all('td', {'class': 'ListText'}) ):
        stuff.append(tr.findAll('td'))

for item in stuff: print item
