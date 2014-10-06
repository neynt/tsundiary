from tsundiary.views import *

# For "scroll-down" content loading
@app.route('/+<author_sid>/<datestamp>')
def fetch_next_post(author_sid, datestamp):
    author = User.query.filter_by(sid = author_sid).first()
    if author:
        y, m, d = map(int, datestamp.split('-'))
        hidden_day = calc_hidden_day(author)
        cur_date = date(y, m, d)
        post = (author.posts
               .filter(Post.posted_date < cur_date)
               .order_by(Post.posted_date.desc())
               .first())
        if post:
            return render_template('entry.html', p=post, hidden_day=hidden_day)
        else:
            return 'no more'
    else:
        return page_not_found()

