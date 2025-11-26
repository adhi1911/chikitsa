from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from pydantic import ValidationError

from ...core.auth import admin_required
from ...core.logger import logger

from ...auth.schema import RegisterPatient

from .service import AdminService
from .schemas import DepartmentCreate, DepartmentUpdate, DoctorCreate, DoctorUpdate

from ..patients.service import PatientService
from ..patients.schemas import PatientUpdate

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

##### DEPARTMENT ROUTES #####
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



##### DOCTOR ROUTES #####
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
                    'department_id': doctor.department_id,
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
            doctor_data = {
                'id': doc.id,
                'first_name': doc.first_name,
                'last_name': doc.last_name,
                'department_id': doc.department_id,
                'department_name': dept,
                'qualification': doc.qualification,
                'specialization': doc.specialization,
                'is_available': doc.is_available,
                'phone': doc.phone,
                'consultation_fee': float(doc.consultation_fee),
                'experience_years': doc.experience_years
            }
            doctors.append(doctor_data)



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
    

##### PATIENT ROUTES #####

# get all patients
@admin_bp.route('/patients', methods=['GET'])
@jwt_required()
@admin_required
def get_patients():
    """Get all patients"""
    try:
        include_inactive = request.args.get('include_inactive', '').lower() == 'true'
        patients = PatientService.get_patients(include_inactive)
        return jsonify({
            'status': 'success',
            'data': {'patients': patients}
        })
    except Exception as e:
        logger.error(f"Failed to fetch patients: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500
    
# get patient by patient_id
@admin_bp.route('/patients/<int:patient_id>', methods=['GET'])
@jwt_required()
@admin_required
def get_patient(patient_id):
    """Get patient by ID"""
    try:
        patient = PatientService.get_patient(patient_id)
        if not patient:
            return jsonify({'status': 'error', 'message': 'Patient not found'}), 404
        return jsonify({
            'status': 'success',
            'data': {'patient': patient}
        })
    except Exception as e:
        logger.error(f"Failed to fetch patient {patient_id}: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500


# admin create patient
@admin_bp.route('/patients', methods=['POST'])
@jwt_required()
@admin_required
def create_patient():
    """Create a new patient"""
    try:
        data = RegisterPatient(**request.get_json())
        patient = PatientService.create_patient(data)
        return jsonify({
            'status': 'success',
            'message': 'Patient created successfully',
            'data': {'patient': patient}
        }), 201
    except ValidationError as e:
        return jsonify({'status': 'error', 'message': 'Validation error', 'errors': e.errors()}), 400
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        logger.error(f"Patient creation failed: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500


# admin update patient by patient_id
@admin_bp.route('/patients/<int:patient_id>', methods=['PATCH'])
@jwt_required()
@admin_required
def update_patient(patient_id):
    """Update patient profile"""
    try:
        data = PatientUpdate(**request.get_json())
        patient = PatientService.update_patient(patient_id, data.model_dump(exclude_unset=True))
        return jsonify({
            'status': 'success',
            'message': 'Patient updated successfully',
            'data': {'patient': patient}
        })
    except ValidationError as e:
        return jsonify({'status': 'error', 'message': 'Validation error', 'errors': e.errors()}), 400
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        logger.error(f"Patient update failed: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500




####### USER MANAGEMENT ROUTES #######
@admin_bp.route('/users/<int:user_id>/status', methods=['PATCH'])
@jwt_required()
@admin_required
def toggle_user_status(user_id):
    """Blacklist or activate a user

        blacklist: soft-delete - set is_active to False
        activate: set is_active to True 
    """
    try:    
        result = AdminService.toggle_user_status(user_id)
        action = 'activated' if result['is_active'] else 'blacklisted'
        return jsonify({
            'status': 'success',
            'message': f'User {action} successfully',
            'data': result
        })
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        logger.error(f"Failed to toggle user status: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500


# delete a user
@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_user(user_id):
    """Delete a user (doctor or patient)"""
    try:
        AdminService.delete_user(user_id)
        return jsonify({'status': 'success', 'message': 'User deleted successfully'})
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        logger.error(f"Failed to delete user: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500