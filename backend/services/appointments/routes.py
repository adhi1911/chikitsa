from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime

from ...core.cache import cached
from ...core.logger import logger
from .service import AppointmentService

appointment_bp = Blueprint('appointments', __name__, url_prefix='/appointments')


@appointment_bp.route('/slots/<int:doctor_id>', methods=['GET'])
@jwt_required()
@cached('slots', ttl=60) 
def get_available_slots(doctor_id):
    """Get available slots for a doctor on a specific date"""
    try:
        date_str = request.args.get('date')
        if not date_str:
            return jsonify({'status': 'error', 'message': 'Date required (YYYY-MM-DD)'}), 400

        apt_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        slots = AppointmentService.get_available_slots(doctor_id, apt_date)

        return jsonify({
            'status': 'success',
            'data': {'slots': slots}
        })
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        logger.error(f"Failed to get slots: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500