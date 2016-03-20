#!/usr/bin/env python
import os
from app import app
from fbook import db
from fbook.models import User, Role, Post
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand
from config import config as app_conf

manager = Manager(app)
migrate = Migrate(app, db)

def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Post=Post)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


if __name__ == '__main__':
    manager.run()
