from .site import bp as bpp

from blog.dbmodels import login_manager,db
# from flask_web_log import Log
from flask import Flask

# from flask_compress import Compress
# from flask_cors import CORS
from flask_login  import current_user

app = Flask(__name__)
# com = Compress()

# CORS(app)

# Log(app)

# com.init_app(app)

login_manager.init_app(app)

login_manager.login_message = 'Please login to access this page'

login_manager.login_view = 'site.login'

login_manager.login_message_category = 'danger'

login_manager.session_protection = 'strong'

app.config['SECRET_KEY'] = 'hello123'

app.config['UPLOAD_FOLDER'] = 'static/profile_pictures/'

app.config['ENV'] = 'development'

app.register_blueprint(bpp)

app_ctx = app.app_context()

app_ctx.push()

@app.before_request
def before_request():
    db.connect()

@app.after_request
def after_request(response):
    db.close()
    return response