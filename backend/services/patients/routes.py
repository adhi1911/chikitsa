from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from pydantic import ValidationError

from ...core.logger import logger
from ...core.auth import patient_required
from ...core.models import Patient
from ..appointments.service import AppointmentService
from ..appointments.schemas import AppointmentCreate, AppointmentUpdate

patient_bp = Blueprint('patients', __name__, url_prefix='/patient')


def get_patient_id_from_user(user_id: int) -> int:
    """Get patient ID from user ID"""
    patient = Patient.query.filter_by(user_id=user_id).first()
    return patient.id if patient else None


######### APPOINTMENT ROUTES #########

# get all appointments
@patient_bp.route('/appointments', methods=['GET'])
@jwt_required()
@patient_required
def get_my_appointments():
    """Get patient's appointments"""
    try:
        user_id = get_jwt_identity()
        patient_id = get_patient_id_from_user(user_id)

        if not patient_id:
            return jsonify({'status': 'error', 'message': 'Patient not found'}), 404

        status = request.args.get('status')
        upcoming = request.args.get('upcoming', 'false').lower() == 'true'

        appointments = AppointmentService.get_by_patient(patient_id, status, upcoming)

        return jsonify({
            'status': 'success',
            'data': {'appointments': appointments}
        })
    except Exception as e:
        logger.error(f"Failed to get appointments: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500
    

# book an appointment
@patient_bp.route('/appointments', methods=['POST'])
@jwt_required()
@patient_required
def book_appointment():
    """Book a new appointment"""
    try:
        user_id = get_jwt_identity()
        patient_id = get_patient_id_from_user(user_id)

        if not patient_id:
            return jsonify({'status': 'error', 'message': 'Patient not found'}), 404

        data = AppointmentCreate(**request.get_json())

        appointment = AppointmentService.create_appointment(
            patient_id=patient_id,
            doctor_id=data.doctor_id,
            appointment_date=data.appointment_date,
            appointment_time=data.appointment_time,
            notes=data.booking_notes
        )

        return jsonify({
            'status': 'success',
            'message': 'Appointment booked successfully',
            'data': {'appointment': appointment}
        }), 201
    except ValidationError as e:
        return jsonify({'status': 'error', 'message': 'Validation error', 'errors': e.errors()}), 400
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        logger.error(f"Failed to book appointment: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500



# get specific appointment
@patient_bp.route('/appointments/<int:appointment_id>', methods=['GET'])
@jwt_required()
@patient_required
def get_appointment(appointment_id):
    """Get specific appointment"""
    try:
        user_id = get_jwt_identity()
        patient_id = get_patient_id_from_user(user_id)

        appointment = AppointmentService.get_by_id(appointment_id)

        if not appointment:
            return jsonify({'status': 'error', 'message': 'Appointment not found'}), 404

        if appointment['patient_id'] != patient_id:
            return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403

        return jsonify({
            'status': 'success',
            'data': {'appointment': appointment}
        })
    except Exception as e:
        logger.error(f"Failed to get appointment: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500
    

# reschedule a booked appointment
@patient_bp.route('/appointments/<int:appointment_id>/reschedule', methods=['PUT'])
@jwt_required()
@patient_required
def reschedule_appointment(appointment_id):
    """Reschedule an appointment"""
    try:
        user_id = get_jwt_identity()
        patient_id = get_patient_id_from_user(user_id)

        existing = AppointmentService.get_by_id(appointment_id)

        if not existing:
            return jsonify({'status': 'error', 'message': 'Appointment not found'}), 404

        if existing['patient_id'] != patient_id:
            return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403

        data = request.get_json()
        new_date = data.get('appointment_date')
        new_time = data.get('appointment_time')

        if not new_date or not new_time:
            return jsonify({'status': 'error', 'message': 'Date and time required'}), 400

        from datetime import datetime
        new_date = datetime.strptime(new_date, '%Y-%m-%d').date()

        appointment = AppointmentService.reschedule(appointment_id, new_date, new_time)

        return jsonify({
            'status': 'success',
            'message': 'Appointment rescheduled',
            'data': {'appointment': appointment}
        })
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        logger.error(f"Failed to reschedule: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500
    

#update booking notes 
@patient_bp.route('/appointments/<int:appointment_id>/notes', methods=['PUT'])
@jwt_required()
@patient_required
def update_booking_notes(appointment_id):
    """Update booking notes for an appointment"""
    try:
        user_id = get_jwt_identity()
        patient_id = get_patient_id_from_user(user_id)

        existing = AppointmentService.get_by_id(appointment_id)

        if not existing:
            return jsonify({'status': 'error', 'message': 'Appointment not found'}), 404

        if existing['patient_id'] != patient_id:
            return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403

        data = request.get_json()
        new_notes = data.get('booking_notes')

        if new_notes is None:
            return jsonify({'status': 'error', 'message': 'Booking notes required'}), 400

        appointment = AppointmentService.update_notes(appointment_id, new_notes)

        return jsonify({
            'status': 'success',
            'message': 'Booking notes updated',
            'data': {'appointment': appointment}
        })
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        logger.error(f"Failed to update notes: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

# cancel scheduled appointment 
@patient_bp.route('/appointments/<int:appointment_id>/cancel', methods=['POST'])
@jwt_required()
@patient_required
def cancel_appointment(appointment_id):
    """Cancel an appointment"""
    try:
        user_id = get_jwt_identity()
        patient_id = get_patient_id_from_user(user_id)

        existing = AppointmentService.get_by_id(appointment_id)

        if not existing:
            return jsonify({'status': 'error', 'message': 'Appointment not found'}), 404

        if existing['patient_id'] != patient_id:
            return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403

        data = request.get_json() or {}
        reason = data.get('reason')

        appointment = AppointmentService.update_status(appointment_id, 'cancelled', reason)

        return jsonify({
            'status': 'success',
            'message': 'Appointment cancelled',
            'data': {'appointment': appointment}
        })
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        logger.error(f"Failed to cancel: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500