from flask import Blueprint, current_app
bp = Blueprint('site', __name__)

from . import views
