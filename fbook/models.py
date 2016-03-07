from .db import db
from sqlalchemy.dialects import postgresql
import bleach
from markdown import markdown
from datetime import datetime

from flask.ext import admin
from flask.ext.admin.contrib import sqla
from flask.ext.admin.contrib.sqla import filters

class Permission:
    pass

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username

class Post(db.Model):

    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))
    
    
class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    content = db.Column(db.String(500))


class Image(db.Model):
    __tablename__ = 'images'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    file = 0

    
class Privacy:
    pass


class Friend(db.Model):
    __tablename__ = "friends"
    a_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    b_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    
    def integrityCheck(self, a_id, b_id):
        return a_id == b_id
    
class Follow(db.Model):
    __tablename__ = "follows"
    requester_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    requestee_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    
    def integrityCheck(self, requester_id, requestee_id):
        return requester_id == requestee_id
    

class Node(db.Model):
    __tablename__ = "nodes"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    ip_addr = db.Column(postgresql.INET)
    auth_code = db.Column(db.String(128))
    isRestricted = False
    verified_date = db.Column(db.DateTime)

    def __unicode__(self):
        return self.name

class NodeRequest(db.Model):
    __tablename__ = "nodeRequests"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    ip_addr = db.Column(postgresql.INET)

# class APIRequest:
    # __tablename__ = "apiRequests"
    # id = db.Column(db.Integer, primary_key=True)


# class NodeAPI:
    # __tablename__ = "nodeAPIs"
    # node_id = db.Column(db.Integer, db.ForeignKey('nodes.id'), primary_key=True)
    # request_id = db.Column(db.Integer, db.ForeignKey('apiRequests.id'), primary_key=True)
