import numpy as np
import time
from typing import Dict, Optional, Any

class AudioAnalyzer:
    """
    Audio signal extraction and explainable activity analysis (Epic 3.1 & 3.2).
    Processes 16kHz mono audio chunks streamed over WebSocket.
    Computes RMS energy, calibrated decibels, zero-crossing rate, speech ratio, and activity states.
    """

    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        # Session-level accumulators
        self.history_samples: list[float] = [] # Recent RMS values
        self.speech_frames: int = 0
        self.total_frames: int = 0
        self.noise_db_history: list[float] = []
        self.max_window_size = 100 # ~25 seconds of chunks (at 4096 samples/chunk ~0.25s)

    def reset_session(self):
        """Reset session metrics when a new session starts"""
        self.history_samples = []
        self.speech_frames = 0
        self.total_frames = 0
        self.noise_db_history = []

    def analyze_audio_chunk(self, audio_data: Any) -> Optional[Dict[str, Any]]:
        """
        Analyzes a single PCM audio chunk:
        - Normalizes channels and format
        - Computes RMS energy and calibrated decibels (dB)
        - Computes Zero Crossing Rate (ZCR)
        - Detects speech activity vs background noise
        - Returns timestamped audio metrics
        """
        try:
            # 1. Format and Channel Normalization (Epic 3.1)
            if isinstance(audio_data, bytes):
                # 16-bit PCM conversion
                y = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
            elif isinstance(audio_data, np.ndarray):
                y = audio_data.astype(np.float32)
            else:
                return None

            if len(y) == 0:
                return None

            # Multi-channel normalization: convert stereo to mono if necessary
            if y.ndim > 1:
                y = np.mean(y, axis=1)

            # 2. RMS Energy & Decibel Calculation (Epic 3.2)
            rms = float(np.sqrt(np.mean(y ** 2)))
            # Calibrated SPL approximation: maps typical mic floor (-60 dBFS) to ~35 dB and loud (-6 dBFS) to ~85 dB
            raw_dbfs = 20.0 * np.log10(max(rms, 1e-5))
            calibrated_db = max(30.0, min(95.0, 95.0 + raw_dbfs))

            # 3. Zero-Crossing Rate (ZCR) - Explainable speech cue
            zcr = float(np.mean(np.abs(np.diff(np.sign(y)))) / 2.0) if len(y) > 1 else 0.0

            # 4. Activity Classification & Speech Detection
            # Speech typically has moderate energy (0.008 - 0.20) and ZCR within 0.03 - 0.25
            is_speech = False
            if rms < 0.006:
                activity_type = 'silent'
            elif rms > 0.22:
                activity_type = 'chaotic_loud'
            elif 0.02 <= zcr <= 0.25:
                activity_type = 'normal_discussion'
                is_speech = True
            else:
                activity_type = 'background_noise'

            # 5. Track Window & Session-Level Metrics
            self.total_frames += 1
            if is_speech:
                self.speech_frames += 1

            self.history_samples.append(rms)
            self.noise_db_history.append(calibrated_db)
            if len(self.history_samples) > self.max_window_size:
                self.history_samples.pop(0)
                self.noise_db_history.pop(0)

            # Instantaneous and rolling speech ratio
            rolling_speech_ratio = (self.speech_frames / max(1, self.total_frames))
            active_ratio = sum(1 for r in self.history_samples if r >= 0.006) / max(1, len(self.history_samples))

            return {
                'timestamp': time.time(),
                'noise_db': round(calibrated_db, 1),
                'rms_energy': round(rms, 4),
                'zcr': round(zcr, 3),
                'speech_ratio': round(float(rolling_speech_ratio), 2),
                'activity_ratio': round(float(active_ratio), 2),
                'activity_type': activity_type,
                'is_speaking': is_speech,
                'engagement_level': self._map_to_engagement(calibrated_db, activity_type)
            }
        except Exception as e:
            print(f"Audio analysis error: {e}")
            return None

    def _map_to_engagement(self, noise_db: float, activity: str) -> str:
        if activity == 'silent':
            return 'passive'
        elif activity == 'normal_discussion':
            return 'active_discussion'
        elif activity == 'chaotic_loud':
            return 'distracted_loud'
        return 'moderate'

    def get_session_summary(self) -> Dict[str, Any]:
        """Produce session-level aggregated audio metrics (Epic 3.2)"""
        avg_db = float(np.mean(self.noise_db_history)) if self.noise_db_history else 40.0
        speech_ratio = (self.speech_frames / max(1, self.total_frames)) if self.total_frames > 0 else 0.0
        return {
            'average_noise_db': round(avg_db, 1),
            'speech_ratio': round(float(speech_ratio), 2),
            'total_audio_frames': self.total_frames,
            'speech_frames': self.speech_frames
        }
