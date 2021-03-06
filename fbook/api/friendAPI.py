from .api import api
from ..db import db
from .. models import *
from flask_restful import Resource, reqparse
from flask.ext.login import current_user
from flask import request
from bauth import auth
from apiHelper import ApiHelper

helper = ApiHelper()

class friends(Resource):
	decorators = [auth.login_required]
	# a reponse of users friends
	# ask a service http://service/friends/<authorid>
	def get(self, authorid):
		data = {}

		friendsList = []

		a = Friend.query.filter_by(a_id=authorid).all()
		b = Friend.query.filter_by(b_id=authorid).all()
		for friend in a:
			friendsList.append(friend.b_id)
		for friend in b:
			friendsList.append(friend.a_id)

		
		
		data['query'] = 'friends'
		data['friends'] = friendsList

		return data

	# ask a service if anyone in the list is a friend
	# POST to http://service/friends/<authorid>
	def post(self, authorid):
		parser = reqparse.RequestParser()
		parser.add_argument('query')
		parser.add_argument('author')
		parser.add_argument('authors')
		args = parser.parse_args();

		friends = []
		print(request.get_json()['authors'])
		for author_id in request.get_json()['authors']:
			a = Friend.query.filter_by(a_id=author_id, b_id=authorid).all()
			b = Friend.query.filter_by(b_id=author_id, a_id=authorid).all()
			if a or b:
				friends.append(author_id)

		data = {}

		data['query'] = args['query']
		data['author'] = authorid
		data['authors'] = friends

		return data

# Profile API calls
# GET http://service/author/9de17f29c12e8f97bcbbd34cc908f1baba40658e
# Enables viewing of foreign author's profiles
class profile(Resource):
	decorators = [auth.login_required]
	def get(self, authorid):
		data = {}

		user = User.query.filter_by(id=authorid).first_or_404()
		
		data["id"] = user.id
		data["host"] = user.host
		data["displayname"] = user.username
		data["url"] = user.host+"/author/"+user.id

		query = ProfileImageMap.query.filter_by(user_id=user.id).first()
		if (query):
			image_id = query.image_id
			data['image'] = 'http://floating-sands-69681.herokuapp.com/image/' + str(image_id)
		else:
			data['image'] = None

		data["friends"] = []
		friendsList = []

		a = Friend.query.filter_by(a_id=authorid).all()
		b = Friend.query.filter_by(b_id=authorid).all()
		
		for friend in a:
			user = User.query.filter_by(id=friend.b_id).first()
			if user != None:
				friendsList.append(user)
			else:
				user = RemoteUser.query.filter_by(id=friend.b_id).first()
				if user != None:
					friendsList.append(user)

		for friend in b:
			user = User.query.filter_by(id=friend.a_id).first()
			if user != None:
				friendsList.append(user)
			else:
				user = RemoteUser.query.filter_by(id=friend.a_id).first()
				if user != None:
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
# Send a friend request (follow)
#
class friend_request(Resource):
	decorators = [auth.login_required]
	def post(self):
		data = {}
		print "request from remote"
		# parser = reqparse.RequestParser()
		# parser.add_argument("author", type=dict, required=True, help='author not provided')
		# parser.add_argument("friend", type=dict, required=True, help='friend not provided')
		# args = parser.parse_args();
		# author = args.author
		# friend = args.friend
		req = request.get_json(force=True)
		author = req['author']
		friend = req['friend']
		#print author
		#print friend

		#try to add author to remote authors

		print "hey"
		if author['host'] != friend['host']:
			check = RemoteUser.query.filter_by(id=author['id']).first()
			print check
			if check != None:
				a = 10
			else:
				userx = RemoteUser(username=author['displayname'], id=author['id'], host=author['host'])
				db.session.add(userx)
		

		follow = Follow(requester_id=author['id'], requestee_id=friend['id'])

		following = Follow.query.filter_by(requester_id=friend['id'], requestee_id=author['id']).first()
		if following:
			new_friend = Friend(a_id=friend['id'],b_id=author['id'])
			db.session.add(new_friend)

		db.session.add(follow)
		db.session.commit()

		return data, 200

# send two user id's return whether or not they are friends
class friend(Resource):
	decorators = [auth.login_required]
	def get(self, authorid1, authorid2):
		data = {}
		friends = False

		a = Friend.query.filter_by(a_id=authorid2,b_id=authorid1).first()
		b = Friend.query.filter_by(b_id=authorid2,a_id=authorid1).first()

		if a or b:
			friends = True

		friendsList = [authorid1, authorid2]
		
		data['query'] = 'friends'
		data['authors'] = friendsList
		data['friends'] = friends

		return data

api.add_resource(profile, '/api/author/<string:authorid>')
api.add_resource(friends, '/api/friends/<string:authorid>')
api.add_resource(friend, '/api/friends/<string:authorid1>/<string:authorid2>')
api.add_resource(friend_request, '/api/friendrequest')
