from flask import jsonify
from webapp.services import userService
from flask_login import login_user, current_user, logout_user
from sqlalchemy.exc import IntegrityError
import os
from flask import Blueprint, render_template, request, current_app, send_from_directory
from webapp.services import imageService
from werkzeug.exceptions import RequestEntityTooLarge
import io
from PIL import Image


test = Blueprint('test', __name__)


@test.route('/api/register', methods=['POST'])
def register():
    error = None
    form = request.form
    if form:
        user_with_username = userService.get_user_by_username(username=form['username'])
        if user_with_username:
            return make_response(409, "User already exists.", form['username'])
        else:
            try:
                userService.create_user(username=form['username'], password=form['password'])
                os.makedirs(os.path.join(current_app.config["IMAGES_UPLOAD_URL"], form['username']))
                return make_response(200, "User created successfully.", form['username'])
            except IntegrityError:
                return make_response(500, "Database Internal Error.", form['username'])
    else:
        return make_response(400, "Bad Request!, request body not found", None)


@test.route('/api/upload', methods=['POST'])
def upload():
    form = request.form
    files = request.files

    if form and files:
        username = form['username']
        password = form['password']
        image = files['file']
        authenticated_user = userService.is_authenticated(username, password)
        if authenticated_user:
            try:
                login_user(authenticated_user)
            except:
                return make_response(500, "Internal Error! Login failed", form['username'])
            try:
                blob = image.read()
                size = len(blob)
                if not imageService.allowed_image_size(size):
                    error = "Image size exceeded maximum limit!"
                    return make_response(400, error, None)
                file = Image.open(io.BytesIO(blob))
                image_path = imageService.save_image(file, image.filename)
                if image_path:
                    message = "Image " + image.filename + " is uploaded successfully!"
                    return make_response(200, message, None)
                else:
                    error = 'Image ' + image.filename + \
                            ' already exists, please upload another image or type in a different image name.'
                    return make_response(409, error, None)
            except Exception as e:
                return make_response(500, "Internal Error!" + str(e), None)
        else:
            error = "Login Unsuccessful. Please check username and password."
            return make_response(401, error, form['username'])
    else:
        return make_response(400, "Bad Request!, request body missing", None)


def make_response(status_code, message, payload):
    response = jsonify(status=status_code, message=message, payload=payload)
    response.status_code = status_code
    return response
