from bs4 import BeautifulSoup
import urllib2

'''
Don't fetch the html each time, put this in later

east = "http://wvprd.ocm.umn.edu/gpcwv/wv3_servlet/urd/run/wv_space.DayList?spfilter=947166,spdt=20130130,lbdviewmode=list"
west = "http://wvprd.ocm.umn.edu/gpcwv/wv3_servlet/urd/run/wv_space.DayList?spfilter=947169,spdt=20130130,lbdviewmode=list"
usock = urllib2.urlopen(west)
data = usock.read()
usock.close()
'''

soup = BeautifulSoup(open('WestBank.html'))
content = soup.find('div', {'id': 'ContentBox'})
table = BeautifulSoup(content)
for tr in table.find_all('tr'):
    td = tr.find('td', {'id': 'ListText'})
    print td
