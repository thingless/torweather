import hmac
import os
import warnings

KEY = os.environ.get('UNSUB_KEY')
if not KEY:
    warnings.warn("Using insecure key for HMAC!")
    KEY = 'thisisinsecure'

def generate(msg):
    return hmac.new(KEY, msg).hexdigest()

def verify(sec, msg):
    return hmac.compare_digest(generate(msg), sec)

if __name__ == '__main__':
    assert verify(generate('12345'), '12345')
    print 'tests passed'
