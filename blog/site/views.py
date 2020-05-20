from . import site
from flask import render_template

@site.route('/')
def index():
    return render_template('index.html')
