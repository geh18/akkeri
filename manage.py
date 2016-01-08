# encoding=utf-8

import os
from flask.ext.script import Manager

from app import app, db
from models import User

manager = Manager(app)


if __name__ == '__main__':
    manager.run()
