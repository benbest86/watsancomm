import os, re, logging
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from google.appengine.dist import use_library
use_library('django', '1.2')
from datetime import date
from google.appengine.ext import db, webapp
from google.appengine.ext.webapp import template
from google.appengine.api.mail import EmailMessage
from settings import TEMPLATE_DIR, MEMBERS


class ValidationError(Exception):
    pass

class ParseError(Exception):
    pass

members_dict = dict(MEMBERS)

class WeeklyUpdate(db.Model):
    sender = db.StringProperty(required=True)
    html_body = db.TextProperty()
    plain_body = db.TextProperty()
    datetime_received_at = db.DateTimeProperty(auto_now_add=True)

    def parse(self):
        """
        Takes input like
        *** Header 1 ***
        text under header 1

        *** Header 2 ***
        text under header 2

        and returns
        [('Header 1', 'text under header 1'), ('Header 2', 'text under header 2')]
        """
        parse_re = re.compile(r'\*\*\*(.*?)\*\*\*\n([^*]*)')
        body = self.plain_body or self.html_body
        if body is None:
            return ""
        try:
            parsed_body = parse_re.findall(body)
        except Exception, e:
            raise ParseError("Failed to parse the message.")
        return parsed_body

    def put(self):
        try:
            self.parse()
        except ParseError:
            raise ValidationError("Failed to parse message.")
        if self.sender not in members_dict:
            raise ValidationError("The sender %s is not a recognized member." % self.sender)
        super(WeeklyUpdate, self).put()

    @classmethod
    def generate_summary_content(cls, updates):
        content = {}
        for msg in updates:
            for header, text in msg.parse():
                if header not in content:
                    content[header] = []
                content[header].append({'sender': msg.sender, 'text': text})
        return content

    @classmethod
    def generate_summary_email(cls, content):
        plain_path = os.path.join(TEMPLATE_DIR, 'plain_text_mail.txt')
        html_path = os.path.join(TEMPLATE_DIR, 'html_mail.html')
        body = template.render(plain_path, {'content': content})
        html = template.render(html_path, {'content': content})
        sender = "weeklysummary@watsancomm.appspotmail.com"
        to = cls.recipients()
        subject = "WatSan Weekly Summary Email - %s" % date.today().strftime("%d %b %Y")
        email = EmailMessage(
                body=body,
                html=html,
                sender=sender,
                to=to,
                subject=subject,
                )
        return email

    @classmethod
    def recipients(cls):
        return ['ben.best@gmail.com',]

