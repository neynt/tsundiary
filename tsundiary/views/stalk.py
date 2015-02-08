from tsundiary.views import *

# Stalk a list of authors.
#@app.route('/stalk')
def stalk_list_given():
    if not g.user:
        return page_not_found()
    if not g.user.stalks:
        g.user.stalks = ''

    victims = g.user.stalks.split(',')
    posts = defaultdict(list)

    for victim_name in victims:
        author = User.query.filter_by(sid = uidify(victim_name)).first()

        if not author:
            continue

        oldest_date = their_date() - timedelta(days=2)

        hidden_day = calc_hidden_day(author)
        cutoff_day = calc_cutoff_day(author)
        latest_posts = author.posts.order_by(Post.posted_date.desc()).filter(Post.posted_date >= oldest_date).all()

        if latest_posts:
            for p in latest_posts:
                posts[p.posted_date].append((author, p, hidden_day, cutoff_day))

    posts_by_date = []
    for d in sorted(posts.keys(), reverse=True):
        posts_by_date.append((d, posts[d]))

    return render_template('stalk.html', posts_by_date=posts_by_date)

# Add a user to a user's stalk list.
#@app.route('/stalkadd', methods=['POST'])
def stalk_list_add():
    victim = request.form.get('victim')
    if not g.user:
        return page_not_found()

    stalks = g.user.stalks or ''
    cur_victims = stalks.split(',')
    if victim not in cur_victims:
        g.user.stalks = stalks + "," + uidify(victim)
        db.session.commit()

    return redirect('/stalk')

# Remove a user from a user's stalk list.
#@app.route('/stalkdel/<victim>', methods=['GET'])
def stalk_list_del(victim):
    del_author = victim
    if not g.user:
        return page_not_found()
    authorlist = g.user.stalks.split(',')
    authorlist = [a for a in authorlist if uidify(a) != uidify(del_author)]
    g.user.stalks = ','.join(authorlist)
    db.session.commit()
    return redirect('/stalk')
