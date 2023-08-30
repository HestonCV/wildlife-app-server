from flask import Flask, request, jsonify, send_file
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError
from models import db, User, Camera, Image, PreProvisionedCamera
from PIL import Image as PILImage
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = '5B17LjyoR0qc+yHmxMFpCjPMU9mAsinQfsPWJSbTpfY='

jwt = JWTManager(app)

db.init_app(app)

def generate_hashed_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def check_password(hashed_password, password_attempt):
    return bcrypt.checkpw(password_attempt.encode('utf-8'), hashed_password.encode('utf-8'))
    

# /register takes first name, last name, email, and password.
# it encrypts the password and stores it in the database
@app.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()

    if not data:
        return jsonify({
            'status': 'error',
            'message': 'Invalid JSON'
        }), 400
    try:
        # validate first and last name
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        if not first_name or not last_name:
            return jsonify({
                'status': 'error',
                'message': 'First name and last name are required'
            }), 400
        
        # validate email and password
        email = data.get('email')
        password = data.get('password')
        if not email or not password:
            return jsonify({
                'status': 'error',
                'message': 'Email and password are required'
            }), 400
        
        # check if a user exists with the same email
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({
                'status': 'error',
                'message': 'Email is already in use'
            }), 400
        
        # make new user
        new_user = User(first_name=first_name, last_name=last_name, email=email, password=generate_hashed_password(password))
        db.session.add(new_user)
        
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': 'User created'
        }), 201
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({
          'status': 'error',
          'message': 'Database error'
        }), 500
        

# /login takes email and password, compares the password to the hashed
# password in the database if the email matches, and returns a jwt token
@app.route('/login', methods=['POST'])
def login_user():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        # validate email and password
        if not email or not password:
            return jsonify({
                'status': 'error',
                'message': 'Email and password are required'
            }), 400
        
        # check if user exists
        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            return jsonify({
                'status': 'error',
                'message': 'Invalid email or password'
            }), 401
        
        # validate password
        password_valid = check_password(existing_user.password, password)
        if not password_valid:
            return jsonify({
                'status': 'error',
                'message': 'Invalid email or password'
            }), 401
        
        access_token = create_access_token(identity=existing_user.id)
        return jsonify({
            'status': 'success',
            'message': 'Login match',
            'access_token': access_token
        }), 200
    
    except SQLAlchemyError:
        return jsonify({
            'status': 'error',
            'message': 'Database error'
            }), 500

@app.route('/images', methods=['POST'])
@jwt_required()
def upload_image():
    try:
        camera_id = get_jwt_identity()

        if not os.path.exists('./uploads/full'):
            os.makedirs('./uploads/full')
        if not os.path.exists('./uploads/thumbnail'):
            os.makedirs('./uploads/thumbnail')

        # save image
        image_file = request.files.get('image')
        if image_file and image_file.content_type.startswith('image/'):
            # set custom file name
            current_datetime = datetime.now()
            file_name = f"{camera_id}_{current_datetime.strftime('%Y%m%d%H%M%S')}.jpg"

            full_path = os.path.join('./uploads/full', file_name)
            image_file.save(full_path)
        
            # save thumbnail
            image_file.seek(0)
            img = PILImage.open(image_file)
            img.thumbnail((128,128))
            thumbnail_path = os.path.join('./uploads/thumbnail', file_name)
            img.save(thumbnail_path)


            # TODO: import tensorflow model to classify image
            classification = 'placeholder'
            new_image = Image(
                camera_id=camera_id,
                file_name=file_name,
                classification=classification,
                date_time=current_datetime
                )
            db.session.add(new_image)
            try:
                db.session.commit()
                return jsonify({
                    'status': 'success',
                    'message': 'Image uploaded'
                }), 201
            except SQLAlchemyError:
                db.session.rollback()
                return jsonify({
                    'status': 'error',
                    'message': 'Database error'
                }), 500
        else:
            return jsonify({
                'status': 'error',
                'message': 'No image provided'
            }), 400
    except Exception as e:
      return jsonify({
          'status': 'error',
          'message': str(e)
      }), 500
    
# returns all of the image data for a given user, not including the image file itself
# the image files can be retrieved at /images/<int:image_id>/full or thumbnail
@app.route('/images/data', methods=['GET'])
@jwt_required()
def get_images():
    response_data = []
    try:
        user = User.query.get(get_jwt_identity())

        # for each camera the user owns get every image and append the data to reponse_data
        if user.cameras:
            for camera in user.cameras:
                for image in camera.images:
                    id = image.id
                    classification = image.classification
                    date_time = image.date_time.strftime("%b %d, %Y %-I:%M %p")
                    camera_name = image.camera.name
                    response_data.append({
                        'id': id,
                        'classification': classification,
                        'date_time': date_time,
                        'camera_name': camera_name
                    })
            if response_data:
                return jsonify({
                    'status': 'success',
                    'message': 'Image data retrieved',
                    'data': {
                        'image_data': response_data
                    }
                }), 200
            else:
                return jsonify({
                    'status': 'success',
                    'message': 'No image data to retrieve'
                }), 204
        else:
            return jsonify({
                'status': 'error',
                'message': 'User has no paired cameras'
            }), 404
    except SQLAlchemyError:
        return jsonify({
                    'status': 'error',
                    'message': 'Database error'
                }), 500



