# Multimodal Attendance Agent - Phase 2 Integration Guide

## 1. Overview
Phase 2 adds **Emotion Intelligence** and **Audio Analysis** to the existing platform.
- **Emotion**: Real-time face detection with emotion labels (Happy, Bored, Confused) overlay on video.
- **Audio**: Real-time noise level and activity detection (Silent, Discussion, Chaotic).
- **Dashboard**: New visualizations including Emotion Distribution Chart and Audio Gauge.

## 2. Backend Setup
The backend now includes `fer` (Face Emotion Recognition) and `librosa` (Audio Analysis).

### 2.1 Dependencies
Ensure new requirements are installed:
```bash
pip install -r backend/requirements.txt
```

### 2.2 Database Initialization
The system uses SQLite. The database is automatically initialized on the first run of the backend.
Migration SQL is available in `backend/migrations.sql` if you need to manually inspect or migrate an existing DB.
- **Location**: `backend/student_db/attendance.db`
- **Tables**: `emotion_metrics`, `audio_metrics`

### 2.3 Running the Backend
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```
*Verify Console Output*: You should see "Application startup complete" and no errors regarding FER/Librosa.

## 3. Frontend Setup
New components (`EmotionMetricsCard`, `AudioDisplay`) and dependencies (`recharts`, `lucide-react`) have been added.

### 3.1 Install Dependencies
```bash
cd frontend
npm install
```

### 3.2 Running the Frontend
```bash
npm run dev
```
Access the dashboard at `http://localhost:5173`.

## 4. Testing & Verification

### 4.1 Emotion Detection
1.  **Start Camera**: Ensure your webcam is allowed.
2.  **Dashboard**: Look at the "Live Classroom Feed".
3.  **Action**: Make different facial expressions (Smile, Frown, Look Surprised).
4.  **Verify**:
    *   Green/Red/Yellow boxes appear around your face.
    *   Labels like "Happy (92%)" or "Confused (65%)" appear above the box.
    *   The "Emotion Distribution" Pie Chart updates every 5 seconds with new data.

### 4.2 Audio Analysis
1.  **Microphone**: Allow microphone access when prompted.
2.  **Dashboard**: Observe the "Audio Analysis" card in the sidebar.
3.  **Action**:
    *   Stay silent -> Gauge should be low ("Silent").
    *   Speak normally -> Gauge moves to middle (40-60dB, "Normal Discussion").
    *   Clap or shout -> Gauge peaks (80dB+, "Chaotic").
4.  **Verify**: The "Noise Level" bar reacts in real-time.

## 5. Troubleshooting
- **Camera/Mic not working**: Check browser permissions. Ensure no other app is using the camera.
- **Charts not updating**: Check backend logs for "Emotion detection error". Ensure database file permissions in `backend/student_db`.
- **Performance**: Deep learning models (Emotion) are heavy. If video lag occurs, the backend is throttling detection to preserve FPS.

## 6. Architecture Notes
- **Video Stream**: WebSocket `/ws/video` carries MJPEG frames with server-side text overlay.
- **Audio Stream**: WebSocket `/ws/audio` sends raw PCM data; server returns JSON metrics.
- **History**: API `/api/history/emotions` provides data for the pie chart.
