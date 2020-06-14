from wtforms.validators import ValidationError , InputRequired , EqualTo , Optional , Length
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, BooleanField
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from blog.models import User
from flask_login import current_user
from wtforms.fields.html5 import EmailField
# Login form generated with Flask-WTF
class LoginForm(FlaskForm):
    username = StringField('Username', validators = [InputRequired()])
    password = PasswordField('Password', validators = [InputRequired()])
    rememberme = BooleanField('Remember me')
    submit = SubmitField('Login')


class RegisterForms(FlaskForm):
	name = StringField('Name', validators=[InputRequired()])
	email = EmailField('Email', validators=[InputRequired()])
	username = StringField('Username', validators=[InputRequired()])
	password = PasswordField('Password',validators=[InputRequired(), Length(min=6,max=32)])
	submit = SubmitField('Register')

	def validate_email(self,field):
		user = User.select().where(User.email == field.data)
		if user:
			raise ValidationError('Email exist try another email address')

	def validate_username(self,field):
		user = User.select().where(User.username == field.data)
		if user:
			raise ValidationError('Username exist try another username')

class PostForm(FlaskForm):
	post_content = TextAreaField(validators=[InputRequired()])
	submit = SubmitField('Post')

class UpdatePostForm(FlaskForm):
	post_content = TextAreaField(validators=[InputRequired()])
	submit = SubmitField('update')

class CommentForm(FlaskForm):
	comment_content = TextAreaField(validators=[InputRequired()])
	submit = SubmitField('comment')

class CommentFormUpdate(FlaskForm):
	comment_content_update = TextAreaField(validators=[InputRequired()])
	submit = SubmitField('update')


class UpdateAccountInfo(FlaskForm):
	name = StringField('Name', validators=[InputRequired()])
	email = EmailField('Email', validators=[InputRequired()])
	username = StringField('Username', validators=[InputRequired()])
	photo = FileField('update photo', validators=[FileAllowed(['jpg','png'])])
	submit = SubmitField('update')


	def validate_email(self,field):
		if current_user.email != field.data:
			user = User.select().where(User.email == field.data)
			if user:
				raise ValidationError('Email exist try another email address')

	def validate_username(self,field):
		if field.data != current_user.username:
			user = User.select().where(User.username == field.data)
			if user:
				raise ValidationError('Username exist try another username')