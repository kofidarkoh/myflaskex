from flask import Flask,g
from .auth.views import auth as auth_bp
import os
import arrow
from .errors.views import error as er
from .site.views import site as site_bp
from .models import db,login_manager,relationship,Post, LikePost, User, Comment,messages
from urllib.parse import quote_plus
from markupsafe import Markup

app = Flask(__name__)

app.config['ENV'] = 'development'

app.config['SECRET_KEY'] = 'daniel-oser & and kofi darkoh'

app.config['TEMPLATES_AUTO_RELOAD'] = True

app.config['SESSION_COOKIE_SECURE'] = True

app.config['DEBUG'] = True

login_manager.init_app(app)

login_manager.login_message_category = 'danger'

login_manager.login_view = 'auth.login'

login_manager.session_protection = 'strong'

login_manager.login_message = 'log in to acccess this page'

app.register_blueprint(auth_bp)

app.register_blueprint(site_bp)

app.register_blueprint(er)

# db.connect()

# db.create_tables([User,LikePost,Post, Comment,relationship])

# # db.close()
# @app.before_request
# def before_request():
#     g.db = db
#     g.db.connect()

# @app.after_request
# def after_request(response):
#     g.db.close()
#     return response
@app.template_filter('html')
def html_filter(text):
    return Markup(text)

@app.template_filter('count_pending_request')
def count_pending_request_filter(userid):
	return relationship.pending_relationship_request(userid).count()

@app.template_filter('count_new_messsage')
def count_new_messsage_filter(n):
	return messages.new_message().count()

@app.template_filter('dtime')
def dtime_filter(date):
	utc = arrow.get(date)
	return utc.humanize()