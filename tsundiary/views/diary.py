from tsundiary.views import *

def render_diary(author, posts, title="Recent entries"):
    hidden_day = calc_hidden_day(author)
    cutoff_day = calc_cutoff_day(author)

    # Generate months/years that the user actually posted something
    # e.g. 2014: Jan Feb Mar May
    dates = defaultdict(set)
    written_dates = db.session.query(Post.posted_date).filter(Post.user == author).all()
    for r in written_dates:
        d = r[0]
        dates[d.year].add(d.month)

    print("### Someone's trying to look at ", hidden_day)

    return render_template(
            "diary.html",
            author = author,
            posts = posts,
            hidden_day = hidden_day,
            cutoff_day = cutoff_day,
            dates = dates,
            month_name = calendar.month_name,
            title = title
            )

# A single page from a user's diary.
@app.route('/~<author_sid>/<int:year>/<int:month>/<int:day>')
def diary_day(author_sid, year, month, day):
    author = User.query.filter_by(sid = uidify(author_sid)).first()
    if author:
        try:
            the_date = date(year, month, day)
        except ValueError:
            return page_not_found()
        else:
            post = author.posts.filter(Post.posted_date == the_date).first()
            return render_diary(author, [post])
    else:
        return page_not_found()

# A certain selection of dates from a user's diary.
@app.route('/~<author_sid>/<int:year>/<int:month>')
def diary_month(author_sid, year, month):
    author = User.query.filter_by(sid = uidify(author_sid)).first()
    if author:
        try:
            min_date = date(year, month, 1)
            max_date = date(year, month, calendar.monthrange(year, month)[1])
        except ValueError:
            return page_not_found()
        else:
            posts = author.posts\
                    .filter(Post.posted_date >= min_date)\
                    .filter(Post.posted_date <= max_date)\
                    .order_by(Post.posted_date.asc())\
                    .all()
            return render_diary(author, posts, min_date.strftime('%B %Y'))
    else:
        return page_not_found()

# Custom commands
@app.route('/~<author_sid>/<command>')
def diary_special(author_sid, command):
    author = User.query.filter_by(sid = uidify(author_sid)).first()
    if author:
        if command == 'all':
            posts = author.posts.order_by(Post.posted_date.desc()).all()
            return render_diary(author, posts, "All entries")
        else:
            return page_not_found()
    else:
        return page_not_found()

# Last secret_days + 1 entries of a user's diary.
@app.route('/~<author_sid>')
def diary(author_sid):
    # Dict of year: [list months]
    author = User.query.filter_by(sid = uidify(author_sid)).first()
    if author:
        posts = (author.posts.order_by(Post.posted_date.desc())
                 .limit(max(5, author.secret_days+3)).all())
        return render_diary(author, posts)
    else:
        return page_not_found()
