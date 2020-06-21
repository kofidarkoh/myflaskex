from flask_login import login_user, login_required, logout_user, current_user
from playhouse.flask_utils import get_object_or_404,object_list
from flask import url_for,redirect,render_template,request,current_app,flash
from .authForms import LoginForm,RegisterForms, PostForm
from blog.models import User
from werkzeug.security import safe_join
import os

from . import auth,GenHashPassword,CheckPassword, GenHexDigest
import random


@auth.route('/', methods = ["POST","GET"])
@auth.route('/login', methods = ["POST","GET"])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('site.home'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.get_or_none(User.username == form.username.data)
		if user and CheckPassword(user.password,form.password.data):
			login_user(user,form.rememberme.data)
			flash(f'login successfully,Welcome <strong>{ current_user.name } </strong>','success')
			return redirect(url_for('site.home'))
		flash('Invalid username or password','danger')
	return render_template('auth/login.html', form = form)

@auth.route('/register', methods = ["POST","GET"])
def register():
	form = RegisterForms()
	if form.validate_on_submit():
		user_path_hash = GenHexDigest(len(form.username.data), random.random())
		user_path = os.path.join(current_app.root_path + '/static/photos/'+ user_path_hash)
		data = User.insert(name= form.name.data,username = form.username.data, email = form.email.data,password = GenHashPassword(form.password.data), photo = user_path_hash)
		data.execute()
		os.mkdir(user_path)
		flash('You are now registered','success')
		return redirect(url_for('.login'))
	return render_template('auth/register.html', form = form)

@auth.route('/logout')
@login_required
def logout():
	logout_user()
	flash('You logged out','success')
	return redirect(url_for('.login'))
