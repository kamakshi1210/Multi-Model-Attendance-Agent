# Multimodal Attendance & Engagement Agent
> **Generative AI Capstone Certification Project**  
> *Real-time multimodal session monitoring, presence-based attendance verification, and explainable AI insights powered by Google Gemini.*

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.12](https://img.shields.io/badge/Python-3.12-3776AB.svg?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB.svg?logo=react&logoColor=black)](https://react.dev)
[![Google Gemini](https://img.shields.io/badge/AI-Google%20Gemini-4285F4.svg?logo=google&logoColor=white)](https://ai.google.dev)
[![Tests: Passing](https://img.shields.io/badge/Tests-16%20Passed-success.svg)](backend/tests)

---

## 📌 Executive Summary & Architecture

Traditional educational attendance tools merely take a static snapshot of presence at a single moment in time, providing zero visibility into active attention or classroom dynamics. 

The **Multimodal Attendance & Engagement Agent** continuously monitors real-time classroom sessions by fusing two distinct non-invasive telemetry streams:
1. **Vision Stream**: Tracks participant faces across video frames to accumulate **continuous active presence** and compute visual attention vectors (pitch/yaw/roll head pose and eye contact proxy).
2. **Audio Stream**: Samples 16kHz PCM microphone audio to evaluate calibrated acoustic sound pressure (30–95 dB SPL) and speech activity via Zero-Crossing Rate (ZCR).

The telemetry is fused deterministically and forwarded as aggregated time-window summaries to **Google Gemini** to produce structured, explainable pedagogical suggestions and individual participant reflections.

```mermaid
graph TD
    A[Browser Webcam] -->|WebSocket: Video Frames| B[FastAPI Backend]
    C[Web Audio API: 16kHz PCM] -->|WebSocket: Audio Chunks| B
    
    subgraph Vision Pipeline
        B --> D[MediaPipe FaceLandmarker]
        D --> E[DeepSORT Tracker]
        E --> F[Anonymous ID Assignment<br/>Participant 01, Participant 02]
        F --> G[Active Presence Accumulation]
    end
    
    subgraph Audio Pipeline
        B --> H[RMS Energy & Decibel Calibration<br/>30 - 95 dB SPL]
        H --> I[Zero-Crossing Rate ZCR]
        I --> J[Speech vs Noise Activity Ratio]
    end
    
    G --> K[Multimodal Fusion Engine]
    J --> K
    
    K --> L["Deterministic Engagement Score<br/>E = 0.40(Attn) + 0.30(Pres) + 0.15(Act) + 0.15(Noise)"]
    L --> M[SQLite Database]
    L --> N[Structured Summary Payload<br/>(No Raw Video Frames)]
    
    N --> O[Google Gemini Multimodal Agent<br/>gemini-2.0-flash / Pydantic Schemas]
    O --> P[StructuredAIInsights<br/>Live Teaching Suggestions]
    O --> Q[StudentReflection<br/>Explainable Participant Modal]
    
    P --> R[React 19 Dashboard]
    Q --> R
    M --> S[PDF & CSV Report Exports]
```

---

## 🎯 Mandatory Capstone Epics Completed

| Epic | Specification | Implementation Highlights | Status |
| :--- | :--- | :--- | :---: |
| **Epic 1** | Requirements & Environment Setup | Python 3.12 pinned requirements, automated `.bat` setup scripts, `.env.example`, clean Git baseline. | ✅ Complete |
| **Epic 2** | Computer Vision & Presence Attendance | MediaPipe FaceLandmarker + DeepSORT. Continuous active duration accumulation. Thresholds: $\ge 75\%$ Present, $40-74\%$ Partial, $<40\%$ Absent. Anonymous IDs only. | ✅ Complete |
| **Epic 3** | Audio Processing & Speech Activity | 16kHz PCM Web Audio API, RMS energy, calibrated dB SPL (30–95 dB), Zero-Crossing Rate (ZCR) speech ratio. | ✅ Complete |
| **Epic 4** | Multimodal Fusion & Gemini Integration | Deterministic fusion formula (0–100 score). Google Gemini agent with Pydantic structured schemas and telemetry-grounded local fallback. | ✅ Complete |
| **Epic 5** | Analytics, Explainability & Reports | Multimodal time-series trends (attention + noise dB + speech %). Explainable student reflection modal. PDF & CSV report exports. | ✅ Complete |
| **Epic 6** | Interface, Testing & Deployment | Real-time React 19 dashboard, automated unit test suite (16 tests, 100% pass), production-ready documentation. | ✅ Complete |

---

## 🔒 Privacy & Ethical Design Guarantees

In compliance with strict educational privacy standards:
- **Anonymous Identifiers Only**: All participants are identified sequentially as `Participant 01`, `Participant 02`, etc.
- **Zero Facial Recognition**: No biometric facial databases, facial embedding comparisons, or personal identity matching.
- **No Emotion Pseudoscience**: Banned unscientific emotion classifiers (no "happy", "sad", "angry" labels). System relies strictly on physical head pose, eye gaze vectors, and vocal acoustic activity.
- **Cloud Privacy**: Google Gemini receives **only compact aggregated numerical statistics** (average attention %, noise dB, speech ratio %). **Raw video frames are never transmitted over the internet.**
- **Non-Judgmental Pedagogical Reflection**: AI student reflections are strictly constructive, supportive, and free of evaluative grading.

---

## 📐 Deterministic Engagement Formula

Engagement is calculated deterministically by [`MultimodalFusionEngine`](backend/core/multimodal_fusion.py) before feeding into AI reasoning:

$$\text{Engagement Score} = 100 \times \left( 0.40 \cdot \bar{A} + 0.30 \cdot P + 0.15 \cdot S + 0.15 \cdot Q_{\text{noise}} \right)$$

Where:
- $\bar{A} \in [0, 1]$: Mean visual attention across participants based on gaze orientation and head pose stability.
- $P \in [0, 1]$: Active participant presence ratio relative to elapsed session duration.
- $S \in [0, 1]$: Verbal activity and speech ratio derived from audio Zero-Crossing Rate.
- $Q_{\text{noise}} \in [0, 1]$: Inverse acoustic noise penalty ($1.0$ in quiet/moderate lecture conditions $\le 65\text{ dB}$, degrading gracefully if ambient sound exceeds $70\text{ dB}$).

Engagement classifications:
- **$\ge 75.0$**: *High Engagement* (Optimal classroom pacing)
- **$50.0 - 74.9$**: *Moderate Engagement* (Normal lecture state)
- **$30.0 - 49.9$**: *Low Attention* (Interactive check-in recommended)
- **$< 30.0$**: *Inactive / Distracted* (Instructor intervention alert)

---

## 🛠️ Technology Stack

| Layer | Technologies Used |
| :--- | :--- |
| **Frontend** | React 19, Tailwind CSS, Lucide React, Recharts, Vite |
| **Backend API** | FastAPI, Uvicorn, WebSockets, Pydantic v2 |
| **Computer Vision** | MediaPipe FaceLandmarker (Tasks API), DeepSORT Realtime, OpenCV |
| **Audio Processing** | Web Audio API (Browser AudioContext), NumPy PCM Processing |
| **Generative AI** | Google Gemini API (`gemini-2.0-flash` via `google-genai` / `google-generativeai`) |
| **Persistence** | SQLite, SQLAlchemy ORM |
| **Reporting** | ReportLab (PDF generation), Pandas (CSV exports) |
| **Automated Testing** | Python `unittest` / `pytest` test suite |

---

## 🚀 Quickstart & Setup Guide

### 1. Prerequisites
- **Python 3.12** installed and accessible via PATH.
- **Node.js 18+** and `npm` installed.
- A functional webcam and microphone.
- *(Optional)* A Google Gemini API Key from [Google AI Studio](https://aistudio.google.com/).

### 2. Automated One-Click Setup (Windows)
Double-click [`setup_environment.bat`](setup_environment.bat) or run from terminal:
```cmd
setup_environment.bat
```

### 3. Manual Installation

#### Backend Setup
```bash
# Navigate to backend and create virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env and enter your GEMINI_API_KEY (optional; system will use grounded fallback if unset)
```

#### Frontend Setup
```bash
cd frontend
npm install
```

### 4. Running the System
You can launch both backend and frontend automatically with [`start_system.bat`](start_system.bat):
```cmd
start_system.bat
```

Or run manually in separate terminals:
```bash
# Terminal 1: Backend
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Frontend
cd frontend
npm run dev
```

Open your browser at `http://localhost:5173`.

---

## 🧪 Automated Test Suite

The project includes an automated test suite validating every core module:
```bash
python -m unittest discover backend/tests
```

### Test Coverage Highlights:
- **`test_audio_analysis.py`**: Tests silence rejection, synthetic speech recognition, RMS calculation, and 30–95 dB SPL calibration limits.
- **`test_multimodal_fusion.py`**: Tests mathematical weight verification, bounded 0–100 score limits, engagement state transitions, and Gemini payload safety (zero raw video frame leakage).
- **`test_gemini_agent.py`**: Validates `StructuredAIInsights` and `StudentReflection` Pydantic models, deterministic grounded fallback, and constructive coaching language.
- **`test_attendance_logic.py`**: Tests anonymous ID generation (`Participant 01`), continuous presence accumulation, threshold grading ($\ge 75\%$ Present, $40-74\%$ Partial, $<40\%$ Absent), and session lifecycles.

---

## 📂 Project Structure

```
Multimodal-attendance-agent-/
├── backend/
│   ├── core/
│   │   ├── analytics_service.py       # Multimodal trend aggregation (attention + audio)
│   │   ├── audio_analysis.py          # RMS, calibrated dB SPL, ZCR speech ratio
│   │   ├── camera_service.py          # OpenCV video capture service
│   │   ├── database.py                # SQLite schema (Session, Person, AudioMetric)
│   │   ├── emotion_detector_v2.py     # MediaPipe Tasks FaceLandmarker
│   │   ├── gemini_agent.py            # Gemini Multimodal Agent & Pydantic models
│   │   ├── multimodal_fusion.py       # Deterministic fusion scoring engine
│   │   ├── recommendations_engine.py  # Rule-based real-time alerts
│   │   ├── report_generator.py        # PDF & CSV generation engine
│   │   └── session_manager.py         # Session lifecycle & DeepSORT tracking
│   ├── tests/
│   │   ├── test_attendance_logic.py   # Presence thresholds & anonymous ID tests
│   │   ├── test_audio_analysis.py     # RMS & ZCR speech detection tests
│   │   ├── test_gemini_agent.py       # Pydantic schema & fallback tests
│   │   └── test_multimodal_fusion.py  # Engagement scoring formula tests
│   └── main.py                        # FastAPI application & WebSocket endpoints
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── AnalyticsPage.jsx      # Multimodal trends & reflection modal
│   │   │   ├── AttendanceDashboard.jsx# Main classroom monitoring view
│   │   │   ├── AudioCapture.jsx       # Web Audio API 16kHz PCM streamer
│   │   │   ├── MetricsPanel.jsx       # Live telemetry & AI insights panel
│   │   │   ├── RecommendationsPanel.jsx# Live teacher alert banners
│   │   │   ├── Sidebar.jsx            # Session controls & timer
│   │   │   └── SuggestionBox.jsx      # Gemini prioritized recommendations
│   │   └── App.jsx
│   └── package.json
├── AUDIT_REPORT.md                    # Forensic architectural audit & gap analysis
├── LICENSE                            # MIT License with dual attribution
├── requirements.txt                   # Root Python dependencies
├── setup_environment.bat              # One-click environment configuration
├── start_system.bat                   # One-click dual-server launcher
└── README.md                          # Technical documentation
```

---

## 📜 License & Attribution

This project is licensed under the **MIT License** — see the [`LICENSE`](LICENSE) file for details.

- **Original Starter Codebase**: [Rohith K](https://github.com/Rohithk05/Multimodal-attendance-agent-)
