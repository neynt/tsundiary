from tsundiary.views import *

# Stalk a list of users.
@app.route('/stalk/<authors>')
def stalk_list_given(authors):
    authorlist = authors.split(',')
    posts = []

    for authorname in authorlist:
        author = User.query.filter_by(sid = uidify(authorname)).first()

        if not author:
            continue

        latest_post = author.posts.order_by(Post.posted_date.desc()).first()

        hidden_day = calc_hidden_day(author)
        cutoff_day = calc_cutoff_day(author)

        if latest_post:
            posts.append((author, latest_post, hidden_day, cutoff_day))

    return render_template('stalk.html', posts=posts)

# Stalk users.
@app.route('/stalk')
def stalk_list():
    return render_template('stalk.html')
