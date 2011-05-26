WatSanComm README
=================

This is a small project to acheive the very simple aim of aggregating and
sending a weekly email to a list of recipients. Designed to work in 
low-bandwidth settings where logging on to an external service is time
consuming.

The service runs on appengine so please modify app.yaml for your needs if 
you wish to use it.

Currently the app does some very rudimentary parsing with a regular expression
found in the WeeklyUpdate.parse() in models.py. It parses a header and the text
under that header. Feel free to modify if you want different parsing. The
parsed text is then fed through markdown for the html email body.

Recipients and allowed senders are saved in the MEMBERS variable in settings.py
or optionally in local_settings.py.

Requires markdown (and thus elementtree) for pretty emails, but degrades
(relatively) gracefully.

TODO
====

*   Notification email if contribution does not parse properly
*   More pretty html email
*   <del>Add ability to parse a markup format (such as markdown) to make things
    more pretty</del>
*   <del>Reminders for recipients at time interval before the weekly summary is
    to be sent out</del>
*   <del>Amalgamate multiple emails from the same sender in the same week to
    allow updates without multiple name entries.</del>
