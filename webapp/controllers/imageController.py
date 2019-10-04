from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_user, current_user, logout_user, login_required
from webapp.services import imageService


imageManager = Blueprint("imageManager", __name__)


@imageManager.route("/images", methods=["GET"])
def get_image():
    if current_user.is_authenticated:
        return render_template("images.html", title="Images")
    else:
        return redirect(url_for("users.login"))


@imageManager.route("/images/upload", methods=["GET", "POST"])
def get_upload_image_page():
    if not current_user.is_authenticated:
        return redirect(url_for("users.login"))
    if request.method == "POST":
        if request.files:
            image = request.files["image"]
            if "fileSize" in request.cookies:
                if not imageService.allowed_image_size(request.cookies["fileSize"]):
                    print("Image size exceeded maximum limit")
                    return redirect(request.url)
            if imageService.image_validation(image.filename):
                imageService.save_image(image)
                return redirect(request.url)
    return render_template("imageUpload.html", title="Upload Image")
