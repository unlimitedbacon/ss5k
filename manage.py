#!flask/bin/python3

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from app import app, db
from app.daemon import scan

manager = Manager(app)

migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)

@manager.command
def daemon():
    "Scan junkyards for cars and send emails"
    scan()

if __name__ == "__main__":
    manager.run()
