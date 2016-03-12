from flask_admin import BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.actions import action
from flask import request, url_for, redirect
from ..admin import am
from ..models import *
from flask.ext.login import current_user
import uuid

# Logic for handling and displaying Node Requests
class NodeRequestModelView(ModelView):

	def is_accessible(self):
		if current_user.is_authenticated:
			return current_user.can(Permission.ADMINISTER)

	can_edit = False
	# can_create = False
	column_labels = dict(
		name = "Name",
		username = "User Name",
		password = "Password",
		ip_addr = "IP Address",
		email = "Email Address",
		)
	list_template = "admin/nodeRequest_list.html"

	@action('approve', 'Approve', 'Are you sure you want to approve selected nodes?')
	def action_approve(self, ids):
		try:
			query = NodeRequest.query.filter(NodeRequest.id.in_(ids))

			# Create requests
			nodes = []
			for req in query.all():
				node = 	Node(
					name = req.name, 
					username = req.username,
					password = req.password,
					ip_addr = req.ip_addr,
					email = req.email
					)
				nodes.append(node)
		except Exception as e:
			# No need to rollback, id doesn't exist perhaps?
			# Rare
			print(e)
			return

		try:
			# Add nodes
			db.session.add_all(nodes)
			# Delete requests
			query.delete(synchronize_session='fetch')
			db.session.commit()
		except Exception as e:
			# Problem with db, rollback
			db.session.rollback()
			print(e)

	@expose('/', methods=['post'])
	def approve(self):
		try:
			id = request.form['id']
			req = NodeRequest.query.get(id)

			node = Node(name = req.name,
				username = req.username,
				password = req.password,
				ip_addr = req.ip_addr,
				email = req.email
				)
		except Exception as e:
			# No need to rollback, id doesn't exist perhaps?
			# Rare
			print(e)
			return redirect(url_for('NodeRequest.index_view'))

		try:
			db.session.add(node)
			db.session.delete(req)
			db.session.commit()
		except Exception as e:
			# Problem with db, rollback
			db.session.rollback()
			print(e)

		return redirect(url_for('NodeRequest.index_view'))

class NodeModelView(ModelView):

	def is_accessible(self):
		if current_user.is_authenticated:
			return current_user.can(Permission.ADMINISTER)
	
	can_create = False
	column_labels = dict(
		name = 'Name',
		ip_addr = 'IP Address',
		email = 'Email',
		username = 'User Name',
		password = 'Password',
		isRestricted = 'Is Restricted',
		verified_date = 'Verified Date'
		)

class UserRequestModelView(ModelView):

	def is_accessible(self):
		if current_user.is_authenticated:
			return current_user.can(Permission.ADMINISTER)

	can_edit = False
	can_create = False
	list_template = "admin/userRequest_list.html"

	@action('approve', 'Approve', 'Are you sure you want to approve selected nodes?')
	def action_approve(self, ids):
		try:
			query = UserRequest.query.filter(UserRequest.id.in_(ids))

			# Create requests
			users = []
			for req in query.all():
				user = User(username=req.username,
					password=req.password, host=request.host)
				# TODO Add role ID
				user.set_id()
				users.append(user)

		except Exception as e:
			# No need to rollback, id doesn't exist perhaps?
			# Rare
			print(e)
			return

		try:
			# Add nodes
			db.session.add_all(users)
			# Delete requests
			query.delete(synchronize_session='fetch')
			db.session.commit()
		except Exception as e:
			# Problem with db, rollback
			db.session.rollback()
			print(e)

	@expose('/', methods=['post'])
	def approve(self):
		try:
			id = request.form['id']
			req = UserRequest.query.get(id)

			user = User(username=req.username,
				password=req.password, host=request.host)
			# TODO Add role ID
			user.set_id()
		except Exception as e:
			# No need to rollback, id doesn't exist perhaps?
			# Rare
			print(e)
			return redirect(url_for('UserRequest.index_view'))

		try:
			db.session.add(user)
			db.session.delete(req)
			db.session.commit()
		except Exception as e:
			# Problem with db, rollback
			db.session.rollback()
			print(e)

		return redirect(url_for('UserRequest.index_view'))

class UserModelView(ModelView):

	def is_accessible(self):
		if current_user.is_authenticated:
			return current_user.can(Permission.ADMINISTER)


am.add_view(NodeModelView(Node, db.session, name="Node", category="Nodes", endpoint="Node"))
am.add_view(NodeRequestModelView(NodeRequest, db.session, name="Node Request", category="Nodes", endpoint="NodeRequest"))
am.add_view(UserModelView(User, db.session, name="User", category="Users", endpoint="User"))
am.add_view(UserRequestModelView(UserRequest, db.session, name="User Requests", category="Users", endpoint="UserRequest"))



