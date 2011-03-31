import email, logging
from google.appengine.ext import webapp 
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler 
from google.appengine.ext.webapp.util import run_wsgi_app

class WeeklyUpdateHandler(InboundMailHandler):
    def receive(self, mail_message):
        logging.info("Received a message from: " + mail_message.sender)
        print 'Received a message from %s' % mail_message.sender

application = webapp.WSGIApplication([WeeklyUpdateHandler.mapping()], debug=True)
