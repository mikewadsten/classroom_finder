from bs4 import BeautifulSoup
import urllib2

url = "http://wvprd.ocm.umn.edu/gpcwv/wv3_servlet/urd/run/wv_space.DayList?spfilter=947166,spdt=20130130,lbdviewmode=list"
usock = urllib2.urlopen(url)
data = usock.read()
usock.close()

soup = BeautifulSoup(data)
for entry in soup.find_all('tr'):
    print entry.prettify()
