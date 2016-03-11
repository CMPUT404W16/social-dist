from ..db import db
from .api import api
from flask_restful import Resource, reqparse, abort, Api
from ..models import NodeRequest

parser = reqparse.RequestParser()
parser.add_argument('name')
parser.add_argument('username')
parser.add_argument('password')
parser.add_argument('email')
parser.add_argument('ip_addr')

class serverRequest(Resource):
	def post(self):
		try:
			args = parser.parse_args();
			# add the new information into request from the request
			req = NodeRequest (name= args['name'], username= args['username'], 
				password = args['password'], email= args['email'], ip_addr=args['ip_addr'])
			db.session.add(req)
			db.session.commit()

		except Exception as e:
			db.session.rollback()
			print(e)

api.add_resource(serverRequest, '/noderequest/new')