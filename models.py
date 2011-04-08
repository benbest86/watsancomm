import os, re
from google.appengine.ext import db, webapp
from google.appengine.api.mail import EmailMessage
from settings import TEMPLATE_DIR


class ParseError(Exception):
    pass


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
        self.parse()
        super(WeeklyUpdate, self).put()

    @classmethod
    def generate_summary_content(cls, updates):
        content = {}
        for msg in updates:
            for header, text in msg.parse():
                if header not in headers:
                    headers[header] = []
                content[header].append({'sender': msg.sender, 'text': text})
        return content

    @classmethod
    def generate_summary_email(cls, content):
        plain_path = os.path.join(TEMPLATE_DIR, 'plain_text_mail.txt')
        html_path = os.path.join(TEMPLATE_DIR, 'html_mail.html')
        body = webapp.template.render(content, plain_path)
        html = webapp.template.render(content, html_path)
        sender = "weeklysummary@watsancomm.appspotmail.com"
        to = cls.recipients()
        subject = "WatSan Weekly Summary Email - %s" % date.strftime("%d %b %Y")
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

