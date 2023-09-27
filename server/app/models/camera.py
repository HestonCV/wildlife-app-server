from app import db

class Camera(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(256), nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(100))
    description = db.Column(db.String(500))
    images = db.relationship('Image', backref='camera')