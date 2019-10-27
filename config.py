from datetime import timedelta


class Config(object):
    DEBUG = True
    LOGGING_FILE_PATH = "/ece1779.log"
    TESTING = False
    SECRET_KEY = "fe8e5c349e8eb13bf65bdc261229d43d"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = \
        "mysql://ece1779a2:password123@ece1779a2.csmeodxl9uyw.us-east-1.rds.amazonaws.com/ece1779a2"

    TEXT_DETECTION_PB_PATH = "/static/east/frozen_east_text_detection.pb"
    ALLOWED_IMAGE_EXTENSIONS = ["JPEG", "JPG", "PNG"]
    MAX_IMAGE_SIZE = 0.5 * 2500 * 2500

    REMEMBER_COOKIE_DURATION = timedelta(hours=25)
    S3_BUCKET_LOCATION = "https://ece1779a2-rita.s3.amazonaws.com/"

