from flask import Blueprint, request, jsonify, send_file
from app import jwt, db
from app.models import Image, User, Camera
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from PIL import Image as PILImage
import os

image_routes = Blueprint('image_routes', __name__)

@image_routes.route('/images', methods=['POST'])
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
@image_routes.route('/images/data', methods=['GET'])
@jwt_required()
def get_images_data():
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
@image_routes.route('/images/<int:image_id>/full', methods=['GET'])
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
@image_routes.route('/images/<int:image_id>/thumbnail', methods=['GET'])
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

# removes image with matching id from file and database
@image_routes.route('/images/<int:image_id>', methods=['DELETE'])
@jwt_required()
def delete_image(image_id):
    user = User.query.get(get_jwt_identity())
    cameras = user.cameras
    if cameras:
        # for each image in every camera the user is paired to
        for camera in cameras:
            images = camera.images
            for image in images:
                if image.id == image_id:

                    # delete the image from the file system
                    os.remove(os.path.join('./uploads/full', image.file_name))
                    os.remove(os.path.join('./uploads/thumbnail', image.file_name))

                    # delete the image from the database
                    db.session.delete(image)
                    db.session.commit()
                    return jsonify({
                        "status": "success",
                        "message": "Image deleted",
                    }), 200
        # if no image matches the given id
        return jsonify({
            "status": "error",
            "message": "Image not found"
        }), 404
    # if cameras does not exist
    else:
        return jsonify({
            "status": "error",
            "message": "User has no paired cameras"
        }), 404


@image_routes.route('/cameras/<int:camera_id>/images/data', methods=['GET'])
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

@image_routes.route('/class/<string:class_name>/images/data', methods=['GET'])
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