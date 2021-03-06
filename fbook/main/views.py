from flask import render_template, session, redirect, url_for, current_app, flash, abort, request
from .. import db
from ..models import *
from . import main
from .forms import *
from flask.ext.login import login_user, logout_user, current_user, login_required, LoginManager
from .. import login_manager
from flask import jsonify
from urlparse import urlparse
import json
import re
import requests
from validate_email import validate_email
import socket, httplib, urllib, os
from ..api.apiHelper import ApiHelper
from ..gitapi.gitfetch import GitAPI
from binascii import *
from base64 import b64encode, b64decode
import io

helper = ApiHelper()
git_helper = GitAPI()


@main.route('/', methods=['GET', 'POST'])
@login_required
def index():
    """
    Index page view function.

    Accept GET POST method
    ROUTING: /
    """

    try:
        git_username = current_user._get_current_object().github
        print 'This is the username for github! --->>', git_username
        githubs = git_helper.fetch_events(git_username)
        # print githubs
        if githubs is None:
            githubs = []
    except:
        githubs = []

    form = PostForm()
    if request.method == 'POST':

        if form.image.data: # only if an image to be uploaded has been chosen
            try:
                if (image_allowed(request.files['image'])):

                    post = Post(title=form.title.data,
                                body=form.body.data,
                                author_id=current_user._get_current_object().id,
                                author=current_user._get_current_object().username,
                                markdown=form.mkdown.data,
                                privacy=int(form.privacy.data),
                                target=form.target.data)
                    post.set_id()
                    db.session.add(post)
                    db.session.commit()

                    blob_value = request.files['image'].read()
                    image = Image(file=blob_value)
                    image.set_id()
                    db.session.add(image)
                    db.session.commit()
                    image_posts = Image_Posts(post_id = post.get_id(),
                        image_id = image.get_id()
                        )
                    image_posts.set_id()
                    db.session.add(image_posts)
                    db.session.commit()

                    return redirect(url_for('.index'))

                else:
                    flash("Error: image extension not allowed. Allowed types: \
                .png, .jpg, .jpeg.")
                    return redirect(url_for('.index'))

            except:
                flash ("Unable to post")
                return redirect(url_for('.index'))

        post = Post(title=form.title.data,
                    body=form.body.data,
                    author_id=current_user._get_current_object().id,
                    author=current_user._get_current_object().username,
                    markdown=form.mkdown.data,
                    privacy=int(form.privacy.data),
                    target=form.target.data)
        post.set_id()
        db.session.add(post)
        db.session.commit()

        return redirect(url_for('.index'))

    posts = []
    data = helper.get('posts')

    # print data
    for item in data:
        if type(item) is not dict:
            continue
        posts.extend(item['posts'])

    # print(posts)

    image = {}

    # go through the list of posts and check to see if there are images in them
    for i in range(len(posts)):
        post_id = posts[i]['id']
        query = Image_Posts.query.filter_by(post_id=post_id).all()
        if len(query) > 0:  # there is an image with this post
            image_id = query[0].__dict__['image_id']
            query = Image.query.filter_by(id=image_id).all()
            if len(query) > 0:
                image[post_id] = (b64encode(query[0].__dict__['file']))
        elif 'image' in posts[i]:
            url = posts[i]['image']
            if url != None and url != 'null':
                response = requests.get(url)
                image[post_id] = b64encode(response.content)


    posts_result = []
    # filter for posts
    for item in posts:
        try:
            if item['visibility'] == 0:
                item['visibility'] = 'PUBLIC'
            elif item['visibility'] == 1:
                item['visibility'] = 'PRIVATE'
            elif item['visibility'] == 2:
                item['visibility'] = 'FRIENDS'
            elif item['visibility'] == 3:
                item['visibility'] = 'SOMEONE'
            elif item['visibility'] == 4:
                item['visibility'] = 'SERVERONLY'
            elif item['visibility'] == 5:
                item['visibility'] = 'FOAF'
            else:
                item['visibility'] = 'PUBLIC'
        except:
            item['visibility'] = 'PUBLIC'

        flag = ''
        try:
            flag = item['target']
        except:
            flag = ''
        if flag is not '' and flag == current_user._get_current_object().username and item['visibility']=='SOMEONE':
            posts_result.append(item)
        elif item['author']['id'] == current_user._get_current_object().id:
            posts_result.append(item)
        elif item['visibility'].upper() == 'PUBLIC':
            posts_result.append(item)
        elif item['visibility'].upper() == 'PRIVATE':
            if item['author']['id'] == current_user._get_current_object().id:
                posts_result.append(item)
        elif item['visibility'].upper() == 'FRIENDS':
            if current_user._get_current_object().is_friend(item['author']['id']):
                posts_result.append(item)
        elif item['visibility'].upper() == "SERVERONLY":
            if item['author']['host'] == current_user._get_current_object().host:
                posts_result.append(item)

    posts = posts_result

    if len(image) > 0:
        return render_template('index.html',
                           form=form,
                           name=current_user.username,
                           posts=posts,
                           image=image,
                           events=githubs
                           )
    else:
        return render_template('index.html',
                           form=form,
                           name=current_user.username,
                           posts=posts,
                           image={},
                           events=githubs
                           )

