import os
ROOT_PATH = os.path.join(os.path.dirname(__file__))
# List of callables that know how to import templates from various sources.
TEMPLATE_DIR = os.path.join(ROOT_PATH, 'templates')

MEMBERS = (
        ('benbest@example.com', 'Ben Best'),
        ('user2@example.com', 'User 2'),
)

# integer from 0 to 6 where Monday is 0 and Sunday is 6
# like the date.weekday() function
# http://docs.python.org/library/datetime.html#datetime.date.weekday
# the weekly email is generated and sent at 23:59 of this day.
CUTOFF_DAY = 6

# import from local_settings - proper email addresses will be here
from local_settings import *
