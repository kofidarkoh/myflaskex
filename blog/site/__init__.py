from flask import Blueprint, current_app

site = Blueprint('site', __name__)

from . import views
