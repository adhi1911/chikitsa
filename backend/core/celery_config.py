import os 
from celery import Celery 
from celery.schedules import crontab

DAILY_REMINDER_HOUR = int(os.getenv('DAILY_REMINDER_HOUR', 7))
DAILY_REMINDER_MINUTE = int(os.getenv('DAILY_REMINDER_MINUTE', 0))

MONTHLY_REPORT_DAY = int(os.getenv('MONTHLY_REPORT_DAY', 1))
MONTHLY_REPORT_HOUR = int(os.getenv('MONTHLY_REPORT_HOUR', 9))
MONTHLY_REPORT_MINUTE = int(os.getenv('MONTHLY_REPORT_MINUTE', 0))

REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

def make_celery(app=None):

    celery = Celery(
        'chikitsa',
        broker=REDIS_URL,
        backend=REDIS_URL,
        include=[
            'backend.utils.tasks'
        ]
    )

    celery.conf.update(

        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',

        # timezxone
        timezone='Asia/Kolkata',
        enable_utc=True,

        task_acks_late=True,
        task_reject_on_worker_lost=True,
        result_expires=3600,

        worker_prefetch_multiplier=1,
        worker_concurrency=2,

        beat_schedule={
            'daily-appointment-reminders': {
                'task': 'backend.utils.tasks.send_daily_reminders_task',
                'schedule': crontab(hour=DAILY_REMINDER_HOUR, minute=DAILY_REMINDER_MINUTE),  
            },
            'monthly-doctor-reports': {
                'task': 'backend.utils.tasks.send_monthly_reports_task',
                'schedule': crontab(day_of_month=MONTHLY_REPORT_DAY, hour=MONTHLY_REPORT_HOUR, minute=MONTHLY_REPORT_MINUTE), 
            },
        }
    )

    if app:
        celery.conf.update(app.config)

        class ContextTask(celery.Task):
            def __call__(self,*args,**kwargs):
                with app.app_context():
                    return self.run(*args, **kwargs)

        celery.Task = ContextTask

    return celery

celery_app = make_celery()