from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import current_user
from webapp.services import imageService
from webapp.services import userService


imageManager = Blueprint("imageManager", __name__)


@imageManager.route("/images", methods=["GET"])
def get_image():
    if current_user.is_authenticated:
        return render_template("images.html", title="Images")
    else:
        return redirect(url_for("users.login"))


@imageManager.route("/images/upload", methods=["GET", "POST"])
def get_upload_image_page():
    error = None
    if not current_user.is_authenticated:
        error = 'You need to login first.'
        login_form = userService.LoginForm()
        return render_template("login.html", form=login_form, error=error)
    upload_image_form = imageService.UploadImageForm()
    if upload_image_form.validate_on_submit():
        print("image")
        image = upload_image_form.image
        print(image)
        if "fileSize" in request.cookies:
            print("Cookie found!!!!!")
            if not imageService.allowed_image_size(request.cookies["fileSize"]):
                error = "Image size exceeded maximum limit!"
                return render_template("imageUpload.html", form=upload_image_form, error=error)
        image_name = upload_image_form.imageName.data + "." + image.data.filename.split('.')[1] \
            if upload_image_form.imageName and len(upload_image_form.imageName.data.strip()) != 0 else image.data.filename
        if imageService.image_validation(image_name):
            image_path = imageService.save_image(image, image_name)
            if image_path:
                print("The image name is : " + image_name)
                message = "Image " + image_name + " is uploaded successfully!"
                return render_template("imageUpload.html", form=upload_image_form, message=message)
            else:
                error = 'Image ' + image_name + \
                        ' already exists, please upload another image or type in a different image name.'
                return render_template("imageUpload.html", form=upload_image_form, error=error)
    else:
        print(upload_image_form.errors)

    return render_template("imageUpload.html", title="Upload Image", form=upload_image_form)
