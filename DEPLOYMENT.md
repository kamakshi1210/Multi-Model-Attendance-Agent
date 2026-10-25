# Deployment & Production Architecture Guide

This document outlines deployment configurations, containerization, and hosting instructions for the **Multimodal Attendance & Engagement Agent**.

---

## 🔒 Crucial Production Rule: HTTPS for MediaDevices

> [!IMPORTANT]
> Modern web browsers (Google Chrome, Microsoft Edge, Safari) strictly enforce that `navigator.mediaDevices.getUserMedia` (webcam and microphone access) **only functions over secure origins**:
> - `http://localhost` or `http://127.0.0.1` (Allowed for local testing)
> - `https://your-domain.com` (Required for all remote/production deployments)
> 
> If you deploy the frontend over plain remote `http://`, the browser will automatically block camera and microphone access. Always configure an SSL certificate (automatic via Render, Vercel, Railway, Caddy, or Let's Encrypt).

---

## 🐳 Option 1: Single-Container Deployment (Recommended)

The repository includes a multi-stage [`Dockerfile`](Dockerfile) that:
1. Builds the React 19 frontend into optimized production static assets.
2. Packages the Python 3.12 FastAPI backend with required Linux OpenCV dependencies (`libgl1`, `libglib2.0-0`).
3. Embeds and serves the React dashboard directly via FastAPI on port 8000.

### Local Docker Run
```bash
# 1. Build and run with Docker Compose
docker-compose up --build

# 2. Or build directly with Docker
docker build -t multimodal-agent .
docker run -p 8000:8000 -e GEMINI_API_KEY="your_api_key_here" multimodal-agent
```
Open `http://localhost:8000` in your browser.

---

## ☁️ Option 2: Deploy to Cloud Platforms

### A. Deploy to Render (Free / Low Cost)
1. Push your repository to GitHub.
2. Sign in to [Render](https://render.com) and click **New +** -> **Web Service**.
3. Connect your GitHub repository: `https://github.com/Prithviraj-Singh0268/Multimodal-attendance-agent-`.
4. Select **Docker** as the Runtime (it will automatically detect the [`Dockerfile`](Dockerfile)).
5. Under **Environment Variables**, add:
   - `GEMINI_API_KEY` = your Google Gemini API key
   - `PORT` = `8000`
6. Click **Deploy Web Service**. Render provides a free `https://your-app.onrender.com` domain with automatic SSL certificates!

### B. Deploy to Railway
1. Sign in to [Railway](https://railway.app).
2. Click **New Project** -> **Deploy from GitHub repo**.
3. Select this repository.
4. Under **Variables**, add `GEMINI_API_KEY`.
5. Under **Settings**, generate a public networking domain (`https://...up.railway.app`).

### C. Deploy to Hugging Face Spaces (Docker Space)
1. Create a new Space on [Hugging Face](https://huggingface.co/spaces).
2. Select **Docker** as the Space SDK.
3. Push or mirror the repository files.
4. Add `GEMINI_API_KEY` to **Settings -> Repository secrets**.
5. Hugging Face will automatically build and host the app with free HTTPS and GPU/CPU acceleration.

---

## 🖥️ Option 3: Local Offline Classroom Server (Institutional Deployment)

For university classrooms or corporate seminar rooms without reliable high-speed internet:
1. Run the system on the teacher's workstation or local classroom server via [`start_system.bat`](start_system.bat).
2. Connect the room's high-definition wide-angle webcam and conference microphone.
3. Because the system runs on `localhost`, all browser media APIs operate with zero network latency.
4. If an external internet connection is unavailable, `GeminiMultimodalAgent` automatically executes deterministic, telemetry-grounded local pedagogical reasoning without external API calls.
