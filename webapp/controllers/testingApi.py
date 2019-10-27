from flask import jsonify
from webapp.services import userService
from sqlalchemy.exc import IntegrityError
import os
from flask import Blueprint,  request, current_app
from webapp.services import imageService
import io
from PIL import Image
from flask_login import login_user


test = Blueprint('test', __name__)


@test.route('/api/register', methods=['POST'])
def register():
    form = request.form
    if form and 'username' in form and 'password' in form:
        if len(form['username']) < 2 or len(form['username']) > 30:
            return make_response(400, "Bad Request!, the length of username must between 2 to 30 characters", None)
        if len(form['password']) < 6 or len(form['password']) > 20:
            return make_response(400, "Bad Request!, the length of password must between 6 to 20", None)
        user_with_username = userService.get_user_by_username(username=form['username'])
        if user_with_username:
            return make_response(409, "User already exists.", form['username'])
        else:
            try:
                userService.create_user(username=form['username'], password=form['password'])
                return make_response(200, "User created successfully.", form['username'])
            except IntegrityError:
                return make_response(500, "Database Internal Error.", None)
    else:
        return make_response(400, "Bad Request!, request body missing", None)


@test.route('/api/upload', methods=['POST'])
def upload():
    form = request.form
    files = request.files

    if form and 'username' in form and 'password' in form and files:
        username = form['username']
        password = form['password']
        image = files['file']
        authenticated_user = userService.is_authenticated(username, password)
        if authenticated_user:
            login_user(authenticated_user)
            if imageService.image_validation(image.filename):
                try:
                    blob = image.read()
                    size = len(blob)
                    if not imageService.allowed_image_size(size):
                        error = "Image size exceeded maximum limit 2500*2500!"
                        return make_response(400, error, None)
                    file = Image.open(io.BytesIO(blob))

                    image_name = image.filename
                    if len(image_name) > 30:
                        error = "Image name can not longer than 30 characters."
                        return make_response(400, error, None)

                    image_name_stored = imageService.save_image(image.filename, blob)
                    if image.filename.lower() == image_name_stored.lower():
                        message = "Image " + image.filename + " is uploaded successfully!"
                        return make_response(200, message, None)
                    else:
                        message = "Image with name '" + image.filename + \
                                  "' already exists, image uploaded successfully with a different name: '" \
                                  + image_name_stored + "' !"
                        return make_response(200, message, None)
                except Exception as e:
                    return make_response(500, "Internal Error!" + str(e), None)
            else:
                error = "Invalid Image! Only JPEG, JPG, PNG files are accepted!"
                return make_response(400, error, None)
        else:
            error = "Login Unsuccessful. Please check username and password."
            return make_response(401, error, form['username'])
    else:
        return make_response(400, "Bad Request!, request body missing", None)


def make_response(status_code, message, payload):
    response = jsonify(status=status_code, message=message, payload=payload)
    response.status_code = status_code
    return response
