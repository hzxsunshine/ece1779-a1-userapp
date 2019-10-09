from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_user, current_user, logout_user
from webapp.services import userService
from sqlalchemy.exc import IntegrityError
import os
from flask import current_app


users = Blueprint('users', __name__)


@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('imageManager.get_images'))
    form = userService.LoginForm()
    if form.validate_on_submit():
        authenticated_user = userService.is_authenticated(username=form.username.data, password=form.password.data)
        if authenticated_user:
            login_user(authenticated_user, remember=form.remember_user.data)
            next_page = request.args.get('next')
            current_app.logger.info("----------User '{}' login success !----------".format(authenticated_user.username))
            return redirect(next_page) if next_page else redirect(url_for('imageManager.get_images'))
        else:
            error = "Login Unsuccessful. Please check username and password."
            current_app.logger.error("----------User '{}' Login failed, username/password do not match record----------"
                                     .format(form.username))
            return render_template('login.html', title='Login', form=form, error=error), 401
    else:
        if request == 'POST':
            error = "Internal Error, please try again later."
            current_app.logger.error("----------Internal Error: {}----------".format(form.errors))
            return render_template('login.html', title='Login', form=form, error=error), 500
    return render_template('login.html', title='Login', form=form)


@users.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    form = userService.CreateUserForm()
    if current_user.is_authenticated:
        return redirect(url_for('imageManager.get_images'))
    if form.validate_on_submit():
        user_with_username = userService.get_user_by_username(username=form.username.data)

        if user_with_username:
            error = "User with username '" + form.username.data + "' already existed."
            current_app.logger.error("----------409 Registration conflict: {}----------".format(error))
            return render_template('register.html', title='Register', form=form, error=error), 409
        else:
            try:
                user = userService.create_user(username=form.username.data, password=form.password.data)
                message = "Registration successful, please login."
                os.makedirs(os.path.join(current_app.config["IMAGES_UPLOAD_URL"], form.username.data))
                login_form = userService.LoginForm()
                current_app.logger.info("----------User '{}' register successful----------".format(user.username))
                return render_template('login.html', title='Login', form=login_form, message=message)
            except IntegrityError as e:
                error = "Create user failed, please try again later."
                current_app.logger.error("----------Database action error: {}----------".format(str(e)))
                return render_template('register.html', title='Register', form=form, error=error), 500
    else:
        if request.method == 'POST':
            error = "Internal Error, please try again later."
            current_app.logger.error("----------Internal Error: {}----------".format(form.errors))
            return render_template('register.html', title='Register', form=form, error=error), 500
    return render_template('register.html', title='Register', form=form)


@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('users.login'))
