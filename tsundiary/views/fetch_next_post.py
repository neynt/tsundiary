from datetime import date

from flask import render_template

from tsundiary import app
from tsundiary.views import page_not_found
from tsundiary.models import User, Post

# For "scroll-down" content loading
@app.route('/+<author_sid>/<datestamp>')
def fetch_next_post(author_sid, datestamp):
    author = User.query.filter_by(sid = author_sid).first()
    if author:
        y, m, d = map(int, datestamp.split('-'))
        cur_date = date(y, m, d)
        post = (author.posts
               .filter(Post.posted_date < cur_date)
               .order_by(Post.posted_date.desc())
               .first())
        if post:
            return render_template('entry-base.html', p=post)
        else:
            return 'no more'
    else:
        return page_not_found()
