from . import auth
from playhouse.flask_utils import get_object_or_404,object_list
from flask import url_for,redirect,render_template
from .authForms import LoginForm
from blog.models import BaseModel

@auth.route('/LoginOrRegister', methods = ["POST","GET"])
def register():
    form = LoginForm()
    if form.validate_on_submit():
        pass
    return render_template('auth/form.html', form = form)