# takes an image id and returns the full sized image from the file system
@app.route('/images/<int:image_id>/full', methods=['GET'])
@jwt_required()
def get_full_image(image_id):
    try:
        user = User.query.get(get_jwt_identity())
        image = Image.query.get(image_id)
        if not image:
            return jsonify({
                'status': 'error',
                'message': 'Image not found'
            }), 404
        if image.camera.user == user:
            file_path = os.path.join('./uploads/full', image.file_name)
            return send_file(file_path, mimetype='image/jpeg')
        else:
            return jsonify({
                'status': 'error',
                'message': 'Image not found'
            }), 404
    except SQLAlchemyError:
        return jsonify({
                    'status': 'error',
                    'message': 'Database error'
                }), 500


# takes an image id and returns the thumbnail sized image from the file system
@app.route('/images/<int:image_id>/thumbnail', methods=['GET'])
@jwt_required()
def get_thumbnail_image(image_id):
    try:
        user = User.query.get(get_jwt_identity())
        image = Image.query.get(image_id)
        if not image:
            return jsonify({
                'status': 'error',
                'message': 'Image not found'
            }), 404
        if image.camera.user == user:
            file_path = os.path.join('./uploads/thumbnail', image.file_name)
            return send_file(file_path, mimetype='image/jpeg')
        else:
            return jsonify({
                'status': 'error',
                'message': 'Image not found'
            }), 404
    except SQLAlchemyError:
        return jsonify({
                    'status': 'error',
                    'message': 'Database error'
                }), 500



@app.route('/cameras/<int:camera_id>/images/data', methods=['GET'])
@jwt_required()
def get_camera_images(camera_id):
    response_data = []
    try:
        user = User.query.get(get_jwt_identity())
        camera = Camera.query.get(camera_id)
        if camera.user == user:
            for image in camera.images:
                id = image.id
                classification = image.classification
                date_time = image.date_time.strftime("%b %d, %Y %-I:%M %p")
                camera_name = camera.name
                response_data.append({
                    'id': id,
                    'classification': classification,
                    'date_time': date_time,
                    'camera_name': camera_name
                })
            if response_data:
                return jsonify({
                    'status': 'success',
                    'message': 'Image data retrieved',
                    'data': {
                        'image_data': response_data
                    }
                }), 200
            else:
                return jsonify({
                    'status': 'success',
                    'message': 'No image data to retrieve'
                }), 204
        else:
            return jsonify({
                'status': 'error',
                'message': 'Camera not found'
            }), 404
            
    except SQLAlchemyError:
        return jsonify({
                    'status': 'error',
                    'message': 'Database error'
                }), 500

@app.route('/class/<string:class_name>/images/data', methods=['GET'])
@jwt_required()
def get_class_images(class_name):
    response_data = []
    try:
        user = User.query.get(get_jwt_identity())
        for camera in user.cameras:
            for image in camera.images:
                if image.classification == class_name:
                    id = image.id
                    classification = image.classification
                    date_time = image.date_time.strftime("%b %d, %Y %-I:%M %p")
                    camera_name = camera.name
                    response_data.append({
                        'id': id,
                        'classification': classification,
                        'date_time': date_time,
                        'camera_name': camera_name
                    })
            if response_data:
                return jsonify({
                    'status': 'success',
                    'message': 'Image data retrieved',
                    'data': {
                        'image_data': response_data
                    }
                }), 200
            else:
                return jsonify({
                    'status': 'success',
                    'message': 'No image data to retrieve'
                }), 204
        return jsonify({
                'status': 'error',
                'message': 'User has no paired cameras'
            }), 404  
    except SQLAlchemyError:
        return jsonify({
                    'status': 'error',
                    'message': 'Database error'
                }), 500
    
@app.route('/cameras', methods=['POST'])
@jwt_required()
def pair_camera():
    user = User.query.get(get_jwt_identity())
    data = request.get_json()
    token = data.get('token')
    name = data.get('name')
    description = data.get('description')
    pre_camera = PreProvisionedCamera.query.filter_by(token=token, paired=False).first()
    if pre_camera:
        new_camera = Camera(name=name, description=description, user_id=user.id, token=token)
        db.session.add(new_camera)
        pre_camera.paired = True
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': 'Camera Paired'
        }), 201
    else:
        return jsonify({
            'status': 'error',
            'message': 'Invalid token or camera is already paired'
        }), 400

@app.route('/preprovisioned-cameras/<string:token>/check_pair', methods=['GET'])
def check_camera_pair(token):
    pre_camera = PreProvisionedCamera.query.filter_by(token=token, paired=True).first()
    if pre_camera:
        camera = Camera.query.filter_by(token=token).first()
        access_token = create_access_token(identity=camera.id)
        return jsonify({
            'status': 'success',
            'message': 'Camera is paired',
            'data': {
                'access_token': access_token
            }
        }), 201
    return jsonify({
        'status': 'error',
        'message': 'Invalid token or camera is not paired'
    }), 400

    
if __name__ == '__main__':
    app.run('localhost', port=5000, debug=True)