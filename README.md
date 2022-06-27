# Tor Weather

Tor Weather will inform the user listed in [torrc's](https://support.torproject.org/tbb/tbb-editing-torrc/) `ContactInfo` field via email in the event of downtime lasting longer than 48 hours.

## Tor Weather's History

The original Tor Weather was decommissioned by the Tor project. This replacement is now maintained independently and its source code can be found in this GitHub repo. More info about about the original Tor Weather can be found [here](https://lists.torproject.org/pipermail/tor-relays/2016-June/009424.html).

Unlike the original Tor Weather, this project only sends emails for down time to the nodes owner. It does not send emails about t-shirts or support any configuration (beyond "unsubscribe"). Reducing the scope of Tor Weather makes it easier to maintain.

## Running the Source Code

```bash
# Create the virtualenv
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt

# Common configuration
DIR=$(dirname $0)
export MAILGUN_KEY=(your-mailgun-creds)
export PROD=1
export UNSUB_KEY=(random-string-for-key)
export PYTHONPATH=$DIR
export PORT=8888

# To run the unsubscribe server
venv/bin/python server.py

# To run the cron job (run every hour)
venv/bin/python torweather.py
```
