#!flask/bin/python3

from flask_script import Manager

from app import app
from app.daemon import scan

manager = Manager(app)

@manager.command
def daemon():
    "Scan junkyards for cars and send emails"
    scan()

if __name__ == "__main__":
    manager.run()
