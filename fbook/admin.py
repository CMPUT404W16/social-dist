from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin, AdminIndexView, expose
from flask import redirect
from models import *
from flask.ext.login import current_user

class MyAdminIndexView(AdminIndexView):

	@expose('/')
	def index(self):
		if not current_user.is_authenticated:
			return redirect('/')
		return super(MyAdminIndexView, self).index()


am = Admin(index_view=MyAdminIndexView())

