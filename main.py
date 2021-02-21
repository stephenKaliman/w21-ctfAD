from bs4 import BeautifulSoup
from flask import Flask, make_response, render_template, request, redirect, abort
from os import environ
from redis_namespace import StrictRedis
from uuid import uuid4

app = Flask(__name__)
level = 2
redis = StrictRedis(
        host=environ.get('REDIS_HOST', 'localhost'),
        port=environ.get('REDIS_PORT', '6379'),
        namespace=f'{level}:')

#def sanitize(data):
#        if level == 2:
#                return f'<textarea readonly="true">{data}</textarea>'
#        elif level == 3:
#                soup = BeautifulSoup(data)
#                for script in soup.find_all('script'):
#                        script.extract()
#                return soup.renderContents().decode()
#        else:
#                return data

@app.route('/')
def index():
        return render_template('index.html')

@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered bpage for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


#@app.route('/posts', methods=['POST'])
#def submit():
#        data = request.form['input']
#        uuid = str(uuid4())
#        redis.set(uuid, sanitize(data).encode())
#        return redirect(f'/post/{uuid}')

#@app.route('/post/<uuid>')
#def level1(uuid):
#        if redis.exists(uuid):
#                resp = make_response(render_template('post.html', post=redis.get(uuid).decode()))
#                if level == 4:
#                        resp.headers['Content-Security-Policy'] = 'script-src google.com *.google.com'
#                return resp
#        abort(404)

if __name__ == '__main__':
        app.run(host='0.0.0.0', port=8000)

