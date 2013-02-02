## UMN classroom schedule listing  

This project seeks to create an easy interface to UMN classroom schedules by providing a 
lookup for gaps in classroom usage along with classroom info.

### The Scrapers
To get fresh html source data, run the main scraper (`scraper.py`) with 
`SCRAPER_ENV=production python scraper.py` otherwise it'll assume you want 
the EastBank.html dump for testing. This supplies you with the sqlite3 database

### The web app
The Flask app accesses the db created by scrapers and allows you to interact with it.

### Starting the app
To get started:
- make sure you have pip and virtualenv
- `virtualenv venv`
- `. venv/bin/activate`
- `pip install -r requirements.pip`
- `python app.py`
