from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, jwt_required 
from pydantic import ValidationError

from ..core.auth import authenticate_user, get_current_user, refresh_access_token, update_last_login
from ..core.models import User
from .schema import LoginSchema, RegisterPatient, TokenResponse
from .service import AuthService

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = LoginSchema(**request.get_json())
        intended_role = data.role.lower()
        tokens = authenticate_user(data.username, data.password) 
        
        if not tokens:
            return jsonify({
                'status': 'error',
                'message': 'Invalid credentials'
            }), 401
        
        user = User.query.filter_by(username=data.username).first()
        if user.role != intended_role:
            return jsonify({
                'status': 'error',
                'message': f'You are not authorised to login as {intended_role.upper()} '
            }), 403
        
        # update last login for user id
        update_last_login(user.id)

        return jsonify({
            'status': 'success',
            'message': 'Login successful',
            'data': tokens
        }), 200

    except ValidationError as e:
        return jsonify({
            'status': 'error',
            'message': 'Validation error',
            'errors': e.errors()
        }), 400
    

@auth_bp.route('/register/patient', methods=['POST'])
def register():
    try:
        data = RegisterPatient(**request.get_json())
        tokens = AuthService.register_patient(data)

        print(data.dob)

        return jsonify({
            'status': 'success',
            'message': 'Registration successful',
            'data': tokens
            }), 201
    
    except ValidationError as e:
        # print(e)
        return jsonify({
            'status': 'error',
            'message': 'Validation error',
            'errors': e.errors()
        }), 400
    
    except ValueError as ve:
        return jsonify({
            'status': 'error',
            'message': str(ve)
        }), 400
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500
    


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout the current user"""
    jwt_data = get_jwt()
    # print("JWT Data:", jwt_data)  
    # print("Authorization Header:", request.headers.get('Authorization'))
    try:
        jti = get_jwt()["jti"]
        AuthService.logout(jti)
        return jsonify({
            'status': 'success',
            'message': 'Successfully logged out'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
    
@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    try:
        current_user = get_current_user()
        
        if not current_user:
            return jsonify({
                'status': 'error',
                'message': 'User not found'
            }), 404

        profile_data = AuthService.get_user_profile(current_user.id)

        return jsonify({
            'status': 'success',
            'data': profile_data
        }), 200

    except ValueError as ve:
        return jsonify({
            'status': 'error',
            'message': str(ve)
        }), 404

    except Exception as e:
        print(e)
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500
    

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update current user profile"""
    try:
        current_user = get_current_user()
        
        if not current_user:
            return jsonify({
                'status': 'error',
                'message': 'User not found'
            }), 404

        update_data = request.get_json()
        
        if not update_data:
            return jsonify({
                'status': 'error',
                'message': 'No data provided'
            }), 400

        AuthService.update_user_profile(current_user.id, update_data)

        return jsonify({
            'status': 'success',
            'message': 'Profile updated successfully'
        }), 200

    except ValueError as ve:
        return jsonify({
            'status': 'error',
            'message': str(ve)
        }), 400

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user_info():
    """Get basic current user info (lightweight version)"""
    try:
        # print("Authorization Header:", request.headers.get('Authorization'))
        current_user = get_current_user()
        
        if not current_user:
            return jsonify({
                'status': 'error',
                'message': 'User not found'
            }), 404

        user_info = {
            'id': current_user.id,
            'username': current_user.username,
            'email': current_user.email,
            'role': current_user.role,
            'is_active': current_user.is_active
        }

        return jsonify({
            'status': 'success',
            'data': user_info
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500