from flask import Flask,g
from .auth.views import auth as auth_bp
import os
from .errors.views import error as er
from .site.views import site as site_bp
from .models import db,login_manager,relationship
from urllib.parse import quote_plus
from markupsafe import Markup

app = Flask(__name__)
app.config['ENV'] = 'development'
app.config['SECRET_KEY'] = 'daniel-oser & and kofi darkoh'
app.config['TEMPLATES_AUTO_RELOAD'] = True
login_manager.init_app(app)
login_manager.login_message_category = 'danger'
login_manager.login_view = 'auth.login'
login_manager.login_message = 'log in to acccess this page'
app.register_blueprint(auth_bp)
app.register_blueprint(site_bp)
app.register_blueprint(er)

@app.template_filter('urlencode')
def urlencode_filter(s):
    if type(s) == 'Markup':
        s = s.unescape()
    if type(s) == int:
    	s = str(s)
    s = s.encode('utf8')
    s = quote_plus(s)
    return Markup(s)

