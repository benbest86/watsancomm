WatSanComm README
=================

This is a small project to acheive the very simple aim of aggregating and
sending a weekly email to a list of recipients. Designed to work in 
low-bandwidth settings where logging on to an external service is time
consuming.

The service runs on appengine so please modify app.yaml for your needs if 
you wish to use it.

Currently the app does some very rudimentary parsing with a regular expression
found in the WeeklyUpdate.parse() in models.py. Feel free to modify if you
want different parsing.

Recipients and allowed senders are saved in the MEMBERS variable in settings.py
or optionally in local_settings.py.

TODO
====

*   Notification email if contribution does not parse properly
*   More pretty html email
*   Add ability to parse a markup format (such as markdown) to make things
    more pretty
*   Reminders for recipients at time interval before the weekly summary is
    to be sent out
*   Amalgamate multiple emails from the same sender in the same week to allow
    updates without multiple name entries.
