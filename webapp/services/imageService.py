from flask import current_app
from flask_login import current_user
import os, uuid
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
import boto3


class UploadImageForm(FlaskForm):
    imageName = StringField('Image Name',
                            validators=[optional(), Length(max=30),
                                        Regexp(
                                            "^[0-9a-zA-Z\\^\\&\\'\\@\\{\\}\\[\\]\\,\\$\\=\\!\\-\\#\\(\\)\\%\\+\\~\\_ ]+$",
                                            message="Please enter a valid image name. The only characters allowed are "
                                                    "alphabetic, numeric, "
                                                    "and ^ & ' @ { } [ ] , $ = ! - # ( ) % + ~ _ ")])
    image = FileField('image', validators=[FileRequired(message="Image is required!")])
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


def save_image(image_name, blob):
    image_name_org = image_name
    current_app.logger.info("----------Start to upload image!----------")

    image_name_split = image_name.rsplit('.', 1)
    image_name_ = image_name_split[0]
    image_name_extension = image_name_split[1]
    image_name = image_name_ + '_{}.'.format(uuid.uuid1().int) + image_name_extension

    filename_to_store = secure_filename(image_name)
    image_path = current_user.username + '/' + filename_to_store
    upload_to_s3(image_path, blob)
    # Create thumbnail
    current_app.logger.info("---------- Start to upload thumbnail! ----------")
    image_tn_name_to_store, image_tn_path = create_thumbnail(image_name, blob)
    current_app.logger.info("---------- Thumbnail saved to {} ! Name is {} ----------"
                            .format(image_tn_path, image_tn_name_to_store))
    # Text detection
    current_app.logger.info("---------- Start to upload text detected image! ----------")
    image_de_name_to_store, image_de_path = create_detection(image_name, blob)
    current_app.logger.info("---------- Image after text detection saved to {} ! Name is {} ----------"
                            .format(image_de_path, image_de_name_to_store))
    imageRepository.save_image(image_name_org, image_path, image_tn_path, image_de_path, current_user.id)
    return image_name_org


def get_images_by_user():
    return imageRepository.get_images_by_user_id(current_user.id)


def get_images_by_filename(filename):
    image_path = current_user.username + "/" + filename
    return imageRepository.get_images_by_path(image_path)


def create_thumbnail(image_name, blob):
    with Image(blob=blob).clone() as img:
        img.resize(200, 150)
        image_tn_name = image_name.rsplit(".", 1)[0] + "_tn." + image_name.rsplit(".", 1)[1]
        filename_tn = secure_filename(image_tn_name)
        image_tn_path = current_user.username + "/" + filename_tn
        upload_to_s3(image_tn_path, img.make_blob())
    return image_tn_name, image_tn_path


def create_detection(image_name, blob):
    with Image(blob=blob) as img:
        img_buffer = np.asarray(bytearray(img.make_blob()), dtype=np.uint8)
    image = cv2.imdecode(img_buffer, cv2.IMREAD_UNCHANGED)
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
    east = current_app.root_path + current_app.config["TEXT_DETECTION_PB_PATH"]
    net = cv2.dnn.readNet(east)
    blob = cv2.dnn.blobFromImage(image, 1.0, (W, H), (123.68, 116.78, 103.94), swapRB=True, crop=False)
    net.setInput(blob)
    (scores, geometry) = net.forward(layerNames)
    (numRows, numCols) = scores.shape[2:4]
    rects = []
    confidences = []
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
    filename_de = secure_filename(image_de_name)
    image_de_path = current_user.username + "/" + filename_de
    upload_to_s3(image_de_path, cv2.imencode('.'+filename_de.rpartition('.')[-1], orig)[1].tobytes())
    return image_de_name, image_de_path


def upload_to_s3(image_path, image):
    s3 = boto3.resource('s3')
    bucket_name = current_app.config["S3_BUCKET_NAME"]
    s3.Bucket(bucket_name).put_object(Key=image_path, Body=image)


def read_from_s3(image_path):
    s3 = boto3.resource('s3')
    bucket_name = current_app.config["S3_BUCKET_NAME"]
    return s3.Bucket(bucket_name).Object(image_path).toByteArray()


