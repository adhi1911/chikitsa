from datetime import datetime
from http.client import HTTPException 
from flask_bcrypt import Bcrypt
from flask_jwt_extended import get_jwt


from ..core.database import db
from ..core.models import User, Patient, TokenBlacklist
from ..core.auth import generate_tokens, update_last_login
from .schema import LoginSchema, RegisterPatient

bcrypt = Bcrypt()

class AuthService:
    """Service class for authentication related operations"""


    @staticmethod
    def register_patient(data: RegisterPatient):
        """Authenticate user and generate tokens"""
        if User.query.filter_by(username = data.username).first():
            raise ValueError("Username already exists")
        
        if User.query.filter_by(email = data.email).first():
            raise ValueError("Email already registered")
        
        try:
            # creating user 
            user = User(
                username = data.username,
                email = data.email,
                password_hash = bcrypt.generate_password_hash(data.password).decode('utf-8'),
                role = 'patient',
                is_active = True
            )

            db.session.add(user)
            db.session.flush() # to get user.id before commit

            # creating patient profile
            patient = Patient(
                user_id = user.id,
                first_name = data.first_name,
                last_name = data.last_name,
                dob = data.dob,
                gender = data.gender,
                blood_group = data.blood_group,
                phone = data.phone,
                address = data.address,
                emergency_contact_name = data.emergency_contact_name,
                emergency_contact_phone = data.emergency_contact_phone,
                medical_history = data.medical_history
            )

            db.session.add(patient)

            # commit all changes
            db.session.commit()
            return generate_tokens(user)
        
        except Exception as e:
            db.session.rollback()
            raise e
        except HTTPException as he:
            db.session.rollback()
            raise he


    @staticmethod
    def logout(jti: str):
        """Invalidate user token when logout"""
        try:
            blacklisted_token = TokenBlacklist(jti = jti)
            db.session.add(blacklisted_token)
            db.session.commit()

            return True

        except Exception as e:
            db.session.rollback()
            raise e

