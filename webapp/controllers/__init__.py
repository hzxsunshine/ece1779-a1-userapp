from .mainController import *
from .userController import *
from .imageController import *
from .testingApi import *


def init_app(app):
    app.register_blueprint(main)
    app.register_blueprint(users)
    app.register_blueprint(imageManager)
    app.register_blueprint(test)
    return app
