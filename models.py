import os, re, logging


os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from google.appengine.dist import use_library
use_library('django', '1.2')
from datetime import date, datetime, timedelta
from google.appengine.ext import db, webapp
from google.appengine.ext.webapp import template
from google.appengine.api.mail import EmailMessage
from settings import TEMPLATE_DIR, MEMBERS, CUTOFF_DAY

# try importing markdown - if it fails
# make the markdown function simply escape
# the input and return it
try:
    from markdown import markdown
except:
    import cgi
    def markdown(text):
        return cgi.escape(text)

class ValidationError(Exception):
    pass

class ParseError(Exception):
    pass

members_dict = dict(MEMBERS)
# from http://www.noah.org/wiki/RegEx_Python
email_re = re.compile(r'[a-zA-Z0-9+_\-\.]+@[0-9a-zA-Z][.-0-9a-zA-Z]*.[a-zA-Z]+')

class WeeklyUpdate(db.Model):
    sender = db.StringProperty(required=True)
    html_body = db.TextProperty()
    plain_body = db.TextProperty()
    datetime_received_at = db.DateTimeProperty(auto_now_add=True)

    def __init__(self, *args, **kwargs):
        # turn sender into an email address alone:
        if 'sender' in kwargs:
            m = email_re.search(kwargs['sender'])
            if m:
                kwargs['sender'] = m.group()
        return super(WeeklyUpdate, self).__init__(*args, **kwargs)

    def parse(self):
        """
        Takes input like
        ### Header 1 ###
        text under header 1

        ### Header 2 ###
        text under header 2

        and returns
        [('Header 1', 'text under header 1', '###'), ('Header 2', 'text under header 2', '')]

        If using findall. Ignore the third group, just necessary for matching.
        """
        parse_re = re.compile(r'###(.*?)###(.*?)(?=(###|\Z))', re.DOTALL)
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
        return super(WeeklyUpdate, self).put()

    @classmethod
    def generate_summary_content(cls, updates):
        content = {}
        for msg in updates:
            for header, text, garbage in msg.parse():
                # do some sort of standardizing of case and whitespace to avoid duplicate headers
                header = header.strip().title()
                if header not in content:
                    content[header] = {}
                # use members_dict.get in case the sender has been removed from the MEMBERS list since
                # they sent an email to the list (although this is unlikely).
                sender = members_dict.get(msg.sender, msg.sender)
                if sender not in content[header]:
                    content[header][sender] = {'text':text, 'html': markdown(text)}
                else:
                    content[header][sender]['text'] += text
                    content[header][sender]['html'] += markdown(text)
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
        return members_dict.keys()

    @classmethod
    def missing_updates(cls):
        rs = cls.recipients()
        updates = cls.get_weekly_updates()
        for u in updates:
            try:
                rs.remove(u.sender)
            except ValueError:
                # we may have already removed them if they've sent two emails
                logging.warning("Tried to remove %s from recipients but they didn't exist. Have they sent twice?" % u.sender)
        return rs

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
    
    @classmethod
    def generate_reminder_email(cls):
        plain_path = os.path.join(TEMPLATE_DIR, 'plain_text_reminder.txt')
        html_path = os.path.join(TEMPLATE_DIR, 'html_reminder.html')
        body = template.render(plain_path, {})
        html = template.render(html_path, {})
        sender = "weekly@watsancomm.appspotmail.com"
        bcc = cls.missing_updates()
        subject = "WatSan Weekly: Reminder Email"
        email = EmailMessage(
                body=body,
                html=html,
                sender=sender,
                bcc=bcc,
                subject=subject,
                )
        return email
