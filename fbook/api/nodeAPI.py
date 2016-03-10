from ..db import db
from .api import api
from flask_restful import Resource, reqparse, abort, Api
from .. models import NodeRequest

parser = reqparse.RequestParser()
parser.add_argument('name')
parser.add_argument('ip_addr')
parser.add_argument('email')

class serverRequest(Resource):
	def post(self):
		try:
			args = parser.parse_args();
			# add the new information into request from the request
			req = NodeRequest (name= args['name'], 
			ip_addr= args['ip_addr'], email= args['email'])
			db.session.add(req)
			db.session.commit()

		except Exception as e:
			db.session.rollback()
			print(e)

api.add_resource(serverRequest, '/noderequest/new')