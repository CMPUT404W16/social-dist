from flask import render_template, session, redirect, url_for, current_app, flash, abort, request
from .. import db
from ..models import *
from ..email import send_email
from . import main
from .forms import *
from flask.ext.login import login_user, logout_user, current_user, login_required, LoginManager
from .. import login_manager


@main.route('/', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.body.data,
                author_id=current_user._get_current_object().id)
        db.session.add(post)
        return redirect(url_for('.index'))
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('index.html',
                           form=form, name=current_user.username,
                           posts=posts)


@main.route('/login', methods=['GET', 'POST'])
def login():
    loginForm = LoginForm()
    signupForm = SignupForm()

    # signup form
    if signupForm.validate_on_submit():
        user = User.query.filter_by(username=signupForm.username.data).first()
        if user is None:
            # this needs to add UUID?
            user = User(username=signupForm.username.data, password=signupForm.password.data)
            user.authenticated = True
            db.session.commit();
            login_user(user, remember=True)

            flash("User Created Successfully")
            db.session.add(user)
            db.session.commit()
            session['known'] = False

            return redirect(url_for('.index'))
        else:
            flash("Username Already Exists")

    elif loginForm.validate_on_submit():
        user = User.query.filter_by(username=loginForm.name.data).first()
        if user:
            # this needs to be changed for hashing
            print(user.password)
            print(loginForm.password.data)
            if user.password == loginForm.password.data:
                db.session.add(user)
                user.authenticated = True
                db.session.commit()
                login_user(user, remember=True)
                session['known'] = False
                flash("login successful")
                return redirect(url_for('.index'))
            else:
                flash("Incorrect username/password combination")
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
    friends_list = None
    return render_template('user/friends.html', friends=friends_list)

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

@login_required
@main.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('.index'))

@login_manager.user_loader
def load_user(id):
    user = User.query.filter_by(username=id).first()
    return user
