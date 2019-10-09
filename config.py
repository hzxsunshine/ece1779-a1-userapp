from datetime import timedelta


class Config(object):
    DEBUG = True
    TESTING = False
    SECRET_KEY = "fe8e5c349e8eb13bf65bdc261229d43d"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = "mysql://ece1779a1:password123@localhost/ece1779a1"

    IMAGES_UPLOAD_URL = "/home/ubuntu/Desktop/uploaded_photo"
    TEXT_DETECTION_PB_PATH = "/static/east/frozen_east_text_detection.pb"
    ALLOWED_IMAGE_EXTENSIONS = ["JPEG", "JPG", "PNG"]
    MAX_IMAGE_SIZE = 0.5 * 1024 * 1024

    REMEMBER_COOKIE_DURATION = timedelta(hours=25)

