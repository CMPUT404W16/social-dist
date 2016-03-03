from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, PasswordField, validators
from wtforms.validators import Required, EqualTo
from flask.ext.pagedown.fields import PageDownField



class NameForm(Form):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')

class PostForm(Form):
    body = PageDownField('What is on your mind?', validators=[Required()])
    submit = SubmitField("Post")

# form for logging in the user
class LoginForm(Form):
	name = StringField('Username', validators=[Required()])
	password = PasswordField('Password', validators=[Required()])
	submit = SubmitField('Login')

class SignupForm(Form):
	username = StringField('Username')
	password = PasswordField('New Password', validators=[Required(), EqualTo('confirm', message='Passwords must match')])
	confirm = PasswordField('Repeat Password')
	submit = SubmitField('Sign Up')

# for for setting new password
class NewPasswordForm(Form):
    new_password = PasswordField('New Password', validators=[Required()])
    confirm = PasswordField('Confirm NewPassword', validators=[Required(),
        EqualTo('confirm', message='New password mismatch!')])
    submit = SubmitField('Set')
