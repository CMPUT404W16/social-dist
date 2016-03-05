from flask import render_template, session, redirect, url_for, current_app, flash, abort, request
from .. import db
from ..models import User
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

@login_required
@main.route('/users/<username>', methods=['GET', 'POST'])
def show_profile(username):
    return render_template('user/profile.html', user_profile=username)

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

@login_required
@main.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('.index'))

@login_manager.user_loader
def load_user(id):
    user = User.query.filter_by(username=id).first()
    return user
