from .api import api
from ..db import db
from .. models import Post, User, Comment, RemoteUser
from flask_restful import Resource, reqparse
from flask.ext.login import current_user
from flask import request, abort
from bauth import auth
from apiHelper import ApiHelper
import json
import dateutil.parser
import datetime

helper = ApiHelper()


class BasePostAPI(Resource):
    decorators = [auth.login_required]
    BASE_URL = ""
    API_URL = ""

    def generate_post_response(self, page=0, page_size=50):
        response = {"query": "posts",
                    "size": page_size}
        posts = self.posts.order_by(Post.timestamp.desc()).paginate(page+1,
                page_size)
        response['count'] = posts.total

        total_page = posts.total / page_size

        # check whether the page is the first page
        if page != 0:
            response['previous'] = self.API_URL + "?page=%s&size=%s" % (page-1,
                    page_size)

        if page != total_page-1 and total_page > 1:
            response['next'] = self.API_URL + "?page=%s&size=%s" % (page+1,
                    page_size)

        response['posts'] = [self.generate_post(x) for x in posts.items]

        return response

    def generate_author(self, id):
        user = User.query.filter_by(id=id).first()
        if user is None:
            user = RemoteUser.query.filter_by(id=id).first()
            if user is None:
                u = helper.get('author', {'author_id': id})
                if len(u) > 0:
                    u = u[0]
                    author = {
                        "id": u['id'],
                        "host": u['host'],
                        "displayname": u['displayname'],
                        "url": "%s/author/%s" % (u['host'], u['id'])
                    }
                    remote = RemoteUser(id=u['id'], host=u['host'],
                            username=u['displayname'])
                    db.session.add(remote)
                    db.session.commit()
                else:
                    author = {
                        'id': id,
                        'host': 'Unknown',
                        'displayname': 'Unknown',
                        'url': 'Unknown'
                    }
            else:
                author = {
                    "id": user.id,
                    "host": user.host,
                    "displayname": user.username,
                    "url": "%s/author/%s" % (user.host, user.id)
                }
        else:
            author = {"id": user.id,
                      "host":  user.host,
                      "displayname": user.username,
                      "github": user.github,
                      "url": "%s/author/%s" % (user.host, user.id)}

        return author

    def generate_post(self, cu):
        post = {"title": cu.title,
                "content": cu.body,
                "author": self.generate_author(cu.author_id),
                "published": cu.timestamp.isoformat(),
                "id": cu.id,
                "visibility": cu.privacy,
                "target": cu.target
                }

        post["contentType"] = "text/x-markdown" if cu.markdown == "T" else "text/plain"

        # 5 comments per page.
        comments = cu.comments.paginate(1, 5)
        post["count"] = comments.total

        if comments.pages > 1:
            post["next"] = self.BASE_URL + "posts/%s/comments" % cu.id

        post["comments"] = [self.generate_comment(x) for x in comments.items]

        return post

    def generate_comment_response(self, cu, page=0, page_size=50):
        response = {"query": "comments",
                    "size": page_size}

        comments = cu.order_by(Comment.timestamp.desc()).paginate(page+1,
                page_size)
        response['count'] = comments.total

        total_page = comments.total / page_size

        # check whether the page is the first page
        if page != 0:
            response['previous'] = self.API_URL + "?page=%s&size=%s" % (page-1,
                    page_size)

        if page != total_page-1 and total_page > 1:
            response['next'] = self.API_URL + "?page=%s&size=%s" % (page+1,
                    page_size)

        response['comments'] = [self.generate_comment(x) for x in comments.items]

        return response

    def generate_comment(self, cu):
        comments = {"comment": cu.body,
                    "contentType": "text/plain",
                    "id": cu.id,
                    "published": cu.timestamp.isoformat(),
                    "author": self.generate_author(cu.author_id),
                    }
        return comments


class PostAPI(BasePostAPI):

    def get(self, post_id=None):
        parser = reqparse.RequestParser()
        parser.add_argument('page', type=int, default=0)
        parser.add_argument('page_size', type=int, default=50)

        args = parser.parse_args()

        if post_id is None:
            self.posts = Post.query.filter_by(privacy=0)  # editing here
            # self.posts = Post.query
        else:
            self.posts = Post.query.filter_by(id=post_id)
            # check post exist or not
            self.posts.first_or_404()

        return self.generate_post_response(args.page, args.page_size)

    def put(self, post_id):
        pass

    def post(self, post_id):
        parser = reqparse.RequestParser()
        parser.add_argument('page', type=int, default=0)
        parser.add_argument('page_size', type=int, default=50)

        args = parser.parse_args()

        self.posts = Post.query.filter_by(id=post_id)
        self.posts.first_or_404()

    def options(self):
        return {"Hello": "World"}


class AuthorPost(BasePostAPI):

    def get(self, author_id=None):
        parser = reqparse.RequestParser()
        parser.add_argument('page', type=int, default=0)
        parser.add_argument('page_size', type=int, default=50)

        args = parser.parse_args()

        if author_id is None:
            # return all post visible to current authenticated user
            # self.posts = Post.query.filter_by(0)
            self.posts = Post.query
        else:
            # check user exist or not.
            user = User.query.filter_by(id=author_id).first_or_404()
            # return all post write by author_id
            # and visible to current authenticated user
            self.posts = Post.query.filter_by(author_id=author_id)

        return self.generate_post_response(args.page, args.page_size)


class CommentAPI(BasePostAPI):

    def get(self, post_id):
        parser = reqparse.RequestParser()
        parser.add_argument('page', type=int, default=0)
        parser.add_argument('page_size', type=int, default=50)

        args = parser.parse_args()

        # check user exist or not.
        cu = Post.query.filter_by(id=post_id).first_or_404()

        return self.generate_comment_response(cu.comments, args.page, args.page_size)

    def post(self, post_id):
        post = Post.query.get_or_404(post_id)

        parser = reqparse.RequestParser()
        parser.add_argument("author", type=dict, required=True)
        parser.add_argument("comment", type=str, required=True)
        parser.add_argument("contentType", default='text/plain', type=str)
        parser.add_argument("published", default='text/plain', type=str)

        args = parser.parse_args()

        author_id = args.author.get("id", None)
        author_name = args.author.get("displayName", None)

        if author_id is None or author_name is None:
            abort(400, "Missing author_id or displayName.")

        # parse time
        try:
            date = dateutil.parser.parse(args.published)
        except ValueError:
            date = datetime.datetime.utcnow()

        comment = Comment(body=args.comment,
                          post=post,
                          timestamp=date,
                          author_id=author_id,
                          author=author_name)
        comment.set_id()
        db.session.add(comment)
        db.session.commit()
        return self.get(post_id)

api.add_resource(PostAPI, '/api/posts', endpoint="public_post")
api.add_resource(PostAPI, '/api/posts/')
api.add_resource(PostAPI, '/api/posts/<string:post_id>', endpoint="post_id")
api.add_resource(AuthorPost, '/api/author/posts', endpoint="author_post")
api.add_resource(AuthorPost, '/api/author/<string:author_id>/posts',
        endpoint='author_post_id')
api.add_resource(CommentAPI, '/api/posts/<string:post_id>/comments',
        endpoint="post_comments")
