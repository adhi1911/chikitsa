from datetime import datetime, time, timedelta, date
from typing import Optional, List

from ...core.database import db
from ...core.logger import logger
from ...core.models import Appointment, Doctor, DoctorWorkingHours, DoctorUnavailability

DAY_NAMES = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday"
}


class DoctorService:

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


    @staticmethod
    def get_working_hours(doctor_id: int) -> List[dict]:
        """Get all working hours for a doctor"""
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            raise ValueError("Doctor not found")

        hours = DoctorWorkingHours.query.filter_by(doctor_id=doctor_id).order_by(
            DoctorWorkingHours.day_of_week
        ).all()

        return [DoctorService._working_hours_to_dict(h) for h in hours]

    @staticmethod
    def create_working_hours(doctor_id: int, schedule: List[dict]) -> List[dict]:
        """Create working hours for entire week"""
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            raise ValueError("Doctor not found")

        # check for existing working hours
        existing = DoctorWorkingHours.query.filter_by(doctor_id=doctor_id).first()
        if existing:
            raise ValueError("Working hours already exist. Use update instead.")

        logger.info(f"Creating working hours for doctor {doctor_id}")

        created = []
        for day in schedule:
            hours = DoctorWorkingHours(
                doctor_id=doctor_id,
                day_of_week=day['day_of_week'],
                start_time=DoctorService._parse_time(day['start_time']),
                end_time=DoctorService._parse_time(day['end_time']),
            )
            db.session.add(hours)
            created.append(hours)

        db.session.commit()
        logger.info(f"Created {len(created)} working hour entries for doctor {doctor_id}")

        return [DoctorService._working_hours_to_dict(h) for h in created]

    @staticmethod
    def update_working_hours_day(doctor_id: int, day_of_week: int, data: dict) -> dict:
        """Update working hours for a specific day"""
        hours = DoctorWorkingHours.query.filter_by(
            doctor_id=doctor_id,
            day_of_week=day_of_week
        ).first()

        if not hours:
            raise ValueError(f"Working hours not found for day {day_of_week}")

        logger.info(f"Updating working hours for doctor {doctor_id}, day {day_of_week}")

        if 'start_time' in data:
            hours.start_time = DoctorService._parse_time(data['start_time'])
        if 'end_time' in data:
            hours.end_time = DoctorService._parse_time(data['end_time'])

        db.session.commit()
        return DoctorService._working_hours_to_dict(hours)

    @staticmethod
    def bulk_update_working_hours(doctor_id: int, schedule: List[dict]) -> List[dict]:
        """Replace entire week schedule"""
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            raise ValueError("Doctor not found")

        logger.info(f"Bulk updating working hours for doctor {doctor_id}")

        # Delete existing
        DoctorWorkingHours.query.filter_by(doctor_id=doctor_id).delete()

        # Create new
        created = []
        for day in schedule:
            hours = DoctorWorkingHours(
                doctor_id=doctor_id,
                day_of_week=day['day_of_week'],
                start_time=DoctorService._parse_time(day['start_time']),
                end_time=DoctorService._parse_time(day['end_time']),
            )
            db.session.add(hours)
            created.append(hours)

        db.session.commit()
        logger.info(f"Bulk updated {len(created)} working hour entries for doctor {doctor_id}")

        return [DoctorService._working_hours_to_dict(h) for h in created]

    @staticmethod
    def delete_working_hours(doctor_id: int) -> bool:
        """Delete all working hours for a doctor"""
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            raise ValueError("Doctor not found")

        deleted = DoctorWorkingHours.query.filter_by(doctor_id=doctor_id).delete()
        db.session.commit()

        logger.info(f"Deleted {deleted} working hour entries for doctor {doctor_id}")
        return True

    ########### UNAVAILABILITY ###########

    @staticmethod
    def get_unavailability(doctor_id: int, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[dict]:
        """Get unavailability periods for a doctor"""
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            raise ValueError("Doctor not found")

        query = DoctorUnavailability.query.filter_by(doctor_id=doctor_id)

        # Filter by date range if provided
        if start_date:
            query = query.filter(DoctorUnavailability.end_datetime >= start_date)
        if end_date:
            query = query.filter(DoctorUnavailability.start_datetime <= end_date)

        unavailability = query.order_by(DoctorUnavailability.start_datetime).all()

        return [DoctorService._unavailability_to_dict(u) for u in unavailability]

    @staticmethod
    def create_unavailability(doctor_id: int, data: dict) -> dict:
        """Create unavailability period"""
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            raise ValueError("Doctor not found")

        logger.info(f"Creating unavailability for doctor {doctor_id}")

        unavailability = DoctorUnavailability(
            doctor_id=doctor_id,
            start_datetime=data['start_datetime'],
            end_datetime=data['end_datetime'],
            reason=data.get('reason')
        )

        db.session.add(unavailability)
        db.session.commit()

        logger.info(f"Created unavailability {unavailability.id} for doctor {doctor_id}")
        return DoctorService._unavailability_to_dict(unavailability)

    @staticmethod
    def update_unavailability(unavail_id: int, data: dict) -> dict:
        """Update unavailability period"""
        unavailability = DoctorUnavailability.query.get(unavail_id)
        if not unavailability:
            raise ValueError("Unavailability not found")

        logger.info(f"Updating unavailability {unavail_id}")

        if 'start_datetime' in data:
            unavailability.start_datetime = data['start_datetime']
        if 'end_datetime' in data:
            unavailability.end_datetime = data['end_datetime']
        if 'reason' in data:
            unavailability.reason = data['reason']

        db.session.commit()
        return DoctorService._unavailability_to_dict(unavailability)

    @staticmethod
    def delete_unavailability(unavail_id: int) -> bool:
        """Delete unavailability period"""
        unavailability = DoctorUnavailability.query.get(unavail_id)
        if not unavailability:
            raise ValueError("Unavailability not found")

        logger.info(f"Deleting unavailability {unavail_id}")

        db.session.delete(unavailability)
        db.session.commit()
        return True


    ########## CALENDER INTEGRATION ##########
    @staticmethod 
    def get_calendar(doctor_id: int, start_date: Optional[str] = None, end_date: Optional[str] = None) -> dict:
        """
        Get doctor's calendar view with working hours, unavailability, and appointments.
        Returns a month view by default.
        """
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            raise ValueError("Doctor not found")

        # Default to current month if no dates provided
        today = date.today()
        if start_date:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
        else:
            start = today.replace(day=1)  # First day of current month

        if end_date:
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
        else:
            # Last day of current month
            next_month = start.replace(day=28) + timedelta(days=4)
            end = next_month - timedelta(days=next_month.day)

        # Get working hours (indexed by day_of_week)
        working_hours = DoctorWorkingHours.query.filter_by(doctor_id=doctor_id).all()
        working_hours_map = {wh.day_of_week: wh for wh in working_hours}

        # Get unavailability periods in date range
        unavailability = DoctorUnavailability.query.filter(
            DoctorUnavailability.doctor_id == doctor_id,
            DoctorUnavailability.start_datetime <= datetime.combine(end, time.max),
            DoctorUnavailability.end_datetime >= datetime.combine(start, time.min)
        ).all()

        # Get appointments in date range
        appointments = Appointment.query.filter(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date >= start,
            Appointment.appointment_date <= end
        ).all()

        # Group appointments by date
        appointments_by_date = {}
        for apt in appointments:
            date_key = apt.appointment_date.isoformat()
            if date_key not in appointments_by_date:
                appointments_by_date[date_key] = []
            appointments_by_date[date_key].append({
                'id': apt.id,
                'time': apt.appointment_time.strftime('%H:%M'),
                'patient_id': apt.patient_id,
                'patient_name': f"{apt.patient.first_name} {apt.patient.last_name}" if apt.patient else None,
                'status': apt.status
            })

        # Build calendar days
        calendar_days = []
        current_date = start

        while current_date <= end:
            day_of_week = current_date.weekday()
            date_str = current_date.isoformat()

            # Check working hours for this day
            wh = working_hours_map.get(day_of_week)
            is_working_day = wh is not None

            # Check if fully unavailable
            day_start = datetime.combine(current_date, time.min)
            day_end = datetime.combine(current_date, time.max)

            day_unavailability = []
            is_fully_unavailable = False

            for unavail in unavailability:
                if unavail.start_datetime <= day_start and unavail.end_datetime >= day_end:
                    is_fully_unavailable = True
                    day_unavailability.append({
                        'id': unavail.id,
                        'reason': unavail.reason,
                        'is_full_day': True
                    })
                elif unavail.start_datetime.date() <= current_date <= unavail.end_datetime.date():
                    day_unavailability.append({
                        'id': unavail.id,
                        'start_time': unavail.start_datetime.strftime('%H:%M') if unavail.start_datetime.date() == current_date else '00:00',
                        'end_time': unavail.end_datetime.strftime('%H:%M') if unavail.end_datetime.date() == current_date else '23:59',
                        'reason': unavail.reason,
                        'is_full_day': False
                    })

            # Get day's appointments
            day_appointments = appointments_by_date.get(date_str, [])

            # Calculate availability status
            if not is_working_day:
                status = 'off_day'
            elif is_fully_unavailable:
                status = 'unavailable'
            elif current_date < today:
                status = 'past'
            else:
                status = 'available'

            # Count appointments by status
            scheduled_count = len([a for a in day_appointments if a['status'] == 'scheduled'])
            completed_count = len([a for a in day_appointments if a['status'] == 'completed'])

            calendar_days.append({
                'date': date_str,
                'day_of_week': day_of_week,
                'day_name': current_date.strftime('%A'),
                'status': status,
                'is_working_day': is_working_day,
                'working_hours': {
                    'start': wh.start_time.strftime('%H:%M') if wh else None,
                    'end': wh.end_time.strftime('%H:%M') if wh else None
                } if is_working_day else None,
                'unavailability': day_unavailability,
                'appointments': {
                    'total': len(day_appointments),
                    'scheduled': scheduled_count,
                    'completed': completed_count
                },
                'is_today': current_date == today
            })

            current_date += timedelta(days=1)

        return {
            'doctor_id': doctor_id,
            'doctor_name': f"Dr. {doctor.first_name} {doctor.last_name}",
            'start_date': start.isoformat(),
            'end_date': end.isoformat(),
            'days': calendar_days,
            'summary': {
                'total_days': len(calendar_days),
                'working_days': len([d for d in calendar_days if d['is_working_day']]),
                'unavailable_days': len([d for d in calendar_days if d['status'] == 'unavailable']),
                'total_appointments': sum(d['appointments']['total'] for d in calendar_days)
            }
        }

    @staticmethod
    def get_daily_schedule(doctor_id: int, schedule_date: str) -> dict:
        """
        Get detailed schedule for a specific day with time slots.
        Shows working hours broken into slots with availability status.
        """
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            raise ValueError("Doctor not found")

        try:
            target_date = datetime.strptime(schedule_date, '%Y-%m-%d').date()
        except ValueError:
            raise ValueError("Invalid date format. Use YYYY-MM-DD")

        day_of_week = target_date.weekday()
        today = date.today()
        now = datetime.now()

        # Get working hours for this day
        working_hours = DoctorWorkingHours.query.filter_by(
            doctor_id=doctor_id,
            day_of_week=day_of_week
        ).first()

        if not working_hours:
            return {
                'doctor_id': doctor_id,
                'doctor_name': f"Dr. {doctor.first_name} {doctor.last_name}",
                'date': schedule_date,
                'day_name': target_date.strftime('%A'),
                'is_working_day': False,
                'message': 'Not a working day',
                'slots': []
            }

        # Get unavailability for this day
        day_start = datetime.combine(target_date, time.min)
        day_end = datetime.combine(target_date, time.max)

        unavailability = DoctorUnavailability.query.filter(
            DoctorUnavailability.doctor_id == doctor_id,
            DoctorUnavailability.start_datetime <= day_end,
            DoctorUnavailability.end_datetime >= day_start
        ).all()

        # Check for full day unavailability
        full_day_unavail = None
        for unavail in unavailability:
            if unavail.start_datetime <= day_start and unavail.end_datetime >= day_end:
                full_day_unavail = unavail
                break

        if full_day_unavail:
            return {
                'doctor_id': doctor_id,
                'doctor_name': f"Dr. {doctor.first_name} {doctor.last_name}",
                'date': schedule_date,
                'day_name': target_date.strftime('%A'),
                'is_working_day': True,
                'is_unavailable': True,
                'unavailability_reason': full_day_unavail.reason,
                'working_hours': {
                    'start': working_hours.start_time.strftime('%H:%M'),
                    'end': working_hours.end_time.strftime('%H:%M')
                },
                'slots': []
            }

        # Get appointments for this day
        appointments = Appointment.query.filter(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date == target_date
        ).all()

        # Create appointment lookup by time
        appointments_by_time = {
            apt.appointment_time.strftime('%H:%M'): apt for apt in appointments
        }

        # Generate time slots (30-minute intervals)
        SLOT_DURATION = 30  # minutes
        slots = []

        current_time = datetime.combine(target_date, working_hours.start_time)
        end_time = datetime.combine(target_date, working_hours.end_time)

        while current_time < end_time:
            slot_time_str = current_time.strftime('%H:%M')
            slot_end = current_time + timedelta(minutes=SLOT_DURATION)

            # Determine slot status
            slot_status = 'available'
            slot_data = {
                'time': slot_time_str,
                'end_time': slot_end.strftime('%H:%M'),
                'status': 'available',
                'appointment': None,
                'unavailability': None
            }

            # Check if past
            if target_date < today or (target_date == today and current_time <= now):
                slot_status = 'past'

            # Check if unavailable (partial day)
            for unavail in unavailability:
                if unavail.start_datetime <= current_time < unavail.end_datetime:
                    slot_status = 'unavailable'
                    slot_data['unavailability'] = {
                        'id': unavail.id,
                        'reason': unavail.reason
                    }
                    break

            # Check if booked
            if slot_time_str in appointments_by_time:
                apt = appointments_by_time[slot_time_str]
                slot_status = 'booked'
                slot_data['appointment'] = {
                    'id': apt.id,
                    'patient_id': apt.patient_id,
                    'patient_name': f"{apt.patient.first_name} {apt.patient.last_name}" if apt.patient else None,
                    'status': apt.status,
                    'notes': apt.booking_notes
                }

                # Override status based on appointment status
                if apt.status == 'completed':
                    slot_status = 'completed'
                elif apt.status == 'cancelled':
                    slot_status = 'cancelled'
                elif apt.status == 'no_show':
                    slot_status = 'no_show'

            slot_data['status'] = slot_status
            slots.append(slot_data)

            current_time = slot_end

        # Calculate summary
        summary = {
            'total_slots': len(slots),
            'available': len([s for s in slots if s['status'] == 'available']),
            'booked': len([s for s in slots if s['status'] == 'booked']),
            'completed': len([s for s in slots if s['status'] == 'completed']),
            'cancelled': len([s for s in slots if s['status'] == 'cancelled']),
            'no_show': len([s for s in slots if s['status'] == 'no_show']),
            'unavailable': len([s for s in slots if s['status'] == 'unavailable']),
            'past': len([s for s in slots if s['status'] == 'past'])
        }

        return {
            'doctor_id': doctor_id,
            'doctor_name': f"Dr. {doctor.first_name} {doctor.last_name}",
            'date': schedule_date,
            'day_name': target_date.strftime('%A'),
            'is_working_day': True,
            'is_today': target_date == today,
            'is_past': target_date < today,
            'working_hours': {
                'start': working_hours.start_time.strftime('%H:%M'),
                'end': working_hours.end_time.strftime('%H:%M')
            },
            'slots': slots,
            'summary': summary
        }

    ########### HELPERS ###########

    @staticmethod
    def _working_hours_to_dict(hours: DoctorWorkingHours) -> dict:
        """Convert working hours to dictionary"""
        return {
            'id': hours.id,
            'doctor_id': hours.doctor_id,
            'day_of_week': hours.day_of_week,
            'day_name': DAY_NAMES.get(hours.day_of_week, "Unknown"),
            'start_time': DoctorService._format_time(hours.start_time),
            'end_time': DoctorService._format_time(hours.end_time),
        }

    @staticmethod
    def _unavailability_to_dict(unavail: DoctorUnavailability) -> dict:
        """Convert unavailability to dictionary"""
        return {
            'id': unavail.id,
            'doctor_id': unavail.doctor_id,
            'start_datetime': unavail.start_datetime.isoformat() if unavail.start_datetime else None,
            'end_datetime': unavail.end_datetime.isoformat() if unavail.end_datetime else None,
            'reason': unavail.reason,
            'created_at': unavail.created_at.isoformat() if unavail.created_at else None
        }