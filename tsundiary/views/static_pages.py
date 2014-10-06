from tsundiary.views import *

# Route static files
static_file_dir = os.path.dirname(os.path.realpath(__file__)) + '/static'
@app.route('/static/<path:filename>')
def static_file(filename):
    return send_from_directory(static_file_dir, filename)

@app.route('/h-hello...')
def who_am_i():
    return render_template('what-is-this.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/markdown')
def markdown_guide():
    return render_template('markdown-guide.html')

# Google webmaster verification
google = os.environ.get('GOOGLE_WEBMASTER')
if google:
    @app.route('/' + google)
    def submit_to_botnet():
        return "google-site-verification: " + google

