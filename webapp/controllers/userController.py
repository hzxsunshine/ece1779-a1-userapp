from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_user, current_user, logout_user, login_required
from webapp.services import userService
from sqlalchemy.exc import IntegrityError
import os
from flask import current_app


users = Blueprint('users', __name__)


@users.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if current_user.is_authenticated:
        return redirect(url_for('imageManager.get_image'))
    form = userService.LoginForm()
    if form.validate_on_submit():
        user = userService.get_user_by_email(email=form.email.data, password=form.password.data)
        if user:
            login_user(user, remember=form.remember_user.data)
            next_page = request.args.get('next')
            print(next_page)
            return redirect(next_page) if next_page else redirect(url_for('imageManager.get_image'))
        else:
            error = "Login Unsuccessful. Please check email and password."
            return render_template('login.html', title='Login', form=form, error=error)
    return render_template('login.html', title='Login', form=form)


@users.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    form = userService.CreateUserForm()
    if current_user.is_authenticated:
        return redirect(url_for('imageManager.get_image'))
    if form.validate_on_submit():
        user_with_email = userService.get_user_by_email(email=form.email.data, password=form.password.data)
        user_with_username = userService.get_user_by_username(username=form.username.data)

        if user_with_email or user_with_username:
            error = "User with email '" + form.email.data + "' already existed." \
              if user_with_email else "The username '" + form.username.data + "' already existed."
            return render_template('register.html', title='Register', form=form, error=error)
        else:
            try:
                userService.create_user(username=form.username.data, email=form.email.data, password=form.password.data)
                message = "Registration successful, please login."
                os.makedirs(os.path.join(current_app.config["IMAGES_UPLOAD_URL"], form.username.data))
                return render_template('login.html', title='Login', form=form, error=message)
            except IntegrityError:
                error = "Create user failed, please try again later"
                return render_template('register.html', title='Register', form=form, error=error)
    else:
        print(form.errors)
    return render_template('register.html', title='Register', form=form)


@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('users.login'))
