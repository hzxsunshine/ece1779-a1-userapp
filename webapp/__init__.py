from flask import Flask


def create_app():
    from webapp import services
    from webapp import models
    from webapp import controllers
    app = Flask(__name__)
    app.config.from_object("config.Config")
    models.init_app(app)
    controllers.init_app(app)

    return app
