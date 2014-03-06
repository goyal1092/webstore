from flask.ext.script import Manager
from app import db

from flask import Flask
app = Flask(__name__)

manager = Manager(app)

@manager.command
def create():
    ''' Create Database Tables '''
    db.create_all()

@manager.command
def drop():
    ''' Drop Database Tables '''
    db.drop_all()

@manager.command
def recreate():
    ''' Drop and Create again  '''
    drop()
    create()

if __name__ == "__main__":
    manager.run()
