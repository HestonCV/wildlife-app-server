from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    cameras = db.relationship('Camera', backref=('user'))
  
class Camera(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(500))
    token = db.Column(db.String(256), unique=True)
    images = db.relationship('Image', backref='camera')

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    camera_id = db.Column(db.Integer, db.ForeignKey('camera.id'), nullable=False)
    file_name = db.Column(db.String(250), nullable=False, unique=True)
    classification = db.Column(db.String(50), nullable=False)
    date_time = db.Column(db.DateTime, nullable=False)

class PreProvisionedCamera(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(256), nullable=False, unique=True)
    paired = db.Column(db.Boolean, nullable=False, default=False)