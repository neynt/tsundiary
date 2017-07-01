from tsundiary.views import *

@app.route('/toggle_post_hidden', methods=['POST'])
def hide_entry():
    the_date = request.form.get('post_date')
    entry = g.user.posts.filter_by(posted_date=the_date).first()
    if entry:
        print("Changing ", entry.hidden)
        entry.hidden = int(not entry.hidden)
        print("To ", entry.hidden)
        db.session.commit()
        return json.dumps({ 'entry_hidden': entry.hidden })
    else:
        print(the_date)
        return json.dumps({ 'entry_hidden': -1 })
