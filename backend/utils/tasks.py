from ..core.celery_config import celery_app 
from ..core.logger import logger 
from ..app import create_app
from .driver import send_daily_reminders, send_monthly_report 

from flask import current_app 

@celery_app.task(bind=True, name='backend.utils.tasks.send_daily_reminders_task', max_retries=1)
def send_daily_reminders_task(self):
    """ 
    send daily appointment reminders to patients.
    """
    logger.info("Starting daily appointment reminders task...")
    try:
        try:
            app = current_app._get_current_object()
        except RuntimeError:
            app = create_app()
        
        with app.app_context():
            result = send_daily_reminders(hospital_phone=app.config.get('HOSPITAL_PHONE'))
            logger.info("Daily appointment reminders task completed.")
            return result
    
    except Exception as e:
        logger.error(f"Error in daily appointment reminders task: {e}")
        raise self.retry(exc=e, countdown=60)  # 60 sec retry 


@celery_app.task(bind=True, name='backend.utils.tasks.send_monthly_reports_task', max_retries=1)
def send_monthly_reports_task(self):
    """ 
    send monthly reports to doctors.
    """
    logger.info("Starting monthly doctor reports task...")
    try:
        try: 
            app = current_app._get_current_object()
        except RuntimeError:
            app = create_app()

        with app.app_context():
            result = send_monthly_report() 
            logger.info("Monthly doctor reports task completed.")
            return result
        
    except  Exception as e:
        logger.error(f"Error in monthly doctor reports task: {e}")
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries)) # retry with exponential backoff
    