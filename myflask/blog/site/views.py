import os

import secrets

from datetime import datetime as dt

from functools import wraps

from flask import (abort, current_app, flash, redirect, render_template,
                   request, session, url_for,safe_join,Markup as mark)

from flask_login import current_user, login_required, login_user, logout_user

from peewee import fn

from playhouse.flask_utils import (get_current_url, get_next_url,
                                   get_object_or_404, object_list)

from werkzeug.security import check_password_hash, generate_password_hash

from werkzeug.utils import secure_filename

from blog.dbforms import (ArticleCommentForm, ArticleForms, LoginForms,
                          RegisterForms, UpdateAccountForms,
                          UpdateArticleForms)

from blog.dbmodels import Article,Rstatus_code, Comment, User, Article_Likes, get_or_404, human_time,Relationship

from . import bp

meth = ["GET","POST"]

@bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('.home'))
    return render_template('index.html')


@bp.route('/register', methods= meth)
def register():
    form = RegisterForms()
    if current_user.is_authenticated:
        return redirect(url_for('.home'))
    if form.validate_on_submit():
        passhash = generate_password_hash(
            form.password.data, salt_length=len(form.password.data))
        user = User.insert(name=form.name.data, username=form.username.data,
                           email=form.email.data, password=passhash, location=request.form['location'])
        user.execute()
        os.mkdir(os.path.join(current_app.root_path,
                              'static/profile_pictures/', form.username.data))
        flash('You successfully registed and can login now', 'success')
        return redirect(url_for('.login'))
    return render_template('register.html', form=form, title='Register', passwd = form.password.data)


@bp.route('/login', methods= meth)
def login():
    form = LoginForms()
    user_password = None
    if current_user.is_authenticated:
        return redirect(url_for('.home'))
    if form.validate_on_submit():

        user = User.get_or_none(User.username == form.username.data )
        user_password = user.password
        if user and check_password_hash(user.password, form.password.data):

            login_user(user, form.rememberme.data)
            flash('You login successfully', 'success')
            return redirect(url_for('.home'))
        else:
            flash('Invalid Credentials or User not found', 'danger')
    return render_template('login.html', form=form, title='Login')


@bp.route('/home')
@login_required
def home():
    page = request.args.get('page', 1, type=int)
    article = current_user.user_friend_article()
    return object_list('user-home/home.html', article,human_time
    = human_time, paginate_by=4, page=page,title  = f"Home | { current_user.name }" , int = int)


def save_user_picture(form_picture):
    #from PIL import Image
    'save photo to file system and database'
    secure_name = secrets.token_hex(18)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = secure_filename(secure_name + f_ext)
    picture_path = safe_join(current_app.root_path,f'static/profile_pictures/{current_user.username}/' + picture_fn)
    #pic = Image.open(form_picture)
    #out_pic = (250,180)
    #pic.thumbnail(out_pic)
    form_picture.save(picture_path)

    return picture_fn


@bp.route('/account', methods= meth)
@login_required
def account():
    form = UpdateAccountForms()
    image = url_for('static', filename='profile_pictures/' + current_user.username +'/'+
                    current_user.picture)
    if form.validate_on_submit():
        update_user = User.update(name=form.name.data, email=form.email.data, username=form.username.data,
                                  location=request.form['location']).where(User.id == current_user.id)
        if form.picture.data:
            ss = os.system(f"rm {safe_join(current_app.root_path,f'static/profile_pictures/{current_user.username}/' + current_user.picture)}")
            profile_pic = save_user_picture(form.picture.data)
            User.update(picture=profile_pic).where(
                User.id == current_user.id).execute()
        update_user.execute()
        flash('Account Updated', 'success')
        return redirect(url_for('.account'))
    elif request.method == 'GET':
        form.name.data = current_user.name
        form.email.data = current_user.email
        form.username.data = current_user.username
    return render_template('user-home/account.html', image=image, form=form)


@bp.route('/account/<string:id>', methods= meth)
@login_required
def user_account(id):
    user = get_or_404(User,User.id == id)
    image = url_for('static', filename='profile_pictures/'+user.username+'/' + user.picture)
    return render_template('user-home/user-account.html', user=user, image=image, title = f'{user.name} Account')

@bp.route('/delete_account/<string:id>', methods= meth)
@login_required
def delete_account(id):
    Article.delete().where(Article.user == current_user.id).execute()
    Comment.delete().where(Comment.user == current_user.id).execute()
    userd = os.path.join(current_app.root_path,'static/profile_pictures/' + current_user.username)
    os.system(f"rm -rf {userd} ")
    User.delete_by_id(id)
    flash('Your Account has been deleted','success')
    logout_user()
    return redirect(url_for('.login'))

@bp.route('/people', methods= meth)
@login_required
def people():
    users = User.select().where(User.id != current_user.id)
    return object_list('user-home/people.html',users,rstatus = Rstatus_code)


