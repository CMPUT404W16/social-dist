from .api import api
from ..db import db
from .. models import Friend, User
from flask_restful import Resource
import json
from flask.ext.login import current_user


class Friends(Resource):
	# a reponse if friends or not
	# ask a service http://service/friends/<authorid>
	def get(self, authorid):
		print("hi")
		data = {}
		friends = False

		a = Friend.query.filter_by(a_id=current_user.id,b_id=authorid).first()
		b = Friend.query.filter_by(b_id=current_user.id,a_id=authorid).first()

		if a or b:
			friends = True

		friendsList = [current_user.id, authorid]
		
		data['query'] = 'friends'
		data['authors'] = friendsList
		data['friends'] = friends

		return json.dumps(data)

	# ask a service if anyone in the list is a friend
	# POST to http://service/friends/<authorid>
	def post(self, authorid):
		data = {}
		return json.dumps(data)

api.add_resource(Friends, '/api/friends/<string:authorid>')
