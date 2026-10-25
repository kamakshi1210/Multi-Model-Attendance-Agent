-- Migration for Emotion and Audio Metrics

CREATE TABLE IF NOT EXISTS emotion_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id VARCHAR,
    emotion VARCHAR,
    confidence FLOAT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audio_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id VARCHAR,
    noise_db FLOAT,
    speech_ratio FLOAT,
    activity_type VARCHAR,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Index for faster querying
CREATE INDEX IF NOT EXISTS idx_emotion_timestamp ON emotion_metrics(timestamp);
CREATE INDEX IF NOT EXISTS idx_audio_timestamp ON audio_metrics(timestamp);
