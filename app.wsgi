import sys
import os.path

home_dir = os.path.expanduser('~')
sys.path.insert(0, home_dir + '/akkeri-flask')

from app import app as application
