from flask_httpauth import HTTPBasicAuth
from ..models import Node

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
	print(username, password)
	node = Node.query.filter_by(username=username).first()
	if not node:
		return False
	return node.verify_password(password)
