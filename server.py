import tornado.ioloop
import tornado.web
import os

class UnsubscribeHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

if __name__ == "__main__":
    app = tornado.web.Application([
        (r"/unsubscribe", UnsubscribeHandler),
    ])
    port = os.environ.get('PORT', 8080)
    print "listening on 127.0.0.1:{}".format(port)
    app.listen(port)
    tornado.ioloop.IOLoop.current().start()