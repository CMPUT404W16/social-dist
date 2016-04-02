import requests
import base64
from ..models import *
from flask.ext.login import current_user

class ApiHelper():

	def __init__(self):
		pass

	def urlPost(params):
		if params == None:
			return '/posts'
		elif 'curr_author' in params:
			if 'author_id' in params:
				return '/author/' + str(params['author_id']) + '/posts'
			else:
				return '/author/posts'
		elif 'post_id' in params:
			url = '/posts/' + str(params['post_id'])
			if 'comments' in params:
				url += '/comments'
			return url
		else:
			return '/posts'

	def urlFriends(params):
		if params['author_id']:
			return '/friends/' + params['author_id']
		else:
			print 'No user id provided'

	def urlAuthor(params):
		if params['author_id']:
			return '/author/' + params['author_id']
		else:
			print 'No user id provided'

	# def urlFollowers(params):

	def urlFriendRequest(params):
		return '/friendrequest'

	# FILL ME IN
	urlFuncs = {
		'posts' : urlPost,
		'friends': urlFriends,
		'author': urlAuthor,
		# 'followers': urlFollowers
		'friend_request': urlFriendRequest
	}

	def filterPost(response):
		return response

	def filterFriends(response):
		friends_ids = []
		for res in response:
			friends_ids += res['friends']

		return friends_ids


	def filterAuthors(response):
		return response

	filterFuncs = {
		'posts' : filterPost,
		'friends': filterFriends,
		'author': filterAuthors,
	}

	def createHeaders(self, username, password):
		authDetails = base64.b64encode(username + ":" + password)
		return {'Authorization': 'Basic ' + authDetails}

	def get(self, type, params=None):
		callback = self.urlFuncs[type]
		if callback != None:
			uri = callback(params)

		responses = []
		nodes = RemoteNode.query.all()
		for node in nodes:
			headers = self.createHeaders(node.username, node.password)
			if node.prefix != None:
				url = 'http://' + node.service + node.prefix + uri
			else:
				url = 'http://' + node.service + uri
			#print url
			r = requests.get(url, headers=headers)

			#print r.text

			if r.status_code == 200:
				responses.append(r.json())

		callback = self.filterFuncs[type]
		return callback(responses)

	def post(self, type, body, host, params=None):
		callback = self.urlFuncs[type]
		if callback != None:
			uri = callback(params)

		responses = []
		nodes = RemoteNode.query.all()
		for node in nodes:

			if "http://" + node.service + "/" == host or "http://" + node.service + "/" == current_user.host:

				headers = self.createHeaders(node.username, node.password)
				if node.prefix != None:
					url = 'http://' + node.service + node.prefix + uri
				else:
					url = 'http://' + node.service + uri
				print node.service
				if node.service == 'socialp2p.herokuapp.com':
					url = url + '/'

				print url
				r = requests.post(url, headers=headers, json=body)
				print r.text
				if r.status_code == 200:
					responses.append(r.json())

		return responses


	# Test functionality, uncomment caller in views
	# def test(self):
	# 	# url = self.get('friends')
	# 	# print url
	# 	url = "http://floating-sands-69681.herokuapp.com/somepath"
	# 	headers = self.createHeaders('akt', 'sad')
	# 	r = requests.get(url, headers=headers)
	# 	print r.json()
	# 	return r.text
