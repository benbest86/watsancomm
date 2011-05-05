import email, logging, os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from google.appengine.dist import use_library
use_library('django', '1.2')
from google.appengine.ext import webapp 
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler 
from google.appengine.ext.webapp.util import run_wsgi_app
from models import WeeklyUpdate, ValidationError

class DisregardHandler(InboundMailHandler):
    def receive(self, mail_message):
        logging.info('Disregarding email from %s.' % mail_message.sender)
        pass

application = webapp.WSGIApplication([DisregardHandler.mapping()], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == '__main__':
    main()


