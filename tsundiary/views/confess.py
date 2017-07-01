from datetime import datetime, timedelta
import json

from flask import request, g

from tsundiary import app
from tsundiary.utils import unix_timestamp, date_from_stamp, valid_date
from tsundiary.models import Post, db

# Updating diary content
@app.route('/confess', methods=['POST'])
def confess():
    content = request.form.get('content')
    try:
        cur_date = date_from_stamp(request.form.get('cur_date'))
    except ValueError:
        print("h-help!! i can't handle the ",
              request.form.get('cur_date'),
              ", onii-chan!!")
        return json.dumps({
            'success': 0,
            'message': "w-what are you trying to do to me???"
        })
    if not valid_date(cur_date):
        return json.dumps({
            'success': 0,
            'message': "... you want to go on a DATE with me!?"
        })
    elif len(content) == 0:
        p = g.user.posts.filter_by(posted_date = cur_date)
        if p:
            p.delete()
            db.session.commit()
        combo = 0

        return_success = 1
        return_message = "deleted!"
        return_timestamp = unix_timestamp(datetime.now())

    elif len(content) > 20000:
        return json.dumps({
            'success': 0,
            'message': "onii-chan, it's too big! "
                       "you're gonna split me in half!"
        })

    else:
        new_post = Post(g.user.sid, content, cur_date)
        new_post.update_time = datetime.now()
        db.session.merge(new_post)

        db.session.commit()

        return_success = 1
        return_message = "saved!"
        return_timestamp = unix_timestamp(new_post.update_time)

    # Update number of entries
    g.user.num_entries = g.user.posts.count()
    # Update latest post date
    g.user.latest_post_date = cur_date
    # Update combo
    #combo = 1
    #cd = cur_date - timedelta(days = 1)
    #while g.user.posts.filter_by(posted_date = cd).first():
    #    combo += 1
    #    cd -= timedelta(days = 1)
    #g.user.combo = combo
    db.session.commit()

    return json.dumps({
        'success': return_success,
        'message': return_message,
        'timestamp': return_timestamp,
        'num_entries': g.user.num_entries
    })
