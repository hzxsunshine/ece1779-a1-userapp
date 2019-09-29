from .main import *
from .user import *


def init_app(app):
    app.register_blueprint(main)
    app.register_blueprint(users)
    return app
