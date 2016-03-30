from flask import Flask, render_template, request, current_app
app = Flask(__name__)

import logging, threading, os
logging.disable(logging.FATAL)

@app.template_filter('enumerate')
def do_enumerate(L): return enumerate(L)

@app.route('/')
def index():
    vars = {}
    return render_template('index.html', **vars)

def start():
	T=threading.Thread(None,app.run)
	T.start()

if __name__ == "__main__":
    app.run(debug=True)

