from flask import Blueprint,render_template

error = Blueprint('error', __name__)

@error.app_errorhandler(404)
def pageNotFound(error):
	return render_template('errors/page404.html'),404

@error.app_errorhandler(403)
def page403(error):
	return render_template('errors/page403.html'),403