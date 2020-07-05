from peewee import *
from flask_login import UserMixin, LoginManager, current_user
from playhouse.sqliteq import SqliteQueueDatabase  # peewee extra lib playhouse
import arrow  # time and date
from datetime import datetime as dtime
import os
from flask import abort

login_manager = LoginManager()

# sqlite database file path
db_path = os.path.join(os.path.dirname(__file__) + '/blogDB.db')

# peeweee sqlite database config
db = SqliteDatabase(db_path, pragmas={'foreign_keys': 1, 'cache_size': 1024, 'journal_mode': 'wal'})
# db = MySQLDatabase(database='mydb',user = 'admin',password='cybertron')
# all table base


@login_manager.user_loader
def load_user(user_id):
    try:
        user = User.get_by_id(user_id)
        return user
    except DoesNotExist:
        pass
    return None

class BaseModel(Model):

    class Meta:
        database = db

class msg_status:
	read_pending = 0
	read = 1
	delete = 3

class rstatus:
    pending = 0
    accept = 1
    ignore = 2
    cancel = 3
    delete = 4


class User(BaseModel, UserMixin):
    name = CharField()
    email = CharField(unique=True)
    username = CharField(unique=True)
    password = CharField()
    lastseen = CharField(default=dtime.now())
    photo = CharField(default='photo.jpg')
    joined = DateTimeField(default=dtime.now)

    def dtime(self):
        utc = arrow.get(self.joined)
        return utc.humanize()

    def count_user_post(self):
        return Post.user_post().count()


class Post(BaseModel):
    content = TextField()
    date = DateTimeField(default=dtime.now)
    user = ForeignKeyField(User, backref='user_post',
                           on_delete='cascade', on_update='cascade')
    likes = CharField(default=0)

    def __unicode__(self):
        return self.content

    @classmethod
    def dtime(cls, date):
        utc = arrow.get(date)
        return utc.humanize()

    @classmethod
    def user_posts(cls):
        user1 = Post.select(Post,relationship).join(relationship,on=(relationship.status == rstatus.accept)).where((relationship.to_user == current_user.id) & (relationship.from_user == Post.user))

        user2 = Post.select(Post,relationship).join(relationship,on=(relationship.status == rstatus.accept)).where((relationship.to_user == Post.user) & (relationship.from_user == current_user.id) | (Post.user == current_user.id))
        result = user1 | user2.order_by(Post.date.desc())
        if result:
        	return result
        return Post.select().where(Post.user == current_user.id).order_by(Post.date.desc())

    @classmethod
    def user_post(cls):
        # .where(Post.user == current_user.id)
        return Post.select(Post, relationship).join(relationship, on=(relationship.from_user == Post.user)).where((relationship.status == rstatus.accept))

    @classmethod
    def delete_post(cls, pid):
        if Post.select().where(Post.id == pid):
            Comment.delete().where(Comment.post == pid).execute()
            return Post.delete().where(Post.id == pid).execute()

    @classmethod
    def is_post_liked(self, pid, user):
        return (LikePost.select().where((LikePost.post == pid) & (LikePost.user == user)).exists())

    @classmethod
    def like_post(cls, pid, user):
        if not Post.is_post_liked(pid, user):
            post = Post.get(Post.id == pid)
            LikePost.create(post=pid, user=user)
            Post.update(likes=int(post.likes) + 1).where((Post.id ==
                                                          post.id) & (Post.user == post.user)).execute()

    @classmethod
    def unlike_post(cls, pid, user):
        if Post.is_post_liked(pid, user):
            post = Post.get(Post.id == pid)
            Post.update(likes=int(post.likes) - 1).where((Post.id ==
                                                          post.id) & (Post.user == post.user)).execute()


class LikePost(BaseModel):
    post = ForeignKeyField(Post, backref='post_like',
                           on_delete='cascade', on_update='cascade')
    user = ForeignKeyField(User, backref='like_user',
                           on_delete='cascade', on_update='cascade')
    date = DateTimeField(default=dtime.now())

    @classmethod
    def delete_like(cls, pid, user):
        return cls.delete().where((cls.post == pid) & (cls.user == user)).execute()


class Comment(BaseModel):
    content = TextField()
    post = ForeignKeyField(Post, backref='post_comment',
                           on_delete='cascade', on_update='cascade')
    date = DateTimeField(default=dtime.now)
    user = ForeignKeyField(User, backref='comment_user',
                           on_delete='cascade', on_update='cascade')
    likes = CharField(default=0)

    @classmethod
    def create_comment(cls, comment_content, user, post):
        return cls.insert(content=comment_content, user=user, post=post).execute()

    @classmethod
    def get_post_comments(cls, pid):
        res = cls.select().where(cls.post == pid)
        return res

    @classmethod
    def update_comment(cls, comment_content, post, user):
        return cls.update(content=comment_content).where((cls.post == post) & (cls.user == user)).execute()

    @classmethod
    def delete_comment(cls, cid, pid):
        com = cls.get(cls.id == cid)
        return cls.delete().where((cls.date == com.date) & (cls.post == pid)).execute()


