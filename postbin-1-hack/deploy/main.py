from bs4 import BeautifulSoup
from flask import Flask, flash, make_response, render_template, request, redirect, abort
from os import environ
from redis_namespace import StrictRedis
from uuid import uuid4
import re

app = Flask(__name__)
level = 3
redis = StrictRedis(
	host=environ.get('REDIS_HOST', 'localhost'),
	port=environ.get('REDIS_PORT', '6379'),
	namespace=f'{level}:')

triggers = ["script", "onabort", "onblur", "onchange", "onclick", "ondblclick",
        "ondragdrop", "onerror", "onfocus", "onkeydown", "onkeypress",
        "onkeyup", "onload", "onmousedown", "onmousemove", "onmouseout",
        "onmouseover", "onmouseup", "onmove", "onreset", "onresize", "onselect",
        "onsubmit", "onunload", "javascript"]
camelTriggers = ["Script", "onAbort", "onBlur", "onChange", "onClick", "onDblClick",
        "onDragDrop", "onError", "onFocus", "onKeyDown", "onKeyPress",
        "onKeyUp", "onLoad", "onMouseDown", "onMouseMove", "onMouseOut",
        "onMouseOver", "onMouseUp", "onMove", "onReset", "onResize", "onSelect",
        "onSubmit", "onUnload", "Javascript", "javaScript", "JavaScript"]


def sanitize(data):
        if (level == 1):
            for trig in triggers:
                Trig = "O"+trig[1:]
                data = data.replace(trig,"")
                data = data.replace(Trig,"")
            for trig in camelTriggers:
                Trig = "O"+trig[1:]
                data=data.replace(trig,"")
                data=data.replace(Trig,"")
                #classic cAsE dOdGiNg
        elif (level == 2):
            for trig in triggers:
                data = re.sub(trig,"",data, flags=re.IGNORECASE)
                #classic wedging
        elif (level == 3):
            for trig in triggers:
                while(re.search(trig,data,flags=re.IGNORECASE)):
                    data=re.sub(trig,"",data, flags=re.IGNORECASE)
                    #this took way too long to find <object data=java&#0115;cript:alert(1)> *
        elif (level == 4):
            data=re.sub(r"[a-zA-Z]","",data)
        return data

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/posts', methods=['POST'])
def submit():
	data = request.form['input']
	uuid = str(uuid4())
	redis.set(uuid, sanitize(data).encode())
	return redirect(f'/post/{uuid}')

@app.route('/post/<uuid>')
def level1(uuid):
	if redis.exists(uuid):
		resp = make_response(render_template('post.html', post=redis.get(uuid).decode()))
		if level == 5:
			resp.headers['Content-Security-Policy'] = 'script-src google.com *.google.com'
		return resp
	abort(404)

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8000)
