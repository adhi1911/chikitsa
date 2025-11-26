from datetime import datetime
from typing import Optional, List

from ...core.database import db
from ...core.logger import logger
from ...core.models import User, Patient
from ...auth.service import AuthService
from ...auth.schema import RegisterPatient


class PatientService:
    """
    Patient service - used by both patient and admin routes.
    Note: delete and blacklist operations are in AdminService.
    """

    @staticmethod
    def get_patient(patient_id: int) -> Optional[dict]:
        """Get patient by ID"""
        result = db.session.query(Patient, User).join(
            User, Patient.user_id == User.id
        ).filter(Patient.id == patient_id).first()

        if not result:
            logger.warning(f"Patient with id {patient_id} not found")
            return None

        patient, user = result
        return PatientService._to_dict(patient, user)

    @staticmethod
    def get_patient_by_user_id(user_id: int) -> Optional[dict]:
        """Get patient by user ID"""
        result = db.session.query(Patient, User).join(
            User, Patient.user_id == User.id
        ).filter(User.id == user_id).first()

        if not result:
            return None

        patient, user = result
        return PatientService._to_dict(patient, user)

    @staticmethod
    def get_patients(include_inactive: bool = False) -> List[dict]:
        """Get all patients"""
        query = db.session.query(Patient, User).join(User, Patient.user_id == User.id)

        if not include_inactive:
            query = query.filter(User.is_active == True)

        results = query.all()
        patients = [PatientService._to_dict(p, u) for p, u in results]

        logger.info(f"Fetched {len(patients)} patients")
        return patients

    @staticmethod
    def create_patient(data: RegisterPatient) -> dict:
        """Create patient - wraps AuthService.register_patient"""
        result = AuthService.register_patient(data)
        
        # Fetch created patient
        user = User.query.filter_by(username=data.username).first()
        patient = Patient.query.filter_by(user_id=user.id).first()
        
        logger.info(f"Patient created with id: {patient.id}")
        return PatientService._to_dict(patient, user)

    @staticmethod
    def update_patient(patient_id: int, data: dict) -> dict:
        """Update patient profile"""
        patient = Patient.query.get(patient_id)
        if not patient:
            raise ValueError("Patient not found")

        user = User.query.get(patient.user_id)
        if not user:
            raise ValueError("User not found")

        logger.info(f"Updating patient id {patient_id}")

        # updating email
        if 'email' in data and data['email']:
            existing = User.query.filter(User.email == data['email'], User.id != user.id).first()
            if existing:
                raise ValueError("Email already exists")
            user.email = data['email']

        # updating patient fields
        patient_fields = [
            'first_name', 'last_name', 'phone', 'address', 'dob',
            'gender', 'blood_group', 'emergency_contact_name',
            'emergency_contact_phone', 'medical_history'
        ]

        for field in patient_fields:
            if field in data:
                setattr(patient, field, data[field])

        patient.updated_at = datetime.utcnow()
        db.session.commit()

        logger.info(f"Patient id {patient_id} updated successfully")
        return PatientService.get_patient(patient_id)

    # response purposes
    @staticmethod
    def _to_dict(patient: Patient, user: User) -> dict:
        """Convert patient and user to dictionary"""
        return {
            'id': patient.id,
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': patient.first_name,
            'last_name': patient.last_name,
            'full_name': f"{patient.first_name} {patient.last_name}",
            'phone': patient.phone,
            'dob': patient.dob.isoformat() if patient.dob else None,
            'gender': patient.gender,
            'blood_group': patient.blood_group,
            'address': patient.address,
            'emergency_contact_name': patient.emergency_contact_name,
            'emergency_contact_phone': patient.emergency_contact_phone,
            'medical_history': patient.medical_history,
            'is_active': user.is_active,
            'created_at': patient.created_at.isoformat() if patient.created_at else None,
            'updated_at': patient.updated_at.isoformat() if patient.updated_at else None
        }
    
    #