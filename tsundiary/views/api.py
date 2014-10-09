from tsundiary.views import *

@app.route('/api/my_current_entry')
def api_my_current_entry():
    p = g.user.posts.filter(Post.posted_date == g.date).first()
    if p:
        return json.dumps({ 'timestamp': 'whatever man', 'content': p.content })
    else:
        return json.dumps({ 'timestamp': 'null', 'content': '' })
