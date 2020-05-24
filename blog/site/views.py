from . import site
from flask import render_template
from playhouse.flask_utils import get_object_or_404,object_list


@site.route('/')
def index():
    return render_template('index.html')
