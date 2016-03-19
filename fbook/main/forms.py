from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, PasswordField, validators, SelectField
from wtforms.validators import Required, EqualTo
from flask.ext.pagedown.fields import PageDownField

class PostForm(Form):
    title = StringField('Title', validators=[Required()])
    body = PageDownField('What is on your mind?', validators=[Required()])
    mkdown = SelectField('Use markdown for this post?', choices=[("False", 'No'),("True", 'Yes')], default=False)
    privacy = SelectFiled('Public', choices=[("Public", 'Public'),("Only me", 'Only me'),("Only me and my friend",'Only me and my friend')], default=False)
    submit = SubmitField("Post")

# form for logging in the user
class LoginForm(Form):
	name = StringField('Username', validators=[Required()])
	password = PasswordField('Password', validators=[Required()])
	submitLogin = SubmitField('Login')

# for singup
class SignupForm(Form):
	username = StringField('Username')
	password = PasswordField('New Password', validators=[Required(), EqualTo('confirm', message='Passwords must match')])
	confirm = PasswordField('Repeat Password')
	submit = SubmitField('Sign Up')

# form for submitting an nodeAPI request
class APIForm(Form):
	name = StringField('Name', validators =[Required()])
	username = StringField('UserName', validators = [Required()])
	password = PasswordField('New Password', validators=[Required(), EqualTo('confirm', message='Passwords must match')])
	confirm = PasswordField('Repeat Password', validators=[Required()])
	email = StringField('Email', validators =[Required()])
	submit = SubmitField('Submit Request')

# for for setting new password
class ChangePasswordForm(Form):
    new_password = PasswordField('New Password', validators=[Required()])
    confirm_password = PasswordField('Confirm New Password',
        validators=[Required(), EqualTo('new_password',
        message='New password mismatch!')])
    submit_p = SubmitField('Set Password')

# for for setting new password
class ChangeUsernameForm(Form):
    new_username = StringField('New Username', validators=[Required()])
    confirm = StringField('Confirm New Username',
        validators=[Required(), EqualTo('new_username',
        message='New username mismatch!')])
    submit_u = SubmitField('Set Username')

class CommentForm(Form):
    body = StringField('', validators=[Required()])
    submit = SubmitField('Submit')
