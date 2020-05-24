from flask import Flask
from .auth import auth as auth_bp
from .site import site as site_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = 'daniel-oser & and kofi darkoh'
app.register_blueprint(auth_bp)
app.register_blueprint(site_bp)