@main.route('/image/<string:id>', methods=['GET', 'POST'])
def image(id):
    image = Image.query.get_or_404(id)

    query = Image.query.filter_by(id = id).all()
    image = query[0].__dict__['file']

    from flask import send_file
    return send_file(io.BytesIO(image), mimetype='images/png')

@main.route('/post/<string:id>', methods=['GET', 'POST'])
def post(id):
    """
    Post page view function.
    Accept GET POST method
    ROUTING: /post/<int:id>
    """
    #post = Post.query.get_or_404(id)
    api = ApiHelper()
    posts = api.get('posts', {"post_id": id})
    if len(posts) == 0:
        abort(404)

    posts = posts[0].get("posts", None)

    if posts is None:
        abort(403, "Cannot retrive post from origin hosts.")

    form = CommentForm()
    if form.validate_on_submit():
        #post = Post.query.get_or_404(id)
        #comment = Comment(body=form.body.data,
        #                  post=post,
        #                  author_id=current_user._get_current_object().id,
        #                  author=current_user._get_current_object().username)
        #comment.set_id()
        #db.session.add(comment)
        #db.session.commit()
        user = current_user._get_current_object()
        comment_body = {'comment': form.body.data}
        comment_body['contentType'] = 'text/plain'
        comment_body['author'] = {'id': user.id,
                                  'host': "http://" + user.host,
                                  'displayName': user.username,
                                  'url': "http://%s/author/%s" % (user.host, user.id),
                                  'github': user.github
                                  }
        print comment_body
        api.post('posts', comment_body, posts[0]['author']['host'], {"post_id": id, "comments":""})

        flash('Your comment has been created')
        return redirect(url_for('.post', id=id))

    #comments = Comment.query.filter_by(post_id=post.id)
    comments = posts[0]['comments']
    #print comments

    image = {}
    image_id = []
    query = Image_Posts.query.filter_by(post_id=id).all()
    if len(query) > 0: # there is an image with this post
        for i in query:
            image_id.append(i.__dict__['image_id'])

    if len(image_id) > 0: # there is an image
        image_query = Image.query.filter_by(id=image_id[0]).all()
        if len(image_query) > 0:
            for i in image_query:
                # serve the image give i.__dict__['file'] contains the bytes of the image
                # print i.__dict__['file']
                image[id] = (b64encode(i.__dict__['file']))

        return render_template('post/post.html', posts=posts, form=form,
                               comments=comments, image=image, show=True)
    else:
        return render_template('post/post.html', posts=posts, form=form,
                               comments=comments, image={}, show=True)

