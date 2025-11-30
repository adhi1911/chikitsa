from datetime import datetime , time
from typing import Optional, List 
from flask_bcrypt import Bcrypt 
from sqlalchemy.exc import IntegrityError

from ...core.database import db
from ...core.logger import logger
from ...core.auth import admin_required
from ...core.models import User, Doctor, Department, DoctorUnavailability
from .schemas import DepartmentCreate, DepartmentUpdate, DoctorCreate, DoctorUpdate

bcrypt = Bcrypt()

class AdminService:

    ########### DEPARTMENTS #############
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
    def get_departments(include_inactive: bool = False) -> List[dict]:
        """Get all departments with doctor count"""
        query = Department.query
        if not include_inactive:
            query = query.filter_by(is_active=True)

        # Get total doctors in each department
        doctors = db.session.query(
            Doctor.department_id,
            db.func.count(Doctor.id).label('total_doctors')
        ).group_by(Doctor.department_id).all()
        dept_doctor_count = {d.department_id: d.total_doctors for d in doctors}

        # Prepare the result with doctor count
        departments = []
        for dept in query.all():
            departments.append({
                'id': dept.id,
                'name': dept.name,
                'description': dept.description,
                'is_active': dept.is_active,
                'created_at': dept.created_at,
                'updated_at': dept.updated_at,
                'total_doctors': dept_doctor_count.get(dept.id, 0)
            })

        logger.info(f"Fetching departments, include_inactive={include_inactive}")
        return departments
    

    @staticmethod
    @admin_required
    def delete_department(dept_id: int) -> None:
        """ Delete a department """
        try:
            logger.info(f"Deleting department id {dept_id}")
            department = Department.query.get(dept_id)
            if not department:
                logger.error(f"Department deletion failed: Department with id {dept_id} not found")
                raise ValueError("Department not found.")

            db.session.delete(department)
            db.session.commit()
            logger.info(f"Department id {dept_id} deleted successfully")

        except Exception as e:
            logger.error(f"Department deletion failed: {str(e)}", exc_info=True)
            db.session.rollback()
            raise e

    ########### DOCTORS #############

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
        """Update doctor profile, including email in the user table"""
        try:
            logger.info(f"Updating doctor id {doctor_id}")
            doctor = Doctor.query.get(doctor_id)
            if not doctor:
                raise ValueError("Doctor not found")

            # Update fields in the doctor table
            for field, value in data.dict(exclude_unset=True).items():
                if field != "email":  # Skip email for now
                    setattr(doctor, field, value)

            # Update email in the associated user account if provided
            if "email" in data.dict(exclude_unset=True):
                user = User.query.get(doctor.user_id)
                if not user:
                    raise ValueError("Associated user not found")
                user.email = data.email
                user.updated_at = datetime.utcnow()

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


    ########### USERS #############
    @staticmethod
    @admin_required
    def toggle_user_status(user_id: int) -> User:
        """ Activate or deactivate a user account """
        try:
            logger.info(f"Toggling status for user id {user_id} ")
            user = User.query.get(user_id)
            if not user:
                raise ValueError("User not found")

            user.is_active = not user.is_active
            user.updated_at = datetime.utcnow()
            db.session.commit()
            logger.info(f"User id {user_id} status updated to is_active={user.is_active}")
            return {
                'id': user.id,
                'username': user.username,
                'role': user.role,
                'is_active': user.is_active
            }

        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to toggle status for user id {user_id}: {str(e)}", exc_info=True)
            raise e

    # delete user 
    @staticmethod
    @admin_required
    def delete_user(user_id: int) -> None:
        """ Delete a user account """
        try:
            logger.info(f"Deleting user id {user_id} ")
            user = User.query.get(user_id)
            if not user:
                raise ValueError("User not found")

            db.session.delete(user)
            db.session.commit()
            logger.info(f"User id {user_id} deleted successfully")

        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to delete user id {user_id}: {str(e)}", exc_info=True)
            raise e
        
    ########### HOSPITAL HOLIDAYS #############
    @staticmethod
    def create_hospital_holiday(date: str, reason: str) -> dict:
        """
        Create hospital-wide holiday by marking all doctors unavailable.
        """
        # Parse date
        holiday_date = datetime.strptime(date, '%Y-%m-%d').date()
        
        # Get all active doctors
        doctors = Doctor.query.filter_by(is_available=True).all()
        
        if not doctors:
            raise ValueError("No active doctors found")

        logger.info(f"Creating hospital holiday on {date} for {len(doctors)} doctors")

        # Start and end of the day
        start_datetime = datetime.combine(holiday_date, time(0, 0, 0))
        end_datetime = datetime.combine(holiday_date, time(23, 59, 59))

        created_count = 0
        for doctor in doctors:
            # Check if unavailability already exists for this date
            existing = DoctorUnavailability.query.filter(
                DoctorUnavailability.doctor_id == doctor.id,
                DoctorUnavailability.start_datetime <= end_datetime,
                DoctorUnavailability.end_datetime >= start_datetime
            ).first()

            if not existing:
                unavailability = DoctorUnavailability(
                    doctor_id=doctor.id,
                    start_datetime=start_datetime,
                    end_datetime=end_datetime,
                    reason=f"[Hospital Holiday] {reason}"
                )
                db.session.add(unavailability)
                created_count += 1

        db.session.commit()
        
        logger.info(f"Hospital holiday created for {created_count} doctors")
        return {
            'date': date,
            'reason': reason,
            'doctors_affected': created_count
        }

    @staticmethod
    def delete_hospital_holiday(date: str) -> dict:
        """
        Remove hospital-wide holiday by deleting unavailability entries.
        """
        holiday_date = datetime.strptime(date, '%Y-%m-%d').date()
        start_datetime = datetime.combine(holiday_date, time(0, 0, 0))
        end_datetime = datetime.combine(holiday_date, time(23, 59, 59))

        logger.info(f"Removing hospital holiday on {date}")

        # Delete all hospital holiday entries for this date
        deleted = DoctorUnavailability.query.filter(
            DoctorUnavailability.start_datetime == start_datetime,
            DoctorUnavailability.end_datetime == end_datetime,
            DoctorUnavailability.reason.like('[Hospital Holiday]%')
        ).delete(synchronize_session=False)

        db.session.commit()

        logger.info(f"Removed hospital holiday for {deleted} doctors")
        return {
            'date': date,
            'doctors_affected': deleted
        }