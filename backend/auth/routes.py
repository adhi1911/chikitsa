from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required 
from pydantic import ValidationError

from ..core.auth import authenticate_user, refresh_access_token
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
    
