from flask import Blueprint, current_app

auth = Blueprint('auth', __name__, url_prefix='/auth')

from . import views
