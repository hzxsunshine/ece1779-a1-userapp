from webapp.models.user import User
from webapp.models.base import db


def get_user_by_email(email):
    print(email)
    return User.query.filter_by(email=email).first()


def get_user_by_username(username):
    return User.query.filter_by(username=username).first()


def create_user(username, email, password):
    user = User(username, email, password)
    db.session.add(user)
    db.session.commit()
