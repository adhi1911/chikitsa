from datetime import datetime
from http.client import HTTPException 
from flask_bcrypt import Bcrypt
from flask_jwt_extended import get_jwt


from ..core.database import db
from ..core.models import Doctor, User, Patient, TokenBlacklist
from ..core.auth import generate_tokens, update_last_login, get_current_user
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
            # print("Token added to blacklist")

            return True

        except Exception as e:
            db.session.rollback()
            raise e


    @staticmethod
    def get_user_profile(user_id: int):
        """Get user profile with role-specific data"""
        try:
            user = User.query.get(user_id)
            if not user:
                raise ValueError("User not found")

            profile_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'is_active': user.is_active,
                'created_at': user.created_at.isoformat() if hasattr(user, 'created_at') else None,
                'last_login': user.last_login.isoformat() if hasattr(user, 'last_login') and user.last_login else None
            }

            # role specific data
            if user.role == 'patient':
                patient = Patient.query.filter_by(user_id=user.id).first()
                if patient:
                    profile_data.update({
                        'first_name': patient.first_name,
                        'last_name': patient.last_name,
                        'full_name': f"{patient.first_name} {patient.last_name}",
                        'phone': patient.phone,
                        'date_of_birth': patient.dob.isoformat() if patient.dob else None,
                        'gender': patient.gender,
                        'blood_group': patient.blood_group,
                        'address': patient.address,
                        'emergency_contact_name': patient.emergency_contact_name,
                        'emergency_contact_phone': patient.emergency_contact_phone,
                        'medical_history': patient.medical_history
                    })

            elif user.role == 'doctor':
                # join to dept to get dept name from dept id 
                doctor = Doctor.query.filter_by(user_id=user.id).first()
                if doctor:
                    profile_data.update({
                        'first_name': doctor.first_name,
                        'last_name': doctor.last_name,
                        'full_name': f"{doctor.first_name} {doctor.last_name}",
                        'phone': doctor.phone,
                        'specialization': doctor.specialization,
                        'qualification': doctor.qualification,
                        'experience_years': doctor.experience_years,
                        'consultation_fee': doctor.consultation_fee,
                        'is_available': doctor.is_available,
                        'department_id': doctor.department_id
                    })

            return profile_data

        except Exception as e:
            raise e

    @staticmethod
    def update_user_profile(user_id: int, update_data: dict):
        """Update user profile with role-specific data"""
        try:
            user = User.query.get(user_id)
            if not user:
                raise ValueError("User not found")

            # basic user info
            if 'email' in update_data:
                # Check if email is already taken by another user
                existing_user = User.query.filter(User.email == update_data['email'], User.id != user_id).first()
                if existing_user:
                    raise ValueError("Email already exists")
                user.email = update_data['email']

            # role -specific
            if user.role == 'patient':
                patient = Patient.query.filter_by(user_id=user.id).first()
                if patient:
                    if 'phone' in update_data:
                        patient.phone = update_data['phone']
                    if 'address' in update_data:
                        patient.address = update_data['address']
                    if 'emergency_contact_name' in update_data:
                        patient.emergency_contact_name = update_data['emergency_contact_name']
                    if 'emergency_contact_phone' in update_data:
                        patient.emergency_contact_phone = update_data['emergency_contact_phone']
                    if 'medical_history' in update_data:
                        patient.medical_history = update_data['medical_history']

            elif user.role == 'doctor':
                doctor = Doctor.query.filter_by(user_id=user.id).first()
                if doctor:
                    if 'phone' in update_data:
                        doctor.phone = update_data['phone']
                    if 'specialization' in update_data:
                        doctor.specialization = update_data['specialization']

            db.session.commit()
            return True

        except Exception as e:
            db.session.rollback()
            raise e
