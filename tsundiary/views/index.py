from tsundiary.views import *
from tsundiary.prompts import PROMPTS
import hashlib

# Index/home!
@app.route('/', methods=['GET', 'POST'])
def index():
    # handle logouts
    submit_action = request.form.get('action')
    if submit_action == 'logout':
        return logout()

    if g.user:
        current_post = g.user.posts.filter_by(posted_date = g.date).first()
        if current_post:
            current_content = current_post.content
            update_time = unix_timestamp(current_post.update_time)
        else:
            current_content = ""
            update_time = 0

        prompt = PROMPTS[int(hashlib.md5(datestamp(g.date)).hexdigest(), 16) % len(PROMPTS)] % g.user.name

        old_posts = []
        deltas = [(1, "yesterday"), (7, "one week ago"), (30, "30 days ago"),
                  (90, "90 days ago"), (365, "365 days ago")]
        for delta, delta_name in deltas:
            day = g.date - timedelta(days=delta)
            print("checking", day)
            p = g.user.posts.filter_by(posted_date=day).first()
            if p:
                old_posts.append((delta_name, p))

        print(old_posts)

        return render_template(
                'write.html',
                old_posts = old_posts,
                prompt = prompt,
                update_time = update_time,
                current_content = current_content)
    else:
        return render_template('front.html')
