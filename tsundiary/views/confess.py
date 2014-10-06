from tsundiary.views import *

# Updating content
@app.route('/confess', methods=['POST'])
def confess():
    content = request.form.get('content').strip()
    try:
        cur_date = date_from_stamp(request.form.get('cur_date'))
    except:
        return "w-what are you trying to do to me???"
    if valid_date(cur_date):
        return_message = ""

        if 0 < len(content) <= 20000:
            new_post = Post(g.user.sid, content, cur_date)
            db.session.merge(new_post)
            combo = 1
            return_message = "saved!"
        elif len(content) == 0:
            p = g.user.posts.filter_by(posted_date = cur_date)
            if p:
                p.delete()
            combo = 0
            return_message = "deleted!"
        else:
            return_message = "onii-chan, it's too big! you're gonna split me in half!"

        db.session.commit()

        # Update number of entries
        g.user.num_entries = g.user.posts.count()
        # Update latest post date
        g.user.latest_post_date = cur_date
        # Update combo
        cd = cur_date - timedelta(days = 1)
        while g.user.posts.filter_by(posted_date = cd).first():
            combo += 1
            cd -= timedelta(days = 1)
        g.user.combo = combo

        db.session.commit()

        return return_message
    else:
        return "... you want to go on a DATE with me!?"
