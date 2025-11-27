from flask import Blueprint, request, jsonify 
from flask_jwt_extended import jwt_required, get_jwt_identity
from pydantic import ValidationError

from ...core.logger import logger
from ...core.auth import doctor_required

from .service import DoctorService
from ..appointments.service import AppointmentService
from .schemas import UnavailabilityCreate, UnavailabilityUpdate
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