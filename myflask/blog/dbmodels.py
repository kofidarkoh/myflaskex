from peewee import *
from threading import Thread
from datetime import datetime as dt

from flask_login import LoginManager, UserMixin, current_user

from secrets import token_hex

from flask import abort

from werkzeug.security import check_password_hash, generate_password_hash

import os

import arrow

from playhouse.sqlite_ext import SqliteExtDatabase

from flask import current_app

login_manager = LoginManager()

db_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'site.db')

db = SqliteExtDatabase(db_path, pragmas={'journal_mode': 'wal', 'cache_size': -64 * 1000})
# '/home/koficrypto/myflask/site.db'
# db = PostgresqlDatabase(host='127.0.0.1',database='mydb',user='cybertron',password='cybertron')

class BaseModel(Model):

    class Meta:
        database = db


class AdminUser(BaseModel):
    name = CharField()
    password_hash = CharField()
    username = CharField(unique=True)
    email = CharField(unique=True)

    @classmethod
    def hash_password(cl, password):
        AdminUser.password_hash = generate_password_hash(password)

    @classmethod
    def verify_password(cl, password):
        return check_password_hash(AdminUser.password_hash, password)


class User(BaseModel, UserMixin):
    date_join = CharField(default=dt.now)
    email = CharField(unique=True)
    kcrypto_id = CharField(default=token_hex(14))
    last_login = CharField(default='none')
    location = CharField()
    name = CharField()
    password = CharField()
    picture = CharField(default='picture.jpg')
    username = CharField(unique=True)

    class Meta:
        table_name = 'user'

    def __unicode__(self):
        return self.username

    def is_relationship(self, user):
        return (Relationship.select().where((Relationship.to_user == self) | (Relationship.from_user == user) | (Relationship.from_user == self) & (Relationship.status_code == Rstatus_code.accepted)))

    def is_pending_relationship(self,user):
        return Relationship.select().where((Relationship.to_user == user ) and (Relationship.from_user == self) & (Relationship.status_code == Rstatus_code.pending)).exists()

    def get_all_pending_relationship(self,user):
        return Relationship.select().where((Relationship.to_user == self) & (Relationship.from_user == user) & (Relationship.status_code == Rstatus_code.pending) )

    def count_pending_relationship(self):
         return Relationship.select(Relationship.status_code).where((Relationship.to_user == self) & (Relationship.status_code == Rstatus_code.pending)).count()

    def AddUser(self, user):
        if not self.is_pending_relationship(user):
            Relationship.insert(from_user=self, to_user=user,status_code = Rstatus_code.pending,action_user = self).execute()

    def confirm_relationship(self,user):
        return (Relationship.update(status_code = Rstatus_code.accepted).where((Relationship.to_user == self) & (Relationship.from_user == user) & (Relationship.status_code == Rstatus_code.pending)).execute())

    def disclined_relationship(self,user):
        Relationship.update(status_code = Rstatus_code.disclined).where((Relationship.to_user == self) & (Relationship.from_user == user) & (Relationship.status_code == Rstatus_code.pending)).execute()
    def is_disclined_relationship(self,user):
        return Relationship.select(Relationship.status_code).where((Relationship.to_user == self) & (Relationship.from_user == user) & (Relationship.status_code == Rstatus_code.disclined))

    def unfriend(self, user):
        Relationship.delete().where((Relationship.to_user == user) & (Relationship.status_code == Rstatus_code.accepted) & (Relationship.from_user == self))

    @staticmethod
    def user_friends(userid):
        return Relationship.select().where((Relationship.to_user == userid) & (Relationship.status_code == Rstatus_code.accepted))

    def user_friend_article(self):
        return Article.select().join(User).join(Relationship,on=Relationship.to_user).where((Relationship.from_user == self)| (Relationship.to_user == self) & (Relationship.status_code == Rstatus_code.accepted)).order_by(Article.date_posted.desc())

    def user_lastseen(self, id):
        user = User.get_by_id(id)
        utc = arrow.get(user.last_login)
        return utc.humanize()

    def ping_lastlogin(self):
        User.update(last_login=dt.now()).where(User.id == self.id).execute()

    def user_like_article(self, pid, userid):
        if not current_user.is_artliked(pid):
            Article_Likes.insert(post=pid, user=userid).execute()

    def is_artliked(self, pid):
        return (Article_Likes.select().where((Article_Likes.user == self) & (Article_Likes.post == pid)).exists())

    def get_art_like(self, id):
        return (Article_Likes.select().where(Article_Likes.post == id).count())

    def update_art_like(self, pid):
        Article.update(likes=current_user.get_art_like(pid)).where(Article.id == pid).execute()

    def get_userlike(self, userid, pid):
        return Article_Likes.select(Article_Likes.user).where((Article_Likes.post == pid) & (Article_Likes.user == userid))

    def unlike_art(self, userid, pid):
        art = Article.get(Article.id == pid)
        Article.update(likes=int(art.likes) - 1).where(Article.id == pid).execute()
        Article_Likes.delete().where((Article_Likes.user == userid) & (Article_Likes.post == pid)).execute()


