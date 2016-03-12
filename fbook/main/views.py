from flask import render_template, session, redirect, url_for, current_app, flash, abort, request
from .. import db
from ..models import *
from ..email import send_email
from . import main
from .forms import *
from flask.ext.login import login_user, logout_user, current_user, login_required, LoginManager
from .. import login_manager
from flask import jsonify
from urlparse import urlparse
from validate_email import validate_email
import socket, httplib, urllib, os


@main.route('/', methods=['GET', 'POST'])
@login_required
def index():
    """
    Index page view function.

    Accept GET POST method
    ROUTING: /
    """
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data,body=form.body.data, author_id=current_user._get_current_object().id, author=current_user._get_current_object().username)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('.index'))
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('index.html',
                           form=form, name=current_user.username,
                           posts=posts)



@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    """
    Post page view function.

    Accept GET POST method
    ROUTING: /post/<int:id>
    """
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          post=post,
                          author_id=current_user._get_current_object().id,
                          author=current_user._get_current_object().username)
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been created')
        return redirect(url_for('.post', id=post.id))
    comments = Comment.query.filter_by(post_id=post.id)
    return render_template('post/post.html', posts=[post], form=form, comments=comments, show=True)


@main.route('/edit/<int:id>', methods=['GET', 'POST'])
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

@main.route('/delete_post/<int:id>', methods=['POST', 'GET'])
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
    inv = InvForm()

    # signup form
    if signupForm.validate_on_submit():
        # temp_user = User(username='admin_new', role_id=2, authenticated=1, host='localhost');
        # temp_user.set_password('p1')
        # temp_user.set_id()
        # db.session.add(temp_user)
        # db.session.commit()
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
    
    return render_template('login.html', loginForm=loginForm, signupForm=signupForm, inv=inv)

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

# <user> requires a username
@login_required
@main.route('/users/<user>', methods=['GET', 'POST'])
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
    """

    userx = User.query.filter_by(username=user).first_or_404()
    if (userx):
        idx = userx.id
    return render_template('user/profile.html', user_profile=user, user_id=idx, user_obj=userx)


@login_required
@main.route('/settings', methods=['GET', 'POST'])
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

    return render_template('user/settings.html', un_form=new_username_form, pass_form=new_password_form)


# returns followers.html with a list of user's followers
@login_required
@main.route('/users/<user>/followers', methods=['GET'])
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
    """

    userx = User.query.filter_by(username=user).first()

    followerID = Follow.query.filter_by(requestee_id=current_user.id).all()
    followersx = []
    for follow in followerID:
        f = User.query.filter_by(id=follow.requester_id).first()
        followersx.append([f.username, f.id])


    return render_template('user/followers.html', followers=followersx, user_profile=user, user_id=current_user.id, user_obj=userx)

# returns friends.html with a list of user's friends
@login_required
@main.route('/users/<user>/friends', methods=['GET'])
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
    """

    userx = User.query.filter_by(username=user).first()

    friends_list = Friend.query.filter_by(a_id=current_user.id).all()
    friends_list2 = Friend.query.filter_by(b_id=current_user.id).all()
    friendsx = None
    if (friends_list):
        friendsx = []
        for f in friends_list:
            fid = User.query.filter_by(id=f.b_id).first()
            friendsx.append(fid.username)
    if (friends_list2):
        if (not friendsx):
            friendsx = []
        for f in friends_list2:
            fid = User.query.filter_by(id=f.a_id).first()
            friendsx.append(fid.username)

    return render_template('user/friends.html', friends=friendsx, user_profile=user, user_id=current_user.id, user_obj=userx)

# # returns friends.html with a list of user's friends
# @login_required
# @main.route('/users/<user>/friends', methods=['GET'])
# def show_friends(user):
#     friends_list = None
#     return render_template('user/friends.html', friends=friends_list)

# current user follows user
@login_required
@main.route('/follow/<user>', methods=['GET', 'POST'])
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

    requestee_idx = User.query.filter_by(username=user).first().id
    new_follow = Follow(requester_id=current_user.id,
                        requestee_id=requestee_idx)

    following = Follow.query.filter_by(requester_id=requestee_idx,
                        requestee_id=current_user.id).first()

    if following:
        new_friend = Friend(a_id=current_user.id,
                        b_id=requestee_idx)
        db.session.add(new_friend)


    db.session.add(new_follow)
    db.session.commit()

    flash("You have just followed "+user)

    return redirect("/users/"+user)

# current user befriends user
@login_required
@main.route('/befriend/<user>', methods=['GET', 'POST'])
def befriend(user):
    """
    User befriend route action function.

    Accept GET POST method
    ROUTING: /befriend/<user>

    The URL verb for befriending <user>. Creates a new Friend object and
    redirects to <user>'s friends page.
    """

    friend_idx = User.query.filter_by(username=user).first().id
    new_friend = Friend(a_id=current_user.id,
                        b_id=friend_idx)
    new_follow = Follow(requester_id=current_user.id, requestee_id=friend_idx)
    db.session.add(new_follow)
    db.session.add(new_friend)
    db.session.commit()

    flash("You have just befriended "+user)

    return redirect("/users/"+current_user.username+"/friends")

@login_required
@main.route('/unfollow/<user>', methods=['GET', 'POST'])
def unfollow(user):
    """
    User unfollow route action function.

    Accept GET POST method
    ROUTING: /unfollow/<user>

    The URL verb for unfollowing <user>. Uses User model function unfriend.
    Redirects to <user>'s profile page.
    """

    requestee_idx = User.query.filter_by(username=user).first()
    current_user.unfriend(requestee_idx)
    db.session.commit()

    flash("You have just unfollowed "+user)

    return redirect("/users/"+user)

@login_required
@main.route('/logout', methods=['GET', 'POST'])
def logout():
    """
    User logout route action function.

    Accept GET POST method
    ROUTING: /logout

    The URL verb for logout. Redirects to / with the user logged out.
    """

    logout_user()
    return redirect(url_for('.index'))

@login_manager.user_loader
def load_user(id):
    user = User.query.filter_by(username=id).first()
    return user
