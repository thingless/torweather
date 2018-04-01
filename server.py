import os
import sqlite3
import tornado.ioloop
import tornado.template
import tornado.web

from verifier import verify

def wrap_render(template, *args, **kwargs):
    if isinstance(template, tornado.template.Template):
        out = template.generate(*args, **kwargs)
    else:
        out = template

    return """<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport"
content="width=device-width, initial-scale=1"><title>Tor
Weather</title><style type="text/css">body{margin:40px
auto;max-width:650px;line-height:1.6;font-size:18px;color:#444;padding:0
10px}h1,h2,h3{line-height:1.2}</style></head><body>
""" + out + "</body></html>"

UNSUB_GET_TEMPLATE = tornado.template.Template("""
<h1>TorWeather Unsubscribe</h1>
<p>Sorry to see you go. :(</p>
<p>(To change the frequency of emails instead, you can go
<a href="/subscribe?hmac={{hmac}}&fingerprint={{fingerprint}}">here</a>.)</p>
<form action="/unsubscribe" method="POST">
<input type="submit" value="Unsubscribe" />
<input type="hidden" name="hmac" value="{{hmac}}" />
<input type="hidden" name="fingerprint" value="{{fingerprint}}" />
</form>
<p>Go <a href="/">home</a>?</p>
""")

SUB_GET_TEMPLATE = tornado.template.Template("""
<h1>TorWeather Email Frequency</h1>
<p>Update your notification sensitivity.</p>
<form action="/subscribe" method="POST">
<select name="frequency">
    <option value="10800">3 Hours</option>
    <option value="43200">12 Hours</option>
    <option value="86400">1 Day</option>
    <option value="172800">2 Days (default)</option>
    <option value="604800">1 Week</option>
</select>
<input type="submit" value="Update" />
<input type="hidden" name="hmac" value="{{hmac}}" />
<input type="hidden" name="fingerprint" value="{{fingerprint}}" />
</form>
<p>Go <a href="/">home</a>?</p>
""")

class UnsubscribeHandler(tornado.web.RequestHandler):
    def get(self):
        fingerprint = self.get_argument('fingerprint')
        hmac = self.get_argument('hmac')

        if not verify(hmac, fingerprint):
            self.set_status(403)
            self.write('hmac invalid :(')
            return

        self.write(wrap_render(UNSUB_GET_TEMPLATE, fingerprint=fingerprint, hmac=hmac))

    def post(self):
        fingerprint = self.get_argument('fingerprint')
        hmac = self.get_argument('hmac')

        if not verify(hmac, fingerprint):
            self.set_status(403)
            self.write('hmac invalid :(')
            return

        conn = sqlite3.connect('TorWeather.db')
        with conn:
            conn.execute("INSERT OR REPLACE INTO unsubscribe (fingerprint) VALUES (:fingerprint);",
                         {'fingerprint': fingerprint})

        self.write(wrap_render("Successfully unsubscribed."))

class SubscribeHandler(tornado.web.RequestHandler):
    def get(self):
        fingerprint = self.get_argument('fingerprint')
        hmac = self.get_argument('hmac')

        if not verify(hmac, fingerprint):
            self.set_status(403)
            self.write('hmac invalid :(')
            return

        self.write(wrap_render(SUB_GET_TEMPLATE, fingerprint=fingerprint, hmac=hmac))

    def post(self):
        fingerprint = self.get_argument('fingerprint')
        frequency = self.get_argument('frequency')
        parsedfreq = 60 * 60 * 24 * 2
        hmac = self.get_argument('hmac')

        if not verify(hmac, fingerprint):
            self.set_status(403)
            self.write('hmac invalid :(')
            return

        try:
            parsedfreq = int(frequency)
            if parsedfreq < 1:
                self.set_status(403)
                self.write('frequency invalid :(')
                return
        except ValueError:
            self.set_status(403)
            self.write('frequency invalid :(')
            return

        conn = sqlite3.connect('TorWeather.db')
        with conn:
            conn.execute("INSERT OR REPLACE INTO subscribe (fingerprint, frequency) VALUES (:fingerprint, :frequency);",
                         {'fingerprint': fingerprint, 'frequency': parsedfreq})

        self.write(wrap_render("Successfully unsubscribed."))


class RootHandler(tornado.web.RequestHandler):
    def get(self):
        self.redirect('https://github.com/thingless/torweather')

if __name__ == "__main__":
    app = tornado.web.Application([
        (r"/unsubscribe", UnsubscribeHandler),
        (r"/subscribe", SubscribeHandler),
        (r"/", RootHandler),
    ])
    port = os.environ.get('PORT', 8080)
    print "listening on 127.0.0.1:{}".format(port)
    app.listen(port)
    tornado.ioloop.IOLoop.current().start()
