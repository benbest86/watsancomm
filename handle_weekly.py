import email, logging, os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from google.appengine.dist import use_library
use_library('django', '1.2')
from google.appengine.ext import webapp 
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler 
from google.appengine.ext.webapp.util import run_wsgi_app
from models import WeeklyUpdate, ValidationError

class WeeklyUpdateHandler(InboundMailHandler):
    def receive(self, mail_message):
        sender = mail_message.sender
        html_body = None
        plain_body = None
        for content_type, body in mail_message.bodies('text/plain'):
            plain_body = body.decode()
        for content_type, body in mail_message.bodies('text/html'):
            html_body = body.decode()
        message_date = mail_message.date
        wu = WeeklyUpdate(
                sender=sender,
                plain_body=plain_body,
                html_body=html_body,
                )
        try:
            wu.put()
        except ValidationError, e:
            logging.warning(e.message)

application = webapp.WSGIApplication([WeeklyUpdateHandler.mapping()], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == '__main__':
    main()


