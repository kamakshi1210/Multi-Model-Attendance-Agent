from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import pandas as pd
import io
import os
from .database import Session as SessionModel, SessionPerson, PersonMetric, AudioMetric, get_db, SessionLocal

class ReportGenerator:
    def __init__(self):
        pass

    def generate_pdf_report(self, session_id: int):
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet
        except ImportError:
            print("[WARNING] reportlab not installed. PDF generation requires 'pip install reportlab'.")
            return None

        styles = getSampleStyleSheet()
        db = SessionLocal()
        try:
            session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
            if not session:
                return None
            
            attendees = db.query(SessionPerson).filter(SessionPerson.session_id == session_id).all()
            audio_records = db.query(AudioMetric).filter(AudioMetric.session_id == str(session_id)).all()
            
            avg_noise = round(sum(a.noise_db for a in audio_records) / len(audio_records), 1) if audio_records else 45.0
            avg_speech = round((sum(a.speech_ratio for a in audio_records) / len(audio_records)) * 100, 1) if audio_records else 0.0
            
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            elements = []
            
            # Header
            elements.append(Paragraph("Multimodal Attendance & Engagement Report", self.styles['Title']))
            elements.append(Spacer(1, 12))
            
            # Info
            duration_str = str(session.end_time - session.start_time).split('.')[0] if session.end_time else "In Progress"
            info_data = [
                ["Session ID", str(session.id)],
                ["Date", session.start_time.strftime("%Y-%m-%d %H:%M")],
                ["Duration", duration_str],
                ["Total Participants", str(session.people_count)],
                ["Avg Visual Attention", f"{session.total_attention_avg or 0.0:.1f}%"],
                ["Avg Noise Level", f"{avg_noise} dB"],
                ["Speech Activity Ratio", f"{avg_speech}%"]
            ]
            t = Table(info_data)
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#1e293b')),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            elements.append(t)
            elements.append(Spacer(1, 20))
            
            # Attendees Table
            elements.append(Paragraph("Presence-Based Attendance Summary", self.styles['Heading2']))
            elements.append(Spacer(1, 6))
            data = [["Participant ID", "Active Time", "Presence %", "Attendance Status", "Avg Attention"]]
            for p in attendees:
                data.append([
                    p.person_id or "Participant",
                    f"{p.total_time_present:.1f}s",
                    f"{getattr(p, 'presence_percentage', 0.0):.1f}%",
                    getattr(p, 'attendance_status', 'N/A'),
                    f"{p.avg_attention:.1f}%"
                ])
                
            if len(data) == 1:
                data.append(["No participants recorded", "--", "--", "--", "--"])
                
            t2 = Table(data)
            t2.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#64748b')),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(t2)
            
            doc.build(elements)
            buffer.seek(0)
            return buffer
            
        finally:
            db.close()

    def generate_csv_export(self, session_id: int):
        db = SessionLocal()
        try:
            attendees = db.query(SessionPerson).filter(SessionPerson.session_id == session_id).all()
            if not attendees:
                # Fallback to metrics if no session person records yet
                metrics = db.query(PersonMetric).filter(PersonMetric.session_id == session_id).all()
                if not metrics:
                    return None
                data = [{
                    'session_id': session_id,
                    'timestamp': m.timestamp,
                    'participant_id': m.person_id,
                    'attention_score': m.attention_score
                } for m in metrics]
                return pd.DataFrame(data).to_csv(index=False)
                
            data = [{
                'session_id': session_id,
                'participant_id': p.person_id,
                'active_time_seconds': round(p.total_time_present or 0.0, 1),
                'presence_percentage': round(getattr(p, 'presence_percentage', 0.0) or 0.0, 1),
                'attendance_status': getattr(p, 'attendance_status', 'N/A'),
                'avg_attention': round(p.avg_attention or 0.0, 1)
            } for p in attendees]
            
            df = pd.DataFrame(data)
            return df.to_csv(index=False)
        finally:
            db.close()
