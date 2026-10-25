from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime
import os

# Ensure the directory exists
DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "student_db")
os.makedirs(DB_DIR, exist_ok=True)

SQLALCHEMY_DATABASE_URL = f"sqlite:///{os.path.join(DB_DIR, 'attendance.db')}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class EmotionMetric(Base):
    __tablename__ = "emotion_metrics"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, index=True, default="unknown")
    emotion = Column(String)
    confidence = Column(Float)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class AudioMetric(Base):
    __tablename__ = "audio_metrics"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True, default="default")
    noise_db = Column(Float)
    speech_ratio = Column(Float)
    activity_type = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(String, default="default_teacher")
    class_id = Column(String, default="default_class")
    start_time = Column(DateTime, default=datetime.datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    people_count = Column(Integer, default=0)
    total_attention_avg = Column(Float, default=0.0)
    status = Column(String, default="active") # active, completed

class SessionPerson(Base):
    __tablename__ = "session_people"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    person_id = Column(String, index=True)
    name = Column(String, nullable=True)
    total_time_present = Column(Float, default=0.0)
    presence_percentage = Column(Float, default=0.0)
    attendance_status = Column(String, default="Absent") # "Present" (>=75%), "Partial" (40-74%), "Absent" (<40%)
    avg_attention = Column(Float, default=0.0)
    dominant_emotion = Column(String, nullable=True)
    first_seen = Column(DateTime, nullable=True)
    last_seen = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)

class PersonMetric(Base):
    __tablename__ = "person_metrics"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    person_id = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    emotion = Column(String)
    emotion_confidence = Column(Float)
    attention_score = Column(Float)
    gaze_focus = Column(Float, nullable=True)
    head_pose = Column(String, nullable=True)
    audio_noise = Column(Float, nullable=True)
    speech_ratio = Column(Float, nullable=True)

class Insight(Base):
    __tablename__ = "insights"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    person_id = Column(String, nullable=True)
    insight_type = Column(String) # student, classroom
    insight_text = Column(Text)
    generated_at = Column(DateTime, default=datetime.datetime.utcnow)

class SystemLog(Base):
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=True)
    event_type = Column(String)
    message = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
