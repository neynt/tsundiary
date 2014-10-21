from tsundiary.views import *

@app.route('/api/my_current_entry')
def api_my_current_entry():
    p = g.user.posts.filter(Post.posted_date == g.date).first()
    if p:
        return json.dumps({ 'timestamp': unix_timestamp(p.update_time), 'content': p.content, "datestamp": datestamp(p.posted_date) })
    else:
        return json.dumps({ 'timestamp': 'null', 'content': '' })