class relationship(BaseModel):
    from_user = ForeignKeyField(
        User, backref='rel_user', on_delete='cascade', on_update='cascade')
    to_user = ForeignKeyField(User, backref='rel_user',
                              on_delete='cascade', on_update='cascade')
    status = IntegerField(default=rstatus.pending)
    action_user = ForeignKeyField(
        User, backref='rel_user', on_delete='cascade', on_update='cascade')
    date = DateTimeField(default=dtime.now)

    @classmethod
    def is_to_relationship_pending(cls, to_user, from_user):
        return (cls.select().where((cls.to_user == to_user) & (cls.from_user == from_user) & (cls.status == rstatus.pending)))

    @classmethod
    def is_from_relationship_pending(cls, to_user, from_user):
        return (cls.select().where((cls.to_user == to_user) & (cls.from_user == from_user) & (cls.status == rstatus.pending)))

    @classmethod
    def pending_relationship_request(cls, to_user):
        return (cls.select().where((cls.to_user == to_user) & (cls.status == rstatus.pending)))

    @classmethod
    def add_friend(cls, from_user, to_user):
        if not cls.is_from_relationship_pending(to_user, from_user) or not cls.is_to_relationship_pending(to_user, from_user):
            return (relationship.create(from_user=from_user, to_user=to_user, action_user=from_user))

    @classmethod
    def cancel_relationship(cls, action_user, to_user):
        return cls.update(status=rstatus.cancel).where((cls.action_user == action_user) & (cls.to_user == to_user)).execute()

    @classmethod
    def delete_pending_relationship(cls, action_user, to_user):
        return cls.update(status=rstatus.delete).where((cls.action_user == action_user) & (cls.to_user == to_user)).execute()

    @classmethod
    def is_related(cls, to_user, from_user):
        return cls.select().where((cls.to_user == to_user) & (cls.from_user == from_user) & (cls.status == rstatus.accept))

    @classmethod
    def delete_relationship(cls, touser):
        return cls.delete().where((cls.from_user == touser) | (cls.to_user == touser) & (cls.status == rstatus.accept)).execute()

    @classmethod
    def accept_relationship(cls, fromuser):
    	return (cls.update(status=rstatus.accept).where((cls.to_user == current_user.id) & (cls.from_user == fromuser) & (cls.status == rstatus.pending))).execute()


class messages(BaseModel):
	content = CharField()
	date = DateTimeField(default= dtime.now())
	status = IntegerField(default=  msg_status.read_pending )
	from_user = ForeignKeyField(User, backref='send_user', on_delete='cascade', on_update='cascade')
	to_user = ForeignKeyField(User, backref='recv_user', on_delete='cascade', on_update='cascade')

	@classmethod
	def send(cls,to_user,content):
		return cls.insert(from_user = current_user.id, to_user = to_user, content = content).execute()

	@classmethod
	def messages(cls):
		new_recv_msg = (cls.select().where((cls.to_user == current_user.id) & (cls.status == msg_status.read_pending )))
		sent_msg = (cls.select().where((cls.from_user == current_user.id) & (cls.status == msg_status.read_pending )))
		result = new_recv_msg | sent_msg
		print(result)
		return result


	@classmethod
	def new_message(cls):
		return (cls.select().where((cls.to_user == current_user.id) & (cls.status == msg_status.read_pending )))

	@classmethod
	def read_message(cls,fromuser):
		return cls.update(status = msg_status.read).where((messages.to_user == current_user.id) & (messages.from_user == fromuser ) & (messages.status == msg_status.read )).execute()


class reply_message(BaseModel):
	content = CharField()
	date = DateTimeField(default= dtime.now())
	status = IntegerField(default=  msg_status.read_pending )
	user = ForeignKeyField(User, backref='msg_user', on_delete='cascade', on_update='cascade')
	msg = ForeignKeyField(messages, on_delete='cascade', on_update='cascade')

	@classmethod
	def reply(cls,content,user,mid):
		return cls.insert(content = content,user = user,msg = mid).execute()

	@classmethod
	def msg_reply(cls,mid):
		guser = cls.select().where(cls.msg == mid)
		return guser

	@classmethod
	def to_message(cls):
		fuser = messages.select().where(messages.from_user == current_user.id)
		result = fuser
		return result

db.connect()

db.create_tables([User,LikePost,Post, reply_message, messages,Comment,relationship])

db.close()