@main.route('/edit/<id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    """
    Edit post page view function.
    Accept GET POST method
    ROUTING: /edit/<int:id>
    """
    post = Post.query.get_or_404(id)
    if current_user.id != post.author_id:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        post.title = form.title.data
        db.session.add(post)
        db.session.commit()
        flash('The post has been updated.')
        return redirect(url_for('.index'))
    form.title.data = post.title
    form.body.data = post.body
    return render_template('post/edit_post.html', form=form)

@main.route('/delete_post/<id>', methods=['POST', 'GET'])
@login_required
def delete_post(id):
    """
    Edit post page view function.
    Accept GET POST method
    ROUTING: /edit/<int:id>
    """

    p = Post.query.get_or_404(id)
    if current_user.id != p.author_id:
        abort(403)

    img_post = Image_Posts.query.filter_by(post_id=id).all()
    if len(img_post) > 0:
        image_id = img_post[0].__dict__['image_id']

        db.session.delete(img_post[0])
        db.session.commit()

        img = Image.query.filter_by(id=image_id).all()
        if len(img) > 0:
            db.session.delete(img[0])
            db.session.commit()

    db.session.delete(p)
    db.session.commit()

    form = PostForm()
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return redirect(url_for('.index'))


@main.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login/Signup page view function.
    Accept GET POST method
    ROUTING: /login
    Uses WTForms to handle forms. Renders login.html passing a LoginForm and a
    SignupForm Form objects. Uses FLask-Login and redirects the user back to /.
    The view is passed with:
    loginForm: Form object
    signupFOrm: Form object
    """

    loginForm = LoginForm()
    signupForm = SignupForm()

    # signup form
    if signupForm.validate_on_submit():
        user = User.query.filter_by(username=signupForm.username.data).first()
        if user is None:
            ureq = UserRequest(username=signupForm.username.data)
            ureq.set_password(signupForm.password.data)
            try:
                db.session.add(ureq)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(e)

            flash("Signup Request Submitted")

            return redirect('/')
        else:
            flash("Username Already Exists")

    # if login request
    elif loginForm.validate_on_submit():
        # check user exists and verify password
        user = User.query.filter_by(username=loginForm.name.data).first()
        if user is not None:
            if user.verify_password(loginForm.password.data):
                # login user
                user.authenticated = True
                db.session.commit()
                login_user(user, remember=True)

                flash("login successful")
                return redirect(url_for('.index'))
            else:
                flash("Incorrect Password")
        else:
            flash("User does not exist")

    return render_template('login.html', loginForm=loginForm, signupForm=signupForm)

# Can be used to test remote_api calls, uncomment form in template
# @main.route('/test', methods=['GET', 'POST'])
# def test():
#     helper = ApiHelper()
#     # return helper.test()
#     return helper.get('author', {'author_id': 'd10fe1f5-b426-48eb-840c-50fcd295014c'})


@main.route('/request', methods = ['GET', 'POST'])
def register():
    apiForm = APIForm()

    if apiForm.validate_on_submit(): # wants to request access from our server
        valid_info = True
        name = apiForm.name.data
        ip_addr = request.remote_addr
        email = apiForm.email.data
        username = apiForm.username.data
        password = apiForm.password.data

        # check validity of ip address
        try:
            socket.inet_aton(ip_addr)
        except socket.error as e:
            flash("Invalid IP Address")
            valid_info = False
            print(e)

        # check validity of email

        is_valid = validate_email(email, verify=True)
        if is_valid == False:
            flash("Invalid Email Address")
            valid_info = False

        # check if email is unique in the table Node and NodeRequest

        equery = Node.query.filter_by(email=email).all()
        print equery

        if len(equery) > 0: # means email already exists
            flash("Invalid Email Address")
            valid_info = False

        # check if username is unique in the table Node and NodeRequest
        uquery = Node.query.filter_by(username=username).all()

        if len(uquery) > 0: # means username already exists
            flash("Invalid Username")
            valid_info = False

        if valid_info == True: # valid information, commit to db
            # add the new information into request from the request
            req = NodeRequest (name= name, username= username,
                password= password, email= email, ip_addr= ip_addr)
            req.set_password(password)
            try:
                db.session.add(req)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(e)

            flash("Request sent")
            return redirect(url_for('.index'))
        else: # invalid information, do not send request info
            return redirect(url_for('.index'))

    return render_template('request.html', apiForm=apiForm)

# <user> requires a id
@main.route('/users/<user>', methods=['GET', 'POST'])
@login_required
def show_profile(user):
    """
    Profile page view function.
    Accept GET POST method
    ROUTING: /users/<user>
    Returns the profile page populated with <user>'s information.
    The view is passed with:
    user_profile: <user>'s username: string
    user_id: <user>'s id: string
    user_obj: User model object
    upi: user's profile image
    """

    # remote-user e8d08d8e-c161-49e2-a60b-0e388f246a46'
    u = helper.get('author', {'author_id': user})

    if (len(u) > 0):
        u = u[0]

        user = u['displayname']

        # store in remote db
        check = RemoteUser.query.filter_by(id=u['id']).first()
        userx = RemoteUser(username=u['displayname'], id=u['id'], host=u['host'])
        if check == None:
            db.session.add(userx)
            db.session.commit()

        idx = userx.id

        profile_image = None
        pi_map = ProfileImageMap.query.filter_by(user_id=idx).first()
        pimage = None
        if (pi_map):
            pimage = Image.query.filter_by(id=pi_map.image_id).first()
            if (pimage):
                profile_image = b64encode(pimage.__dict__['file'])

        elif 'image' in u:
            url = u['image']
            if url != None and url != 'null':
                response = requests.get(url)
                profile_image = b64encode(response.content)

        return render_template('user/profile.html', user_profile=user,
                                user_id=idx, user_obj=userx, upi=profile_image)
    else:
        flash('ERROR user not found')
        return render_template('404.html')

@main.route('/settings', methods=['GET', 'POST'])
@login_required
def show_settings():
    """
    Settings page view function.
    Accept GET POST method
    ROUTING: /settings
    Returns the settings.html view with a form to change the user's password.
    Redirects back to the settings page upon successful password change.
    The view is passed with:
    pass_form: Form object
    """

    new_username_form = ChangeUsernameForm()
    new_password_form = ChangePasswordForm()
    github_form = GithubUsernameForm()

    if new_username_form.validate_on_submit() and new_username_form.submit_u.data:
        # check for existing username
        user_temp = User.query.filter_by(username=new_username_form.new_username.data).first()
        if (user_temp):
            flash("Username already exists.")
            return redirect(url_for('.show_settings'))

        else:
            user = User.query.filter_by(username=current_user.username).first()
            if (user):
                # change password in db
                user.username = new_username_form.new_username.data
                db.session.commit()
                user.authenticated = True
                login_user(user, remember=True)

                flash("New username set.")
                return redirect(url_for('.show_settings'))

    elif new_password_form.validate_on_submit() and new_password_form.submit_p.data:
        user = User.query.filter_by(username=current_user.username).first()
        if (user):
            # change password in db
            user.set_password(new_password_form.new_password.data)
            db.session.commit()

            flash("New password set.")
            return redirect(url_for('.show_settings'))
    elif github_form.validate_on_submit() and github_form.submit_g.data:
        # change github in db
        user = User.query.filter_by(username=current_user.username).first()
        if (user):
            if 'github.com/' in github_form.gitName.data:
                user.github = github_form.gitName.data
            else:
                user.github = 'http://www.github.com/' + github_form.gitName.data
            print user.github
            db.session.commit()

            flash("Github Username set.")
            return redirect(url_for('.show_settings'))

    return render_template('user/settings.html', un_form=new_username_form, pass_form=new_password_form, git_form=github_form)

def image_allowed(image):
    allowed_extensions = ['png', 'jpg', 'jpeg']
    f_ext = image.filename.rsplit('.')[1]
    # flash("Image is of type: "+str(f_ext))
    if (f_ext in allowed_extensions):
        return True
    else:
        return False

# upload and set new profile image
@main.route('/upload_pimage', methods=['POST'])
@login_required
def upload_pimage():
    # check for profile image upload
    if (request.method=='POST' and 'pimage' in request.files):
        image_upload = request.files['pimage']
        if (image_upload):
            # flash("File found")
            if (image_allowed(image_upload)):
                user = User.query.filter_by(
                        username=current_user.username).first()
                if (user):
                    # save image and reference image to current user
                    # flash("Trying to set image.")

                    image_upload = image_upload.read()

                    new_image = Image(file=image_upload)
                    new_image.set_id()
                    db.session.add(new_image)
                    db.session.commit()

                    # check for old profile image map
                    temp_pi = ProfileImageMap.query.filter_by(
                                user_id=current_user.get_uuid()).first()
                    # old profile img selection found
                    if (temp_pi):
                        flash("Old profile image found, setting new profile image.")
                        db.session.delete(temp_pi)
                        db.session.commit()

                    new_pi_map = ProfileImageMap(user_id=current_user.get_uuid(),
                                                image_id=new_image.get_id())
                    new_pi_map.set_id()

                    db.session.add(new_pi_map)
                    db.session.commit()

                    flash("Image successfully uploaded and set.")
            else:
                flash("Error: image extension not allowed. Allowed types: \
                .png, .jpg, .jpeg.")
        else:
            flash("Error: No image was selected, found, or transferred.")

    return redirect(url_for('.show_settings'))

# returns posts.html with a list of user's posts
@main.route('/users/<user>/posts', methods=['GET'])
@login_required
def show_self_posts(user):
    """
    Author's own posts page view function.
    Accept GET method
    ROUTING: /users/<user>/posts
    Returns the posts.html populated with <user>'s posts from a db
    query.

    The view is passed with:
    posts: a list of <user>'s posts
    image: a list of <user>'s posts' images
    user_profile: <user>'s username: string
    user_id: <user>'s id: string
    user_obj: User mode object
    upi: user's profile image
    """

    # if target user is not current user, redirect the target user's main
    # profile page
    if (user != current_user.id):
        return redirect("/users/"+user)

    userx = User.query.filter_by(id=user).first()

    posts=[]
    data = helper.get('posts', {'curr_author': user, 'author_id': user})

    #print data
    for item in data:
        if type(item) is not dict:
            continue
        posts.extend(item['posts']) # switch to u'posts ?? or not??

    image = {}

    # go through the list of posts and check to see if there are images in them
    for i in range(len(posts)):
        post_id = posts[i]['id']
        query = Image_Posts.query.filter_by(post_id=post_id).all()
        if len(query) > 0:  # there is an image with this post
            image_id = query[0].__dict__['image_id']
            query = Image.query.filter_by(id=image_id).all()
            if len(query) > 0:
                image[post_id] = (b64encode(query[0].__dict__['file']))
        elif 'image' in posts[i]:
            url = posts[i]['image']
            if url != None and url != 'null':
                response = requests.get(url)
                image[post_id] = b64encode(response.content)

    profile_image = None
    pi_map = ProfileImageMap.query.filter_by(user_id=user).first()
    pimage = None
    if (pi_map):
        pimage = Image.query.filter_by(id=pi_map.image_id).first()
        if (pimage):
            profile_image = b64encode(pimage.__dict__['file'])

    if (len(image) > 0):
        return render_template('user/posts.html',
                                posts=posts,
                                image=image,
                                user_profile=current_user.username,
                                user_id=current_user.id,
                                user_obj=userx,
                                upi=profile_image)
    else:
        return render_template('user/posts.html',
                                posts=posts,
                                image={},
                                user_profile=current_user.username,
                                user_id=current_user.id,
                                user_obj=userx,
                                upi=profile_image)

# returns followers.html with a list of user's followers
@main.route('/users/<user>/followers', methods=['GET'])
@login_required
def show_followers(user):
    """
    Followers page view function.
    Accept GET method
    ROUTING: /users/<user>/followers
    Returns the followers.html populated with <user>'s followers from a db
    query.
    The view is passed with:
    followers: a Python list of <user>'s followers
    user_profile: <user>'s username: string
    user_id: <user>'s id: string
    upi: user's profile image
    """

    # if target user is not current user, redirect the target user's main
    # profile page
    if (user != current_user.id):
        return redirect("/users/"+user)

    userx = User.query.filter_by(id=user).first()

    followerID = Follow.query.filter_by(requestee_id=current_user.id).all()
    followersx = []
    for follow in followerID:
        f = User.query.filter_by(id=follow.requester_id).first()
        if f:
            followersx.append([f.username, f.id])
        else:
            f = RemoteUser.query.filter_by(id=follow.requester_id).first()
            if f:
                followersx.append([f.username, f.id])


    # u = helper.get('author', {'author_id': user})
    # if (len(u) == 1):
    #     u = u[0]
    #     user = u['displayname']
    #     userx = User(username=u['displayname'], id=u['id'], host=u['host'])
    #     idx = userx.id

    #     return render_template('user/profile.html', user_profile=user, user_id=idx, user_obj=userx)
    # else:
    #     flash('ERROR user not found')
    #     return render_template('404.html')

    # u = helper.get()

    profile_image = None
    pi_map = ProfileImageMap.query.filter_by(user_id=user).first()
    pimage = None
    if (pi_map):
        pimage = Image.query.filter_by(id=pi_map.image_id).first()
        if (pimage):
            profile_image = b64encode(pimage.__dict__['file'])

    return render_template('user/followers.html', followers=followersx, user_profile=userx.username, user_id=current_user.id, user_obj=userx, upi=profile_image)

# returns friends.html with a list of user's friends
@main.route('/users/<user>/friends', methods=['GET'])
@login_required
def show_friends(user):
    """
    Friends page view function.
    Accept GET method
    ROUTING: /users/<user>/friends
    Returns the friends.html populated with <user>'s friends from a db
    query. It executes two queries since <user> could be on either of a_id or
    b_id of the Friends model.
    The view is passed with:
    friends: a Python list of <user>'s friends
    user_profile: <user>'s username: string
    user_id: <user>'s id: string
    upi: user's profile image
    """

    # if target user is not current user, redirect the target user's main
    # profile page
    if (user != current_user.id):
        return redirect("/users/"+user)

    userx = User.query.filter_by(id=user).first()

    # friends_list = Friend.query.filter_by(a_id=current_user.id).all()
    # friends_list2 = Friend.query.filter_by(b_id=current_user.id).all()
    # friendsx = None
    # if (friends_list):
    #     friendsx = []
    #     for f in friends_list:
    #         fid = User.query.filter_by(id=f.b_id).first()
    #         friendsx.append(fid.username)
    # if (friends_list2):
    #     if (not friendsx):
    #         friendsx = []
    #     for f in friends_list2:
    #         fid = User.query.filter_by(id=f.a_id).first()
    #         friendsx.append(fid.username)

    # remote-user d10fe1f5-b426-48eb-840c-50fcd295014c'
    # u = helper.get('author', {'author_id': user})
    # if (len(u) == 1):
    #     u = u[0]
    #     user = u['displayname']
    #     userx = User(username=u['displayname'], id=u['id'], host=u['host'])
    #     idx = userx.id

    #     return render_template('user/profile.html', user_profile=user, user_id=idx, user_obj=userx)
    # else:
    #     flash('ERROR user not found')
    #     return render_template('404.html')

    friendsList = helper.get('friends', {'author_id': user})

    nameList = []

    for user_id in friendsList:
        profile = helper.get('author', {'author_id': user_id})

        if (len(profile) > 0):
            profile = profile[0]
            name = profile['displayname']
            uid = profile['id']
            nameList.append([name, uid])

    profile_image = None
    pi_map = ProfileImageMap.query.filter_by(user_id=user).first()
    pimage = None
    if (pi_map):
        pimage = Image.query.filter_by(id=pi_map.image_id).first()
        if (pimage):
            profile_image = b64encode(pimage.__dict__['file'])

    return render_template('user/friends.html', friends=nameList, user_profile=current_user.username, user_id=current_user.id, user_obj=userx, upi=profile_image)

# # returns friends.html with a list of user's friends
# @login_required
# @main.route('/users/<user>/friends', methods=['GET'])
# def show_friends(user):
#     friends_list = None
#     return render_template('user/friends.html', friends=friends_list)

# current user follows user
@main.route('/follow/<user>', methods=['GET', 'POST'])
@login_required
def follow(user):
    """
    User follow route action function.
    Accept GET POST method
    ROUTING: /follow/<user>
    The URL verb for following <user>. Creates a new Follow with the requester
    as the current user and the requestee as <user>. If the requestee has
    already followed the current user, an automatic friendship is created.
    Redirects to <user>'s profile page.
    """

    # requestee_idx = User.query.filter_by(username=user).first()
    # new_follow = Follow(requester_id=current_user.id,
    #                     requestee_id=requestee_idx)

    # following = Follow.query.filter_by(requester_id=requestee_idx,
    #                     requestee_id=current_user.id).first()

    # if following:
    #     new_friend = Friend(a_id=current_user.id,
    #                     b_id=requestee_idx)
    #     db.session.add(new_friend)


    # db.session.add(new_follow)
    # db.session.commit()

    u = helper.get('author', {'author_id': user})

    if (len(u) > 0):
        u = u[0]
        user = u['displayname']
        userx = User(username=u['displayname'], id=u['id'], host=u['host'])
        idx = userx.id
        userURL = u['url']
    else:
        flash('ERROR user not found')
        return render_template('404.html')

    body = {
        "query":"friendrequest",
        "author": {
            "id": current_user.id,
            "host":current_user.host,
            "displayName":current_user.username
        },
        "friend": {
            "id": userx.id,
            "host":userx.host,
            "displayName":userx.username,
            "url": userURL
        }
    }

    helper.post('friend_request', body, userx.host)

    flash("You have just followed "+user)

    return redirect("/users/"+userx.id)

# current user befriends user
@main.route('/befriend/<user>', methods=['GET', 'POST'])
@login_required
def befriend(user):
    """
    User befriend route action function.
    Accept GET POST method
    ROUTING: /befriend/<user>
    The URL verb for befriending <user>. Creates a new Friend object and
    redirects to <user>'s friends page.
    """

    # friend_idx = User.query.filter_by(username=user).first().id
    # new_friend = Friend(a_id=current_user.id,
    #                     b_id=friend_idx)
    # new_follow = Follow(requester_id=current_user.id, requestee_id=friend_idx)
    # db.session.add(new_follow)
    # db.session.add(new_friend)
    # db.session.commit()

    u = helper.get('author', {'author_id': user})
    if (len(u) > 0):
        u = u[0]
        user = u['displayname']
        userx = User(username=u['displayname'], id=u['id'], host=u['host'])
        idx = userx.id
        userURL = u['url']
    else:
        flash('ERROR user not found')
        return render_template('404.html')

    body = {
        "query":"friendrequest",
        "author": {
            "id": current_user.id,
            "host":current_user.host,
            "displayName":current_user.username
        },
        "friend": {
            "id": userx.id,
            "host":userx.host,
            "displayName":userx.username,
            "url": userURL
        }
    }

    helper.post('friend_request', body, userx.host)
    helper.post


    flash("You have just befriended "+user)

    return redirect("/users/"+current_user.id+"/followers")

@main.route('/unfollow/<user>', methods=['GET', 'POST'])
@login_required
def unfollow(user):
    """
    User unfollow route action function.
    Accept GET POST method
    ROUTING: /unfollow/<user>
    The URL verb for unfollowing <user>. Uses User model function unfriend.
    Redirects to <user>'s profile page.
    """

    requestee_idx = User.query.filter_by(id=user).first()
    if requestee_idx:
        current_user.unfriend(requestee_idx)
    else:
        requestee_idx = RemoteUser.query.filter_by(id=user).first()
        if requestee_idx:
            current_user.unfriend(requestee_idx)
    db.session.commit()

    flash("You have just unfollowed "+requestee_idx.username)

    return redirect("/users/"+requestee_idx.id)

@main.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    """
    User logout route action function.
    Accept GET POST method
    ROUTING: /logout
    The URL verb for logout. Redirects to / with the user logged out.
    """

    logout_user()
    return redirect(url_for('.index'))


@main.route('/githubpage', methods=['GET', 'POST'])
@login_required
def githubpage():
    git_id = current_user.github
    return redirect(git_id)


@main.route('/githubrepo', methods=['GET', 'POST'])
@login_required
def githubrepo():
    git_id = current_user.github
    return redirect(git_id)

@login_manager.user_loader
def load_user(id):
    user = User.query.filter_by(username=id).first()
    return user
