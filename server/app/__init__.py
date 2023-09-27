from flask import Flask
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
  app = Flask(__name__)
  app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
  app.config['JWT_SECRET_KEY'] = '5B17LjyoR0qc+yHmxMFpCjPMU9mAsinQfsPWJSbTpfY='
  app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

  db.init_app(app)
  jwt.init_app(app)

  from .models import User, Camera, Image

  with app.app_context():
    db.create_all()

  from app.routes.user_routes import user_routes
  from app.routes.camera_routes import camera_routes
  from app.routes.image_routes import image_routes

  app.register_blueprint(user_routes)
  app.register_blueprint(camera_routes)
  app.register_blueprint(image_routes)

  return app