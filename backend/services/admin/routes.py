from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from pydantic import ValidationError

from ...core.auth import admin_required
from ...core.logger import logger
from .service import AdminService
from .schemas import DepartmentCreate, DepartmentUpdate, DoctorCreate, DoctorUpdate

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Department Routes
@admin_bp.route('/departments', methods=['POST'])
@jwt_required()
@admin_required
def create_department():
    """Create a new department"""
    try:
        data = DepartmentCreate(**request.get_json())
        department = AdminService.create_department(data)
        return jsonify({
            'status': 'success',
            'message': 'Department created successfully',
            'data': {
                'department': {
                    'id': department.id,
                    'name': department.name,
                    'description': department.description,
                    'is_active': department.is_active,
                    'created_at': str(department.created_at)
                }
            }
        }), 201
    except ValidationError as e:
        logger.error(f"Department creation validation error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Validation error',
            'errors': e.errors()
        }), 400
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Department creation failed: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500

@admin_bp.route('/departments/<int:dept_id>', methods=['PATCH'])
@jwt_required()
@admin_required
def update_department(dept_id):
    """Update an existing department"""
    try:
        data = DepartmentUpdate(**request.get_json())
        department = AdminService.update_department(dept_id, data)
        return jsonify({
            'status': 'success',
            'message': 'Department updated successfully',
            'data': {
                'department': {
                    'id': department.id,
                    'name': department.name,
                    'description': department.description,
                    'is_active': department.is_active,
                    'updated_at': str(department.updated_at)
                }
            }
        })
    except ValidationError as e:
        logger.error(f"Department update validation error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Validation error',
            'errors': e.errors()
        }), 400
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Department update failed: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500

@admin_bp.route('/departments', methods=['GET'])
@jwt_required()
def get_departments():
    """Get all departments"""
    try:
        include_inactive = request.args.get('include_inactive', '').lower() == 'true'
        departments = AdminService.get_departments(include_inactive)
        return jsonify({
            'status': 'success',
            'data': {
                'departments': [{
                    'id': d.id,
                    'name': d.name,
                    'description': d.description,
                    'is_active': d.is_active,
                    'created_at': str(d.created_at),
                    'updated_at': str(d.updated_at) if d.updated_at else None
                } for d in departments]
            }
        })
    except Exception as e:
        logger.error(f"Failed to fetch departments: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500


@admin_bp.route('/departments/<int:dept_id>', methods=['GET'])
@jwt_required()
def get_department(dept_id):
    """Get department by ID"""
    try:
        department = AdminService.get_department(dept_id)
        if not department:
            return jsonify({
                'status': 'error',
                'message': 'Department not found'
            }), 404

        return jsonify({
            'status': 'success',
            'data': {
                'department': {
                    'id': department.id,
                    'name': department.name,
                    'description': department.description,
                    'is_active': department.is_active,
                    'created_at': str(department.created_at),
                    'updated_at': str(department.updated_at) if department.updated_at else None
                }
            }
        })
    except Exception as e:
        logger.error(f"Failed to fetch department id {dept_id}: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500

# Doctor Routes
@admin_bp.route('/doctors', methods=['POST'])
@jwt_required()
@admin_required
def create_doctor():
    """Create a new doctor"""
    try:
        data = DoctorCreate(**request.get_json())

        doctor = AdminService.create_doctor(data)
        return jsonify({
            'status': 'success',
            'message': 'Doctor created successfully',
            'data': {
                'doctor': {
                    'id': doctor.id,
                    'first_name': doctor.first_name,
                    'last_name': doctor.last_name,
                    'email': data.email,
                    'department_id': doctor.department_id,
                    'is_available': doctor.is_available,
                    'created_at': str(doctor.created_at)
                }
            }
        }), 201
    except ValidationError as e:
        logger.error(f"Doctor creation validation error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Validation error',
            'errors': e.errors()
        }), 400
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Doctor creation failed: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500


@admin_bp.route('/doctors/<int:doctor_id>', methods=['PATCH'])
@jwt_required()
@admin_required
def update_doctor(doctor_id):
    """Update an existing doctor"""
    try:
        data = DoctorUpdate(**request.get_json())
        doctor = AdminService.update_doctor(doctor_id, data)
        return jsonify({
            'status': 'success',
            'message': 'Doctor updated successfully',
            'data': {
                'doctor': {
                    'id': doctor.id,
                    'first_name': doctor.first_name,
                    'last_name': doctor.last_name,
                    'email': doctor.email,
                    'department_id': doctor.department_id,
                    'is_available': doctor.is_available,
                    'updated_at': str(doctor.updated_at)
                }
            }
        })
    except ValidationError as e:
        logger.error(f"Doctor update validation error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Validation error',
            'errors': e.errors()
        }), 400
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Doctor update failed: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500

@admin_bp.route('/doctors/<int:doctor_id>', methods=['GET'])
@jwt_required()
def get_doctor(doctor_id):
    """Get doctor by ID"""
    try:
        doctor, department_name, email, user_id = AdminService.get_doctor(doctor_id)
        if not doctor:
            return jsonify({
                'status': 'error',
                'message': 'Doctor not found'
            }), 404

        
        
        return jsonify({
            'status': 'success',
            'data': {
                'doctor': {
                    'user_id': user_id,
                    'first_name': doctor.first_name,
                    'last_name': doctor.last_name,
                    'email': email,
                    'phone': doctor.phone,
                    'department_name': department_name,
                    'specialization': doctor.specialization,
                    'qualification': doctor.qualification,
                    'consultation_fee': doctor.consultation_fee,
                    'is_available': doctor.is_available,
                    'created_at': str(doctor.created_at),
                    'updated_at': str(doctor.updated_at) if doctor.updated_at else None
                }
            }
        })
    except Exception as e:
        logger.error(f"Failed to fetch doctor id {doctor_id}: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500
    
@admin_bp.route('/doctors', methods=['GET'])
@jwt_required()
def get_doctors():
    """Get all doctors, optionally filtered by department and availability"""
    try:
        department_id = request.args.get('department_id', type=int)
        only_available = request.args.get('only_available', '').lower() == 'true'
        docs = AdminService.get_doctors(department_id, only_available)

        doctors = []
        for doc, dept in docs:
            t = {}
            t['first_name'] = doc.first_name
            t['last_name'] = doc.last_name
            t['department_name'] = dept
            t['qualification'] = doc.qualification
            t['specialization'] = doc.specialization
            t['is_available'] = doc.is_available
            t['phone'] = doc.phone

            doctors.append(t)


        return jsonify({
            'status': 'success',
            'data': {
                'doctors': doctors
            }
        })
    except Exception as e:
        logger.error(f"Failed to fetch doctors: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500
