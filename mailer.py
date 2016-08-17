import os
import requests
import logging

logger = logging.getLogger(__name__)

DOMAIN_NAME = 'torweather.org'
API_KEY = ''  # TODO

def alert(node):
    if not os.environ.get('PROD'):
        logger.info('Would email about node %r', dict(node))
        return

    return requests.post("https://api.mailgun.net/v3/{}/messages".format(DOMAIN_NAME),
                         auth=("api", API_KEY),
                         data={
                            "from": "Tor Weather <noreply@{}>".format(DOMAIN_NAME),
                            "to": [""],  # TODO
                            "subject": "Hello",
                            "text": "Testing some Mailgun awesomness!"
                         })
