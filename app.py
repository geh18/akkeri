# encoding=utf-8

import os
from flask import Flask, render_template
from flask.ext.script import Manager
from flask.ext.bootstrap import Bootstrap
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(
        os.environ.get('APP_SETTINGS', 'config.DevelopmentConfig'))

bootstrap = Bootstrap(app)
db = SQLAlchemy(app)

# from models import User, ...


@app.route('/')
def hello():
    return render_template('hello.html')

if __name__ == '__main__':
    print "For development server, use manage.py"
