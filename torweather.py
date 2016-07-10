import sqlite3
import requests
import dateutil.parser
import json
from time import mktime
from datetime import datetime
import re


#import requests

#r = requests.get('https://api.github.com/events')
#r.json()

#dateutil.parser.parse("2016-07-06 09:00:00")

def parse_time_str(time):
    return dateutil.parser.parse(time)

def to_timestamp(datetime):
    return mktime(datetime.timetuple())

def from_timestamp(timestamp):
    return datetime.fromtimestamp(int(timestamp))

def scrape_email(text):
    pass

def main():
    #get json file
    with open('mock_data.json') as data_file:    
        data = json.load(data_file)
    #data = equests.get('https://onionoo.torproject.org/details').json()
    #connect and init db if not inited
    conn = sqlite3.connect('torweather.db')
    try:
        conn.execute("SELECT * FROM nodes;") #if there is not a nodes table this will fail
    except sqlite3.OperationalError:
        conn.execute('''CREATE TABLE nodes (
            fingerprint TEXT PRIMARY KEY,
            last_seen INTEGER,
            email TEXT,
            first_seen INTEGER,
            consensus_weight REAL,
            contact TEXT,
            nickname TEXT,
            unsubscribed INTEGER DEFAULT 0);''')
    #update or add new records
    for node in data['relays']:
        fingerprint = node['fingerprint']
        email = re.search(r'[\w\.-]+@[\w\.-]+', node.get('contact',''))
        email = email and email.group(0)
        conn.execute('''
            INSERT OR REPLACE INTO nodes 
            (fingerprint, last_seen, email, first_seen, consensus_weight, contact, nickname, unsubscribed) values (
                :fingerprint,
                :last_seen,
                :email,
                :first_seen,
                :consensus_weight,
                :contact,
                :nickname,
                (select unsubscribed from nodes where fingerprint = :fingerprint)
            );
        ''', {
            "fingerprint":fingerprint,
            "last_seen":to_timestamp(parse_time_str(node['last_seen'])),
            "email":email or None,
            "first_seen":to_timestamp(parse_time_str(node['first_seen'])),
            "consensus_weight":node.get('consensus_weight'),
            "contact":node.get('contact'),
            "nickname":node.get('nickname'),
        })
    #find nodes whos down/up state has changed