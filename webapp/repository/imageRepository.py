from webapp.models.image import *

from webapp.models.base import db


def get_images_by_user_id(user_id):
    images = db.session.query(Image).filter(Image.user_id == user_id)
    return images


def get_images_by_path(path):
    images = db.session.query(Image).filter(Image.image_path == path).first()
    return images


def save_image(image_name, image_path, image_tn_path, image_de_path, user_id):
    image = Image(image_name, image_path, image_tn_path, image_de_path, user_id)
    db.session.add(image)
    db.session.commit()


