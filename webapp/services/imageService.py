from flask import current_app
import os
from werkzeug.utils import secure_filename


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


def save_image(image):
    filename = secure_filename(image.filename)
    image.save(os.path.join(current_app.config["IMAGES_UPLOAD_URL"], filename))

