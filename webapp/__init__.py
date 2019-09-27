from flask import Flask


def create_app():
    from webapp import services
    from webapp import models
    from webapp import controllers
    app = Flask(__name__)
    models.init_app(app)
    controllers.init_app(app)
    services.init_app(app)
    return app
