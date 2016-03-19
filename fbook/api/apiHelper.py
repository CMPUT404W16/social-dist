import requests
import base64
from ..models import *

class ApiHelper():


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
		return '/friends/ec24ed8b3fa04d88917f42b09d64f49b'

	# FILL ME IN
	urlFuncs = {
		'posts' : urlPost,
		'friends': urlFriends
	}

	def createHeaders(self, username, password):
		authDetails = base64.b64encode(username + ":" + password)
		return {'Authorization': 'Basic ' + authDetails}

	def get(self, type, params=None):
		callback = self.urlFuncs[type]		
		if callback != None:
			uri = callback(params)
		
		nodes = RemoteNode.query.all()
		for node in nodes:
			headers = self.createHeaders(node.username, node.password)
			if node.prefix != None:
				url = 'http://' + node.service + node.prefix + uri
			else:
				url = 'http://' + node.service + uri
			print url
			r = requests.get(url, headers=headers)
			print r.text

	# TODO
	def post(self, type, id=None):
		pass

	# Test functionality, uncomment caller in views
	# def test(self):
	# 	url = self.get('friends')
	# 	# print url
	# 	url = "http://floating-sands-69681.herokuapp.com/somepath"
	# 	headers = self.createHeaders('akt', 'sad')
	# 	r = requests.get(url, headers=headers)
	# 	print r.json()
	# 	return r.text
