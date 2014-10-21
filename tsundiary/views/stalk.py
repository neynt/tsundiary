from tsundiary.views import *

# Stalk a list of authors.
@app.route('/stalk/<authors>')
def stalk_list_given(authors):
    authorlist = authors.split(',')
    posts = defaultdict(list)

    # Save stalks
    if g.user:
        g.user.stalks = authors
        db.session.commit()

    for authorname in authorlist:
        author = User.query.filter_by(sid = uidify(authorname)).first()

        if not author:
            continue

        hidden_day = calc_hidden_day(author)
        cutoff_day = calc_cutoff_day(author)

        latest_posts = author.posts.order_by(Post.posted_date.desc()).filter(Post.posted_date <= hidden_day).limit(1).all()

        if latest_posts:
            for p in latest_posts:
                posts[p.posted_date].append((author, p, hidden_day, cutoff_day))

    posts_by_date = []
    for d in sorted(posts.keys(), reverse=True):
        posts_by_date.append((d, posts[d]))

    return render_template('stalk.html', posts_by_date=posts_by_date)

# Add a user to a user's stalk list.
@app.route('/stalkadd', methods=['POST'])
def stalk_list_add():
    add_author = request.form.get('victim')
    if not g.user:
        return page_not_found()
    g.user.stalks += "," + add_author
    db.session.commit()
    return redirect('/stalk')

# Remove a user from a user's stalk list.
@app.route('/stalkdel', methods=['POST'])
def stalk_list_del():
    del_author = request.form.get('victim')
    if not g.user:
        return page_not_found()
    authorlist = g.user.stalks.split(',')
    authorlist = [a for a in authorlist if uidify(a) != uidify(del_author)]
    g.user.stalks = ','.join(authorlist)
    db.session.commit()
    return redirect('/stalk')

# Stalk users.
@app.route('/stalk')
def stalk_list():
    if g.user and g.user.stalks:
        return stalk_list_given(g.user.stalks)
    elif g.user:
        return render_template('stalk.html')
    else:
        return page_not_found()
