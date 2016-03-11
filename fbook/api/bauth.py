from flask_httpauth import HTTPBasicAuth
from ..models import Node

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
	node = Node.query.filter_by(username=username).first()
	if node is None:
		return False
	if node.verify_access():
		return node.verify_password(password)
	else:
		return False
