from urlparse import urlparse, urlunparse
from datetime import datetime, date, timedelta
from flask import g, render_template
import bleach
from markdown import markdown
from tsundiary import app

def valid_date(cur_date):
    """Checks if a certain time is a valid time to post an entry now"""
    return abs(cur_date-date.today()).days <= 2

def their_time():
    """Gets the user's local time based on timezone cookie."""
    return datetime.utcnow() - timedelta(minutes=g.timezone)

def their_date():
    """Returns the user's date based on timezone cookie."""
    return (their_time()-timedelta(hours=4)).date()

@app.template_filter('unix_timestamp')
def unix_timestamp(dt):
    return (dt - datetime(1970, 1, 1)).total_seconds()

def date_from_stamp(ds):
    """Returns a date object from a datestamp string (e.g. 20140120)"""
    yyyy, mm, dd = map(int, [ds[0:4], ds[4:6], ds[6:8]])
    return date(yyyy, mm, dd)

def datestamp(d):
    """Turns a date object into a datestamp (e.g. "20140120")"""
    return d.strftime("%Y%m%d")

@app.template_filter('prettydate')
def nice_date(d):
    """Returns the date formatted prettily.
       e.g.: January 20, 2014"""

    if d:
        return d.strftime("%A, %B %-d, %Y")
    else:
        return "Never!"

@app.template_filter('nicedate')
def pretty_date(d):
    """Returns the date formatted nicely, substituted when possible.
       e.g.: Monday, January 20, 2014
             Today
             Yesterday
             Last Wednesday"""
    if d:
        days = (their_date() - d).days
        if days == 0:
            return "Today"
        elif days == -1:
            # It happens with timezone differences
            return "Tomorrow"
        elif days == 1:
            return "Yesterday"
        elif days == 7:
            return "One week ago"
        elif their_date().year == d.year:
            return d.strftime("%B %-d")
        else:
            return d.strftime("%B %-d, %Y")
    else:
        return "Never!"

def filter_iframe(name, value):
    """Returns True if an iframe is allowed."""
    if name in ['allowfullscreen']:
        return True
    if name == 'src':
        p = urlparse(value)
        print(p.netloc)
        return (not p.netloc) or p.netloc in {'www.youtube.com', 'youtube.com'}
    return False

@app.template_filter('my_markdown')
def my_markdown(t):
    """Turns a tsundiary post into HTML."""
    return bleach.clean(markdown(t, extensions=['nl2br']),
        [
            'p', 'strong', 'em', 'br', 'img', 'ul', 'ol', 'li', 'a',
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote',
            'pre', 'code', 'hr', 'iframe', 'sup', 'sub'
        ],
        {
            'img': ['src', 'alt', 'title'],
            'a': ['href', 'title'],
            'iframe': filter_iframe
        }
    )

@app.template_filter('render_entry')
def render_entry(p):
    """Renders the HTML for a single tsundiary entry."""
    return render_template('entry.html', p=p)

app.jinja_env.globals.update(render_entry=render_entry)

def datestamp_today():
    return datestamp(g.date)

def uidify(string):
    """Turn a string (e.g. a username) into a uid for db prettiness."""
    return ''.join(c for c in string.lower().replace(' ', '-') if c.isalnum())
