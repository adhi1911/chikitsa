from flask import Flask, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, get_jwt_identity, jwt_required
from flask_cors import CORS

# module imports

from backend.core.database import db
from backend.core.config import Config
from backend.core.models import (User, 
                         Patient,
                         Doctor, Department, DoctorUnavailability, DoctorWorkingHours,
                         Appointment, Notification, MedicalRecord, PrescriptionItem, TokenBlacklist)

from backend.auth.routes import auth_bp
from backend.services.admin.routes import admin_bp


bcrypt = Bcrypt()
jwt = JWTManager()

@jwt.token_verification_failed_loader
def verification_failed_callback(jwt_header, jwt_payload):
    print("Token verification failed:", jwt_header, jwt_payload)
    return jsonify({
        'status': 'error',
        'message': 'Token verification failed'
    }), 422

@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return jsonify({
        'status': 'error',
        'message': 'Token has been revoked'
    }), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    print("Invalid token:", error)
    return jsonify({
        'status': 'error',
        'message': 'Invalid token'
    }), 422

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({
        'status': 'error',
        'message': 'Token has expired'
    }), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        'status': 'error',
        'message': 'Missing Authorization header'
    }), 401

# functin to create root instance of the application
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    bcrypt.init_app(app)
    jwt.init_app(app)

    CORS(app, origins=["http://localhost:8080", "http://127.0.0.1:8080"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS","PATCH"],
        allow_headers=["Content-Type", "Authorization"],
        expose_headers=["Authorization"],
        supports_credentials=True)


    db.init_app(app)

    # blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)

    with app.app_context():
        db.create_all()

        admin_user = User.query.filter_by(role='admin').first()
        if not admin_user:
            admin = User(
                username = app.config['ADMIN_USERNAME'],
                email = "admin.chikitsa@admin.com",
                password_hash = bcrypt.generate_password_hash(app.config['ADMIN_PASSWORD']).decode('utf-8'),
                role = 'admin',
                is_active = True
            )
            db.session.add(admin)
            db.session.commit()
    return app

app = create_app()

@app.route('/')
def root():
    return {"status":"ok",
            "message":"still alive and running"}, 200

@app.route('/admin')
def admin_route():
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        return {"status":"error",
                "message":"Admin user not found"}, 404
    return {"status":"ok",
            "admin_username":admin.username,
            "admin_email":admin.email}, 200



# run the application
if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])