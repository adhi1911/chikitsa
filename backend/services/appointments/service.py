from datetime import datetime, time, date, timedelta
from typing import List, Optional

from ...core.database import db
from ...core.logger import logger
from ...core.models import Doctor, DoctorWorkingHours, DoctorUnavailability, Appointment, Patient

class AppointmentService: 

    SLOT_DURATION = 30  # mins 
    MAX_ADVANCE_DAYS = 30  # days
    MIN_CANCEL_HOURS = 2  # hours

    @staticmethod
    def _parse_time(time_str: str) -> time:
        """Convert time string 'HH:MM' to time object"""
        return datetime.strptime(time_str, '%H:%M').time()
    
    @staticmethod
    def _format_time(t: time) -> str:
        """Convert time object to 'HH:MM' string"""
        if t is None:
            return None
        return t.strftime('%H:%M')
    
    ######## APPOINTMENT SCHEDULING ###########
    @staticmethod
    def get_available_slots(doctor_id: int, appointment_date:date) -> List[dict]: 
        """Get available slot for a doctor on a specific date"""
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            raise ValueError("Doctor not found")
        
        if not doctor.is_available:
            return []
        
        if appointment_date < date.today():
            return []    # cant book past dates
        
        if appointment_date > date.today() + timedelta(days=AppointmentService.MAX_ADVANCE_DAYS):
            return []  # beyond max advance booking
        
        day_of_week = appointment_date.weekday()  # 0=Monday, 6=Sunday

        working_hours = DoctorWorkingHours.query.filter_by(
            doctor_id=doctor_id, day_of_week=day_of_week
        ).first()

        if not working_hours:
            return []  # Doctor does not work on this day
        
        # check for unavailability in working hours 
        start_of_day = datetime.combine(appointment_date, working_hours.start_time)
        end_of_day = datetime.combine(appointment_date, working_hours.end_time)

        unavailability = DoctorUnavailability.query.filter(
            DoctorUnavailability.doctor_id == doctor_id,
            DoctorUnavailability.start_datetime <= start_of_day,
            DoctorUnavailability.end_datetime >= end_of_day,
        ).all()

        # existing appointments
        existing_appointments = Appointment.query.filter(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date == appointment_date,
            Appointment.status.in_(["scheduled", "completed"])
        ).all()

        booked_times = {apt.appointment_time for apt in existing_appointments}

        # generating slots 
        slots = []
        current_time = start_of_day
        end_time = end_of_day

        while current_time < end_time: 
            slot_time = current_time.time()
            slot_end = (current_time + timedelta(minutes=AppointmentService.SLOT_DURATION)).time()

            # check if slot is in past for today 
            is_past = False 
            if appointment_date == date.today(): 
                if slot_time <= datetime.now().time():
                    is_past = True

            # check if already booked 
            is_booked = slot_time in booked_times

            is_available = False 
            slot_datetime = datetime.combine(appointment_date, slot_time)
            for unavail in unavailability:
                if unavail.start_datetime <= slot_datetime < unavail.end_datetime:
                    is_available = False
                    break
            
            is_available = not is_booked and not is_past and not is_available

            slots.append({
                "time": AppointmentService._format_time(slot_time),
                "is_available": is_available,
                'is_past': is_past,
                'is_booked': is_booked
            })

            current_time += timedelta(minutes=AppointmentService.SLOT_DURATION)

        return slots


    @staticmethod 
    def create_appointment(patient_id: int, doctor_id: int, appointment_date:date, appointment_time: str, notes: Optional[str]= None) -> dict:
        """Create a new appointment"""
        patient = Patient.query.get(patient_id)
        if not patient:
            raise ValueError("Patient not found")
        
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            raise ValueError("Doctor not found")
        
        if not doctor.is_available:
            raise ValueError("Doctor is not available for appointments")
    
        apt_time = AppointmentService._parse_time(appointment_time)

        slots = AppointmentService.get_available_slots(doctor_id, appointment_date)
        slot = next((s for s in slots if s['time'] == appointment_time), None)

        if not slot or not slot['is_available']:
            raise ValueError("Selected time slot is not available")
        
        # cross-checking for double booking
        existing_appointment = Appointment.query.filter_by(
            doctor_id=doctor_id,
            appointment_date=appointment_date,
            appointment_time=apt_time,
            status="scheduled"
        ).first()

        if existing_appointment:
            raise ValueError("The selected time slot is already booked")
        
        appointment = Appointment(
            patient_id=patient_id,
            doctor_id=doctor_id,
            appointment_date=appointment_date,
            appointment_time=apt_time,
            status="scheduled",
            booking_notes=notes,
            created_at=datetime.utcnow()
        )

        db.session.add(appointment)
        db.session.commit()

        logger.info(f"Created appointment {appointment.id} for patient {patient_id} with doctor {doctor_id} on {appointment_date} at {appointment_time}")

        return AppointmentService._to_dict(appointment)
    

    ###### GETTERS #########
    @staticmethod 
    def get_by_id(appointment_id: int) -> Optional[dict]:
        """Get appointment by ID"""
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            return None
        return AppointmentService._to_dict(appointment)
    

    @staticmethod
    def get_by_patient(patient_id: int, status: Optional[str] = None, upcoming_only: bool = False) -> List[dict]:
        """Get appointments for a patient"""
        query = Appointment.query.filter(Appointment.patient_id == patient_id)

        if status:
            query = query.filter(Appointment.status == status)

        if upcoming_only:
            query = query.filter(Appointment.appointment_date >= date.today())

        appointments = query.order_by(
            Appointment.appointment_date,
            Appointment.appointment_time
        ).all()

        return [AppointmentService._to_dict(apt) for apt in appointments]
    
    @staticmethod
    def get_by_doctor(doctor_id: int, status: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None, upcoming_only: bool = False) -> List[dict]:
        """Get appointments for a doctor"""
        query = Appointment.query.filter(Appointment.doctor_id == doctor_id)

        if status:
            query = query.filter(Appointment.status == status)

        if start_date:
            query = query.filter(Appointment.appointment_date >= start_date)

        if end_date:
            query = query.filter(Appointment.appointment_date <= end_date)

        if upcoming_only:
            query = query.filter(Appointment.appointment_date >= date.today())

        appointments = query.order_by(
            Appointment.appointment_date,
            Appointment.appointment_time
        ).all()

        return [AppointmentService._to_dict(apt) for apt in appointments]


    @staticmethod
    def get_all(doctor_id: Optional[int] = None, patient_id: Optional[int] = None, status: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[dict]:
        """Get all appointments with filters (admin)"""
        query = Appointment.query

        if doctor_id:
            query = query.filter(Appointment.doctor_id == doctor_id)

        if patient_id:
            query = query.filter(Appointment.patient_id == patient_id)

        if status:
            query = query.filter(Appointment.status == status)

        if start_date:
            query = query.filter(Appointment.appointment_date >= start_date)

        if end_date:
            query = query.filter(Appointment.appointment_date <= end_date)

        appointments = query.order_by(
            Appointment.appointment_date.desc(),
            Appointment.appointment_time
        ).all()

        return [AppointmentService._to_dict(apt) for apt in appointments]


########### UPDATE APPOINTMENT ###########

    @staticmethod
    def reschedule(appointment_id:int, new_date: date, new_time:str) -> dict: 
        """Reschedule an appointment"""
        appointment = Appointment.query.get(appointment_id)
        if not appointment: 
            raise ValueError("Appointment not found")
        
        if appointment.status != "scheduled":
            raise ValueError("Only scheduled appointments can be rescheduled")

        slots = AppointmentService.get_available_slots(appointment.doctor_id, new_date)
        slot = next((s for s in slots if s['time'] == new_time), None)

        if not slot or not slot['is_available']:
            raise ValueError("Selected time slot is not available")
        
        appointment.appointment_date = new_date
        appointment.appointment_time = AppointmentService._parse_time(new_time)
        appointment.updated_at = datetime.utcnow()

        db.session.commit()
        logger.info(f"Rescheduled appointment {appointment_id} to {new_date} at {new_time}")

        return AppointmentService._to_dict(appointment)
    
    @staticmethod
    def update_notes(appointment_id:int, new_notes:str) -> dict:
        """Update appointment notes"""
        appointment = Appointment.query.get(appointment_id)
        if not appointment: 
            raise ValueError("Appointment not found")
        
        appointment.booking_notes = new_notes
        appointment.updated_at = datetime.utcnow()
        db.session.commit()

        logger.info(f"Updated notes for appointment {appointment_id}")
        return AppointmentService._to_dict(appointment)

    @staticmethod
    def update_status(appointment_id:int, new_status:str, reason:Optional[str] = None) -> dict: 
        """Update appointment status"""
        appointment = Appointment.query.get(appointment_id)
        if not appointment: 
            raise ValueError("Appointment not found")
        
        valid_statuses = ["scheduled", "completed", "canceled", "no-show"]
        if new_status not in valid_statuses:
            raise ValueError("Invalid status value")
        
        # check for cancellation
        if new_status == "cancelled" and appointment.status == "scheduled":
            appointment_datetime = datetime.combine(appointment.appointment_date, appointment.appointment_time)
            if appointment_datetime - datetime.utcnow() < timedelta(hours=AppointmentService.MIN_CANCEL_HOURS):
                raise ValueError(f"Appointments can only be cancelled at least {AppointmentService.MIN_CANCEL_HOURS} hours in advance")
        
        # check for completion

        old_status = appointment.status
        appointment.status = new_status

        # save reason if provided 
        if reason:
            appointment.booking_notes = (appointment.booking_notes or '') + f"\nStatus changed to {new_status}: {reason}"
        
        appointment.updated_at = datetime.utcnow()
        db.session.commit()

        logger.info(f"Updated appointment {appointment_id} status from {old_status} to {new_status}")
        return AppointmentService._to_dict(appointment)
    
######## STATS ##########




########## DICT CONVERTER ##########
    @staticmethod
    def _to_dict(apt: Appointment) -> dict:
        """Convert appointment to dictionary"""
        return {
            'id': apt.id,
            'patient_id': apt.patient_id,
            'patient_name': f"{apt.patient.first_name} {apt.patient.last_name}" if apt.patient else 'Unknown',
            'patient_phone': apt.patient.phone if apt.patient else None,
            'doctor_id': apt.doctor_id,
            'doctor_name': f"Dr. {apt.doctor.first_name} {apt.doctor.last_name}" if apt.doctor else 'Unknown',
            'department_name': apt.doctor.department.name if apt.doctor and apt.doctor.department else None,
            'consultation_fee': float(apt.doctor.consultation_fee) if apt.doctor and apt.doctor.consultation_fee else None,
            'appointment_date': apt.appointment_date.isoformat(),
            'appointment_time': apt.appointment_time.strftime('%H:%M'),
            'status': apt.status,
            'booking_notes': apt.booking_notes,
            'created_at': apt.created_at.isoformat() if apt.created_at else None
        }