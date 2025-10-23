from functools import wraps
from datetime import datetime
from flask import jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    get_jwt,
    verify_jwt_in_request
)
from ..core.database import db
from ..core.models import User

def generate_tokens(user):
    """Generate access and refresh tokens for a user"""

    additional_claims = {
        'role': user.role,
        'username': user.username,
        'user_id': str(user.id)  
    }

    access_token = create_access_token(
        identity=str(user.id), 
        additional_claims=additional_claims
    )

    refresh_token = create_refresh_token(
        identity=str(user.id), 
        additional_claims=additional_claims
    )
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'bearer'
    }

def update_last_login(user_id):
    """Update the last login timestamp for a user"""
    user = User.query.get(user_id)
    if user:
        user.last_login = datetime.utcnow()
        db.session.commit()


def authenticate_user(username, password):
    """Authenticate user and return tokens"""
    from flask_bcrypt import Bcrypt
    bcrypt = Bcrypt()
    
    user = User.query.filter_by(username=username).first()
    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        return None
        
    if not user.is_active:
        return None
        
    update_last_login(user.id)
    return generate_tokens(user)


def refresh_access_token():
    """Generate new access token using refresh token"""
    identity = get_jwt_identity()
    user = User.query.get(identity)
    
    if not user or not user.is_active:
        return None
        
    additional_claims = {
        'role': user.role,
        'username': user.username,
        'email': user.email
    }
    
    return create_access_token(
        identity=identity,
        additional_claims=additional_claims
    )


def get_current_user():
    """Get the current authenticated user from JWT token"""
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or not user.is_active:
            return None
        
        return user 

    except Exception:
        return None


def get_current_user_claims():
    """Get the claims of the current authenticated user from JWT token"""
    try:
        verify_jwt_in_request()
        claims = get_jwt()
        return claims
    except Exception:
        return None
    


## Decorators 
def role_required(*roles):
    """Decorator to protect routes with role-based access control"""
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args,**kwargs):
            verify_jwt_in_request()
            claims = get_jwt()

            if claims.get('role') in roles:
                return fn(*args, **kwargs)
            return jsonify({
                'status':'error',
                'message':'Access forbidden: insufficient permissions'
            }), 403
        return decorator
    return wrapper

# role specific decorators
admin_required = role_required('admin')
doctor_required = role_required('doctor')
patient_required = role_required('patient')

def token_required(f):
    """Decorator to protect routes with JWT token verification"""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
            current_user = get_current_user()
            
            if not current_user:
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid or expired token'
                }), 401
                
            return f(current_user, *args, **kwargs)
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': 'Token verification failed'
            }), 401
    
    return decorated