from flask import current_app
from flask_mail import Message, Mail
from typing import List, Dict, Optional 
from .logger import logger 

import time 

mail = Mail() 

def init_mail(app): 
    mail.init_app(app)

def test_connection() -> bool:
    """Test SMTP connection - call this to verify setup"""
    try:
        with mail.connect() as conn:
            logger.info("SMTP connection successful!")
            return True
    except Exception as e:
        logger.error(f"SMTP connection failed: {e}")
        return False

def send_email(
        to:str | List[str],
        subject: str, 
        html_body: str, 
        text_body:Optional[str] = None, 
        attachments: Optional[List[Dict]] = None 
)-> bool: 

    """Send email using flask mail"""
    try: 
        recipients = [to] if isinstance(to, str) else to 

        # sender details 
        sender_email = current_app.config.get('MAIL_DEFAULT_SENDER') 
        sender_name = current_app.config.get('MAIL_DEFAULT_SENDER_NAME', 'Chikitsa HMS')
        sender =  f"{sender_name} <{sender_email}>" if sender_name else sender_email

        msg = Message(
            subject=subject,
            recipients=recipients,
            sender=sender,
            html=html_body,
            body=text_body or ''
        )

        if attachments: 
            for attachment in attachments: 
                data = attachment.get('data')
                if isinstance(data, str):
                    data = data.encode('utf-8')
                msg.attach(
                    filename=attachment.get('filename', 'attachment'),
                    content_type=attachment.get('content_type', 'application/octet-stream'),
                    data=data
                )

        mail.send(msg)
        logger.info(f"Email sent to {to} with subject '{subject}'")
        return True
    
    except Exception as e:
        logger.error(f"Failed to send email to {to}: {e}")
        return False
    

def send_email_with_retry(
    to: str | List[str],
    subject: str,
    html_body: str,
    text_body: Optional[str] = None,
    attachments: Optional[List[Dict]] = None,
    max_retries: int = 3
) -> bool: 
    """Send email with retry mechanism"""
    for attempt in range(max_retries): 
        if send_email(to, subject, html_body, text_body, attachments):
            return True 

        if attempt < max_retries - 1:
            wait_time = 2 ** attempt 
            logger.info(f"Email attempt {attempt + 1} failed. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)

    logger.error(f"All {max_retries} email attempts failed for {to}.")
    return False

        