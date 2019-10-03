from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_user, current_user, logout_user, login_required
from webapp.services import userService


imageManager = Blueprint('imageManager', __name__)


@imageManager.route('/images', methods=['GET'])
def get_image():
    if current_user.is_authenticated:
        return render_template('images.html', title='Images')
    else:
        return redirect(url_for('users.login'))


@imageManager.route('/image/upload', methods=['GET'])
def get_upload_image_page():
    if current_user.is_authenticated:
        return render_template('imageUpload.html', title='Upload Image')
    else:
        return redirect(url_for('users.login'))

