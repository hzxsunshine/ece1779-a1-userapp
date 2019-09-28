from flask import Blueprint

user = Blueprint('user', __name__)


@user.route('/user')
def getuser():
    return "hello user"
