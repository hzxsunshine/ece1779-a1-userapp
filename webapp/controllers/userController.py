from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_user, current_user, logout_user, login_required
from webapp.services import userService
from sqlalchemy.exc import IntegrityError


users = Blueprint('users', __name__)


@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('imageManager.get_image'))
    form = userService.LoginForm()
    if form.validate_on_submit():
        user = userService.get_user_by_email(email=form.email.data, password=form.password.data)
        if user:
            login_user(user, remember=form.remember_user.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('imageManager.get_image'))
        else:
            return 'Login Unsuccessful. Please check email and password'
    return render_template('login.html', title='Login', form=form)


@users.route('/register', methods=['GET', 'POST'])
def register():
    form = userService.CreateUserForm()
    if current_user.is_authenticated:
        # TODO
        return redirect(url_for('imageManager.get_image'))
    if form.validate_on_submit():
        try:
            userService.create_user(username=form.username.data, email=form.email.data, password=form.password.data)
            return redirect(url_for('users.login'))
        except IntegrityError:
            return 'create user failed!'
    else:
        print(form.errors)
    return render_template('register.html', title='Register', form=form)


@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('users.login'))
