from flask_login import current_user, login_required
from flask import Blueprint, render_template, request, current_app, send_from_directory
from webapp.services import imageService
from PIL import Image
import io


imageManager = Blueprint("imageManager", __name__)


@imageManager.route("/images", methods=["GET"])
@login_required
def get_images():
    username = current_user.username
    images = imageService.get_images_by_user()
    return render_template("images.html", title="Images", username=username, images=images)


@imageManager.route("/images/upload", methods=["GET", "POST"])
@login_required
def get_upload_image_page():
    error = None
    upload_image_form = imageService.UploadImageForm()
    if upload_image_form.validate_on_submit():
        image = upload_image_form.image
        print(image)
        if "fileSize" in request.cookies:
            print("Cookie found!!!!!")
            if not imageService.allowed_image_size(request.cookies["fileSize"]):
                error = "Image size exceeded maximum limit 1024*1024!"
                return render_template("imageUpload.html", form=upload_image_form, error=error)
        else:
            error = "Internal Error: can not obtain image size."
            return render_template("imageUpload.html", form=upload_image_form, error=error)

        image_name = upload_image_form.imageName.data + "." + image.data.filename.split('.')[1] \
            if upload_image_form.imageName and len(
            upload_image_form.imageName.data.strip()) != 0 else image.data.filename
        if imageService.image_validation(image_name):
            try:
                image_name_stored = imageService.save_image(image.data, image_name)
            except Exception as e:
                error = "Internal Error: " + str(e)
                return render_template("imageUpload.html", form=upload_image_form, error=error)
            if image_name.lower() == image_name_stored.lower():
                message = "Image " + image_name + " is uploaded successfully!"
                return render_template("imageUpload.html", form=upload_image_form, message=message)
            else:
                message = "Image with name '" + image_name + \
                        "' already exists, image uploaded successfully with a different name: '" \
                          + image_name_stored + "' !"
                return render_template("imageUpload.html", form=upload_image_form, message=message)
        else:
            error = "Invalid Image! Only JPEG, JPG, PNG files are accepted!"
            return render_template("imageUpload.html", form=upload_image_form, error=error)
    else:
        return render_template("imageUpload.html", form=upload_image_form, error=upload_image_form.errors)


@imageManager.route('/uploads/<path:filename>')
@login_required
def download_file(filename):
    return send_from_directory(current_app.config["IMAGES_UPLOAD_URL"] + "/" + current_user.username + "/", filename,
                               as_attachment=True)


@imageManager.route('/images/<path:filename>')
@login_required
def show_image(filename):
    image = imageService.get_images_by_filename(filename)
    return render_template("imageShow.html", image=image)
