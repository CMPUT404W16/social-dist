from .api import api
from ..db import db
from .. models import Friend, User
from flask_restful import Resource, reqparse
from flask.ext.login import current_user


class friends(Resource):
	# a reponse if friends or not
	# ask a service http://service/friends/<authorid>
	def get(self, authorid):
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

		return data

	#
	# NOT DONE
	#
	# ask a service if anyone in the list is a friend
	# POST to http://service/friends/<authorid>
	def post(self, authorid):
		parser = reqparse.RequestParser()
		parser.add_argument('fid')
		args = parser.parse_args();

		data = {}

		data['args'] = args['fid']

		return 

# Profile API calls
# GET http://service/author/9de17f29c12e8f97bcbbd34cc908f1baba40658e
# Enables viewing of foreign author's profiles
class profile(Resource):
	def get(self, authorid):
		data = {}

		user = User.query.filter_by(id=authorid).first()
		data["id"] = user.id
		data["host"] = user.host
		data["displayname"] = user.username
		data["url"] = user.host+"/author/"+user.id

		data["friends"] = []
		friendsList = []

		a = Friend.query.filter_by(a_id=authorid).all()
		b = Friend.query.filter_by(b_id=authorid).all()
		for friend in a:
			user = User.query.filter_by(id=friend.b_id).first()
			friendsList.append(user)
		for friend in b:
			user = User.query.filter_by(id=friend.a_id).first()
			friendsList.append(user)

		for friend in friendsList:
			usr = {}
			usr["id"] = friend.id
			usr["host"] = friend.host
			usr["displayname"] = friend.username
			usr["url"] = user.host+"/author/"+user.id
			data["friends"].append(usr)

		return data

#
# NOT DONE
#
class friend_request(Resource):
	def post(self):
		parser = reqparse.RequestParser()
		parser.add_argument('fid')
		args = parser.parse_args();

		data = {}

		data['query'] = 'friendrequest'

		author = {}
		author['id'] = current_user.id
		author['host'] = current_user.host
		author['displayname'] = current_user.username

		user = User.query.filter_by(id=args['fid']).first()
		friend = {}
		friend['id'] = user.id
		friend['host'] = user.host
		friend['displayname'] = user.username

		return data

api.add_resource(profile, '/api/author/<string:authorid>')
api.add_resource(friends, '/api/friends/<string:authorid>')
api.add_resource(friend_request, '/api/friendrequest')
