#coding=utf-8
from flask_sqlalchemy import SQLAlchemy

import os
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
def index():
	return render_template('hello.html')

if __name__ == '__main__':
	app.run()
