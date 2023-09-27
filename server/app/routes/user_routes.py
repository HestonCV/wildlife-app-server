from flask import Blueprint, request, jsonify
from app.utils import generate_hashed_password, check_password
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from sqlalchemy.exc import SQLAlchemyError
from app.models import User
from app import jwt, db

user_routes = Blueprint('user_routes', __name__)

# /register takes first name, last name, email, and password.
# it encrypts the password and stores it in the database
@user_routes.route('/register', methods=['POST'])
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
        
        # format names
        first_name = first_name.strip()
        last_name = last_name.strip()

        # format email
        email = email.strip().lower()
        # TODO: validate email and password for formatting

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
    except SQLAlchemyError as e:
        db.session.rollback()
        print("SQLAlchemyError:", e)
        return jsonify({
          'status': 'error',
          'message': 'Database error'
        }), 500
    
# /login takes email and password, compares the password to the hashed
# password in the database if the email matches, and returns a jwt token
@user_routes.route('/login', methods=['POST'])
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
        
        # format email
        email = email.strip().lower()

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
            'data': {
                'access_token': access_token
            }
        }), 200
    
    except SQLAlchemyError as e:
        db.session.rollback()
        print("SQLAlchemyError:", e)
        return jsonify({
            'status': 'error',
            'message': 'Database error'
            }), 500
    
# /validate_token checks a jwt token, if its valid and a user exists it returns true
@user_routes.route('/validate_token', methods=['POST'])
@jwt_required()
def validate_token():
    user = User.query.get(get_jwt_identity())
    if user:
        return jsonify({
            'status': 'success',
            'message': 'User logged in',
            'data': {
                'authorized': True
            }
        }), 200
    else:
        return jsonify({
            'status': 'error',
            'message': 'User not found',
            'data': {
                'authorized': False
            }
        }), 404