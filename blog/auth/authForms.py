from wtforms.validators import ValidationError , InputRequired , Email, EqualTo , Optional , Length
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, BooleanField
from flask_wtf import FlaskForm

# Login form generated with Flask-WTF
class LoginForm(FlaskForm):
    email = StringField('Email', validators = [Email() ])
    password = PasswordField('Password', validators = [InputRequired(), Length(min=6,max=32)])
    rememberme = BooleanField('Remember me')
    submit = SubmitField('Login')
