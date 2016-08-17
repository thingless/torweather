import os
import requests
import logging
from tornado import template

logger = logging.getLogger(__name__)

DOMAIN_NAME = 'torweather.org'
API_KEY = ''  # TODO


EMAIL_DOWN_SUBJECT = '[Tor Weather] Node Down!'
EMAIL_DOWN_BODY = '''
It appears that the Tor node {{nickname}} (fingerprint: {{fingerprint}}) has been uncontactable through the Tor network for at least 48 hours. You may wish to look at it to see why.

You can find more information about the Tor node at:

https://atlas.torproject.org/#details/{{fingerprint}}

You can unsubscribe from these reports at any time by visiting the following url:

{{unsubscribe_url}}

The original Tor Weather was decommissioned by the Tor project and this replacement is now maintained independently. You can learn more here:

https://github.com/thingless/torweather/blob/master/README.md
'''

email_down_template = template.Template(EMAIL_DOWN_BODY)

def alert_down(node):
    parms = dict(node)
    parms['unsubscribe_url'] =` None
    if not os.environ.get('PROD'):
        parms['email'] = 'torweather@moreorcs.com'
    logger.info('Would email about node %r', dict(parms))
    return
    return requests.post("https://api.mailgun.net/v3/{}/messages".format(DOMAIN_NAME),
                         auth=("api", API_KEY),
                         data={
                            "from": "Tor Weather <noreply@{}>".format(DOMAIN_NAME),
                            "to": [parms['email']],
                            "subject": EMAIL_DOWN_SUBJECT,
                            "text": email_down_template.generate(**parms)
                         })
