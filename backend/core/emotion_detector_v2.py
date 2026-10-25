import cv2
import mediapipe as mp
import numpy as np
import os
from dataclasses import dataclass
from typing import Dict, List

# Modern Tasks API
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

@dataclass
class EmotionResult:
    emotion: str
    confidence: float
    explanation: str

class MediaPipeEmotionDetector:
    """
    Emotion detector using MediaPipe Tasks API (Python 3.13 Compatible)
    Uses 'core/face_landmarker.task' model.
    """
    
    def __init__(self):
        self.detector = None
        try:
            model_path = os.path.join(os.path.dirname(__file__), 'face_landmarker.task')
            
            if not os.path.exists(model_path):
                print(f"⚠️ Model not found at {model_path}. Trying absolute path...")
                # Fallback to relative from CWD
                model_path = os.path.abspath("core/face_landmarker.task")

            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Face Landmarker model missing at {model_path}")

            base_options = python.BaseOptions(model_asset_path=model_path)
            options = vision.FaceLandmarkerOptions(
                base_options=base_options,
                output_face_blendshapes=True,
                output_facial_transformation_matrixes=False,
                num_faces=10,
                min_face_detection_confidence=0.5,
                min_face_presence_confidence=0.5,
            )
            self.detector = vision.FaceLandmarker.create_from_options(options)
            print("[OK] MediaPipe (Tasks API) initialized successfully")
        except Exception as e:
            print(f"[WARNING] Error initializing MediaPipe Tasks: {e}")
            self.detector = None
    
    def detect(self, frame) -> List[Dict]:
        output = []
        if self.detector is None:
            return output
            
        try:
            # Prepare Image
            # MediaPipe Tasks expects SRGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            
            # Detect
            detection_result = self.detector.detect(mp_image)
            
            # Process Results
            if detection_result.face_landmarks:
                h, w, c = frame.shape
                
                for idx, landmarks in enumerate(detection_result.face_landmarks):
                    # Convert task landmarks objects to accessible list
                    # landmarks is a list of NormalizedLandmark
                    
                    points = np.array([(lm.x * w, lm.y * h) for lm in landmarks])
                    
                    # BBox
                    x_min, y_min = np.min(points, axis=0)
                    x_max, y_max = np.max(points, axis=0)
                    
                    box_x = max(0, x_min - 10)
                    box_y = max(0, y_min - 10)
                    box_w = min(w - box_x, (x_max - x_min) + 20)
                    box_h = min(h - box_y, (y_max - y_min) + 20)
                    
                    bbox = [int(box_x), int(box_y), int(box_w), int(box_h)]
                    
                    # Emotion Extraction 
                    # Note: tasks API landmarks are indexed same as legacy
                    emotion_data = self._extract_emotion_from_points(points)
                    
                    err_result = EmotionResult(
                        emotion=emotion_data['emotion'],
                        confidence=emotion_data['confidence'],
                        explanation=emotion_data['explanation']
                    )
                    
                    output.append({
                        'bbox': bbox,
                        'emotion': err_result,
                        'landmarks': points
                    })
                    
            return output
            
        except Exception as e:
            # print(f"❌ Detect Error: {e}")
            return []

    def _extract_emotion_from_points(self, points) -> Dict:
        # Re-implement using numpy points array directly
        # Left Eye: 159 (top), 145 (bottom)
        # Right Eye: 386 (top), 374 (bottom)
        # Mouth: 13 (upper), 14 (lower)
        
        try:
            left_eye_h = np.linalg.norm(points[159] - points[145])
            right_eye_h = np.linalg.norm(points[386] - points[374])
            
            # Normalize by face width (roughly 454 - 234)
            face_width = np.linalg.norm(points[454] - points[234])
            if face_width < 1: face_width = 1
            
            avg_eye_open = ((left_eye_h + right_eye_h) / 2) / face_width
            
            mouth_h = np.linalg.norm(points[13] - points[14])
            mouth_open = mouth_h / face_width
            
            # Heuristics (Adjusted for normalized values)
            # Normalized eye open typ ~0.05 - 0.1
            # Mouth open typ ~0.02 - 0.1
            
            if avg_eye_open > 0.06 and mouth_open > 0.05:
                emotion = 'happy'
                confidence = 0.92
                explanation = 'smiling'
            elif avg_eye_open < 0.03:
                emotion = 'bored'
                confidence = 0.85
                explanation = 'sleepy eyes'
            elif mouth_open > 0.1:
                emotion = 'surprised'
                confidence = 0.80
                explanation = 'mouth open'
            elif avg_eye_open > 0.05:
                emotion = 'engaged'
                confidence = 0.85
                explanation = 'attentive'
            else:
                emotion = 'neutral'
                confidence = 0.75
                explanation = 'baseline'
                
            return {
                'emotion': emotion,
                'confidence': confidence,
                'explanation': explanation
            }
        except:
             return {'emotion':'neutral', 'confidence':0.5, 'explanation':'error'}

