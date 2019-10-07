from flask import current_app
from flask_login import current_user
import os
from werkzeug.utils import secure_filename
from webapp.repository import imageRepository
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Length, Regexp, optional
from flask_wtf.file import FileField, FileRequired
from wand.image import Image
from imutils.object_detection import non_max_suppression
import numpy as np
import cv2


class UploadImageForm(FlaskForm):
    imageName = StringField('Image Name',
                            validators=[optional(), Length(max=30),
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
        image_tn_name = create_thumbnail(image_name)
        image_de_name = create_detection(image_name)
        filename_tn = secure_filename(image_tn_name)
        filename_de = secure_filename(image_de_name)
        image_tn_path = os.path.join(current_app.config["IMAGES_UPLOAD_URL"] + "/" + current_user.username, filename_tn)
        image_de_path = os.path.join(current_app.config["IMAGES_UPLOAD_URL"] + "/" + current_user.username, filename_de)
        imageRepository.save_image(image_path, image_tn_path, image_de_path, current_user.id)
        return image_path


def get_images_by_user():
    return imageRepository.get_images_by_user_id(current_user.id)


def get_images_by_filename(filename):
    image_path = os.path.join(current_app.config["IMAGES_UPLOAD_URL"] + "/" + current_user.username, filename)
    return imageRepository.get_images_by_path(image_path)


def create_thumbnail(image_name):
    image_path = os.path.join(current_app.config["IMAGES_UPLOAD_URL"] + "/" + current_user.username, image_name)
    with Image(filename=image_path).clone() as img:
        img.resize(200, 150)
        image_tn_name = image_name.rsplit(".", 1)[0] + "_tn." + image_name.rsplit(".", 1)[1]
        img.save(filename=current_app.config["IMAGES_UPLOAD_URL"] + "/" +
                          current_user.username + "/" + image_tn_name)
    return image_tn_name


def create_detection(image_name):
    image_path = os.path.join(current_app.config["IMAGES_UPLOAD_URL"] + "/" + current_user.username, image_name)
    image = cv2.imread(image_path)
    orig = image.copy()
    (H, W) = image.shape[:2]
    if H % 32 != 0:
        newH = (H // 32 + 1) * 32
    else:
        newH = H
    if W % 32 != 0:
        newW = (W // 32 + 1) * 32
    else:
        newW = W
    rW = W / float(newW)
    rH = H / float(newH)
    image = cv2.resize(image, (newW, newH))
    (H, W) = image.shape[:2]
    layerNames = ["feature_fusion/Conv_7/Sigmoid", "feature_fusion/concat_3"]
    east = "webapp/static/east/frozen_east_text_detection.pb"
    net = cv2.dnn.readNet(east)
    blob = cv2.dnn.blobFromImage(image, 1.0, (W, H), (123.68, 116.78, 103.94), swapRB=True, crop=False)
    net.setInput(blob)
    (scores, geometry) = net.forward(layerNames)
    (numRows, numCols) = scores.shape[2:4]
    rects = []
    confidences = []
    print(numRows)
    print(numCols)
    for y in range(0, numRows):
        scoresData = scores[0, 0, y]
        xData0 = geometry[0, 0, y]
        xData1 = geometry[0, 1, y]
        xData2 = geometry[0, 2, y]
        xData3 = geometry[0, 3, y]
        anglesData = geometry[0, 4, y]
        for x in range(0, numCols):
            if scoresData[x] < 0.5:
                continue
            (offsetX, offsetY) = (x * 4.0, y * 4.0)
            angle = anglesData[x]
            cos = np.cos(angle)
            sin = np.sin(angle)
            h = xData0[x] + xData2[x]
            w = xData1[x] + xData3[x]
            endX = int(offsetX + (cos * xData1[x]) + (sin * xData2[x]))
            endY = int(offsetY - (sin * xData1[x]) + (cos * xData2[x]))
            startX = int(endX - w)
            startY = int(endY - h)
            rects.append((startX, startY, endX, endY))
            confidences.append(scoresData[x])
    boxes = non_max_suppression(np.array(rects), probs=confidences)
    for (startX, startY, endX, endY) in boxes:
        startX = int(startX * rW)
        startY = int(startY * rH)
        endX = int(endX * rW)
        endY = int(endY * rH)
        cv2.rectangle(orig, (startX, startY), (endX, endY), (0, 255, 0), 2)
    image_de_name = image_name.rsplit(".", 1)[0] + "_de." + image_name.rsplit(".", 1)[1]
    filename = current_app.config["IMAGES_UPLOAD_URL"] + "/" + current_user.username + "/" + image_de_name
    cv2.imwrite(filename, orig)
    return image_de_name
