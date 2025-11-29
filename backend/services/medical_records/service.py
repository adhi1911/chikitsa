from datetime import datetime 
from typing import Dict, Optional, List 

from ...core.database import db 
from ...core.logger import logger
from ...core.models import MedicalRecord, PrescriptionItem, Doctor, Patient, Appointment


class MedicalRecordService: 

    ########## MEDICAL RECORD ##########
    @staticmethod
    def create_for_appointment(appointment_id: int, doctor_id: int, data: dict) -> dict:
        """
        Create medical record when completing an appointment.
        Called internally by AppointmentService.complete_with_record()
        """
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            raise ValueError("Appointment not found")

        if appointment.doctor_id != doctor_id:
            raise ValueError("Only the appointment's doctor can create a record")

        # Check if record already exists
        existing = MedicalRecord.query.filter_by(appointment_id=appointment_id).first()
        if existing:
            raise ValueError("Medical record already exists for this appointment")

        # Create record
        followup_date = data.get('followup_date')
        if followup_date and isinstance(followup_date, str):
            followup_date = datetime.strptime(followup_date, '%Y-%m-%d').date()

        record = MedicalRecord(
            appointment_id=appointment_id,
            patient_id=appointment.patient_id,
            doctor_id=doctor_id,
            diagnosis=data['diagnosis'],
            symptoms=data.get('symptoms'),
            treatment_notes=data.get('treatment_notes'),
            doctor_notes=data.get('doctor_notes'),
            followup_date=followup_date,
            created_at=datetime.utcnow()
        )
        db.session.add(record)
        db.session.flush()  # Get record ID

        # Add prescription items
        for item_data in data.get('prescription_items', []):
            item = PrescriptionItem(
                medical_record_id=record.id,
                medicine_name=item_data['medicine_name'],
                dosage=item_data.get('dosage'),
                frequency=item_data.get('frequency'),
                duration=item_data.get('duration'),
                instructions=item_data.get('instructions')
            )
            db.session.add(item)

        # Note: Don't commit here - let AppointmentService handle the transaction
        logger.info(f"Medical record {record.id} created for appointment {appointment_id}")
        return MedicalRecordService._record_to_dict(record, include_doctor_notes=True)


    ########## GETTERS ##########
    @staticmethod
    def get_by_id(record_id: int, include_doctor_notes: bool = False) -> Optional[dict]:
        """Get record by ID"""
        record = MedicalRecord.query.get(record_id)
        if not record:
            raise ValueError("Medical record not found")
        
        return MedicalRecordService._record_to_dict(record, include_doctor_notes=include_doctor_notes)

    @staticmethod
    def get_by_appointment(appointment_id: int, include_doctor_notes: bool = False) -> Optional[dict]:
        """Get record for a specific appointment"""
        record = MedicalRecord.query.filter_by(appointment_id=appointment_id).first()
        if not record:
            raise ValueError("Medical record not found for this appointment")
        
        return MedicalRecordService._record_to_dict(record, include_doctor_notes=include_doctor_notes)


    ########## UPDATE ##########
    @staticmethod
    def update_medical_record(record_id: int, doctor_id: int, data: dict) -> dict: 
        """Update Medical Record"""
        record = MedicalRecord.query.get(record_id)
        if not record:
            raise ValueError("Medical record not found")
        
        if record.doctor_id != doctor_id:
            raise ValueError("Doctor not authorized to update this medical record")
        
        # update fields
        for field in ['diagnosis', 'symptoms', 'treatment_notes', 'doctor_notes', 'followup_date']:
            if field in data:
                setattr(record, field, data[field])
        record.updated_at = datetime.utcnow()

        db.session.commit()
        logger.info(f"Medical record ID {record_id} updated by doctor ID {doctor_id}")

        return MedicalRecordService._record_to_dict(record, include_doctor_notes=True)


    ########## PATIENT HISTORY QUERIES ##########
    @staticmethod
    def get_patient_history(
        patient_id: int, 
        doctor_id: int = None,
        include_doctor_notes: bool = False,
        limit: int = None
    ) -> List[dict]:
        """Get patient's medical history"""
        query = MedicalRecord.query.filter_by(patient_id=patient_id)
        
        if doctor_id:
            query = query.filter_by(doctor_id=doctor_id)
        
        query = query.order_by(MedicalRecord.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        records = query.all()
        
        return [
            MedicalRecordService._record_to_dict(record, include_doctor_notes=include_doctor_notes)
            for record in records
        ]

    @staticmethod
    def get_by_doctor(
        doctor_id: int,
        patient_id: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[dict]:
        """Get all records created by a doctor"""
        query = MedicalRecord.query.filter(MedicalRecord.doctor_id == doctor_id)

        if patient_id:
            query = query.filter(MedicalRecord.patient_id == patient_id)

        if start_date:
            query = query.filter(MedicalRecord.created_at >= start_date)

        if end_date:
            query = query.filter(MedicalRecord.created_at <= end_date)

        records = query.order_by(MedicalRecord.created_at.desc()).all()

        return [MedicalRecordService._record_to_dict(r, include_doctor_notes=True) for r in records]

    @staticmethod
    def get_by_department(
        department_id: int,
        patient_id: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[dict]:
        """Get all records from doctors in a department"""
        query = MedicalRecord.query.join(Doctor).filter(Doctor.department_id == department_id)

        if patient_id:
            query = query.filter(MedicalRecord.patient_id == patient_id)

        if start_date:
            query = query.filter(MedicalRecord.created_at >= start_date)

        if end_date:
            query = query.filter(MedicalRecord.created_at <= end_date)

        records = query.order_by(MedicalRecord.created_at.desc()).all()

        return [MedicalRecordService._record_to_dict(r, include_doctor_notes=True) for r in records]

    @staticmethod
    def get_all(
        patient_id: Optional[int] = None,
        doctor_id: Optional[int] = None,
        department_id: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[dict]:
        """Get all records with filters (admin)"""
        query = MedicalRecord.query

        if patient_id:
            query = query.filter(MedicalRecord.patient_id == patient_id)

        if doctor_id:
            query = query.filter(MedicalRecord.doctor_id == doctor_id)

        if department_id:
            query = query.join(Doctor).filter(Doctor.department_id == department_id)

        if start_date:
            query = query.filter(MedicalRecord.created_at >= start_date)

        if end_date:
            query = query.filter(MedicalRecord.created_at <= end_date)

        records = query.order_by(MedicalRecord.created_at.desc()).all()

        return [MedicalRecordService._record_to_dict(r, include_doctor_notes=True) for r in records]


    @staticmethod 
    def get_patient_export_data(patient_id: int) -> List[Dict]:
        """Get Patients complete medical records for csv """

        try: 
            appointments = Appointment.query.filter(
                Appointment.patient_id == patient_id,
                Appointment.status == 'completed'
            ).order_by(Appointment.date.desc(), Appointment.time.desc()).all()

            export_data = []

            for apt in appointments: 
                doctor = apt.doctor
                record = MedicalRecord.query.filter_by(appointment_id=apt.id).first()

                medicines = []
                if record and record.prescription_items:
                    for item in record.prescription_items: 
                        med_str = item.medicine_name
                        if item.dosage:
                            med_str += f" ({item.dosage})"
                        if item.frequency:
                            med_str += f", {item.frequency}"
                        if item.duration:
                            med_str += f", for {item.duration}"
                        if item.instructions:
                            med_str += f" - {item.instructions}"
                        medicines.append(med_str)
                
                export_data.append({
                    'appointment_date': apt.appointment_date.strftime('%Y-%m-%d'),
                    'appointment_time': apt.appointment_time.strftime('%H:%M'),
                    'doctor_name': f"{doctor.first_name} {doctor.last_name}" if doctor else None,
                    'department': doctor.department.name if doctor and doctor.department else None,
                    'diagnosis': record.diagnosis if record else None,
                    'symptoms': record.symptoms if record else None,
                    'treatment_notes': record.treatment_notes if record else None,
                    'medicines': medicines,
                    'followup_date': record.followup_date.strftime('%Y-%m-%d') if record and record.followup_date else None
                })
            return export_data
        
        except Exception as e:
            logger.error(f"Error fetching export data for patient {patient_id}: {e}")
            raise


    ######### PRESCRIPTION ITEMS #########
    @staticmethod
    def add_prescription_item(record_id: int, doctor_id: int, data: dict) -> dict:
        """Add prescription item to a record"""
        record = MedicalRecord.query.get(record_id)
        if not record:
            raise ValueError("Medical record not found")

        if record.doctor_id != doctor_id:
            raise ValueError("Only the creating doctor can add prescriptions")

        item = PrescriptionItem(
            medical_record_id=record_id,
            medicine_name=data['medicine_name'],
            dosage=data.get('dosage'),
            frequency=data.get('frequency'),
            duration=data.get('duration'),
            instructions=data.get('instructions')
        )
        db.session.add(item)
        db.session.commit()

        logger.info(f"Prescription item {item.id} added to record {record_id}")
        return MedicalRecordService._prescription_item_to_dict(item)

    @staticmethod
    def update_prescription_item(item_id: int, doctor_id: int, data: dict) -> dict: 
        """Update a prescription item"""
        item = PrescriptionItem.query.get(item_id)
        if not item:
            raise ValueError("Prescription item not found")

        record = MedicalRecord.query.get(item.medical_record_id)
        if record.doctor_id != doctor_id:
            raise ValueError("Only the creating doctor can update prescriptions")

        for field in ['medicine_name', 'dosage', 'frequency', 'duration', 'instructions']:
            if field in data:
                setattr(item, field, data[field])

        db.session.commit()
        logger.info(f"Prescription item {item_id} updated by doctor ID {doctor_id}")
        return MedicalRecordService._prescription_item_to_dict(item)

    @staticmethod
    def delete_prescription_item(item_id: int, doctor_id: int) -> bool:
        """Delete prescription item"""
        item = PrescriptionItem.query.get(item_id)
        if not item:
            raise ValueError("Prescription item not found")

        if item.medical_record.doctor_id != doctor_id:
            raise ValueError("Only the creating doctor can delete prescriptions")

        db.session.delete(item)
        db.session.commit()

        logger.info(f"Prescription item {item_id} deleted")
        return True

    ########## ACCESS CONTROL ##########
    @staticmethod 
    def can_doctor_access_record(doctor_id: int, record_id: int) -> bool:
        """Check if a doctor can access a medical record"""
        record = MedicalRecord.query.get(record_id)
        if not record:
            return False
        
        if record.doctor_id == doctor_id:
            return True
        
        doctor = Doctor.query.get(doctor_id)
        record_doctor = Doctor.query.get(record.doctor_id)

        if doctor and record_doctor and doctor.department_id == record_doctor.department_id:
            return True

        return False

    @staticmethod
    def can_doctor_edit_record(doctor_id: int, record_id: int) -> bool:
        """Check if doctor can edit a record (must be record creator)"""
        record = MedicalRecord.query.get(record_id)
        if not record:
            return False
        return record.doctor_id == doctor_id

    @staticmethod
    def can_doctor_access_patient(doctor_id: int, patient_id: int) -> bool:
        """Check if doctor can access patient history"""
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            return False

        exists = MedicalRecord.query.join(Doctor).filter(
            MedicalRecord.patient_id == patient_id,
            Doctor.department_id == doctor.department_id
        ).first()

        return exists is not None

    ########## DICT CONVERSIONS ##########
    @staticmethod
    def _record_to_dict(record: MedicalRecord, include_doctor_notes: bool = False) -> dict: 
        """Convert record to dict"""
        data = {
            'id': record.id,
            'appointment_id': record.appointment_id,
            'patient_id': record.patient_id,
            'patient_name': f"{record.patient.first_name} {record.patient.last_name}" if record.patient else None,
            'doctor_id': record.doctor_id,
            'doctor_name': f"Dr. {record.doctor.first_name} {record.doctor.last_name}" if record.doctor else None,
            'department': record.doctor.department.name if record.doctor and record.doctor.department else None,
            'diagnosis': record.diagnosis,
            'symptoms': record.symptoms,
            'treatment_notes': record.treatment_notes,
            'followup_date': record.followup_date.isoformat() if record.followup_date else None,
            'prescription_items': [
                MedicalRecordService._prescription_item_to_dict(item)
                for item in record.prescription_items
            ],
            'created_at': record.created_at.isoformat() if record.created_at else None,
            'updated_at': record.updated_at.isoformat() if record.updated_at else None
        }

        if include_doctor_notes:
            data['doctor_notes'] = record.doctor_notes

        return data

    @staticmethod
    def _prescription_item_to_dict(item: PrescriptionItem) -> dict:
        """Convert prescription item to dict"""
        return {
            'id': item.id,
            'medicine_name': item.medicine_name,
            'dosage': item.dosage,
            'frequency': item.frequency,
            'duration': item.duration,
            'instructions': item.instructions
        }