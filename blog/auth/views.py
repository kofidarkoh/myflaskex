from . import auth
from playhouse.flask_utils import get_object_or_404,object_list
from flask import url_for,redirect

@auth.route('/register')
def register():
    return "hello friend"
