from blog.models import User,login_manager, Post,LikePost,relationship
from flask import render_template,url_for,redirect,request,flash
from blog.auth.authForms import PostForm,UpdateAccountInfo
from blog.auth.utils import meth, GenHexDigest
from werkzeug.security import safe_join
from random import random
import os
from werkzeug.utils import secure_filename
from flask_login import current_user,login_required
from playhouse.flask_utils import get_object_or_404 as get_or_404,object_list
from flask import Blueprint, current_app,abort

site = Blueprint('site', __name__)


@site.route('/home', methods = meth)
@login_required
def home():
	form = PostForm()
	return render_template('home/home.html', post = Post.user_post(),form = form)

@site.route('/new_post', methods = meth)
@login_required
def new_post():
	form = PostForm()
	if form.validate_on_submit():
		post = Post.insert(content = form.post_content.data,user = current_user.id)
		post.execute()
		flash('New Post created','success')
		return redirect(url_for('.home'))
	# return render_template('home/home.html',form = form)



@site.route('/view/post/<int:pid>', methods = meth)
@login_required
def view_post(pid):
	post = get_or_404(Post, Post.id == pid)
	form = PostForm()
	if form.validate_on_submit():
		if post.user.id != current_user.id:
			return abort(403)
		Post.update(content = form.post_content.data).where(Post.id == post.id).execute()
		flash('Post update','success')
		return redirect(url_for('.view_post', pid = pid))
	if request.method == meth[1]:
		form.post_content.data = post.content
	return render_template('home/view_post.html',post = post,form =form)

@site.route('/like/post/<int:pid>', methods = meth)
@login_required
def like_post(pid):
	Post.like_post(pid,current_user.id)
	flash('Post liked <i class="fa fa-thumbs-up"></i>','success')
	return redirect(url_for('.home'))

@site.route('/unlike/post/<int:pid>', methods = meth)
@login_required
def unlike_post(pid):
	Post.unlike_post(pid,current_user.id)
	LikePost.delete_like(pid, current_user.id)
	flash('Post unliked <i class="fa fa-thumbs-down"></i>','success')
	return redirect(url_for('.home'))

@site.route('/delete/post/<int:pid>', methods = meth)
@login_required
def delete_post(pid):
	Post.delete_post(pid)
	flash('Post deleted','success')
	return redirect(url_for('.home'))

def save_photo(form_photo):
	_, ext = os.path.splitext(form_photo.filename)
	photo_name = secure_filename(GenHexDigest(random(),random())) + ext
	photo_path = safe_join(current_app.root_path +'/static/photos/' + current_user.username, photo_name)
	form_photo.save(photo_path)
	return photo_name

@site.route('/account/<string:username>', methods = meth)
@login_required
def account(username):
	form = UpdateAccountInfo()
	if form.validate_on_submit():
		user = User.update(name = form.name.data,email = form.email.data,username = form.username.data).where(User.id == current_user.id)
		if form.photo.data:
			photoname = save_photo(form.photo.data)
			User.update(photo = photoname).where(User.id == current_user.id).execute()
		user.execute()
		flash('Account updated','success')
		return redirect(url_for('.account', username = username))
	if request.method == meth[1]:
		form.email.data = current_user.email
		form.name.data = current_user.name
		form.username.data = current_user.username
	return render_template('home/account.html',form = form)

@site.route('/people', methods = meth)
@login_required
def people():
	return object_list('home/people.html',User.select().where(User.id != current_user.id),rela = relationship())

@site.route('/follow/user/<int:usid>', methods = meth)
@login_required
def follow(usid):
	relationship.follow(current_user.id, usid)
	flash('<strong> request sent </strong>','success')
	return redirect(url_for('.people'))

@site.route('/cancel_follow_request/user/<int:usid>', methods = meth)
@login_required
def cancel_follow(usid):
	relationship.cancel_relationship(current_user.id, usid)
	flash('<strong> request canceled </strong>','success')
	return redirect(url_for('.people'))

@site.route('/confirm_follow_request/user/<int:usid>', methods = meth)
@login_required
def confirm_follow(usid):
	relationship.accept_relationship(usid, current_user.id)
	flash('<strong>confirmed</strong>','success')
	return redirect(url_for('.people'))

@site.route('/delete_follow_request/user/<int:usid>', methods = meth)
@login_required
def delete_follow(usid):
	relationship.delete_pending_relationship(usid, current_user.id)
	flash('<strong>request deleted</strong>','success')
	return redirect(url_for('.people'))