from .api import api
from flask_restful import Resource
from bauth import auth

class HelloWorld(Resource):
	decorators = [auth.login_required]

	def get(self):
		return {'hello': 'world'}

api.add_resource(HelloWorld, '/somepath')