from peewee import *

from playhouse.sqliteq import SqliteQueueDatabase # peewee extra lib playhouse
import arrow # time and date 

import datetime as dtime
import os 

# sqlite database file path
db_path = os.path.join(os.path.dirname(__file__) + '/auth/database/blogDB.db')

# peeweee sqlite database config
db = SqliteQueueDatabase(db_path, pragmas = {'foreign_keys' : 1,'cache_size': 1024,'journal_mode': 'wal'})

# all table base 
class BaseModel(Model):
    
    class Meta:
        database = db