from datetime import datetime
from typing import Optional, List, Dict

from ...core.database import db
from ...core.logger import logger
from ...core.models import User, Patient
from ...auth.service import AuthService
from ...auth.schema import RegisterPatient
from ..medical_records.service import MedicalRecordService
from  ...utils.csv_export import generate_patient_records_csv, generate_csv_export_mail_html
from ...core.mail import send_email


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
    
    @staticmethod
    def export_patient_records(patient_id: int, email: Optional[str]=None) -> Dict: 
        """Generate and send csv of patient records"""

        logger.info(f"Starting CSV export for patient {patient_id}")

        patient = Patient.query.get(patient_id)
        if not patient:
            return {'status': 'error', 'message': 'Patient not found'}
        
        patient_name = f"{patient.first_name} {patient.last_name}"
        target_email = email or (patient.user.email if patient.user else None)
        
        if not target_email:
            return {'status': 'error', 'message': 'No email address available'}

        try:
            records = MedicalRecordService.get_patient_export_data(patient_id)
            
            if not records:
                return {'status': 'warning', 'message': 'No medical records found'}
            
            csv_content = generate_patient_records_csv(
            patient_id=patient_id,
            patient_name=patient_name,
            records=records
            )

            timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
            filename = f"patient_{patient_id}_records_{timestamp}.csv"

            html_body = generate_csv_export_mail_html(
                patient_name=patient_name,
                filename=filename,
                generated_at=datetime.utcnow(),
                records_count=len(records)
            )

            success = send_email(
                to=target_email,
                subject="Your Medical Records Export",
                html_body=html_body,
                attachments=[{
                    'filename': filename,
                    'content_type': 'text/csv',
                    'data': csv_content
                }]
            )

            if success:
                logger.info(f"Export sent to {target_email} for patient {patient_id}")
                return {
                    'status': 'success',
                    'message': 'Export sent successfully',
                    'email': target_email,
                    'filename': filename,
                    'records_count': len(records)
                }
            else:
                return {'status': 'error', 'message': 'Failed to send email'}
            
        except Exception as e:
            logger.error(f"Export failed for patient {patient_id}: {e}")
            return {'status': 'error', 'message': str(e)}
            
            