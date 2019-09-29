from flask import Blueprint
from webapp.models.user import User

users = Blueprint('users', __name__)


@users.route('/user')
def getuser():
    user = User.query.all()
    print(user)
    return user
