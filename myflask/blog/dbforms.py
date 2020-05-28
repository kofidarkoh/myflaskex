from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (BooleanField, PasswordField, StringField, SubmitField,
                     TextAreaField)
from wtforms.validators import (EqualTo, InputRequired, Length,
                                ValidationError)
from flask_login import current_user
from .dbmodels import User
from wtforms.widgets import PasswordInput

class RegisterForms(FlaskForm):
    name = StringField('Name', validators=[InputRequired('name required')])
    username = StringField('Username', validators=[InputRequired(
        'username required'), Length(max=60, min=5)])
    email = StringField('Email', validators=[
                        InputRequired('email required and must be valid')])
    password = PasswordField('Password', validators=[
                             InputRequired('password required')])
    confirm_password = StringField('Confirm Password', validators=[
                                   EqualTo('password', 'Password do not match')])

    submit = SubmitField('Register')

    def validate_email(self, email):
        if User.select().where(User.email == email.data):
            raise ValidationError('Email is already exist !')

    def validate_username(self, username):
        if User.select().where(User.username == username.data):
            raise ValidationError('Username is already exist !')


class LoginForms(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    rememberme = BooleanField('Remember Me')
    submit = SubmitField('Login')


class ArticleForms(FlaskForm):
    title = TextAreaField('Article Title', id='ftitle',
                        validators=[InputRequired()])
    content = TextAreaField(
        'Article Content', id='fcontent', validators=[InputRequired()])
    photo = FileField('File', validators=[FileAllowed(['png','jpg'])])
    submit = SubmitField('Post Article')


class UpdateArticleForms(FlaskForm):
    title = TextAreaField('Article Title', id='ftitle',
                        validators=[InputRequired()])
    content = TextAreaField(
        'Article Content', id='fcontent', validators=[InputRequired()])
    submit = SubmitField('Update Article')


class UpdateAccountForms(FlaskForm):
    name = StringField('Name', validators=[InputRequired('name required')])
    username = StringField('Username', validators=[InputRequired(
        'username required'), Length(max=60, min=5)])
    email = StringField('Email', validators=[
                        InputRequired(), InputRequired('email required and must be valid')])
    picture = FileField('Update Profile Picture', validators=[
                        FileAllowed(['png', 'jpg'])])
    submit = SubmitField('Update Account')

    def validate_email(self, email):
        if current_user.email != email.data:
            if User.select().where(User.email == email.data):
                raise ValidationError('Email is already exist !')

    def validate_username(self, username):
        if current_user.username != username.data:
            if User.select().where(User.username == username.data):
                raise ValidationError('Username is already exist !')


class ArticleCommentForm(FlaskForm):
    content = TextAreaField(
        'Any idea ? comment here', id='fcontent', validators=[InputRequired()])
    submit = SubmitField('comment')
