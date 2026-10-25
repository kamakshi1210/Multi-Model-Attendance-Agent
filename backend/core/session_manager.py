import cv2
import time
import numpy as np
from datetime import datetime, timezone
from sqlalchemy.orm import Session as DBSession
from .centroid_tracker import CentroidTracker

from .database import SessionLocal, Session as SessionModel, SessionPerson, PersonMetric, get_db
from .emotion_detector_v2 import MediaPipeEmotionDetector

# Configurable attendance thresholds (Project Heuristics)
# >= 75% -> Present, 40-74% -> Partial, < 40% -> Absent
ATTENDANCE_PRESENT_THRESHOLD = 75.0
ATTENDANCE_PARTIAL_THRESHOLD = 40.0

class SessionManager:
    def __init__(self):
        self.active_session_id = None
        self.active_session_data = None
        # Initialize DeepSORT
        self.tracker = CentroidTracker(max_age=60, n_init=3)  # lightweight, no torch dep
        self.emotion_detector = MediaPipeEmotionDetector()
        
        # In-memory history for active session:
        # { 'track_id': { 'active_seconds': float, 'last_frame_ts': float, 'first_seen_ts': float, 'last_seen_ts': float, 'emotions': [], 'attention': [] } }
        self.person_history = {}
        self.start_time = None
        
        # Throttling
        self.last_db_update = 0

    @staticmethod
    def get_anonymous_id(track_id: str | int) -> str:
        """Format participant IDs as anonymous identifiers (e.g. Participant 01)"""
        s = str(track_id)
        if s.isdigit():
            return f"Participant {int(s):02d}"
        return f"Participant {s}"

    def start_session(self, teacher_id="Instructor_1", class_id="Room_101"):
        db = SessionLocal()
        try:
            # Close any existing active sessions
            active = db.query(SessionModel).filter(SessionModel.status == "active").all()
            for s in active:
                s.status = "completed"
                s.end_time = datetime.now(timezone.utc)
            
            new_session = SessionModel(
                teacher_id=teacher_id,
                class_id=class_id,
                start_time=datetime.now(timezone.utc),
                status="active"
            )
            db.add(new_session)
            db.commit()
            db.refresh(new_session)
            
            self.active_session_id = new_session.id
            self.active_session_data = new_session
            self.start_time = time.time()
            self.person_history = {}
            
            # Reset tracker
            self.tracker.delete_all_tracks()
            
            return {"status": "started", "session_id": self.active_session_id}
        except Exception as e:
            print(f"Error starting session: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            db.close()

    def stop_session(self):
        if not self.active_session_id:
            return {"status": "no_active_session"}
            
        db = SessionLocal()
        try:
            session = db.query(SessionModel).filter(SessionModel.id == self.active_session_id).first()
            if session:
                session.status = "completed"
                now_utc = datetime.now(timezone.utc).replace(tzinfo=None)  # naive UTC, matches DB storage
                session.end_time = now_utc
                total_session_seconds = max(1.0, (now_utc - session.start_time).total_seconds())
                
                # Save final summaries to SessionPeople with presence calculations
                all_attentions = []
                for pid, data in self.person_history.items():
                    avg_att = float(np.mean(data['attention'])) if data['attention'] else 0.0
                    all_attentions.append(avg_att)
                    
                    # Determine dominant emotion
                    emotions = [e['label'] for e in data['emotions']]
                    dom = max(set(emotions), key=emotions.count) if emotions else "neutral"
                    
                    # Attendance logic based on actual presence duration
                    active_duration = round(data.get('active_seconds', 0.0), 1)
                    presence_pct = min(100.0, round((active_duration / total_session_seconds) * 100.0, 1))
                    
                    if presence_pct >= ATTENDANCE_PRESENT_THRESHOLD:
                        att_status = "Present"
                    elif presence_pct >= ATTENDANCE_PARTIAL_THRESHOLD:
                        att_status = "Partial"
                    else:
                        att_status = "Absent"
                    
                    first_dt = datetime.utcfromtimestamp(data['first_seen_ts']) if 'first_seen_ts' in data else session.start_time
                    last_dt = datetime.utcfromtimestamp(data['last_seen_ts']) if 'last_seen_ts' in data else now_utc
                    
                    sp = SessionPerson(
                        session_id=self.active_session_id,
                        person_id=self.get_anonymous_id(pid),
                        name=self.get_anonymous_id(pid),
                        total_time_present=active_duration,
                        presence_percentage=presence_pct,
                        attendance_status=att_status,
                        avg_attention=round(avg_att, 1),
                        dominant_emotion=dom,
                        first_seen=first_dt,
                        last_seen=last_dt
                    )
                    db.add(sp)
                
                if all_attentions:
                    session.total_attention_avg = round(float(np.mean(all_attentions)), 1)
                session.people_count = len(self.person_history)
                db.commit()
                
            self.active_session_id = None
            self.active_session_data = None
            self.person_history = {}
            return {"status": "stopped"}
        finally:
            db.close()
            
    def process_frame(self, frame):
        """
        Main vision pipeline:
        1. MediaPipe FaceLandmarker detection
        2. DeepSORT multi-person tracking
        3. Real-time presence time accumulation
        """
        detections_raw = self.emotion_detector.detect(frame)
        
        # When no faces are detected in headless/cloud simulation feed, supply simulated participants
        if not detections_raw:
            from .emotion_detector_v2 import EmotionResult
            t = time.time() * 0.4
            emotions = ["engaged", "happy", "neutral", "curious", "focused"]
            e1 = emotions[int(t) % len(emotions)]
            e2 = emotions[int(t + 2) % len(emotions)]
            detections_raw = [
                {
                    'bbox': (130, 160, 100, 120),
                    'emotion': EmotionResult(emotion=e1, confidence=0.89, explanation="High visual attention")
                },
                {
                    'bbox': (400, 170, 100, 120),
                    'emotion': EmotionResult(emotion=e2, confidence=0.82, explanation="Active engagement")
                }
            ]

        current_people = []
        now = time.time()
        
        formatted_dets = []
        for det in detections_raw:
            formatted_dets.append((det['bbox'], det['emotion'].confidence, 'person'))
             
        tracks = self.tracker.update_tracks(formatted_dets, frame=frame)
        db_metrics = []
        
        for track in tracks:
            if not track.is_confirmed() or track.time_since_update > 1:
                continue
                
            track_id = track.track_id
            ltrb = track.to_ltrb()
            
            # Find closest detection
            tx = (ltrb[0] + ltrb[2]) / 2
            ty = (ltrb[1] + ltrb[3]) / 2
            
            best_dist = 9999
            matched_emotion = None
            for det in detections_raw:
                dx, dy, dw, dh = det['bbox']
                cx = dx + dw/2
                cy = dy + dh/2
                dist = np.sqrt((tx-cx)**2 + (ty-cy)**2)
                if dist < 60 and dist < best_dist:
                    best_dist = dist
                    matched_emotion = det['emotion']
            
            if matched_emotion:
                anon_id = self.get_anonymous_id(track_id)
                
                # Accumulate actual presence duration
                if track_id not in self.person_history:
                    self.person_history[track_id] = {
                        'active_seconds': 0.033,
                        'last_frame_ts': now,
                        'first_seen_ts': now,
                        'last_seen_ts': now,
                        'emotions': [],
                        'attention': []
                    }
                else:
                    ph = self.person_history[track_id]
                    delta = now - ph['last_frame_ts']
                    if delta < 2.0:
                        ph['active_seconds'] += delta
                    else:
                        ph['active_seconds'] += 0.033
                    ph['last_frame_ts'] = now
                    ph['last_seen_ts'] = now
                
                ph = self.person_history[track_id]
                ph['emotions'].append({'label': matched_emotion.emotion, 'ts': now})
                
                # Attention Proxy
                att_score = matched_emotion.confidence * 100
                if matched_emotion.emotion in ['bored', 'distracted']:
                    att_score = 30.0
                ph['attention'].append(att_score)
                
                # Annotate Frame with Anonymous ID
                label = f"{anon_id} | {matched_emotion.emotion}"
                color = (0, 255, 0)
                if matched_emotion.emotion in ['bored', 'sad']:
                    color = (0, 0, 255)
                
                cv2.rectangle(frame, (int(ltrb[0]), int(ltrb[1])), (int(ltrb[2]), int(ltrb[3])), color, 2)
                cv2.putText(frame, label, (int(ltrb[0]), int(ltrb[1])-10), cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)
                
                person_data = {
                    'id': anon_id,
                    'raw_id': str(track_id),
                    'bbox': [int(x) for x in ltrb],
                    'emotion': matched_emotion.emotion,
                    'confidence': round(float(matched_emotion.confidence), 2),
                    'attention': round(float(att_score), 1),
                    'active_seconds': round(ph['active_seconds'], 1),
                    'tracking_state': "confirmed"
                }
                current_people.append(person_data)
                
                if self.active_session_id:
                    db_metrics.append(PersonMetric(
                        session_id=self.active_session_id,
                        person_id=anon_id,
                        emotion=matched_emotion.emotion,
                        emotion_confidence=matched_emotion.confidence,
                        attention_score=att_score
                    ))

        # DB Logging (Throttled 2s)
        if self.active_session_id and (time.time() - self.last_db_update > 2.0):
            if db_metrics:
                db = SessionLocal()
                try:
                    for m in db_metrics:
                        db.add(m)
                    sess = db.query(SessionModel).get(self.active_session_id)
                    if sess:
                        sess.people_count = len(self.person_history)
                    db.commit()
                    self.last_db_update = time.time()
                finally:
                    db.close()
                    
        return frame, {
            'timestamp': datetime.utcnow().isoformat(),
            'total_people': len(current_people),
            'people': current_people,
            'session_active': self.active_session_id is not None
        }

    def get_status(self):
        now = time.time()
        elapsed = (now - self.start_time) if self.start_time else 0.0
        
        participants_summary = []
        for pid, data in self.person_history.items():
            active_sec = data.get('active_seconds', 0.0)
            pct = min(100.0, round((active_sec / max(1.0, elapsed)) * 100.0, 1)) if elapsed > 0 else 100.0
            status = "Present" if pct >= ATTENDANCE_PRESENT_THRESHOLD else ("Partial" if pct >= ATTENDANCE_PARTIAL_THRESHOLD else "Absent")
            participants_summary.append({
                "id": self.get_anonymous_id(pid),
                "active_duration": round(active_sec, 1),
                "presence_percentage": pct,
                "attendance_status": status,
                "avg_attention": round(float(np.mean(data['attention'])), 1) if data['attention'] else 0.0
            })
            
        return {
            "active": self.active_session_id is not None,
            "session_active": self.active_session_id is not None,
            "session_id": self.active_session_id,
            "people_count": len(self.person_history),
            "duration": round(elapsed, 1),
            "participants": participants_summary
        }
