import cv2
import time
import asyncio
import numpy as np
from fastapi import WebSocket

class CameraService:
    def __init__(self, camera_id=0):
        self.camera_id = camera_id
        self.cap = None
        self.is_running = False
        self._frame_count = 0

    def start(self):
        self.is_running = True
        try:
            if self.cap is None:
                self.cap = cv2.VideoCapture(self.camera_id)
                if not self.cap.isOpened():
                    self.cap.release()
                    self.cap = None
        except Exception:
            self.cap = None

    def stop(self):
        self.is_running = False
        if self.cap:
            try:
                self.cap.release()
            except Exception:
                pass
            self.cap = None

    def generate_fallback_frame(self):
        """Generates an animated high-tech classroom simulation feed when no physical camera is attached"""
        self._frame_count += 1
        t = self._frame_count * 0.05
        
        # 640x480 dark classroom background
        frame = np.full((480, 640, 3), (22, 18, 14), dtype=np.uint8)
        
        # Subtle ambient grid lines
        for y in range(60, 480, 60):
            cv2.line(frame, (0, y), (640, y), (35, 30, 24), 1)
        for x in range(80, 640, 80):
            cv2.line(frame, (x, 0), (x, 480), (35, 30, 24), 1)
            
        # Draw 2 simulated participant stations
        # Participant 01
        p1_x = int(180 + np.sin(t * 0.7) * 8)
        p1_y = int(220 + np.cos(t * 0.5) * 5)
        # Head / face
        cv2.ellipse(frame, (p1_x, p1_y), (48, 62), 0, 0, 360, (210, 180, 140), -1)
        cv2.ellipse(frame, (p1_x, p1_y), (48, 62), 0, 0, 360, (80, 220, 100), 2)
        # Hair
        cv2.ellipse(frame, (p1_x, p1_y - 28), (48, 30), 0, 180, 360, (60, 45, 30), -1)
        # Eyes
        eye_offset = int(np.sin(t) * 2)
        cv2.circle(frame, (p1_x - 18, p1_y - 8), 6, (255, 255, 255), -1)
        cv2.circle(frame, (p1_x + 18, p1_y - 8), 6, (255, 255, 255), -1)
        cv2.circle(frame, (p1_x - 18 + eye_offset, p1_y - 8), 3, (40, 40, 40), -1)
        cv2.circle(frame, (p1_x + 18 + eye_offset, p1_y - 8), 3, (40, 40, 40), -1)
        # Shoulders / Torso
        cv2.ellipse(frame, (p1_x, p1_y + 115), (75, 55), 0, 0, 360, (70, 50, 140), -1)

        # Participant 02
        p2_x = int(450 + np.cos(t * 0.6) * 10)
        p2_y = int(230 + np.sin(t * 0.4) * 6)
        cv2.ellipse(frame, (p2_x, p2_y), (46, 60), 0, 0, 360, (195, 165, 130), -1)
        cv2.ellipse(frame, (p2_x, p2_y), (46, 60), 0, 0, 360, (100, 200, 255), 2)
        # Hair
        cv2.ellipse(frame, (p2_x, p2_y - 25), (46, 28), 0, 180, 360, (40, 30, 20), -1)
        # Eyes
        cv2.circle(frame, (p2_x - 16, p2_y - 6), 6, (255, 255, 255), -1)
        cv2.circle(frame, (p2_x + 16, p2_y - 6), 6, (255, 255, 255), -1)
        cv2.circle(frame, (p2_x - 16, p2_y - 6), 3, (30, 30, 30), -1)
        cv2.circle(frame, (p2_x + 16, p2_y - 6), 3, (30, 30, 30), -1)
        # Shoulders / Torso
        cv2.ellipse(frame, (p2_x, p2_y + 110), (70, 50), 0, 0, 360, (40, 100, 120), -1)

        # Status badge overlay
        cv2.rectangle(frame, (10, 10), (330, 42), (0, 0, 0), -1)
        cv2.putText(frame, "LIVE SIMULATED CLASSROOM FEED", (18, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (80, 230, 120), 2)
        return frame

    def get_frame(self):
        if self.is_running and self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret and frame is not None:
                return frame
        # If no physical camera exists (e.g. Render cloud), use simulated classroom frame
        return self.generate_fallback_frame()

