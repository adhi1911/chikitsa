from datetime import datetime 
from typing import Optional, List 
from flask_bcrypt import Bcrypt 
from sqlalchemy.exc import IntegrityError

from ...core.database import db
from ...core.logger import logger
from ...core.auth import admin_required
from ...core.models import User, Doctor, Department
from .schemas import DepartmentCreate, DepartmentUpdate, DoctorCreate, DoctorUpdate

bcrypt = Bcrypt()

class AdminService:

    @staticmethod 
    @admin_required
    def create_department(data: DepartmentCreate) -> Department: 
        """ Crete a new department"""
        try: 
            logger.info(f"Creating new department: {data.name}")
            department = Department(
                name = data.name,
                description = data.description,
                is_active = True,
                created_at = datetime.utcnow()
            )

            db.session.add(department)
            db.session.commit()
            logger.info(f"Department created successfully with id: {department.id}")
            return department
        
        except IntegrityError:
            logger.error(f"Department creation failed: Name '{data.name}' already exists")
            db.session.rollback()
            raise ValueError("Department with this name already exists.")
        
        except Exception as e:
            logger.error(f"Department creation failed: {str(e)}", exc_info=True)
            db.session.rollback()
            raise e
        
    @staticmethod 
    @admin_required
    def update_department(dept_id: int, data: DepartmentUpdate) -> Department:
        """ Update an existing department """
        try:
            department = Department.query.get(dept_id)
            if not department:
                logger.error(f"Department update failed: Department with id {dept_id} not found")
                raise ValueError("Department not found.")

            logger.info(f"Updating department id {dept_id}")

            for field, value in data.dict(exclude_unset=True).items():
                setattr(department, field, value)
            department.updated_at = datetime.utcnow()

            db.session.commit()
            logger.info(f"Department id {dept_id} updated successfully")
            return department
        
        except Exception as e:
            logger.error(f"Department update failed: {str(e)}", exc_info=True)
            db.session.rollback()
            raise e
        
    @staticmethod
    def get_department(dept_id: int) -> Optional[Department]:
        """ Get department by ID """
        department = Department.query.get(dept_id)
        if not department:
            logger.warning(f"Department with id {dept_id} not found")
        return department
    
    @staticmethod
    def get_departments(include_inactive: bool = False) -> List[Department]:
        """Get all departments"""
        query = Department.query
        if not include_inactive:
            query = query.filter_by(is_active=True)

        logger.info(f"Fetching departments, include_inactive={include_inactive}")
        return query.all()
    

    ## Doctors 

    @staticmethod
    @admin_required
    def create_doctor(data: DoctorCreate) -> Doctor:
        """ Create a new doctor with user account"""
        try:
            # check if dept exists
            dept = AdminService.get_department(data.department_id) if data.department_id else None
            if data.department_id and not dept:
                logger.error(f"Doctor creation failed: Department with id {data.department_id} not found")
                raise ValueError("Department not found.")
            
            logger.info(f"Creating new doctor: {data.first_name} {data.last_name}, email: {data.email}")

            # create user account
            hashed_password = bcrypt.generate_password_hash(data.password).decode('utf-8')
            user = User(
                username = data.username,
                email = data.email,
                password_hash = hashed_password,
                role = 'doctor',
                is_active = True,
                created_at = datetime.utcnow()
            )
            db.session.add(user)
            db.session.flush()  # to get user.id

            # create doctor profile

            doctor = Doctor(
                user_id=user.id,
                first_name=data.first_name,
                last_name=data.last_name,
                phone=data.phone,
                department_id=data.department_id,
                specialization=data.specialization,
                qualification=data.qualification,
                experience_years=data.experience_years,
                consultation_fee=data.consultation_fee,
                is_available=True,
                created_at=datetime.utcnow()
            )


            db.session.add(doctor)
            db.session.commit()
            logger.info(f"Doctor created successfully with id: {doctor.id}")

            return doctor

        except IntegrityError as ie:
            logger.error(f"Doctor creation failed: {str(ie)}", exc_info=True)
            db.session.rollback()
            if 'username' in str(ie):
                raise ValueError("Username already exists.")
            elif 'email' in str(ie):
                raise ValueError("Email already exists.")
            else:
                raise ValueError("Integrity error occurred.")
        
        except Exception as e:
            logger.error(f"Doctor creation failed: {str(e)}", exc_info=True)
            db.session.rollback()
            raise e


    @staticmethod
    @admin_required
    def update_doctor(doctor_id: int, data: DoctorUpdate) -> Doctor:
        """Update doctor profile"""
        try:
            logger.info(f"Updating doctor id {doctor_id}")
            doctor = Doctor.query.get(doctor_id)
            if not doctor:
                raise ValueError("Doctor not found")

            # Update fields from data
            for field, value in data.dict(exclude_unset=True).items():
                setattr(doctor, field, value)

            doctor.updated_at = datetime.utcnow()
            db.session.commit()
            logger.info(f"Doctor id {doctor_id} updated successfully")
            return doctor

        except IntegrityError as e:
            db.session.rollback()
            logger.error(f"Doctor update failed: {str(e)}", exc_info=True)
            if 'email' in str(e):
                raise ValueError("Email already registered")
            raise e
        except Exception as e:
            db.session.rollback()
            logger.error(f"Doctor update failed: {str(e)}", exc_info=True)
            raise e
        
    @staticmethod
    def get_doctor(doctor_id: int) -> Optional[Doctor]:
        """ Get doctor by ID """
        doctor = Doctor.query.join(Department).join(User).add_columns(
            Department.name.label('department_name'),
            User.email.label('user_email'),
            User.id.label('user_id')
        ).filter(Doctor.id == doctor_id).first()
        if not doctor:
            logger.warning(f"Doctor with id {doctor_id} not found")
        return doctor
    
    @staticmethod
    def get_doctors(department_id: Optional[int] = None, only_available: bool = False) -> List[Doctor]:
        """ Get list of doctors, optionally filtered by department and availability """
        query = Doctor.query.join(Department).add_columns(Department.name.label('department_name'))
        if department_id:
            query = query.filter_by(department_id=department_id)
        if only_available:
            query = query.filter(Doctor.is_available == True)

        logger.info(f"Fetched doctors, department_id={department_id}, only_available={only_available}")
        return query.all()
        

    @staticmethod 
    @admin_required
    def toggle_doctor_availability(doctor_id: int, is_available: bool) -> Doctor:
        """ Toggle doctor's availability status """
        try:
            logger.info(f"Toggling availability for doctor id {doctor_id} to {is_available}")
            doctor = Doctor.query.get(doctor_id)
            if not doctor:
                raise ValueError("Doctor not found")

            doctor.is_available = is_available
            doctor.updated_at = datetime.utcnow()
            db.session.commit()
            logger.info(f"Doctor id {doctor_id} availability updated to {is_available}")
            return doctor

        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to toggle availability for doctor id {doctor_id}: {str(e)}", exc_info=True)