class ProfilePicture(BaseModel):
    user = ForeignKeyField(User, backref='user_dp', on_delete='cascade', on_update='cascade')


class Article(BaseModel):
    body = TextField()
    date_posted = DateTimeField(default=dt.now)
    kcrypto_id = CharField(default=token_hex(14))
    title = TextField()
    likes = CharField(default=0)
    photo = CharField(default='picture')
    user = ForeignKeyField(column_name='user_id', field='id', model=User,
                           on_delete='cascade', on_update='cascade')

    class Meta:
        table_name = 'article'

    def __unicode__(self):
        return self.body

    @classmethod
    def dtime(cls, date_posted):
        utc = arrow.get(date_posted)
        return utc.humanize()

    @classmethod
    def get_or_404(cls,*args):
        try:
            res = cls.get(*args)
        except DoesNotExist:
            return abort(404)
        return res

class Article_Likes(BaseModel):
    user = ForeignKeyField(User, backref='user_artlike', on_delete='cascade',
                           on_update='cascade', null=True)
    post = ForeignKeyField(Article, backref='art_like', on_delete='cascade',
                           on_update='cascade', null=True)
    likes = CharField(default=0)


class Comment(BaseModel):
    body = TextField()
    date_commented = DateTimeField(default=dt.now)
    kcrypto_id = CharField(default=token_hex(14))
    post = ForeignKeyField(column_name='post_id', field='id',
                           model=Article, on_delete='cascade', on_update='cascade')
    user = ForeignKeyField(column_name='user_id', field='id',
                           model=User, on_delete='cascade', on_update='cascade')

    class Meta:
        table_name = 'comment'

    @classmethod
    def dtime(cls, date_commented):
        utc = arrow.get(date_commented)
        return utc.humanize()


class Relationship(BaseModel):
    from_user = ForeignKeyField(
        column_name='from_user_id', field='id', model=User, on_delete='cascade', on_update='cascade')
    time = DateTimeField(default=dt.now)
    to_user = ForeignKeyField(
        backref='user_to_user', column_name='to_user_id', field='id', model=User, on_delete='cascade', on_update='cascade')
    status_code = IntegerField(null = True)
    action_user = IntegerField()


@login_manager.user_loader
def load_user(user_id):
    return (User.get_by_id(user_id))

def get_or_404(table,*args):
        try:
            res = table.get(*args)
        except DoesNotExist:
            return abort(404)
        return res

def human_time(Datetime):
    utc = arrow.get(Datetime)
    return utc.humanize()
    
# db.connect()
db.create_tables([User, Comment, Article_Likes, Relationship, Article])
# db.close()
class Rstatus_code:
    'Friend Relationship status code'
    accepted = 1
    pending = 0
    disclined = 2
    block = 3
