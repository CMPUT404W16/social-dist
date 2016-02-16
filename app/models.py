from . import db


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
    title = db.Colunm(db.String(64))
    username = db.Column(db.String(64), unique=True, index=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    
class Comment(db.model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    content = title = db.Colunm(db.String(500))


class Image(db.model):
    __tablename__ = 'images'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    file = 0

    
class Privacy:
    pass


class Friend(db.model):
    a_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    b_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def integrityCheck(self, a_id, b_id):
        return a_id == b_id
    
class Follow(db.model):
    requester_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    requestee_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def integrityCheck(self, requester_id, requestee_id):
        return requester_id == requestee_id
    

class Node:
    pass

class APIRequest:
    pass

class NodeAPI:
    pass


