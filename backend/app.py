from flask import Flask
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, get_jwt_identity, jwt_required
from flask_cors import CORS

# module imports

from backend.core.database import db
from backend.core.config import Config
from backend.core.models import (User, 
                         Patient,
                         Doctor, Department, DoctorUnavailability, DoctorWorkingHours,
                         Appointment, Notification, MedicalRecord, PrescriptionItem)

from backend.auth.routes import auth_bp


bcrypt = Bcrypt()
jwt = JWTManager()

# functin to create root instance of the application
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    bcrypt.init_app(app)
    jwt.init_app(app)

    CORS(app, origins=["http://localhost:8080", "http://127.0.0.1:8080"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"])


    db.init_app(app)

    # blueprints
    app.register_blueprint(auth_bp)

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