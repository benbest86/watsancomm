import os, logging
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from google.appengine.dist import use_library
use_library('django', '1.2')
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

from settings import TEMPLATE_DIR
from models import WeeklyUpdate

class PreviewWeekly(webapp.RequestHandler):
    def get(self):
        content = WeeklyUpdate.generate_summary_content([])
        path = os.path.join(TEMPLATE_DIR, 'html_mail.html')
        self.response.out.write(template.render(path, content))

application = webapp.WSGIApplication(
                                     [('/', PreviewWeekly)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
