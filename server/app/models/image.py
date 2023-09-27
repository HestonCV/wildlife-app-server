from app import db

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    camera_id = db.Column(db.Integer, db.ForeignKey('camera.id'), nullable=False)
    file_name = db.Column(db.String(250), nullable=False, unique=True)
    classification = db.Column(db.String(50), nullable=False)
    date_time = db.Column(db.DateTime, nullable=False)