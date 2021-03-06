from .db import db
from sqlalchemy.dialects import postgresql
import bleach
from markdown import markdown
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

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
    id = db.Column(db.Integer(), primary_key=True)
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
    """
    User Model.

    :param int id: Unique user id.
    :param str username: Unique username.
    :param int role_id: The id of the user's role.
    :param str password: The password of the user.
    :param bool authenticated: Whether the user is authenticated.
    """

    __tablename__ = 'users'
    id = db.Column(db.String(128), unique=True, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password = db.Column(db.String(128))
    authenticated = db.Column(db.Boolean, default=False)
    host = db.Column(db.String(64))
    github = db.Column(db.String(64), nullable=True)

    @property
    def is_authenticated(self):
        return self.authenticated

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def set_id(self):
        self.id = str(uuid.uuid4())

    def get_id(self):
        return self.username

    def get_uuid(self):
        return self.id

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password, password)

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

    def unfriend(self, user):
        opt1 = Friend.query.filter_by(a_id=self.id, b_id=user.id).delete()
        opt2 = Friend.query.filter_by(a_id=user.id, b_id=self.id).delete()
        Follow.query.filter_by(requester_id=self.id).delete()

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

class UserRequest(db.Model):
    __tablename__ = 'user_requests'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password = db.Column(db.String(128))

    def set_password(self, password):
        self.password = generate_password_hash(password)


class Post(db.Model):
    """
    Post Model.

    :param int id: Unique post id.
    :param str title: Post title.
    :param str body: Post content.
    :param DateTime timestamp: The post creation time.
    :param int author_id: Author id.
    :param str author: Author username.
    :param obj comments: Referent to comments object.
    :param int privacy: Whether shows post or not.
    :param int markdown: Whether the post content in markdown or not.
    """

    __tablename__ = 'posts'
    id = db.Column(db.String(128), primary_key=True)
    title = db.Column(db.Text)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.String(128))
    author = db.Column(db.String(64))
    comments = db.relationship('Comment', backref='post', lazy='dynamic')
    privacy = db.Column(db.Integer, default=0)
    markdown = db.Column(db.String, default="F")
    target = db.Column(db.String(128), default='')

    def set_id(self):
        self.id = str(uuid.uuid4())

    def get_id(self):
        return self.id



class Comment(db.Model):
    """
    Comment Model.

    :param int id: Unique post id.
    :param str body: comment content.
    :param DateTime timestamp: The post creation time.
    :param int author_id: Author id.
    :param str author: Author username.
    :param int post_id: Referent to a post's id.
    """
    __tablename__ = 'comments'
    id = db.Column(db.String(128), primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.String(128))
    author = db.Column(db.String(64))
    post_id = db.Column(db.String(128), db.ForeignKey('posts.id'))

    def set_id(self):
        self.id = str(uuid.uuid4())


class Image(db.Model):
    __tablename__ = 'images'
    id = db.Column(db.String(128), primary_key=True)
    file = db.Column(db.LargeBinary)

    def set_id(self):
        self.id = str(uuid.uuid4())

    def get_id(self):
        return self.id

class Image_Posts(db.Model):
    __tablename__ = 'image_posts'
    id = db.Column(db.String(128), primary_key=True)
    post_id = db.Column(db.String(128), db.ForeignKey('posts.id'))
    image_id = db.Column(db.String(128), db.ForeignKey('images.id'))

    def set_id(self):
        self.id = str(uuid.uuid4())

class ProfileImageMap(db.Model):
    __tablename__ = 'profile_image_map'
    id = db.Column(db.String(128), primary_key=True)
    user_id = db.Column(db.String(128), db.ForeignKey('users.id'), unique=True)
    image_id = db.Column(db.String(128), db.ForeignKey('images.id'))

    def set_id(self):
        self.id = str(uuid.uuid4())

    def get_user_id(self):
        return self.user_id

    def get_image_id(self):
        return self.image_id



class Friend(db.Model):
    __tablename__ = "friends"
    a_id = db.Column(db.String(128), primary_key=True)
    b_id = db.Column(db.String(128), primary_key=True)

    def integrityCheck(self, a_id, b_id):
        return a_id == b_id

class Follow(db.Model):
    __tablename__ = "follows"
    requester_id = db.Column(db.String(128), primary_key=True)
    requestee_id = db.Column(db.String(128), primary_key=True)

    def integrityCheck(self, requester_id, requestee_id):
        return requester_id == requestee_id


class Node(db.Model):
    __tablename__ = "nodes"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    username = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(128))

    ip_addr = db.Column(postgresql.INET)
    email = db.Column(db.String(64), unique=True)
    isRestricted = db.Column(db.Boolean, default=False)
    verified_date = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __unicode__(self):
        return self.name

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password, password)

    def verify_access(self):
        return not self.isRestricted

class NodeRequest(db.Model):
    __tablename__ = "node_requests"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    username = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(128))
    ip_addr = db.Column(postgresql.INET)
    email = db.Column(db.String(64), unique=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)


class RemoteNode(db.Model):
    __tablename__ = "remote_nodes"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    username = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(128))
    service = db.Column(db.String(64))
    prefix = db.Column(db.String(64))

class RemoteUser(db.Model):
    __tablename__ = "remote_users"
    id = db.Column(db.String(128), primary_key=True)
    host = db.Column(db.String(64))
    username = db.Column(db.String(64))
