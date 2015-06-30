import os

from flask import render_template, send_from_directory, request

from tsundiary import app

# Route static files
static_file_dir = os.path.join(app.root_path, 'static')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(static_file_dir, "favicon.ico",
            mimetype='image/vnd.microsoft.icon')

@app.route('/favicon.png')
def favicon_png():
    return send_from_directory(static_file_dir, "favicon.png")

@app.route('/static/<path:filename>')
def static_file(filename):
    return send_from_directory(static_file_dir, filename)

@app.route('/robots.txt')
def static_from_root():
    return send_from_directory(static_file_dir, request.path[1:])

@app.route('/what-is-this')
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
