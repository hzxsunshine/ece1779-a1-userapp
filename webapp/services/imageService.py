from flask import current_app
from flask_login import current_user
import os
from werkzeug.utils import secure_filename
from webapp.repository import imageRepository
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Length, Regexp
from flask_wtf.file import FileField, FileRequired


class UploadImageForm(FlaskForm):
    imageName = StringField('Image Name',
                            validators=[Length(max=30),
                                        Regexp(
                                          "^[0-9a-zA-Z\\^\\&\\'\\@\\{\\}\\[\\]\\,\\$\\=\\!\\-\\#\\(\\)\\%\\+\\~\\_ ]+$",
                                          message="Please enter a valid image name. The only characters allowed are "
                                                  "alphabetic, numeric, "
                                                  "and ^ & ' @ { } [ ] , $ = ! - # ( ) % + ~ _ ")])
    image = FileField('image', validators=[FileRequired()])
    submit = SubmitField('Upload')


def image_validation(filename):
    if filename == "":
        return False
    if "." not in filename:
        return False

    # Split the extension from the filename
    ext = filename.rsplit(".", 1)[1]

    # Check if the extension is in ALLOWED_IMAGE_EXTENSIONS
    if ext.upper() in current_app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return True
    else:
        return False


def allowed_image_size(filesize):
    if int(filesize) <= current_app.config["MAX_IMAGE_SIZE"]:
        return True
    else:
        return False


def save_image(image, image_name):
    filename = secure_filename(image_name)
    image_path = os.path.join(current_app.config["IMAGES_UPLOAD_URL"] + "/" + current_user.username, filename)
    if imageRepository.get_images_by_path(image_path):
        return None
    else:
        image.data.save(image_path)
        imageRepository.save_image(image_path, current_user.id)
        return image_path


def get_images_by_user():
    return imageRepository.get_images_by_user_id(current_user.id)

