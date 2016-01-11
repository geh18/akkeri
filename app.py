# encoding=utf-8

import os
from flask import Flask, render_template
from flask.ext.script import Manager
from flask.ext.bootstrap import Bootstrap
from flask.ext.sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from akkeri.decorators import templated

app = Flask(__name__)
app.config.from_object(
        os.environ.get('APP_SETTINGS', 'config.DevelopmentConfig'))

bootstrap = Bootstrap(app)
db = SQLAlchemy(app)

import models

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return models.User.query.get(int(id))

from views.admin import setup_admin
admin = setup_admin(app, db, login_manager)

from views.akkeri import index


if __name__ == '__main__':
    print "For development server, use"
    print "  manage.py runserver --host=0.0.0.0 --port=xxxx"
