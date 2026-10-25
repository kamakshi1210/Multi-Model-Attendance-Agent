from sqlalchemy.orm import Session
from sqlalchemy import func
from .database import SessionLocal, Session as SessionModel, SessionPerson, PersonMetric, AudioMetric

class AnalyticsService:
    def get_session_trends(self, session_id: int):
        """
        Aggregates visual attention and audio dynamics over time for multimodal session trends.
        """
        db = SessionLocal()
        try:
            metrics = db.query(PersonMetric)\
                .filter(PersonMetric.session_id == session_id)\
                .order_by(PersonMetric.timestamp.asc())\
                .all()
                
            audio_metrics = db.query(AudioMetric)\
                .filter(AudioMetric.session_id == str(session_id))\
                .order_by(AudioMetric.timestamp.asc())\
                .all()
            
            timeline = {}
            for m in metrics:
                ts_str = m.timestamp.strftime("%H:%M:%S")
                if ts_str not in timeline:
                    timeline[ts_str] = {'att': []}
                timeline[ts_str]['att'].append(m.attention_score)
                
            for a in audio_metrics:
                ts_str = a.timestamp.strftime("%H:%M:%S")
                if ts_str not in timeline:
                    timeline[ts_str] = {'att': []}
                timeline[ts_str]['noise_db'] = round(a.noise_db, 1)
                timeline[ts_str]['speech_ratio'] = round(a.speech_ratio * 100, 1)
            
            graph_data = []
            for ts in sorted(timeline.keys()):
                val = timeline[ts]
                att_avg = round(sum(val['att']) / len(val['att']), 1) if val['att'] else 0.0
                graph_data.append({
                    'time': ts, 
                    'avg_attention': att_avg,
                    'student_count': len(val['att']),
                    'noise_db': val.get('noise_db', 45.0),
                    'speech_ratio': val.get('speech_ratio', 0.0)
                })
                
            return graph_data
        finally:
            db.close()
            
    def get_student_heatmap(self, session_id: int):
        """
        Returns per-participant attendance presence, status, and attention scores.
        """
        db = SessionLocal()
        try:
            people = db.query(SessionPerson).filter(SessionPerson.session_id == session_id).all()
            return [{
                'id': p.person_id,
                'name': p.person_id,
                'attention': round(p.avg_attention or 0.0, 1),
                'presence_seconds': round(p.total_time_present or 0.0, 1),
                'presence_percentage': round(getattr(p, 'presence_percentage', 0.0) or 0.0, 1),
                'attendance_status': getattr(p, 'attendance_status', 'N/A') or 'N/A'
            } for p in people]
        finally:
            db.close()
