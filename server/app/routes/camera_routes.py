from app import jwt, db
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from app.models import Camera, User

camera_routes = Blueprint('camera_routes', __name__)

@camera_routes.route('/cameras', methods=['POST'])
@jwt_required()
def pair_camera():
    user = User.query.get(get_jwt_identity())
    data = request.get_json()
    token = data.get('token')
    name = data.get('name')
    description = data.get('description')
    camera = Camera.query.filter_by(token=token).first()
    if camera and not camera.user_id:
        user.cameras.append(camera)
        camera.name = name
        camera.description = description
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

@camera_routes.route('/cameras/<string:token>/check_pair', methods=['GET'])
def check_camera_pair(token):
    camera = Camera.query.filter_by(token=token).first()
    if camera and camera.user_id:
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