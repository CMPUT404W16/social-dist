from flask import render_template, session, redirect, url_for, current_app, flash, abort, request
from .. import db
from ..models import User, Follow, Friend
from ..email import send_email
from . import main
from .forms import *
from flask.ext.login import login_user, logout_user, current_user, login_required, LoginManager
from .. import login_manager
from flask import jsonify

@main.route('/', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            session['known'] = False
            if current_app.config['FLASKY_ADMIN']:
                send_email(current_app.config['FLASKY_ADMIN'], 'New User',
                           'mail/new_user', user=user)
        else:
            session['known'] = True
        session['name'] = form.name.data
        # session['username'] = form.name.data
        return redirect(url_for('.index'))
    return render_template('index.html',
                           form=form, name=current_user.username,
                           known=session.get('known', False))

@main.route('/login', methods=['GET', 'POST'])
def login():
    loginForm = LoginForm()
    signupForm = SignupForm()

    # signup form
    if signupForm.validate_on_submit():
        user = User.query.filter_by(username=signupForm.username.data).first()
        if user is None:
            # add user to db
            user = User(username=signupForm.username.data, authenticated=True)
            user.set_id()
            print(user.id)
            user.set_password(signupForm.password.data);
            db.session.add(user)
            db.session.commit();
            # login user
            login_user(user, remember=True)

            flash("User Created Successfully")

            return redirect(url_for('.index'))
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

# <user> requires a username
@login_required
@main.route('/users/<user>', methods=['GET', 'POST'])
def show_profile(user):
    userx = User.query.filter_by(username=user).first()
    if (userx):
        idx = userx.id
    return render_template('user/profile.html', user_profile=user, user_id=idx)

@login_required
@main.route('/settings', methods=['GET', 'POST'])
def show_settings():
    """
    This function will also handle password changes.
    """

    new_password_form = ChangePasswordForm()

    if new_password_form.validate_on_submit():
        user = User.query.filter_by(username=current_user.username).first()
        if (user):
            # change password in db
            user.password = new_password_form.new_password.data
            db.session.commit()

            flash("New password set.")
            return redirect(url_for('.show_settings'))

    return render_template('user/settings.html', pass_form=new_password_form)

# returns followers.html with a list of user's followers
@login_required
@main.route('/users/<user>/followers', methods=['GET'])
def show_followers(user):
    # followers_list = Follow.query.filter_by(
                        # requestee_id=current_user.id).first()
    # followers_list = db.session.query(Follow).join(User, Follow.requestee_id==current_user.id, Follow.requester_id==User.id).all()
    # followers_list = db.session.query(Follow, User).filter_by(requestee_id=current_user.id).all()
    template = "SELECT u.username, u.id " + \
        "FROM follow f, users u " + \
        "WHERE f.requestee_id = {requestee} " + \
        "AND f.requester_id = u.id"

    query_str = template.format(requestee=current_user.id)
    followers_list = db.engine.execute(query_str)

    followersx = None
    if (followers_list):
        followersx = []
        for row in followers_list:
            followersx.append([row[0], row[1]])

    return render_template('user/followers.html', followers=followersx)

# returns friends.html with a list of user's friends
@login_required
@main.route('/users/<user>/friends', methods=['GET'])
def show_friends(user):
    # list of friends' usernames

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
        for f in followers_list2:
            fid = User.query.filter_by(id=f.a_id).first()
            friendsx.append(fid.username)

    return render_template('user/friends.html', friends=friendsx)

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
    requestee_idx = User.query.filter_by(username=user).first().id
    new_follow = Follow(requester_id=current_user.id,
                        requestee_id=requestee_idx)
    db.session.add(new_follow)
    db.session.commit()

    flash("You have just followed "+user)

    return redirect("/users/"+user)

# current user befriends user
@login_required
@main.route('/befriend/<user>', methods=['GET', 'POST'])
def befriend(user):
    friend_idx = User.query.filter_by(username=user).first().id
    new_friend = Friend(a_id=current_user.id,
                        b_id=friend_idx)
    db.session.add(new_friend)
    db.session.commit()

    flash("You have just befriended "+user)

    return redirect("/users/"+current_user.username+"/friends")

@login_required
@main.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('.index'))

@login_manager.user_loader
def load_user(id):
    user = User.query.filter_by(username=id).first()
    return user
