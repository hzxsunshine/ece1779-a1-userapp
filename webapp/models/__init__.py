from .base import db


def init_app(app):
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://ece1779a1:password123@localhost/ece1779a1'
    db.init_app(app)
    db.create_all('__all__', app)
    return app
