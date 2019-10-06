from .base import db

#
# def load_user(user_id):
#     return User.query.get(int(user_id))


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_path = db.Column(db.String(200), unique=True)
    image_tn_path = db.Column(db.String(200), unique=True)
    image_de_path = db.Column(db.String(200), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('images', lazy=True))

    def __init__(self, image_path, image_tn_path, image_de_path, user_id):
        self.image_path = image_path
        self.image_tn_path = image_tn_path
        self.image_de_path = image_de_path
        self.user_id = user_id

    def __repr__(self):
        return '<Image path %r>' % self.image_path
