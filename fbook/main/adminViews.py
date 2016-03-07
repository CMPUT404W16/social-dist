from flask_admin import BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.actions import action
from flask import request, url_for, redirect
from ..admin import am
from ..models import *

class NodeRequestModelView(ModelView):
	can_edit = False
	# can_create = False
	# can_delete = False
	column_labels = dict(
		name = "Name",
		ip_addr = "IP Address"
		)
	list_template = "admin/nodeRequest_list.html"

	@action('approve', 'Approve', 'Are you sure you want to approve selected nodes?')
	def action_approve(self, ids):
		try:
			query = NodeRequest.query.filter(NodeRequest.id.in_(ids))

			# Create requests
			nodes = []
			for req in query.all():
				node = 	Node(name = req.name, 
					ip_addr = req.ip_addr,
					auth_code = "some code"
					)
				nodes.append(node)

			# Add nodes
			db.session.add_all(nodes)
			# Delete requests
			query.delete(synchronize_session='fetch')
			db.session.commit()
		except Exception as e:
			db.session.rollback()
			print(e)

	@expose('/', methods=['post'])
	def approve(self):
		try:
			id = request.form['id']
			req = NodeRequest.query.get(id)

			node = Node(name = req.name,
				ip_addr = req.ip_addr,
				auth_code = "bleh"
				)

			db.session.add(node)
			db.session.delete(req)
			db.session.commit()
		except Exception as e:
			db.session.rollback()
			print(e)

		return redirect(url_for('NodeRequest.index_view'))

am.add_view(ModelView(Node, db.session, name="Node", category="Nodes", endpoint="Node"))
am.add_view(NodeRequestModelView(NodeRequest, db.session, name="Node Request", category="Nodes", endpoint="NodeRequest"))