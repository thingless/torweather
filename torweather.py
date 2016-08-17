import sqlite3
import requests
import dateutil.parser
import json
import time
import datetime
import re
import os
import logging

from mailer import alert

NODE_DOWN_ALERT_TIMEOUT = 48*60*60 #How long to wait before sending node down alert
logger = logging.getLogger(__name__)

NODE_DOWN_ALERT_TIMEOUT = 48*3600  #How long to wait before sending node down alert

def parse_time_str(tim):
    return dateutil.parser.parse(tim)

def to_timestamp(dt):
    return time.mktime(dt.timetuple())

def from_timestamp(timestamp):
    return datetime.datetime.fromtimestamp(int(timestamp))

def scrape_email(text):
    pass

def main():
    logging.basicConfig(level=logging.INFO)

    #get json file
    if not os.environ.get('PROD'):
        logger.info("Reading details from mock_data.json...")
        with open('mock_data.json') as data_file:
            data = json.load(data_file)
    else:
        logger.info("Fetching details from onionoo...")
        data = requests.get('https://onionoo.torproject.org/details').json()

    #connect and init db if not inited
    conn = sqlite3.connect('TorWeather.db')
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("SELECT COUNT(1) FROM nodes;") #if there is not a nodes table this will fail
    except sqlite3.OperationalError:
        logger.info("Creating database table 'nodes'...")
        conn.execute('''CREATE TABLE nodes (
            fingerprint TEXT PRIMARY KEY,
            last_seen INTEGER,
            email TEXT,
            first_seen INTEGER,
            consensus_weight REAL,
            contact TEXT,
            nickname TEXT,
            last_alert_last_seen INTEGER);''')

    try:
        conn.execute("SELECT COUNT(1) FROM unsubscribe;")
    except sqlite3.OperationalError:
        logger.info("Creating database table 'unsubscribe'...")
        conn.execute('CREATE TABLE unsubscribe (fingerprint TEXT PRIMARY KEY);')

    #update or add new records
    with conn:
        logger.info("Updating database of nodes from onionoo data...")
        for node in data['relays']:
            fingerprint = node['fingerprint']
            email = re.search(r'[\w\.-]+@[\w\.-]+', node.get('contact') or '')  #TODO: make this less shit
            email = email and email.group(0)
            assert node['last_seen'], 'How has a node never been seen?'
            conn.execute('''
                INSERT OR REPLACE INTO nodes
                (fingerprint, last_seen, email, first_seen, consensus_weight, contact, nickname, last_alert_last_seen) VALUES (
                    :fingerprint,
                    :last_seen,
                    :email,
                    :first_seen,
                    :consensus_weight,
                    :contact,
                    :nickname,
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
        logger.info("Updated %r nodes.", len(data['relays']))

    #find nodes whos down/up state has changed
    published = to_timestamp(parse_time_str(data['relays_published']))
    logger.info("Checking which nodes to alert...")
    with conn:
        for node in conn.execute("SELECT n.* FROM nodes n "
                                 "LEFT OUTER JOIN unsubscribe u ON u.fingerprint = n.fingerprint "
                                 "WHERE last_seen < :threshold AND u.fingerprint IS NULL AND "
                                 "(last_alert_last_seen IS NULL OR last_alert_last_seen <> last_seen);", {
                                    'threshold': published - NODE_DOWN_ALERT_TIMEOUT,
                                }):
            # Send the email!
            alert(node)

            # Mark us as having alerted on this node
            conn.execute("UPDATE nodes SET last_alert_last_seen = last_seen WHERE fingerprint = :fingerprint;",
                         {"fingerprint": node['fingerprint']})

if __name__ == "__main__":
    main()
