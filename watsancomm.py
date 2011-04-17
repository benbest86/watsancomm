import os, logging
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from google.appengine.dist import use_library
use_library('django', '1.2')
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from models import WeeklyUpdate

class PreviewWeekly(webapp.RequestHandler):
    def get(self):
        content = WeeklyUpdate.generate_summary_content(WeeklyUpdate.get_weekly_updates())
        email = WeeklyUpdate.generate_summary_email(content)
        self.response.out.write(email.html)

class SendUpdate(webapp.RequestHandler):
    def get(self):
        content = WeeklyUpdate.generate_summary_content(WeeklyUpdate.get_weekly_updates())
        email = WeeklyUpdate.generate_summary_email(content)
        email.send()

class SendReminder(webapp.RequestHandler):
    def get(self):
        email = WeeklyUpdate.generate_reminder_email()
        email.send()

application = webapp.WSGIApplication([
                                        ('/main/preview', PreviewWeekly),
                                        ('/main/send_update', SendUpdate),
                                        ('/main/send_reminder', SendReminder),
                                     ], debug=True,)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
