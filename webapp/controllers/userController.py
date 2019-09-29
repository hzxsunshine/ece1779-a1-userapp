from flask import Blueprint
from flask import render_template
from webapp.models.user import User
from webapp.services import userService

users = Blueprint('users', __name__)


@users.route('/login', methods=['GET', 'POST'])
def login():
    form = userService.LoginForm()
    if form.validate_on_submit():
        # TODO
        return 'Success!'
    return render_template('login.html', title='Login', form=form)


@users.route('/register')
def register():
    form = userService.CreateUserForm()
    if form.validate_on_submit():
        # TODO
        return 'Success!'
    return render_template('register.html', title='Register', form=form)


@users.route('/logout')
def logout():
    return
