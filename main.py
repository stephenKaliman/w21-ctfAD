from bs4 import BeautifulSoup
from flask import Flask, flash, g, make_response, render_template, request, redirect, abort
from os import environ
from redis_namespace import StrictRedis
from uuid import uuid4
import sqlite3

app = Flask(__name__)

DATABASE = '/hkia.db'

app = Flask(__name__)
app.secret_key = b'_p00py1NmyTR00PYjhedjghedgjfsh":{}-=/'
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

def checkin(inpt):
    if (inpt==None): return False
    if (len(inpt)>15): return False
    if (not inpt.isalnum()): return False
    return True

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g.database = sqlite3.connect(DATABASE)
    return db

def makeuser(name, uid, pswd):
    g.db = sqlite3.connect("hkia.db")
    params = (str(uid), str(name), str(pswd))
    uuid = str(uid)
    nam = str(name)
    query = f'select * from users where name=?'
    user = query_db(query, (nam))
    if user is None:
        g.db.execute("INSERT INTO users (uid, name, password) VALUES (?,?,?)", params)
        g.db.commit()
        return True
    else:
        return False

def checklogin(name, pswd):
    g.db = sqlite3.connect("hkia.db")
    nam = str(name)
    pas = str(pswd)
    query = f'select * from users where name=? and password=?'
    user = query_db(query, (nam, pas))
    if user is None:
        return False
    else:
        return True

def query_db(query, args=(), one=False):
    g.db = sqlite3.connect("hkia.db")
    cur = g.db.execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

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

@app.route('/signup', methods=['POST'])
def handle_data():
    name = str(request.form.get('name'))
    pswd = str(request.form.get('pass'))
    uid = uuid4()
    if(not checkin(name)): 
        flash(("name must be 1 to 15 alphanumeric characters"))
        return redirect('/')
    if(not checkin(pswd)): 
        flash(("password must be 1 to 15 alphanumeric characters"))
        return redirect('/')
    if(not makeuser(name, uid, pswd)):
        flash(("user with this name already exists"))
        return redirect('/')
    return redirect(f'/profile/{uid}')

@app.route('/login', methods=['POST'])
def handle():
    name = str(request.form.get('name'))
    pswd = str(request.form.get('pass'))
    if(not checkin(name)):
        flash("name must be 1 to 15 alphanumeric characters")
        return redirect('/')
    if(not checkin(pswd)):
        flash("password must be 1 to 15 alphanumeric characters")
        return redirect('/')
    if(not checklogin(name, pswd)):
        flash("incorrect username or password")
        return redirect('/')
    uid = query_db("select uid from users where name=? and password=?",(name,pswd))
    flash(f"logged in as {name}")
    return redirect(f'/profile/{uid}')


#@app.route('/posts', methods=['POST'])
#def submit():
#        data = request.form['input']
#        uuid = str(uuid4())
#        redis.set(uuid, sanitize(data).encode())
#        return redirect(f'/post/{uuid}')

@app.route('/profile/<uid>')
def profilepage(uid):
    return render_template("index.html")

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

