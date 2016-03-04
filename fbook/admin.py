from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin
from models import *

admin = Admin()

def configureAdmin(app):
	admin.init_app(app)
	admin.add_view(ModelView(User, db.session))
	admin.add_view(ModelView(Node, db.session))
