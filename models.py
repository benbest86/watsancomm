import re
from google.appengine.ext import db, webapp
from google.appengine.api.mail import EmailMessage


class ParseError(Exception):
    pass

parse_re = re.compile(r'\*\*\*(.*?)\*\*\*\n([^*]*)')
class WeeklyUpdate(db.Model):
    sender = db.StringProperty(required=True)
    html_body = db.TextProperty()
    plain_body = db.TextProperty()
    datetime_received_at = db.DateTimeProperty(auto_now_add=True)

    def parse(self):
        body = self.plain_body or self.html_body
        if body is None:
            return ""
        try:
            parsed_body = parse_re.findall(body)
        except Exception, e:
            raise ParseError("Failed to parse the message.")
        return parsed_body

    def put(self):
        self.parse()
        super(WeeklyUpdate, self).put()
