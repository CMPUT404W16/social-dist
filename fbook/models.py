from . import db
import bleach
from markdown import markdown
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import uuid


class Permission:
    pass

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer(), unique=True, primary_key=True)
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

    def set_id(self):
        self.id = int(str(uuid.uuid4().int)[0:10])

    def get_id(self):
        return self.username

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

    # not used; using routes
    def follow(self, user):
        pass

    def unfollow(self, user):
        pass

    # not used; using routes
    def befriend(self, user):
        pass

    def unfriend(self, user):
        opt1 = Friend.query.filter_by(a_id=self.id, b_id=user.id).delete()
        opt2 = Friend.query.filter_by(a_id=user.id, b_id=self.id).delete()
        Follow.query.filter_by(requester_id=self.id).delete()

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
    a_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    b_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)

    def integrityCheck(self, a_id, b_id):
        return a_id == b_id

class Follow(db.Model):
    requester_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    requestee_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)

    def integrityCheck(self, requester_id, requestee_id):
        return requester_id == requestee_id


class Node:
    pass

class APIRequest:
    pass

class NodeAPI:
    pass
