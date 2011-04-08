import os, re, logging
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from google.appengine.dist import use_library
use_library('django', '1.2')
from datetime import date, datetime, timedelta
from google.appengine.ext import db, webapp
from google.appengine.ext.webapp import template
from google.appengine.api.mail import EmailMessage
from settings import TEMPLATE_DIR, MEMBERS, CUTOFF_DAY


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
                # use members_dict.get in case the sender has been removed from the MEMBERS list since
                # they sent an email to the list (although this is unlikely).
                content[header].append({'sender': members_dict.get(msg.sender, msg.sender), 'text': text})
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

    @classmethod
    def get_weekly_updates(cls, ref_date=None):
        """
        Gets all weekly updates for the week the given timestamp belongs to.
        """
        query = cls.all()
        if ref_date is None:
            ref_date = date.today()
        date_diff = ref_date.weekday() - CUTOFF_DAY
        if date_diff <= 0:
            # we have wrapped around the week so add 6 days
            t_delta = timedelta(date_diff + 6)
        elif date_diff > 0:
            # remove one day from the diff so we don't get a one day overlap
            # with last week
            t_delta = timedelta(date_diff - 1)
        start_datetime = datetime.fromordinal((ref_date.toordinal())) - t_delta
        # filter out only updates received after the start time
        query.filter('datetime_received_at >=', start_datetime)
        # order earliest to latest
        query.order('datetime_received_at')
        return query
