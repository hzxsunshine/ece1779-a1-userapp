from .base import *


def init_app(app):
    db.init_app(app)
    db.create_all('__all__', app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message_category = 'info'

    return app
