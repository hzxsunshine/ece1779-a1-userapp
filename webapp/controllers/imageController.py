from flask_login import current_user, login_required
from flask import Blueprint, render_template, request, current_app, send_from_directory
from webapp.services import imageService

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
        print("image")
        image = upload_image_form.image
        print(image)
        if "fileSize" in request.cookies:
            print("Cookie found!!!!!")
            if not imageService.allowed_image_size(request.cookies["fileSize"]):
                error = "Image size exceeded maximum limit!"
                return render_template("imageUpload.html", form=upload_image_form, error=error)
        image_name = upload_image_form.imageName.data + "." + image.data.filename.split('.')[1] \
            if upload_image_form.imageName and len(
            upload_image_form.imageName.data.strip()) != 0 else image.data.filename
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
