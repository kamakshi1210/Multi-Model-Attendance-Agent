import time
import numpy as np
from typing import Dict, List, Any, Optional

class MultimodalFusionEngine:
    """
    Multimodal Signal Fusion & Deterministic Engagement Scoring (Epic 4.2 & 4.3).
    Combines timestamp-aligned visual attention/presence with audio noise and speech metrics.
    Computes an explainable, normalized engagement score (0-100) using configurable weights.
    """

    def __init__(
        self,
        weight_attention: float = 0.40,
        weight_presence: float = 0.30,
        weight_audio_activity: float = 0.15,
        weight_inverse_noise: float = 0.15
    ):
        # Configurable heuristic weights (sum = 1.0)
        # Note: Documented as an interpretable project heuristic, not a clinical measurement.
        self.w_att = weight_attention
        self.w_pres = weight_presence
        self.w_act = weight_audio_activity
        self.w_noise = weight_inverse_noise

        # Temporal slice history: list of { timestamp, elapsed_sec, participant_count, avg_attention, presence_ratio, audio_activity, noise_db, engagement_score }
        self.fusion_history: List[Dict[str, Any]] = []
        self.session_start_time: Optional[float] = None

    def reset_session(self):
        """Reset historical timeline when a session starts"""
        self.fusion_history = []
        self.session_start_time = time.time()

    def fuse_signals(
        self,
        vision_metrics: Dict[str, Any],
        audio_metrics: Optional[Dict[str, Any]] = None,
        session_elapsed_seconds: float = 0.0
    ) -> Dict[str, Any]:
        """
        Fuses real-time vision state and audio state into a unified time slice (Epic 4.2).
        Calculates normalized engagement score (Epic 4.3).
        """
        now = time.time()
        if self.session_start_time is None:
            self.session_start_time = now

        elapsed = session_elapsed_seconds if session_elapsed_seconds > 0 else (now - self.session_start_time)

        # 1. Vision Feature Extraction
        people = vision_metrics.get('people', [])
        participant_count = len(people)

        if participant_count > 0:
            attentions = [p.get('attention', 50.0) for p in people]
            avg_attention = float(np.mean(attentions))
            # Presence ratio: proportion of confirmed participants active in this slice
            presence_ratio = min(1.0, participant_count / max(1, vision_metrics.get('total_people', participant_count)))
        else:
            avg_attention = 0.0
            presence_ratio = 0.0

        # 2. Audio Feature Extraction
        if audio_metrics:
            noise_db = float(audio_metrics.get('noise_db', 40.0))
            # Normalized audio activity ratio (0.0 to 1.0)
            audio_activity = float(audio_metrics.get('activity_ratio', 0.2))
        else:
            noise_db = 40.0
            audio_activity = 0.2

        # 3. Normalized Signal Components (0.0 to 1.0 scale)
        norm_attention = min(1.0, max(0.0, avg_attention / 100.0))
        norm_presence = min(1.0, max(0.0, presence_ratio))
        norm_activity = min(1.0, max(0.0, audio_activity))

        # Inverse noise penalty: moderate conversation (45-65 dB) is good; loud distraction (>75 dB) or dead silence (<35 dB) is penalized
        if 40.0 <= noise_db <= 65.0:
            norm_noise_quality = 1.0
        elif noise_db < 40.0:
            norm_noise_quality = 0.8 # quiet lecture
        else:
            # Degrades linearly from 65 dB down to 0 at 95 dB
            norm_noise_quality = max(0.1, 1.0 - ((noise_db - 65.0) / 30.0))

        # 4. Deterministic Engagement Scoring Formula (Epic 4.3)
        raw_score = (
            (self.w_att * norm_attention) +
            (self.w_pres * norm_presence) +
            (self.w_act * norm_activity) +
            (self.w_noise * norm_noise_quality)
        )
        # Normalize to 0-100 scale
        engagement_score = round(float(raw_score * 100.0), 1)

        # Interpret status
        if engagement_score >= 75.0:
            state = "High Engagement"
        elif engagement_score >= 50.0:
            state = "Moderate Engagement"
        elif engagement_score >= 30.0:
            state = "Low Attention"
        else:
            state = "Inactive / Distracted"

        # 5. Timestamp-aligned Record
        slice_record = {
            "timestamp": now,
            "elapsed_seconds": round(elapsed, 1),
            "participant_count": participant_count,
            "average_attention": round(avg_attention, 1),
            "presence_ratio": round(presence_ratio, 2),
            "audio_activity": round(audio_activity, 2),
            "noise_level_db": round(noise_db, 1),
            "engagement_score": engagement_score,
            "state": state,
            "engagement_state": state
        }

        # Keep rolling slice history
        self.fusion_history.append(slice_record)
        if len(self.fusion_history) > 600: # Retain last ~10-20 minutes of slices
            self.fusion_history.pop(0)

        return slice_record

    def get_latest_fused_metrics(self) -> Dict[str, Any]:
        """Returns the most recent slice record or default idle state"""
        if self.fusion_history:
            return self.fusion_history[-1]
        return {
            "engagement_score": 0.0,
            "engagement_state": "Optimal",
            "state": "Optimal",
            "average_attention": 0.0,
            "presence_ratio": 0.0,
            "audio_activity": 0.0,
            "noise_level_db": 40.0
        }

    def get_session_summary_for_gemini(
        self,
        total_duration_seconds: float = 0.0,
        session_id: Optional[str] = None,
        person_history: Optional[Dict[str, Any]] = None,
        audio_summary: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Aggregates session timeline into a compact structured representation for Gemini (Rule 5).
        Gemini receives structured statistics, NOT raw frames.
        """
        if not self.fusion_history:
            return {
                "session_id": session_id or "unknown",
                "session_duration_seconds": round(total_duration_seconds, 1),
                "attendance_rate": 0.0,
                "average_attention": 0.0,
                "average_audio_activity": 0.0,
                "average_noise_level_db": 40.0,
                "overall_engagement_score": 0.0,
                "low_engagement_periods": [],
                "high_engagement_periods": []
            }

        scores = [h['engagement_score'] for h in self.fusion_history]
        attentions = [h['average_attention'] for h in self.fusion_history]
        presences = [h['presence_ratio'] for h in self.fusion_history]
        activities = [h['audio_activity'] for h in self.fusion_history]
        noises = [h['noise_level_db'] for h in self.fusion_history]

        overall_score = float(np.mean(scores))
        overall_attn = float(np.mean(attentions))
        overall_pres = float(np.mean(presences))
        overall_act = float(np.mean(activities))
        overall_noise = float(np.mean(noises))

        # Detect notable engagement periods
        low_periods = []
        high_periods = []
        current_low_start = None
        current_high_start = None

        for h in self.fusion_history:
            t = h['elapsed_seconds']
            s = h['engagement_score']

            if s < 50.0:
                if current_low_start is None:
                    current_low_start = t
            else:
                if current_low_start is not None:
                    if t - current_low_start >= 10.0: # Significant low period (>=10s)
                        low_periods.append({"start_seconds": int(current_low_start), "end_seconds": int(t)})
                    current_low_start = None

            if s >= 75.0:
                if current_high_start is None:
                    current_high_start = t
            else:
                if current_high_start is not None:
                    if t - current_high_start >= 10.0:
                        high_periods.append({"start_seconds": int(current_high_start), "end_seconds": int(t)})
                    current_high_start = None

        duration = total_duration_seconds if total_duration_seconds > 0 else (
            self.fusion_history[-1]['elapsed_seconds'] if self.fusion_history else 0.0
        )

        return {
            "session_duration_seconds": round(duration, 1),
            "attendance_rate": round(overall_pres, 2),
            "average_attention": round(overall_attn, 1),
            "average_audio_activity": round(overall_act, 2),
            "average_noise_level_db": round(overall_noise, 1),
            "overall_engagement_score": round(overall_score, 1),
            "low_engagement_periods": low_periods[:3],
            "high_engagement_periods": high_periods[:3]
        }
