from flask import Blueprint, request, jsonify 
from flask_jwt_extended import jwt_required, get_jwt_identity
from pydantic import ValidationError

from ...core.logger import logger
from ...core.auth import doctor_required
from ...core.database import db

from .service import DoctorService
from ..appointments.service import AppointmentService
from ..medical_records.service import MedicalRecordService

from .schemas import UnavailabilityCreate, UnavailabilityUpdate
from ..medical_records.schemas import MedicalRecordCreate, MedicalRecordUpdate, PrescriptionItemCreate, PrescriptionItemUpdate
from ...core.models import Doctor

doctor_bp = Blueprint('doctors', __name__, url_prefix='/doctor')


def get_doctor_id_from_user(user_id: int) -> int:
    """Get doctor ID from user ID"""
    doctor = Doctor.query.filter_by(user_id=user_id).first()
    if not doctor:
        return None
    return doctor.id

########### WORKING HOUR ROUTES ###########

@doctor_bp.route('/working-hours', methods=['GET'])
@jwt_required()
@doctor_required
def get_my_working_hours():
    """Get doctor's working hours"""
    try:
        user_id = get_jwt_identity()
        doctor_id = get_doctor_id_from_user(user_id)
        
        if not doctor_id:
            return jsonify({'status': 'error', 'message': 'Doctor not found'}), 404
        
        hours = DoctorService.get_working_hours(doctor_id)
        return jsonify({
            'status': 'success',
            'data': {
                'working_hours': hours
            }
        })
    except Exception as e:
        logger.error(f"Error fetching working hours: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'Failed to fetch working hours'}), 500
    

########### DASHBOARD STATS ###########

@doctor_bp.route('/dashboard/stats', methods=['GET'])
@jwt_required()
@doctor_required
def get_dashboard_stats():
    """Get doctor's dashboard statistics"""
    try:
        user_id = get_jwt_identity()
        doctor_id = get_doctor_id_from_user(user_id)

        if not doctor_id:
            return jsonify({'status': 'error', 'message': 'Doctor not found'}), 404

        from ...core.models import Appointment, MedicalRecord
        from datetime import date, timedelta

        today = date.today()
        week_start = today - timedelta(days=today.weekday())

        # Appointments
        today_appointments = Appointment.query.filter(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date == today
        ).all()

        stats = {
            'today': {
                'total': len(today_appointments),
                'completed': len([a for a in today_appointments if a.status == 'completed']),
                'pending': len([a for a in today_appointments if a.status == 'scheduled']),
                'cancelled': len([a for a in today_appointments if a.status == 'cancelled'])
            },
            'this_week': {
                'total': Appointment.query.filter(
                    Appointment.doctor_id == doctor_id,
                    Appointment.appointment_date >= week_start
                ).count()
            },
            'upcoming': Appointment.query.filter(
                Appointment.doctor_id == doctor_id,
                Appointment.appointment_date >= today,
                Appointment.status == 'scheduled'
            ).count(),
            'total_patients': db.session.query(Appointment.patient_id).filter(
                Appointment.doctor_id == doctor_id
            ).distinct().count(),
            'total_records': MedicalRecord.query.filter_by(doctor_id=doctor_id).count()
        }

        return jsonify({
            'status': 'success',
            'data': {'stats': stats}
        })
    except Exception as e:
        logger.error(f"Failed to get dashboard stats: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

########### UNAVAILABILITY ROUTES ###########

@doctor_bp.route('/unavailability', methods=['GET'])
@jwt_required()
@doctor_required
def get_my_unavailability():
    """Get current doctor's unavailability periods"""
    try:
        user_id = get_jwt_identity()
        doctor_id = get_doctor_id_from_user(user_id)
        
        if not doctor_id:
            return jsonify({'status': 'error', 'message': 'Doctor not found'}), 404
        
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        unavailability = DoctorService.get_unavailability(doctor_id, start_date, end_date)
        return jsonify({
            'status': 'success',
            'data': {'unavailability': unavailability}
        })
    except Exception as e:
        logger.error(f"Failed to get unavailability: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500
    


@doctor_bp.route('/unavailability', methods=['POST'])
@jwt_required()
@doctor_required
def create_my_unavailability():
    """Create unavailability period for current doctor"""
    try:
        user_id = get_jwt_identity()
        doctor_id = get_doctor_id_from_user(user_id)
        
        if not doctor_id:
            return jsonify({'status': 'error', 'message': 'Doctor not found'}), 404
        
        data = UnavailabilityCreate(**request.get_json())
        unavailability = DoctorService.create_unavailability(doctor_id, data.model_dump())
        
        return jsonify({
            'status': 'success',
            'message': 'Unavailability created successfully',
            'data': {'unavailability': unavailability}
        }), 201
    except ValidationError as e:
        logger.error(f"Unavailability validation error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Validation error',
            'errors': e.errors()
        }), 400
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        logger.error(f"Failed to create unavailability: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500


@doctor_bp.route('/unavailability/<int:unavail_id>', methods=['PUT'])
@jwt_required()
@doctor_required
def update_my_unavailability(unavail_id):
    """Update unavailability period"""
    try:
        user_id = get_jwt_identity()
        doctor_id = get_doctor_id_from_user(user_id)
        
        if not doctor_id:
            return jsonify({'status': 'error', 'message': 'Doctor not found'}), 404
        
        # Verify ownership
        from ...core.models import DoctorUnavailability
        unavail = DoctorUnavailability.query.get(unavail_id)
        if not unavail or unavail.doctor_id != doctor_id:
            return jsonify({'status': 'error', 'message': 'Unavailability not found'}), 404
        
        # Check if hospital holiday
        if unavail.reason and unavail.reason.startswith('[Hospital Holiday]'):
            return jsonify({
                'status': 'error',
                'message': 'Cannot modify hospital holidays. Contact admin.'
            }), 403
        
        data = UnavailabilityUpdate(**request.get_json())
        unavailability = DoctorService.update_unavailability(unavail_id, data.model_dump(exclude_unset=True))
        
        return jsonify({
            'status': 'success',
            'message': 'Unavailability updated successfully',
            'data': {'unavailability': unavailability}
        })
    except ValidationError as e:
        logger.error(f"Unavailability validation error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Validation error',
            'errors': e.errors()
        }), 400
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        logger.error(f"Failed to update unavailability: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500


@doctor_bp.route('/unavailability/<int:unavail_id>', methods=['DELETE'])
@jwt_required()
@doctor_required
def delete_my_unavailability(unavail_id):
    """Delete unavailability period"""
    try:
        user_id = get_jwt_identity()
        doctor_id = get_doctor_id_from_user(user_id)
        
        if not doctor_id:
            return jsonify({'status': 'error', 'message': 'Doctor not found'}), 404
        
        # Verify ownership
        from ...core.models import DoctorUnavailability
        unavail = DoctorUnavailability.query.get(unavail_id)
        if not unavail or unavail.doctor_id != doctor_id:
            return jsonify({'status': 'error', 'message': 'Unavailability not found'}), 404
        
        # Check if hospital holiday
        if unavail.reason and unavail.reason.startswith('[Hospital Holiday]'):
            return jsonify({
                'status': 'error',
                'message': 'Cannot delete hospital holidays. Contact admin.'
            }), 403
        
        DoctorService.delete_unavailability(unavail_id)
        return jsonify({
            'status': 'success',
            'message': 'Unavailability deleted successfully'
        })
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        logger.error(f"Failed to delete unavailability: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500



######### CALENDER ROUTES ###########
@doctor_bp.route('/calendar', methods=['GET'])
@jwt_required()
@doctor_required
def get_my_calendar():
    """Get doctor's calendar view with appointments and unavailability"""
    try:
        user_id = get_jwt_identity()
        doctor_id = get_doctor_id_from_user(user_id)
        
        if not doctor_id:
            return jsonify({'status': 'error', 'message': 'Doctor not found'}), 404
        
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        calendar_data = DoctorService.get_calendar(doctor_id, start_date, end_date)
        return jsonify({
            'status': 'success',
            'data': {'calendar': calendar_data}
        })
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        logger.error(f"Failed to get calendar: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500


@doctor_bp.route('/schedule/<string:date>', methods=['GET'])
@jwt_required()
@doctor_required
def get_daily_schedule(date):
    """Get detailed schedule for a specific day"""
    try:
        user_id = get_jwt_identity()
        doctor_id = get_doctor_id_from_user(user_id)
        
        if not doctor_id:
            return jsonify({'status': 'error', 'message': 'Doctor not found'}), 404
        
        schedule_data = DoctorService.get_daily_schedule(doctor_id, date)
        return jsonify({
            'status': 'success',
            'data': {'schedule': schedule_data}
        })
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        logger.error(f"Failed to get daily schedule: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500


########## APPOINTMENT ROUTES ##########

@doctor_bp.route('/appointments', methods=['GET'])
@jwt_required()
@doctor_required
def get_my_appointments():
    """Get doctor's appointments"""
    try:
        user_id = get_jwt_identity()
        doctor_id = get_doctor_id_from_user(user_id)

        if not doctor_id:
            return jsonify({'status': 'error', 'message': 'Doctor not found'}), 404

        status = request.args.get('status')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        upcoming = request.args.get('upcoming', 'false').lower() == 'true'

        appointments = AppointmentService.get_by_doctor(
            doctor_id, status, start_date, end_date, upcoming
        )

        return jsonify({
            'status': 'success',
            'data': {'appointments': appointments}
        })
    except Exception as e:
        logger.error(f"Failed to get appointments: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500


@doctor_bp.route('/appointments/<int:appointment_id>', methods=['GET'])
@jwt_required()
@doctor_required
def get_appointment(appointment_id):
    """Get specific appointment"""
    try:
        user_id = get_jwt_identity()
        doctor_id = get_doctor_id_from_user(user_id)

        appointment = AppointmentService.get_by_id(appointment_id)

        if not appointment:
            return jsonify({'status': 'error', 'message': 'Appointment not found'}), 404

        if appointment['doctor_id'] != doctor_id:
            return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403

        return jsonify({
            'status': 'success',
            'data': {'appointment': appointment}
        })
    except Exception as e:
        logger.error(f"Failed to get appointment: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500
    

@doctor_bp.route('/appointments/<int:appointment_id>/status', methods=['PATCH'])
@jwt_required()
@doctor_required
def update_appointment_status(appointment_id):
    """Update appointment status (complete, no_show, cancel)"""
    try:
        user_id = get_jwt_identity()
        doctor_id = get_doctor_id_from_user(user_id)

        existing = AppointmentService.get_by_id(appointment_id)

        if not existing:
            return jsonify({'status': 'error', 'message': 'Appointment not found'}), 404

        if existing['doctor_id'] != doctor_id:
            return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403

        data = request.get_json()
        new_status = data.get('status')

        valid_statuses = ['scheduled', 'completed', 'cancelled', 'no_show']
        if new_status not in valid_statuses:
            return jsonify({
                'status': 'error',
                'message': f'Invalid status. Must be: {", ".join(valid_statuses)}'
            }), 400

        appointment = AppointmentService.update_status(appointment_id, new_status)

        return jsonify({
            'status': 'success',
            'message': f'Appointment marked as {new_status}',
            'data': {'appointment': appointment}
        })
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        logger.error(f"Failed to update status: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

@doctor_bp.route('/appointments/<int:appointment_id>/complete', methods=['POST'])
@jwt_required()
@doctor_required
def complete_appointment(appointment_id):
    """Complete appointment with medical record in one call"""
    try:
        user_id = get_jwt_identity()
        doctor_id = get_doctor_id_from_user(user_id)

        if not doctor_id:
            return jsonify({'status': 'error', 'message': 'Doctor not found'}), 404

        data = request.get_json()
        
        # Validate required fields
        if not data.get('diagnosis'):
            return jsonify({'status': 'error', 'message': 'Diagnosis is required'}), 400

        result = AppointmentService.complete_with_record(
            appointment_id=appointment_id,
            doctor_id=doctor_id,
            record_data=data
        )

        return jsonify({
            'status': 'success',
            'message': 'Appointment completed successfully',
            'data': result
        })
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        logger.error(f"Failed to complete appointment: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500 

######### MEDICAL RECORD ROUTES #########


@doctor_bp.route('/appointments/<int:appointment_id>/record', methods=['POST'])
@jwt_required()
@doctor_required
def create_medical_record(appointment_id):
    """Create medical record for an appointment"""
    try:
        user_id = get_jwt_identity()
        doctor_id = get_doctor_id_from_user(user_id)

        if not doctor_id:
            return jsonify({'status': 'error', 'message': 'Doctor not found'}), 404

        data = MedicalRecordCreate(**request.get_json())
        
        record = MedicalRecordService.create_medical_record(
            appointment_id=appointment_id,
            doctor_id=doctor_id,
            data=data.model_dump()
        )

        return jsonify({
            'status': 'success',
            'message': 'Medical record created',
            'data': {'record': record}
        }), 201
    except ValidationError as e:
        return jsonify({'status': 'error', 'message': 'Validation error', 'errors': e.errors()}), 400
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        logger.error(f"Failed to create medical record: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500


@doctor_bp.route('/appointments/<int:appointment_id>/record', methods=['GET'])
@jwt_required()
@doctor_required
def get_appointment_record(appointment_id):
    """Get medical record for an appointment"""
    try:
        user_id = get_jwt_identity()
        doctor_id = get_doctor_id_from_user(user_id)

        if not doctor_id:
            return jsonify({'status': 'error', 'message': 'Doctor not found'}), 404

        record = MedicalRecordService.get_by_appointment(appointment_id, include_doctor_notes=True)

        if not record:
            return jsonify({'status': 'error', 'message': 'Medical record not found'}), 404

        # Check access (own record or same department)
        if not MedicalRecordService.can_doctor_access_record(doctor_id, record['id']):
            return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403

        return jsonify({
            'status': 'success',
            'data': {'record': record}
        })
    except Exception as e:
        logger.error(f"Failed to get medical record: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500


@doctor_bp.route('/records/<int:record_id>', methods=['GET'])
@jwt_required()
@doctor_required
def get_medical_record(record_id):
    """Get medical record by ID"""
    try:
        user_id = get_jwt_identity()
        doctor_id = get_doctor_id_from_user(user_id)

        if not doctor_id:
            return jsonify({'status': 'error', 'message': 'Doctor not found'}), 404

        # Check access first
        if not MedicalRecordService.can_doctor_access_record(doctor_id, record_id):
            return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403

        record = MedicalRecordService.get_by_id(record_id, include_doctor_notes=True)

        if not record:
            return jsonify({'status': 'error', 'message': 'Medical record not found'}), 404

        return jsonify({
            'status': 'success',
            'data': {'record': record}
        })
    except Exception as e:
        logger.error(f"Failed to get medical record: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500


@doctor_bp.route('/records/<int:record_id>', methods=['PUT'])
@jwt_required()
@doctor_required
def update_medical_record(record_id):
    """Update medical record (only by creating doctor)"""
    try:
        user_id = get_jwt_identity()
        doctor_id = get_doctor_id_from_user(user_id)

        if not doctor_id:
            return jsonify({'status': 'error', 'message': 'Doctor not found'}), 404

        data = MedicalRecordUpdate(**request.get_json())
        
        record = MedicalRecordService.update_medical_record(
            record_id=record_id,
            doctor_id=doctor_id,
            data=data.model_dump(exclude_unset=True)
        )

        return jsonify({
            'status': 'success',
            'message': 'Medical record updated',
            'data': {'record': record}
        })
    except ValidationError as e:
        return jsonify({'status': 'error', 'message': 'Validation error', 'errors': e.errors()}), 400
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        logger.error(f"Failed to update medical record: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500


@doctor_bp.route('/records', methods=['GET'])
@jwt_required()
@doctor_required
def get_my_records():
    """Get all records created by this doctor"""
    try:
        user_id = get_jwt_identity()
        doctor_id = get_doctor_id_from_user(user_id)

        if not doctor_id:
            return jsonify({'status': 'error', 'message': 'Doctor not found'}), 404

        patient_id = request.args.get('patient_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        records = MedicalRecordService.get_by_doctor(
            doctor_id=doctor_id,
            patient_id=patient_id,
            start_date=start_date,
            end_date=end_date
        )

        return jsonify({
            'status': 'success',
            'data': {'records': records, 'total': len(records)}
        })
    except Exception as e:
        logger.error(f"Failed to get records: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500


@doctor_bp.route('/patients/<int:patient_id>/history', methods=['GET'])
@jwt_required()
@doctor_required
def get_patient_history(patient_id):
    """Get patient's medical history (same department access)"""
    try:
        user_id = get_jwt_identity()
        doctor_id = get_doctor_id_from_user(user_id)

        if not doctor_id:
            return jsonify({'status': 'error', 'message': 'Doctor not found'}), 404

        # Get doctor's department
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            return jsonify({'status': 'error', 'message': 'Doctor not found'}), 404

        # Filter by department (same dept access)
        department_id = request.args.get('department_id', type=int) or doctor.department_id
        filter_doctor_id = request.args.get('doctor_id', type=int)

        records = MedicalRecordService.get_patient_history(
            patient_id=patient_id,
            doctor_id=filter_doctor_id,
            department_id=department_id,
            include_doctor_notes=True
        )

        return jsonify({
            'status': 'success',
            'data': {'records': records, 'total': len(records)}
        })
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        logger.error(f"Failed to get patient history: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500


########## PRESCRIPTION ROUTES ##########

@doctor_bp.route('/records/<int:record_id>/prescription', methods=['POST'])
@jwt_required()
@doctor_required
def add_prescription_item(record_id):
    """Add prescription item to a record"""
    try:
        user_id = get_jwt_identity()
        doctor_id = get_doctor_id_from_user(user_id)

        if not doctor_id:
            return jsonify({'status': 'error', 'message': 'Doctor not found'}), 404

        data = PrescriptionItemCreate(**request.get_json())
        
        item = MedicalRecordService.add_prescription_item(
            record_id=record_id,
            doctor_id=doctor_id,
            data=data.model_dump()
        )

        return jsonify({
            'status': 'success',
            'message': 'Prescription item added',
            'data': {'prescription_item': item}
        }), 201
    except ValidationError as e:
        return jsonify({'status': 'error', 'message': 'Validation error', 'errors': e.errors()}), 400
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        logger.error(f"Failed to add prescription item: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500


@doctor_bp.route('/prescription/<int:item_id>', methods=['PUT'])
@jwt_required()
@doctor_required
def update_prescription_item(item_id):
    """Update prescription item"""
    try:
        user_id = get_jwt_identity()
        doctor_id = get_doctor_id_from_user(user_id)

        if not doctor_id:
            return jsonify({'status': 'error', 'message': 'Doctor not found'}), 404

        data = PrescriptionItemUpdate(**request.get_json())
        
        item = MedicalRecordService.update_prescription_item(
            item_id=item_id,
            doctor_id=doctor_id,
            data=data.model_dump(exclude_unset=True)
        )

        return jsonify({
            'status': 'success',
            'message': 'Prescription item updated',
            'data': {'prescription_item': item}
        })
    except ValidationError as e:
        return jsonify({'status': 'error', 'message': 'Validation error', 'errors': e.errors()}), 400
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        logger.error(f"Failed to update prescription item: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500


@doctor_bp.route('/prescription/<int:item_id>', methods=['DELETE'])
@jwt_required()
@doctor_required
def delete_prescription_item(item_id):
    """Delete prescription item"""
    try:
        user_id = get_jwt_identity()
        doctor_id = get_doctor_id_from_user(user_id)

        if not doctor_id:
            return jsonify({'status': 'error', 'message': 'Doctor not found'}), 404

        MedicalRecordService.delete_prescription_item(item_id, doctor_id)

        return jsonify({
            'status': 'success',
            'message': 'Prescription item deleted'
        })
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        logger.error(f"Failed to delete prescription item: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500