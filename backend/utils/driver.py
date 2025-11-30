from datetime import date, datetime , timedelta 
from typing import Dict, List, Optional, Tuple

from ..core.logger import logger  
from ..core.mail import send_email 
from ..services.appointments.service import AppointmentService
from ..services.doctors.service import DoctorService
from ..core.models import Doctor, Patient

from .email_templates import generate_appointment_reminder_html
from .report_templates import generate_monthly_report_html


## Daily appointment reminders 

def send_daily_reminders(hospital_phone: str) -> Dict: 
    """ Send appointment reminders for appointments scheduled for the next day

    returns: sent_count, failed_count and details
    """

    logger.info("Starting daily reminder job....")
    today = date.today() 

    appointments = AppointmentService.get_all_appointments(
        start_date=today.isoformat(),
        end_date=today.isoformat(), 
        status='scheduled'
    )

    logger.info(f"Found {len(appointments)} appointments for today.")
    if not appointments:
        return {
            "sent_count": 0,
            "failed_count": 0,
            "details": []
        }

    sent_count = 0 
    failed_count = 0
    failed_list = []
    
    logger.info(appointments[0])

    for apt in appointments: 
        patient_id = apt.get('patient_id')
        apt_id = apt.get('id')
        doctor_id = apt.get('doctor_id')
        patient = Patient.query.get(patient_id)
        if not patient or not patient.user.email: 
            logger.warning(f"Skipping appointment {apt.id} - no patient email found.")
            continue
        
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            logger.warning(f"Skipping appointment {apt_id} - no doctor found.")
            continue

        try: 

            apt_time = apt.get('appointment_time')
            if hasattr(apt_time, 'strftime'):
                apt_time = apt_time.strftime('%I:%M %p')
            else:
                time_display =  str(apt_time)

            doctor_name = f"{doctor.first_name} {doctor.last_name or ''}".strip()
            department = doctor.department.name if doctor.department else "General"

            html_body = generate_appointment_reminder_html(
                patient_name = f"{patient.first_name} {patient.last_name or ''}".strip(),
                appointment_date = apt.get('appointment_date'),
                appointment_time = time_display,
                doctor_name = doctor_name,
                department = department,
                hospital_phone = hospital_phone
            )

            sucess = send_email(
                to = patient.user.email,
                subject=f"Appointment Reminder- Today at {time_display}",
                html_body=html_body
            )

            if sucess: 
                sent_count += 1
            else: 
                failed_count += 1
                failed_list.append({'patient_id': apt.get('patient_id'), 'email': patient.user.email})


        except Exception as e:
            logger.error(f"Failed to send reminder for appointment {apt_id} to {patient.user.email}: {str(e)}")
            failed_count += 1
            failed_list.append({'patient_id': apt.get('patient_id'), 'email': patient.user.email})
    
    logger.info(f"Daily reminder job completed. Sent: {sent_count}, Failed: {failed_count}")

    return {
        'sent_count': sent_count,
        'failed_count': failed_count,
        'total': len(appointments),
        'failed_list': failed_list
    }


def send_test_reminder(email: str, hospital_phone: str = '+91-XXXXXXXXXX') -> bool:
    """Send a test reminder email to verify configuration."""
    logger.info(f"Sending test reminder to {email}")
    
    html_body = generate_appointment_reminder_html(
        patient_name='Test Patient',
        appointment_date=date.today(),
        appointment_time='10:30 AM',
        doctor_name='Rajesh Kumar',
        department='Cardiology',
        hospital_phone=hospital_phone
    )
    
    return send_email(
        to=email,
        subject="Test Appointment Reminder",
        html_body=html_body
    )


## Monthly Reports
def get_previous_month_range() ->Tuple[date,date,str]:
    """Get first day, last day and name of previous month"""
    today = date.today()
    first_of_current = today.replace(day=1)
    last_of_previous = first_of_current - timedelta(days=1)
    first_of_previous = last_of_previous.replace(day=1)
    month_name = first_of_previous.strftime('%B %Y')
    return first_of_previous, last_of_previous, month_name

