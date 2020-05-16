from . import site


@site.route('/')
def index():
    return "hello friend"
