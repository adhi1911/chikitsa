from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from pydantic import ValidationError

from ...core.models import MedicalRecord
from ...core.auth import admin_required
from ...core.logger import logger

from ...auth.schema import RegisterPatient

from .service import AdminService
from .schemas import DepartmentCreate, DepartmentUpdate, DoctorCreate, DoctorUpdate

from ..patients.service import PatientService
from ..patients.schemas import PatientUpdate

from ..doctors.service import DoctorService
from ..doctors.schemas import WorkingHoursCreate, WorkingHoursDayUpdate, WorkingHoursBulkUpdate, UnavailabilityCreate, UnavailabilityUpdate

from ..appointments.service import AppointmentService
from ..appointments.schemas import AppointmentCreate, AppointmentUpdate

from ..medical_records.service import MedicalRecordService

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


###### DASHBOARD ROUTES ######

@admin_bp.route('/dashboard/stats', methods=['GET'])
@jwt_required()
@admin_required
def get_dashboard_stats():
    """Get admin dashboard statistics"""
    try:
        from ...core.models import User, Patient, Doctor, Department, Appointment
        from datetime import date, timedelta
        from sqlalchemy import func

        today = date.today()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)

        stats = {
            'users': {
                'total_patients': Patient.query.count(),
                'total_doctors': Doctor.query.count(),
                'active_users': User.query.filter_by(is_active=True).count()
            },
            'departments': {
                'total': Department.query.count(),
                'active': Department.query.filter_by(is_active=True).count()
            },
            'appointments': {
                'total': Appointment.query.count(),
                'today': Appointment.query.filter(Appointment.appointment_date == today).count(),
                'this_week': Appointment.query.filter(Appointment.appointment_date >= week_ago).count(),
                'scheduled': Appointment.query.filter_by(status='scheduled').count(),
                'completed': Appointment.query.filter_by(status='completed').count(),
                'cancelled': Appointment.query.filter_by(status='cancelled').count()
            },
            'medical_records': {
                'total': MedicalRecord.query.count(),
                'this_month': MedicalRecord.query.filter(MedicalRecord.created_at >= month_ago).count()
            }
        }

        return jsonify({
            'status': 'success',
            'data': {'stats': stats}
        })
    except Exception as e:
        logger.error(f"Failed to get dashboard stats: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500


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
                    'id': d['id'],
                    'name': d['name'],
                    'description': d['description'],
                    'is_active': d['is_active'],
                    'created_at': d['created_at'],
                    'updated_at': d['updated_at'] if d['updated_at'] else None,
                    'total_doctors': d['total_doctors']
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

@admin_bp.route('/departments/<int:dept_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_department(dept_id):
    """Delete a department"""
    try:
        AdminService.delete_department(dept_id)
        return jsonify({
            'status': 'success',
            'message': 'Department deleted successfully'
        })
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Department deletion failed: {str(e)}", exc_info=True)
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
    

###### DOCTOR WORKING HOURS & UNAVAILABILITY ROUTES ######
@admin_bp.route('/doctors/<int:doctor_id>/working-hours', methods=['GET'])
@jwt_required()
@admin_required
def get_working_hours(doctor_id):
    """Get doctor's working hours"""
    try:
        hours = DoctorService.get_working_hours(doctor_id)
        return jsonify({
            'status': 'success',
            'data': {'working_hours': hours}
        })
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 404
    except Exception as e:
        logger.error(f"Failed to get working hours: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500


@admin_bp.route('/doctors/<int:doctor_id>/working-hours', methods=['POST'])
@jwt_required()
@admin_required
def create_working_hours(doctor_id):
    """Create working hours for entire week"""
    try:
        data = WorkingHoursCreate(**request.get_json())
        hours = DoctorService.create_working_hours(
            doctor_id, 
            [day.model_dump() for day in data.schedule]
        )
        return jsonify({
            'status': 'success',
            'message': 'Working hours created successfully',
            'data': {'working_hours': hours}
        }), 201
    except ValidationError as e:
        errors = []
        for error in e.errors():
            errors.append({
                'loc': list(error.get('loc', [])),
                'msg': str(error.get('msg', '')),
                'type': error.get('type', '')
            })
        return jsonify({'status': 'error', 'message': 'Validation error', 'errors': errors}), 400
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        logger.error(f"Failed to create working hours: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500


@admin_bp.route('/doctors/<int:doctor_id>/working-hours', methods=['PUT'])
@jwt_required()
@admin_required
def bulk_update_working_hours(doctor_id):
    """Bulk update entire week schedule"""
    try:
        data = WorkingHoursBulkUpdate(**request.get_json())
        hours = DoctorService.bulk_update_working_hours(
            doctor_id,
            [day.model_dump() for day in data.schedule]
        )
        return jsonify({
            'status': 'success',
            'message': 'Working hours updated successfully',
            'data': {'working_hours': hours}
        })
    except ValidationError as e:
        return jsonify({'status': 'error', 'message': 'Validation error', 'errors': e.errors()}), 400
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        logger.error(f"Failed to update working hours: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500


@admin_bp.route('/doctors/<int:doctor_id>/working-hours/<int:day>', methods=['PATCH'])
@jwt_required()
@admin_required
def update_working_hours_day(doctor_id, day):
    """Update working hours for a specific day"""
    try:
        data = WorkingHoursDayUpdate(**request.get_json())
        hours = DoctorService.update_working_hours_day(
            doctor_id,
            day,
            data.model_dump(exclude_unset=True)
        )
        return jsonify({
            'status': 'success',
            'message': 'Working hours updated successfully',
            'data': {'working_hours': hours}
        })
    except ValidationError as e:
        return jsonify({'status': 'error', 'message': 'Validation error', 'errors': e.errors()}), 400
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        logger.error(f"Failed to update working hours: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500


@admin_bp.route('/doctors/<int:doctor_id>/working-hours', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_working_hours(doctor_id):
    """Delete all working hours for a doctor"""
    try:
        DoctorService.delete_working_hours(doctor_id)
        return jsonify({
            'status': 'success',
            'message': 'Working hours deleted successfully'
        })
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        logger.error(f"Failed to delete working hours: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500


@admin_bp.route('/doctors/<int:doctor_id>/unavailability', methods=['GET'])
@jwt_required()
@admin_required
def get_unavailability(doctor_id):
    """Get doctor's unavailability periods (view only)"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        unavailability = DoctorService.get_unavailability(doctor_id, start_date, end_date)
        return jsonify({
            'status': 'success',
            'data': {'unavailability': unavailability}
        })
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 404
    except Exception as e:
        logger.error(f"Failed to get unavailability: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500


@admin_bp.route('/hospital-holiday', methods=['POST'])
@jwt_required()
@admin_required
def create_hospital_holiday():
    """Mark all doctors unavailable for a date"""
    try:
        data = request.get_json()
        date = data.get('date')
        reason = data.get('reason', 'Hospital Holiday')

        if not date:
            return jsonify({'status': 'error', 'message': 'date is required'}), 400

        result = AdminService.create_hospital_holiday(date, reason)
        return jsonify({
            'status': 'success',
            'message': f'Hospital holiday created for {result["doctors_affected"]} doctors',
            'data': result
        }), 201
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        logger.error(f"Failed to create hospital holiday: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500


@admin_bp.route('/hospital-holiday', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_hospital_holiday():
    """Remove hospital holiday for a date"""
    try:
        date = request.args.get('date')

        if not date:
            return jsonify({'status': 'error', 'message': 'date query param required'}), 400

        result = AdminService.delete_hospital_holiday(date)
        return jsonify({
            'status': 'success',
            'message': f'Hospital holiday removed for {result["doctors_affected"]} doctors',
            'data': result
        })
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        logger.error(f"Failed to delete hospital holiday: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500
    

######### APPPOINTMENT ROUTES #########

# get all appointments 
@admin_bp.route('/appointments', methods=['GET'])
@jwt_required()
@admin_required
def get_all_appointments():
    """Get all appointments"""
    try:
        appointments = AppointmentService.get_all(
            doctor_id=request.args.get('doctor_id', type=int),
            patient_id=request.args.get('patient_id', type=int),
            status=request.args.get('status'),
            start_date=request.args.get('start_date'),
            end_date=request.args.get('end_date')
        )

        return jsonify({
            'status': 'success',
            'data': {'appointments': appointments, 'total': len(appointments)}
        })
    except Exception as e:
        logger.error(f"Failed to get appointments: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500
    

@admin_bp.route('/appointments/<int:appointment_id>', methods=['GET'])
@jwt_required()
@admin_required
def get_appointment(appointment_id):
    """Get specific appointment"""
    try:
        appointment = AppointmentService.get_by_id(appointment_id)

        if not appointment:
            return jsonify({'status': 'error', 'message': 'Appointment not found'}), 404

        return jsonify({
            'status': 'success',
            'data': {'appointment': appointment}
        })
    except Exception as e:
        logger.error(f"Failed to get appointment: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500
    


@admin_bp.route('/appointments/<int:appointment_id>/status', methods=['PATCH'])
@jwt_required()
@admin_required
def update_appointment_status(appointment_id):
    """Update appointment status"""
    try:
        data = request.get_json()
        new_status = data.get('status')
        reason = data.get('reason')

        appointment = AppointmentService.update_status(appointment_id, new_status, reason)

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
    
########## MEDICAL RECORD ROUTES ##########

@admin_bp.route('/records', methods=['GET'])
@jwt_required()
@admin_required
def get_all_records():
    """Get all medical records with filters"""
    try:
        records = MedicalRecordService.get_all(
            patient_id=request.args.get('patient_id', type=int),
            doctor_id=request.args.get('doctor_id', type=int),
            department_id=request.args.get('department_id', type=int),
            start_date=request.args.get('start_date'),
            end_date=request.args.get('end_date')
        )

        return jsonify({
            'status': 'success',
            'data': {'records': records, 'total': len(records)}
        })
    except Exception as e:
        logger.error(f"Failed to get records: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500


@admin_bp.route('/records/<int:record_id>', methods=['GET'])
@jwt_required()
@admin_required
def get_record(record_id):
    """Get specific medical record"""
    try:
        record = MedicalRecordService.get_by_id(record_id, include_doctor_notes=True)

        if not record:
            return jsonify({'status': 'error', 'message': 'Medical record not found'}), 404

        return jsonify({
            'status': 'success',
            'data': {'record': record}
        })
    except Exception as e:
        logger.error(f"Failed to get record: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500


@admin_bp.route('/patients/<int:patient_id>/history', methods=['GET'])
@jwt_required()
@admin_required
def get_patient_full_history(patient_id):
    """Get patient's complete medical history"""
    try:
        doctor_id = request.args.get('doctor_id', type=int)
        department_id = request.args.get('department_id', type=int)

        records = MedicalRecordService.get_patient_history(
            patient_id=patient_id,
            doctor_id=doctor_id,
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


@admin_bp.route('/departments/<int:department_id>/records', methods=['GET'])
@jwt_required()
@admin_required
def get_department_records(department_id):
    """Get all records from a department"""
    try:
        records = MedicalRecordService.get_by_department(
            department_id=department_id,
            patient_id=request.args.get('patient_id', type=int),
            start_date=request.args.get('start_date'),
            end_date=request.args.get('end_date')
        )

        return jsonify({
            'status': 'success',
            'data': {'records': records, 'total': len(records)}
        })
    except Exception as e:
        logger.error(f"Failed to get department records: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500