@bp.route('/confirm_friend_request/<int:userid>',methods = meth)
@login_required
def confirm_friend(userid):
    current_user.confirm_relationship(userid)
    flash(' friend request confirmed','success')
    return redirect(url_for('.people'))

@bp.route('/declined_friend_request/<int:userid>', methods = meth)
@login_required
def disclined_friend(userid):
    current_user.disclined_relationship(userid)
    flash(' friend request disclined','success')
    return redirect(url_for('.people'))


@bp.route('/add_friend/<int:id>', methods= meth)
@login_required
def add_friend(id):
    user = User.get_or_none(User.id == id)
    if user is None:
        flash('User does not exist', 'warning')
        return redirect(url_for('.people'))
    current_user.AddUser(user.id)
    flash(f'You have sent { user.name } friend request', 'success')
    return redirect(url_for('.people'))



@bp.route('/unfriend/<int:id>', methods= meth)
@login_required
def unfriend(id):
    user = User.get_or_none(User.id == id)
    if user is None:
        flash('User does not exist', 'warning')
        return redirect(url_for('.people'))
    else:
        current_user.unfriend(user.id)
    flash(f'User unfollowed { user.name }', 'success')
    return redirect(url_for('.people'))

@bp.route('/friends')
@login_required
def friends():
    user = User.user_friends(current_user.id)
    return object_list('user-home/friends.html',user)

def save_post_photo(form_picture):
    _,ext = os.path.splitext(form_picture.filename)
    picture_fn = secrets.token_hex(12) + ext
    secure_file = secure_filename(picture_fn)
    file_path = os.path.join(current_app.root_path,'static/post_image/' + secure_file)
    form_picture.save(file_path)
    return picture_fn

@bp.route('/new-article', methods= meth)
@login_required
def new_article():
    form = ArticleForms()
    if form.validate_on_submit():
        Article.insert(title=form.title.data, body=form.content.data, user=current_user.id).execute()
        if form.photo.data:
            Article.update(photo = save_post_photo(form.photo.data)).where(Article.title == form.title.data).execute()
        flash('Article Added', 'success')
        return redirect(url_for('.home'))
    return render_template('user-home/new_article.html', form=form)


@bp.route('/read/article/<int:pid>', methods= meth)
@login_required
def read_article(pid):
    form = ArticleCommentForm()
    article = Article.get_or_404(Article.id == pid)
    if form.validate_on_submit():
        com = Comment.insert(body=form.content.data,
                             post=article.id, user=current_user.id)
        com.execute()
        flash('New Comment Added', 'success')
        return redirect(url_for('.read_article', pid=article.id))
    return render_template('user-home/article.html', article=article, form=form, comment=(Comment.select().where(Comment.post == pid)))

@bp.route('/<int:id>/like', methods= meth)
def like_article(id):
    if current_user.is_artliked(id):
        flash('You already liked this Article','info')
        return redirect(url_for('.home'))
    current_user.user_like_article(id,current_user.id)
    current_user.update_art_like(id)
    flash('You Liked this Article','success')
    return redirect(url_for('.home'))

@bp.route('/<int:id>/unlike', methods= meth)
def unlike_article(id):
    current_user.unlike_art(current_user.id,id)
    flash('You unLiked this Article','success')
    return redirect(url_for('.home'))

@bp.route('/<int:pid>/delete-comment/<int:id>', methods= meth)
def delete_comment(pid,id):
    com = Comment.get(Comment.id == id)
    Comment.delete().where((Comment.date_commented == com.date_commented ) & (Comment.user == current_user.id)).execute()
    flash('Comment deleted', 'success')
    return redirect(url_for('.read_article',pid=pid))


@bp.route('/delete-article/<int:id>', methods= meth)
@login_required
def delete_article(id):
    artuser = Article.get_by_id(id)
    if artuser.user.id != current_user.id:
        abort(403)
    del_com = Comment.delete().where(Comment.post == id)
    del_com.execute()
    article = Article.delete().where(Article.id == id)
    article.execute()
    flash('Article Deleted Successfully', 'success')
    return redirect(url_for('.home'))


@bp.route('/update/article/<int:pid>', methods= meth)
@login_required
def update_article(pid):
    form = UpdateArticleForms()
    article = get_object_or_404 (Article,Article.id == pid)
    if article.user.id != current_user.id:
        abort(403)
    if form.validate_on_submit():
        art = Article.update(title=form.title.data,
                             body=form.content.data).where(Article.id == pid)
        art.execute()
        flash('Article Updated', 'success')
        return redirect(url_for('.read_article', pid=article.id))
    elif request.method == 'GET':
        form.title.data = article.title
        form.content.data = article.body
    return render_template('user-home/update_article.html', form=form, article=article)


@bp.route('/logout')
@login_required
def logout():
    current_user.ping_lastlogin()
    logout_user()
    flash('You logout', 'success')
    return redirect(url_for('.login'))


@bp.app_errorhandler(404)
def error404(error):
    return render_template('errors/404.html'), 404


@bp.app_errorhandler(403)
def error404(error):
    return render_template('errors/403.html'), 403
