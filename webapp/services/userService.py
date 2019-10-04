from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from webapp.repository import userRepository
from . import bcrypt


class CreateUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_user = BooleanField('Remember Me')
    submit = SubmitField('Login')


def get_user_by_email(email, password):
    user = userRepository.get_user_by_email(email)
    if user and bcrypt.check_password_hash(user.password, password):
        return user
    else:
        return None


def get_user_by_username(username):
    return userRepository.get_user_by_username(username)


def create_user(username, email, password):
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    userRepository.create_user(username, email, hashed_password)







