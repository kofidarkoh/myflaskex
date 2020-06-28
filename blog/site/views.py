from blog.models import User,login_manager, Post,LikePost,relationship,Comment, accept_relationship
from flask import render_template,url_for,redirect,request,flash, session
from blog.auth.authForms import PostForm,UpdateAccountInfo,CommentForm,CommentFormUpdate,UpdatePostForm
from blog.auth.utils import meth, GenHexDigest
from werkzeug.security import safe_join
from random import random
import os
from werkzeug.utils import secure_filename
from flask_login import current_user, login_required
from playhouse.flask_utils import get_object_or_404 as get_or_404, object_list
from flask import Blueprint, current_app,abort

site = Blueprint('site', __name__)

@site.route('/home', methods = meth)
@login_required
def home():
	print(session)
	all_post = Post.user_posts()
	page = request.args.get('page',1,int)
	form = PostForm()
	if all_post:
		return object_list('home/home.html',Post.user_posts(),relationship = relationship, page= page,paginate_by=10, context_variable='post_list',form = form)
	return render_template('home/home.html',post_list = Post.select().where(Post.user == current_user.id),form = form)

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
	page = request.args.get('page',1,int)
	post = get_or_404(Post, Post.id == pid)
	form = UpdatePostForm()
	comment_form = CommentForm()
	com = Comment.get_post_comments(pid)
	if form.validate_on_submit():
		if post.user.id != current_user.id:
			return abort(403)
		Post.update(content = form.post_content.data).where(Post.id == post.id).execute()
		flash('Post update','success')
		return redirect(url_for('.view_post', pid = pid))
	if request.method == meth[1]:
		form.post_content.data = post.content
	all_comment = Comment.get_post_comments(pid)
	if all_comment:
		return object_list('home/view_post.html',Comment.get_post_comments(pid), context_variable='comment_list', post = post,form =form,comment_form = comment_form ,paginate_by=2,page=page)
	return render_template('home/view_post.html',comment_form = comment_form, post = post, form = form, comment_list = all_comment)

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

@site.route('/comment/post/<int:pid>', methods = meth)
@login_required
def comment_post(pid):
	form = CommentForm()
	Comment.create_comment(form.comment_content.data, current_user.id, pid)
	flash('new comment ','success')
	return redirect(url_for('.view_post', pid = pid))

@site.route('/update_comment/post/<int:pid>/<int:cid>', methods = meth)
@login_required
def update_comment_post(pid, cid):
	form = CommentFormUpdate()
	comment = get_or_404(Comment, Comment.id == cid)
	if form.validate_on_submit():
		Comment.update_comment(form.comment_content_update.data, current_user.id, pid)
		flash('comment updated','success')
		return redirect(url_for('view_post', pid = pid))
	if request.method == meth[1]:
		form.comment_content_update.data = comment.content
	return render_template('home/update_comment.html',form = form,comment = comment)


# @site.route('/update_comment/post/<int:pid>', methods = meth)
# @login_required
# def update_comment_post(pid):
# 	form = CommentFormUpdate()
# 	Comment.update_comment(form.comment_content_update.data, pid, current_user.id)
# 	flash('comment updated <i class="fa fa-thumbs-up"></i>','success')
# 	return redirect(url_for('.view_post', pid = pid))

@site.route('/delete/comment/<int:cid>/<int:pid>', methods = meth)
@login_required
def delete_comment(cid,pid):
	Comment.delete_comment(cid,pid)
	flash('comment deleted','success')
	return redirect(url_for('.view_post', pid = pid))

def save_photo(form_photo):
	_, ext = os.path.splitext(form_photo.filename)
	photo_name = secure_filename(GenHexDigest(random(),random())) + ext
	photo_path = os.path.join(current_app.root_path +'/static/photos/' + current_user.username, photo_name)
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
		os.rename(os.path.join(current_app.root_path +'/static/photos/' , current_user.username), os.path.join(current_app.root_path +'/static/photos',form.username.data))
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

@site.route('/add_friend/user/<int:usid>', methods = meth)
@login_required
def add_friend(usid):
	relationship.add_friend(current_user.id, usid)
	flash('<strong> request sent </strong>','success')
	return redirect(url_for('.people'))

@site.route('/cancel_follow_request/user/<int:usid>', methods = meth)
@login_required
def cancel_friend(usid):
	relationship.cancel_relationship(current_user.id, usid)
	flash('<strong> request canceled </strong>','success')
	return redirect(url_for('.people'))

@site.route('/confirm_friend_request/user/<int:usid>')
@login_required
def confirm_friend(usid):
	accept_relationship(usid)
	flash('<strong>confirmed</strong>','success')
	return redirect(url_for('.people'))

@site.route('/unfriend/user/<int:usid>', methods = meth)
@login_required
def unfriend(usid):
	relationship.delete_relationship(usid)
	flash('<strong>unfollowed</strong>','success')
	return redirect(url_for('.people'))

@site.route('/delete_friend_request/user/<int:usid>', methods = meth)
@login_required
def delete_friend(usid):
	relationship.delete_pending_relationship(usid, current_user.id)
	flash('<strong>request deleted</strong>','success')
	return redirect(url_for('.people'))