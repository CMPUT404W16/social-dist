from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, PasswordField, validators
from wtforms.validators import Required, EqualTo
from flask.ext.pagedown.fields import PageDownField



class PostForm(Form):
    body = PageDownField('What is on your mind?', validators=[Required()])
    submit = SubmitField("Post")

# form for logging in the user
class LoginForm(Form):
	name = StringField('Username', validators=[Required()])
	password = PasswordField('Password', validators=[Required()])
	submit = SubmitField('Login')

# for singup
class SignupForm(Form):
	username = StringField('Username')
	password = PasswordField('New Password', validators=[Required(), EqualTo('confirm', message='Passwords must match')])
	confirm = PasswordField('Repeat Password')
	submit = SubmitField('Sign Up')

# form for submitting an nodeAPI request
class APIForm(Form):
	name = StringField('Name', validators =[Required()])
	ip_addr = StringField('IP Address', validators =[Required()])
	email = StringField('Email', validators =[Required()])
	auth = StringField('Authentication', validators = [Required()])
	submit = SubmitField('Submit Request')

# for for setting new password
class ChangePasswordForm(Form):
    new_password = PasswordField('New Password', validators=[Required()])
    confirm_password = PasswordField('Confirm New Password',
        validators=[Required(), EqualTo('new_password',
        message='New password mismatch!')])
    submit = SubmitField('Set')
