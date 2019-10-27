from flask_login import current_user, login_required
from flask import Blueprint, render_template, request, current_app, send_from_directory
from webapp.services import imageService
from PIL import Image
import io

imageManager = Blueprint("imageManager", __name__)

IMAGE_UPLOAD_PAGE = "imageUpload.html"
INTERNAL_ERROR_MSG = "Internal Error, please try again later."
IMAGE_NAME_LENGTH_ERROR = "Image name should be less than 30 characters, you can optional input an image alias instead."
IMAGE_SIZE_ERROR = "Image size exceeds maximum limit 2500*2500!"
IMAGE_TYPE_ERROR = "Invalid Image! Only JPEG, JPG, PNG files are accepted!"
UPLOAD_SUCCESS_MSG = "Image '{}' is uploaded successfully!"


@imageManager.route("/images", methods=["GET"])
@login_required
def get_images():
    username = current_user.username
    images = imageService.get_images_by_user()
    return render_template("images.html", title="Images", username=username, images=images,
                           s3Location=current_app.config["S3_BUCKET_LOCATION"])


@imageManager.route("/images/upload", methods=["GET", "POST"])
@login_required
def upload_image():
    upload_image_form = imageService.UploadImageForm()
    try:
        if upload_image_form.validate_on_submit():
            image = upload_image_form.image

            image_name = upload_image_form.imageName.data + "." + image.data.filename.split('.')[1] \
                if upload_image_form.imageName and len(upload_image_form.imageName.data.strip()) != 0 \
                else image.data.filename
            current_app.logger.info("----------Image name is {} ----------".format(image_name))
            if len(image_name) > 30:
                current_app.logger.error("----------400 {} ----------".format(IMAGE_NAME_LENGTH_ERROR))
                return render_template(IMAGE_UPLOAD_PAGE, form=upload_image_form, error=IMAGE_NAME_LENGTH_ERROR), 400

            blob = image.data.read()
            if request.cookies and "fileSize" in request.cookies:
                current_app.logger.debug("----------fileSize in cookie is found!----------")
                if not imageService.allowed_image_size(request.cookies["fileSize"]):
                    current_app.logger.error("----------400 {} ----------".format(IMAGE_SIZE_ERROR))
                    return render_template(IMAGE_UPLOAD_PAGE, form=upload_image_form, error=IMAGE_SIZE_ERROR), 400
                image_file = image.data
            else:
                current_app.logger.info("----------fileSize in cookie is not found!----------")
                size = len(blob)
                if not imageService.allowed_image_size(size):
                    current_app.logger.error("----------400 {} ----------".format(IMAGE_SIZE_ERROR))
                    return render_template(IMAGE_UPLOAD_PAGE, form=upload_image_form, error=IMAGE_SIZE_ERROR), 400
                image_file = Image.open(io.BytesIO(blob))

            if imageService.image_validation(image_name):
                image_name_org = imageService.save_image(image_name, blob)
                current_app.logger.info("----------200 {} ----------".format(UPLOAD_SUCCESS_MSG.format(image_name_org)))
                return render_template(IMAGE_UPLOAD_PAGE, form=upload_image_form,
                                       message=UPLOAD_SUCCESS_MSG.format(image_name))
            else:
                current_app.logger.error("----------400 {} ----------".format(IMAGE_TYPE_ERROR))
                return render_template(IMAGE_UPLOAD_PAGE, form=upload_image_form, error=IMAGE_TYPE_ERROR), 400
        else:

            if request == 'POST':
                current_app.logger.error("----------Internal Error: {}----------".format(upload_image_form.errors))
                return render_template(IMAGE_UPLOAD_PAGE, form=upload_image_form, error=INTERNAL_ERROR_MSG), 500
        return render_template(IMAGE_UPLOAD_PAGE, form=upload_image_form)
    except Exception as e:
        current_app.logger.error("----------Internal Error: {}----------".format(str(e)))
        return render_template(IMAGE_UPLOAD_PAGE, form=upload_image_form, error=INTERNAL_ERROR_MSG), 500


# @imageManager.route('/uploads/<path:filename>')
# @login_required
# def download_file(filename):
#     return current_app.config["S3_BUCKET_LOCATION"] + current_user.username + "/" + filename


@imageManager.route('/images/<path:filename>')
@login_required
def show_image(filename):
    image = imageService.get_images_by_filename(filename)
    return render_template("imageShow.html", image=image, s3Location=current_app.config["S3_BUCKET_LOCATION"])