def send_monthly_report() -> Dict: 
    """Send monthly reports to active doctors
    
    returns: sent_count, failed_count and details
    """
    logger.info("Strating monthly report job...")
    start_date, end_date,month_name = get_previous_month_range() 
    logger.info(f"Generating reports for {month_name} ({start_date} to {end_date})")

    doctors = DoctorService.get_all_active_doctors()
    logger.info(f"Found {len(doctors)} active doctors")

    if not doctors:
        return {'sent_count': 0, 'failed_count': 0, 'message': 'No active doctors'}

    success_count = 0
    failed_count =0 
    failed_list = []
    for doctor in doctors:
        if not doctor.get('email'):
            logger.warning(f"No email for doctor {doctor.get('id')}, skipping")
            continue 
            
        try: 
            report_data = DoctorService.get_doctor_monthly_report_data(
                doctor_id=doctor['id'],
                start_date=start_date,
                end_date=end_date
            )

            html_body = generate_monthly_report_html(
                    doctor_name=doctor['name'],
                    department=report_data['doctor']['department'],
                    month_name=month_name,
                    total_appointments=report_data['appointments']['total'],
                    completed=report_data['appointments']['completed'],
                    cancelled=report_data['appointments']['cancelled'],
                    no_show=report_data['appointments']['no_show'],
                    top_diagnoeses=report_data['top_diagnosis'],
                    consultations=report_data['consultations'],
                    total_prescriptions=report_data['summary']['total_prescriptions'],
                    total_followups=report_data['summary']['total_followups']
                )

            success = send_email(
                to= doctor['email'],
                subject=f"Monthly activity report - {month_name}",
                html_body=html_body
            )

            if success:
                success_count +=1
            else:
                logger.error(f"Failed to send report for doctor {doctor.get('id')}: {e}")
                failed_count += 1
                failed_list.append({'doctor_id': doctor['id'], 'error': str(e)})
        
        except Exception as e:
            logger.error(f"Encountered error while sending report doctor {doctor.get('id')}: {e}")
            failed_count += 1
            failed_list.append({'doctor_id': doctor['id'], 'error': str(e)})


    logger.info(f"Monthly reports completed: {success_count} sent, {failed_count} failed")

    return {
        'sent_count': success_count,
        'failed_count': failed_count,
        'total': len(doctors),
        'month': month_name,
        'failed_list': failed_list
    }



def send_test_report(doctor_id: int, email: Optional[str] = None) -> bool:
    """Send a test monthly report for a specific doctor."""
    logger.info(f"Sending test report for doctor {doctor_id}")
    
    # Use current month for testing
    today = date.today()
    first_of_month = today.replace(day=1)
    month_name = today.strftime('%B %Y')
    
    try:
        report_data = DoctorService.get_doctor_monthly_report_data(
            doctor_id=doctor_id,
            start_date=first_of_month,
            end_date=today
        )
        
        target_email = email or report_data['doctor'].get('email')
        if not target_email:
            logger.error("No email provided and doctor has no email")
            return False
        
        html_body = generate_monthly_report_html(
            doctor_name=report_data['doctor']['name'].replace('Dr. ', ''),
            department=report_data['doctor']['department'],
            month_name=month_name,
            total_appointments=report_data['appointments']['total'],
            completed=report_data['appointments']['completed'],
            cancelled=report_data['appointments']['cancelled'],
            no_show=report_data['appointments']['no_show'],
            top_diagnoeses=report_data['top_diagnosis'],
            consultations=report_data['consultations'],
            total_prescriptions=report_data['summary']['total_prescriptions'],
            total_followups=report_data['summary']['total_followups']
        )
        
        return send_email(
            to=target_email,
            subject=f"Test Monthly Report - {month_name}",
            html_body=html_body
        )
        
    except Exception as e:
        logger.error(f"Failed to generate test report: {e}")
        return False