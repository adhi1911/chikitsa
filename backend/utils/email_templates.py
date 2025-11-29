from datetime import date, datetime
from typing import List, Optional, Dict

def generate_appointment_reminder_html(
    patient_name: str,
    appointment_date: date,
    appointment_time: str,
    doctor_name: str,
    department: str,
    hospital_phone: str = "+91-XXXXXXXXXX"
) -> str:
    """Generate HTML email for appointment reminder"""
    
    formatted_date = appointment_date.strftime('%A, %B %d, %Y')
    
    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
            margin: 0;
            padding: 0;
        }}
        .container {{
            max-width: 600px;
            margin: 20px auto;
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
            font-weight: 600;
        }}
        .header .icon {{
            font-size: 48px;
            margin-bottom: 10px;
        }}
        .content {{
            padding: 30px;
        }}
        .greeting {{
            font-size: 18px;
            margin-bottom: 20px;
        }}
        .appointment-card {{
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-radius: 10px;
            padding: 25px;
            margin: 20px 0;
            border-left: 4px solid #667eea;
        }}
        .appointment-card .row {{
            display: flex;
            align-items: center;
            margin: 12px 0;
        }}
        .appointment-card .icon {{
            width: 30px;
            font-size: 18px;
        }}
        .appointment-card .label {{
            color: #666;
            width: 100px;
        }}
        .appointment-card .value {{
            font-weight: 600;
            color: #333;
        }}
        .instructions {{
            background: #fff8e1;
            border-radius: 8px;
            padding: 15px 20px;
            margin: 20px 0;
            border-left: 4px solid #ffc107;
        }}
        .instructions h3 {{
            margin: 0 0 10px 0;
            color: #856404;
            font-size: 14px;
        }}
        .instructions ul {{
            margin: 0;
            padding-left: 20px;
            color: #856404;
        }}
        .footer {{
            background: #f8f9fa;
            padding: 20px 30px;
            text-align: center;
            font-size: 13px;
            color: #666;
        }}
        .footer a {{
            color: #667eea;
            text-decoration: none;
        }}
        .btn {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 12px 30px;
            border-radius: 6px;
            text-decoration: none;
            font-weight: 600;
            margin-top: 15px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Appointment Reminder</h1>
        </div>
        <div class="content">
            <p class="greeting">Dear <strong>{patient_name}</strong>,</p>
            
            <p>This is a friendly reminder about your appointment scheduled for <strong>today</strong>.</p>
            
            <div class="appointment-card">
                <div class="row">
                    <span class="label">Date:</span>
                    <span class="value">{formatted_date}</span>
                </div>
                <div class="row">
                    <span class="label">Time:</span>
                    <span class="value">{appointment_time}</span>
                </div>
                <div class="row">
                    <span class="label">Doctor:</span>
                    <span class="value">Dr. {doctor_name}</span>
                </div>
                <div class="row">
                    <span class="label">Department:</span>
                    <span class="value">{department}</span>
                </div>
            </div>
            
            <div class="instructions">
                <h3> PLEASE REMEMBER:</h3>
                <ul>
                    <li>Arrive 15 minutes before your scheduled time</li>
                    <li>Bring a valid ID proof</li>
                    <li>Carry your previous prescriptions and reports</li>
                </ul>
            </div>
            
            <p>If you need to reschedule or cancel your appointment, please contact us at <strong>{hospital_phone}</strong> or log in to your patient portal.</p>
            
            <p>We look forward to seeing you!</p>
            
            <p>Best regards,<br><strong>Chikitsa Hospital</strong></p>
        </div>
        <div class="footer">
            <p>This is an automated reminder. Please do not reply to this email.</p>
            <p>© 2024 Chikitsa Hospital. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""