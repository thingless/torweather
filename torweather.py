import sqlite3
import requests
import dateutil.parser
import json
import time
import datetime
import re
import os

from mailer import alert

NODE_DOWN_ALERT_TIMEOUT = 48*60*60 #How long to wait before sending node down alert

#import requests

#r = requests.get('https://api.github.com/events')
#r.json()

#dateutil.parser.parse("2016-07-06 09:00:00")

def parse_time_str(tim):
    return dateutil.parser.parse(tim)

def to_timestamp(dt):
    return time.mktime(dt.timetuple())

def from_timestamp(timestamp):
    return datetime.datetime.fromtimestamp(int(timestamp))

def scrape_email(text):
    pass

def main():
    #get json file
    if not os.environ.get('PROD'):
        with open('mock_data.json') as data_file:
            data = json.load(data_file)
    else:
        data = requests.get('https://onionoo.torproject.org/details').json()
    #connect and init db if not inited
    conn = sqlite3.connect('torweather.db')
    conn.row_factory = sqlite3.Row
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
            unsubscribed INTEGER,
            last_alert_last_seen INTEGER);''')
    #update or add new records
    with conn:
        for node in data['relays']:
            fingerprint = node['fingerprint']
            email = re.search(r'[\w\.-]+@[\w\.-]+', node.get('contact') or '')  #TODO: make this less shit
            email = email and email.group(0)
            assert node['last_seen'], 'How has a node never been seen?'
            conn.execute('''
                INSERT OR REPLACE INTO nodes
                (fingerprint, last_seen, email, first_seen, consensus_weight, contact, nickname, unsubscribed, last_alert_last_seen) VALUES (
                    :fingerprint,
                    :last_seen,
                    :email,
                    :first_seen,
                    :consensus_weight,
                    :contact,
                    :nickname,
                    (select unsubscribed from nodes where fingerprint = :fingerprint),
                    (select last_alert_last_seen from nodes where fingerprint = :fingerprint)
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
    published = to_timestamp(parse_time_str(data['relays_published']))
    for node in conn.execute("SELECT * FROM nodes WHERE last_seen < :threshold AND "
                             "(last_alert_last_seen IS NULL OR last_alert_last_seen <> last_seen);", {
                                'threshold': published - NODE_DOWN_ALERT_TIMEOUT,
                            }):
        print node
        #alert(node)
        conn.execute("UPDATE nodes SET last_alert_last_seen = last_seen;")

if __name__ == "__main__":
    main();
