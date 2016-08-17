import os
import sqlite3
import tornado.ioloop
import tornado.template
import tornado.web

from verifier import verify

UNSUB_GET_TEMPLATE = tornado.template.Template("""
<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport"
content="width=device-width, initial-scale=1"><title>Unsubscribe from Tor
Weather</title><style type="text/css">body{margin:40px
auto;max-width:650px;line-height:1.6;font-size:18px;color:#444;padding:0
10px}h1,h2,h3{line-height:1.2}</style></head><body> <p>Sorry to see you go. :(
<form action="/unsubscribe" method="POST">
<input type="submit" value="Unsubscribe" />
<input type="hidden" name="hmac" value="{{hmac}}" />
<input type="hidden" name="fingerprint" value="{{fingerprint}}" />
</form>
</body></html>""")
class UnsubscribeHandler(tornado.web.RequestHandler):
    def get(self):
        fingerprint = self.get_argument('fingerprint')
        hmac = self.get_argument('hmac')

        if not verify(hmac, fingerprint):
            self.set_status(403)
            self.write('hmac invalid :(')

        self.write(UNSUB_GET_TEMPLATE.generate(fingerprint=fingerprint, hmac=hmac))

    def post(self):
        fingerprint = self.get_argument('fingerprint')
        hmac = self.get_argument('hmac')

        if not verify(hmac, fingerprint):
            self.set_status(403)
            self.write('hmac invalid :(')

        conn = sqlite3.connect('TorWeather.db')
        with conn:
            conn.execute("INSERT OR REPLACE unsubscribe (fingerprint) VALUES (:fingerprint);",
                         {'fingerprint': fingerprint})

        self.write('Successfully unsubscribed. If you want to resubscribe, contact support@torweather.org.')

if __name__ == "__main__":
    app = tornado.web.Application([
        (r"/unsubscribe", UnsubscribeHandler),
    ])
    port = os.environ.get('PORT', 8080)
    print "listening on 127.0.0.1:{}".format(port)
    app.listen(port)
    tornado.ioloop.IOLoop.current().start()
