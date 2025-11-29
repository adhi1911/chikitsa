from datetime import date , datetime 
from typing import List, Dict, Optional

def generate_monthly_report_html(
        doctor_name: str, 
        department: str,
        month_name: str,
        total_appointments: int,
        completed: int,
        cancelled: int, 
        no_show: int, 
        top_diagnoeses: List[Dict],
        consultations: List[Dict],
        total_prescriptions: int, 
        total_followups: int
) -> str:

    """Generate HTML report for monthly activity of doctor"""

    diagnoses_html = ""
    for i, diag in enumerate(top_diagnoeses[:5], 1):
        diagnoses_html+= f"""
            <tr>
                <td style="padding: 10px 15px;">{i}</td>
                <td style="padding: 10px 15px;">{diag['name']}</td>
                <td style="padding: 10px 15px; text-align: center;">
                    <span style="background: #e3f2fd; color: #1976d2; padding: 4px 12px; border-radius: 20px; font-weight: 600;">
                        {diag['count']}
                    </span>
                </td>
            </tr>
            """

    if not diagnoses_html:
        diagnoses_html = """
            <tr>
                <td colspan="3" style="padding: 10px 15px; text-align: center; color: #777;">
                    No diagnoses recorded.
                </td>
            </tr>
        """

    consultations_html = ""
    for cons in consultations[:15]:
        consultations_html += f"""
        <tr>
            <td style="padding: 10px 15px;">{cons['date']}</td>
            <td style="padding: 10px 15px;">{cons['patient']}</td>
            <td style="padding: 10px 15px;">{cons['diagnosis'] or 'N/A'}</td>
            <td style="padding: 10px 15px; text-align: center;">
                <span style="background: #e8f5e9; color: #388e3c; padding: 2px 8px; border-radius: 10px; font-size: 12px;">
                    {cons['rx_count']} meds
                </span>
            </td>
        </tr>
        """

    if not consultations_html:
        consultations_html = """
            <tr>
                <td colspan="4" style="padding: 10px 15px; text-align: center; color: #777;">
                    No consultations recorded.
                </td>
            </tr>
        """

    completion_rate = (completed / total_appointments * 100) if total_appointments > 0 else 0
    completion_rate = f"{completion_rate:.1f}"

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
            background-color: #f0f2f5;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0 0 5px 0;
            font-size: 28px;
        }}
        .header h2 {{
            margin: 0;
            font-weight: 400;
            opacity: 0.9;
        }}
        .doctor-info {{
            background: rgba(255,255,255,0.1);
            padding: 15px 25px;
            border-radius: 8px;
            margin-top: 20px;
            display: inline-block;
        }}
        .content {{
            padding: 30px;
        }}
        .stats-grid {{
            display: flex;
            gap: 15px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }}
        .stat-card {{
            flex: 1;
            min-width: 150px;
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
        }}
        .stat-card.primary {{ background: #e3f2fd; border-bottom: 3px solid #1976d2; }}
        .stat-card.success {{ background: #e8f5e9; border-bottom: 3px solid #388e3c; }}
        .stat-card.warning {{ background: #fff8e1; border-bottom: 3px solid #f57c00; }}
        .stat-card.danger {{ background: #ffebee; border-bottom: 3px solid #d32f2f; }}
        .stat-number {{
            font-size: 36px;
            font-weight: 700;
            margin-bottom: 5px;
        }}
        .stat-card.primary .stat-number {{ color: #1976d2; }}
        .stat-card.success .stat-number {{ color: #388e3c; }}
        .stat-card.warning .stat-number {{ color: #f57c00; }}
        .stat-card.danger .stat-number {{ color: #d32f2f; }}
        .stat-label {{
            font-size: 13px;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .section {{
            margin: 30px 0;
        }}
        .section-title {{
            font-size: 18px;
            font-weight: 600;
            color: #28a745;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #28a745;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }}
        th {{
            background: #f8f9fa;
            padding: 12px 15px;
            text-align: left;
            font-weight: 600;
            color: #333;
            border-bottom: 2px solid #dee2e6;
        }}
        td {{
            border-bottom: 1px solid #eee;
        }}
        tr:hover {{
            background: #f8f9fa;
        }}
        .summary-box {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 10px;
            display: flex;
            justify-content: space-around;
            text-align: center;
        }}
        .summary-item {{
            padding: 0 20px;
        }}
        .summary-item .number {{
            font-size: 32px;
            font-weight: 700;
        }}
        .summary-item .label {{
            font-size: 13px;
            opacity: 0.9;
        }}
        .completion-rate {{
            background: #f8f9fa;
            padding: 15px 20px;
            border-radius: 8px;
            margin: 20px 0;
            text-align: center;
        }}
        .completion-rate .rate {{
            font-size: 48px;
            font-weight: 700;
            color: #28a745;
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
            <h1>Monthly Activity Report</h1>
            <h2>{month_name}</h2>
            <div class="doctor-info">
                <strong>Dr. {doctor_name}</strong><br>
                {department}
            </div>
        </div>
        
        <div class="content">
            <!-- Stats Grid -->
            <div class="stats-grid">
                <div class="stat-card primary">
                    <div class="stat-number">{total_appointments}</div>
                    <div class="stat-label">Total Appointments</div>
                </div>
                <div class="stat-card success">
                    <div class="stat-number">{completed}</div>
                    <div class="stat-label">Completed</div>
                </div>
                <div class="stat-card warning">
                    <div class="stat-number">{no_show}</div>
                    <div class="stat-label">No Show</div>
                </div>
                <div class="stat-card danger">
                    <div class="stat-number">{cancelled}</div>
                    <div class="stat-label">Cancelled</div>
                </div>
            </div>
            
            <!-- Completion Rate -->
            <div class="completion-rate">
                <div class="rate">{completion_rate}%</div>
                <div style="color: #666;">Completion Rate</div>
            </div>
            
            <!-- Top Diagnoses -->
            <div class="section">
                <h3 class="section-title">
                 Top Diagnoses
                </h3>
                <table>
                    <thead>
                        <tr>
                            <th style="width: 50px;">#</th>
                            <th>Diagnosis</th>
                            <th style="width: 100px; text-align: center;">Patients</th>
                        </tr>
                    </thead>
                    <tbody>
                        {diagnoses_html}
                    </tbody>
                </table>
            </div>
            
            <!-- Recent Consultations -->
            <div class="section">
                <h3 class="section-title">
                    Recent Consultations
                </h3>
                <table>
                    <thead>
                        <tr>
                            <th style="width: 100px;">Date</th>
                            <th>Patient</th>
                            <th>Diagnosis</th>
                            <th style="width: 80px; text-align: center;">Rx</th>
                        </tr>
                    </thead>
                    <tbody>
                        {consultations_html}
                    </tbody>
                </table>
            </div>
            
            <!-- Summary -->
            <div class="section">
                <h3 class="section-title">
                     Monthly Summary
                </h3>
                <div class="summary-box">
                    <div class="summary-item">
                        <div class="number">{total_prescriptions}</div>
                        <div class="label">Prescriptions Written</div>
                    </div>
                    <div class="summary-item">
                        <div class="number">{total_followups}</div>
                        <div class="label">Follow-ups Scheduled</div>
                    </div>
                </div>
            </div>
            
            <p style="margin-top: 30px; text-align: center; color: #666;">
                Thank you for your dedication to patient care!
            </p>
        </div>
        
        <div class="footer">
            <p>This report was automatically generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
            <p>© 2025 Chikitsa Hospital. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""