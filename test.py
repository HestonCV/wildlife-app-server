from models import db, User, Camera, Image

users = db.session.query(Image).all()

for user in users:
    print(user.id, user.first_name, user.last_name, user.email, user.camera_id)