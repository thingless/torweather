import sqlite3
import requests
import dateutil.parser
import json


#import requests

#r = requests.get('https://api.github.com/events')
#r.json()

#dateutil.parser.parse("2016-07-06 09:00:00")

def scrape_email(text):
    

def main():
    #get json file
    with open('mock_data.json') as data_file:    
        data = json.load(data_file)
    
    #https://onionoo.torproject.org/details
    #connect and init db if not inited
    conn = sqlite3.connect('torweather.db')
    try:
        conn.execute("SELECT * FROM nodes")
    except sqlite3.OperationalError:
        c.execute('''CREATE TABLE nodes (fingerprint TEXT, last_seen DATETIME, email TEXT, first_seen DATETIME, consensus_weight real, contact TEXT, nickname TEXT)''')