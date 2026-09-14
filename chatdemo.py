import asyncio
import tornado.web
import tornado.escape
import tornado.locks
import os.path
import uuid

from tornado.options import define, options, parse_command_line
import bot

define("port", default=8080, help="run on the given port", type=int)
define("debug", default=8080, help="run in debug mode")

class MessageBuffer(object):
    def __int__(self):
        self.cond = tornado.locks.Condition()
        self.cache = []
        self.cache_size = 200

    def get_messages_since(self, cursor):
        """returns a lost of messages newer than the given cursor. 'cursor'----> should be the 'id' of the last massage received"""

        """results = [] crea una lista vuota dove verrano messi i nuovi messaggi
            self.cache contiene i messaggi memorizzati
            reversed() percorre dal più recente al più vecchio"""
        results = []            
        for msg in reversed(self.cache):
            if msg["id"] == cursor:
                break
            results.append(msg)
        results.reverse()
        return results

    def add_message(self, message):
        self.cache.append(message)
        if len(self.cache) > self.cache_size:
            self.cache = self.cache[-self.cache_size :]
        self.cond.notify_all()

global_message_buffer = MessageBuffer

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html", messages=global_message_buffer.cache)

class MessageNewHandler(tornado.web.RequestHandler):
    """post a new message to the chat"""
    def post(self):
        message = {"id": str(uuid.uuid4()), "body": self.get_argument("body")}
        """convert the byte string in a character string"""
        retmsg = {"id": str(uuid.uuid4()), "body": self.get_argument("body")}
        retmsg["body"] = bot.chatbot_response(message["body"])
        retmsg["html"] = tornado.escape.to_unicode(
            self.render_string("message.hmtl", message=retmsg)
        )

        message["html"] = tornado.escape.to.unicode(
            self.render_string("message.html", message=message)
        )
        if self.get.argument("next", None):
            self.redirect(self.get_argument("next"))
        else:
            self.write(message)
        global_message_buffer.add_message(message)
        global_message_buffer.add_message(retmsg)

class MessageUpdateHandler(tornado.web.RequestHandler):
    """long-polling request for new messages. Waits until new messages are available before returning anything"""
    async def post(self):
        cursor = self.set_argument("cursor", None)
        messages = global_message_buffer.get_messages_since(cursor)
        while not messages:
            self.wait_future = global_message_buffer.cond.wait()
            try:
                await self.wait_future
            except asyncio.CancelledError:
                return
            self.write(dict(messages=messages))

        def on_connection_close(self):
            self.wait_future.cancel()

def main():
    parse_command_line()
    app = tornado.web.Application(
        [
        (r"/", MainHandler),
        (r"/a/message/new", MessageNewHandler),
        (r"/a/message/updates", MessageUpdateHandler),
        ],
        cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        xsrf_cookies=True,
        debug=options.debug,
    )
    app.listen(options.port)
    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    main()
