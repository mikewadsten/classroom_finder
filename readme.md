### Scraper for UMN classroom schedule listing

This script will eventually run on a server, to be pinged for info.
To get fresh html source data, run with `SCRAPER_ENV=production python scraper.py`
otherwise it'll assume you want the EastBank.html dump for testing 

the flask app just creates a big dumb <ul> of gap events


To get started:
- make sure you have pip and virtualenv
- `virtualenv venv`
- `. venv/bin/activate`
- `pip install -r requirements.pip`
- `python app.py`
