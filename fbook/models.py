from .db import db
from sqlalchemy.dialects import postgresql
import bleach
from markdown import markdown
from datetime import datetime

from flask.ext import admin
from flask.ext.admin.contrib import sqla
from flask.ext.admin.contrib.sqla import filters

class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password = db.Column(db.String(64))
    authenticated = db.Column(db.Boolean, default=False)

    @property
    def is_authenticated(self):
        return self.authenticated

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.username

    # user is an id int
    def is_follower(self, user):
        t = Follow.query.filter_by(requester_id=self.id,
                                    requestee_id=user).first()
        if t:
            return True
        else:
            return False

    def is_friend(self, user):
        t = Friend.query.filter_by(a_id=self.id, b_id=user).first()
        if t:
            return True
        else:
            t = Friend.query.filter_by(a_id=user, b_id=self.id).first()
            if t:
                return True
            else:
                return False

    def follow(self, user):
        pass

    def unfollow(self, user):
        pass

    def befriend(self, user):
        pass

    def unfriend(self, user):
        pass

    def __repr__(self):
        return '<User %r>' % self.username

class UserRequest(db.Model):
    __tablename__ = 'userRequests'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password = db.Column(db.String(64))


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comments = db.relationship('Comment', backref='post', lazy='dynamic')

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
    name = db.Column(db.String(64))
    ip_addr = db.Column(postgresql.INET)
    email = db.Column(db.String(64), unique=True)
    auth_code = db.Column(db.String(128))
    isRestricted = db.Column(db.Boolean, default=False)
    verified_date = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __unicode__(self):
        return self.name

class NodeRequest(db.Model):
    __tablename__ = "nodeRequests"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    ip_addr = db.Column(postgresql.INET)
    email = db.Column(db.String(64), unique=True)

  

# class APIRequest:
    # __tablename__ = "apiRequests"
    # id = db.Column(db.Integer, primary_key=True)


# class NodeAPI:
    # __tablename__ = "nodeAPIs"
    # node_id = db.Column(db.Integer, db.ForeignKey('nodes.id'), primary_key=True)
    # request_id = db.Column(db.Integer, db.ForeignKey('apiRequests.id'), primary_key=True)
