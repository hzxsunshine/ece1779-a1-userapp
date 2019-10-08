from flask import Blueprint, render_template, redirect, url_for, request, session, json, jsonify
from flask_login import login_user, current_user, logout_user
from webapp.services import userService
from sqlalchemy.exc import IntegrityError
import os
from flask import current_app


test = Blueprint('test', __name__)


@test.route('/api/register', methods=['POST'])
def register():
    error = None
    form = request.form
    if form:
        user_with_username = userService.get_user_by_username(username=form['username'])
        if user_with_username:
            response = make_response(409, "User already exists.", form['username'])
        else:
            try:
                userService.create_user(username=form['username'], password=form['password'])
                os.makedirs(os.path.join(current_app.config["IMAGES_UPLOAD_URL"], form['username']))
                response = make_response(200, "User created successfully.", form['username'])
            except IntegrityError:
                response = make_response(500, "Database Internal Error.", form['username'])
    else:
        response = make_response(400, "Bad Request!, request body not found", None)
    return response


def make_response(status_code, message, username):
    response = jsonify(status=status_code, message=message, username=username)
    response.status_code = status_code
    return response
