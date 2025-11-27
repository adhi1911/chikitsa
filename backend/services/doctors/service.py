from datetime import datetime, time, timedelta
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