import csv 
import datetime
from io import StringIO
from typing import List, Dict 
from typing import List, Optional, Dict 

def generate_patient_records_csv(
        patient_id: int, 
        patient_name: str, 
        records: List[Dict]
) -> str:
    """    
    Generate CSV content for patient medical records
    
    Each record dict should have:
    - appointment_date
    - appointment_time
    - doctor_name
    - department
    - diagnosis
    - symptoms
    - treatment_notes
    - medicines (list of medicine dicts)
    - followup_date
    """

    output = StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)

    writer.writerow([
        'Patiend ID',
        'Patient Name',
        'Appointment Date',
        'Appointment Time',
        'Doctor Name',
        'Department',
        'Diagnosis',
        'Symptoms',
        'Treatment Notes',
        'Medicines Prescribed',
        'Follow-up Date'
    ])

    for record in records:
        medicines_str = format_medicines(record['medicines'])

        writer.writerow([
            patient_id, 
            patient_name,
            record['appointment_date'],
            record['appointment_time'],
            record['doctor_name'],
            record['department'],
            record['diagnosis'],
            record['symptoms'],
            record['treatment_notes'],
            medicines_str or '',
            record['followup_date']
        ])

    return output.getvalue()


def format_medicines(medicines: List[Dict]) -> str:
    """ Formatting medicines list into readable string """
    if not medicines:
        return ''

    if isinstance(medicines, list) and len(medicines) > 0:
        if isinstance(medicines[0], str):
            return "; ".join(medicines)
        
        formatted = []
        for med in medicines: 
            med_str = med.get('medicine_name', 'Unknown Medicine')

            if med.get('dosage'):
                med_str += f" ({med['dosage']})"
            if med.get('frequency'):
                med_str += f", {med['frequency']}"
            if med.get('duration'):
                med_str += f", for {med['duration']}"
            if med.get('instructions'):
                med_str += f" - {med['instructions']}"
            
            formatted.append(med_str)

        return "; ".join(formatted)

def generate_csv_export_mail_html(
        patient_name: str, 
        filename: str,
        records_count: int,
        generated_at: datetime
) -> str: 
    
    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
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
        }}
        .content {{
            padding: 30px;
        }}
        .info-card {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            border-left: 4px solid #667eea;
        }}
        .info-row {{
            display: flex;
            margin: 10px 0;
        }}
        .info-label {{
            color: #666;
            width: 120px;
        }}
        .info-value {{
            font-weight: 600;
        }}
        .contents-list {{
            background: #e8f5e9;
            border-radius: 8px;
            padding: 15px 20px;
            margin: 20px 0;
        }}
        .contents-list h4 {{
            margin: 0 0 10px 0;
            color: #388e3c;
        }}
        .contents-list ul {{
            margin: 0;
            padding-left: 20px;
            color: #333;
        }}
        .warning {{
            background: #fff8e1;
            border-radius: 8px;
            padding: 15px;
            margin: 20px 0;
            border-left: 4px solid #ffc107;
            font-size: 13px;
            color: #856404;
        }}
        .footer {{
            background: #f8f9fa;
            padding: 20px 30px;
            text-align: center;
            font-size: 13px;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div style="font-size: 48px; margin-bottom: 10px;">
            Your Medical Records
            </div>
        </div>
        
        <div class="content">
            <p>Dear <strong>{patient_name}</strong>,</p>
            
            <p>Your medical records export is ready! Please find the attached CSV file.</p>
            
            <div class="info-card">
                <div class="info-row">
                    <span class="info-label">File Name:</span>
                    <span class="info-value">{filename}</span>
                </div>
                <div class="info-row">
                    <span class="info-label"> Records:</span>
                    <span class="info-value">{records_count} appointments</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Generated:</span>
                    <span class="info-value">{generated_at}</span>
                </div>
            </div>
            
            <div class="contents-list">
                <h4>File Contents:</h4>
                <ul>
                    <li>Appointment dates and times</li>
                    <li>Consulting doctor information</li>
                    <li>Diagnoses and symptoms</li>
                    <li>Treatment notes</li>
                    <li>Prescribed medicines with dosage</li>
                    <li>Follow-up dates</li>
                </ul>
            </div>
            
            <div class="warning">
                <strong>Privacy Notice:</strong> This file contains sensitive medical information. 
                Please keep it secure and do not share it with unauthorized persons.
            </div>
            
            <p>If you have any questions about your medical records, please contact us.</p>
            
            <p>Best regards,<br><strong>Chikitsa Hospital</strong></p>
        </div>
        
        <div class="footer">
            <p>This is an automated email. Please do not reply.</p>
            <p>© 2024 Chikitsa Hospital. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""