import os
import json
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

# ====================================================================
# Pydantic Schemas for Structured AI Insights (Epic 4.1 & Epic 5)
# ====================================================================

class StructuredAIInsights(BaseModel):
    session_summary: str = Field(description="2-3 sentence overview of classroom attendance and overall dynamics.")
    engagement_interpretation: str = Field(description="Interpretation of attention, presence, and audio activity trends.")
    teaching_suggestions: List[str] = Field(description="2-4 actionable, assistive suggestions for the instructor.")
    notable_periods: List[str] = Field(description="Observed periods of peak engagement or attention drop.")

class StudentReflection(BaseModel):
    participant_id: str
    presence_summary: str
    engagement_pattern: str
    constructive_reflection: str


# ====================================================================
# Gemini Multimodal Agent Implementation (Epic 4.1)
# ====================================================================

class GeminiMultimodalAgent:
    """
    Multimodal AI Agent powered by Google Gemini.
    Processes structured, time-windowed multimodal signals (vision + audio + attendance)
    to produce explainable pedagogical insights and student reflections.
    """

    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        self.model_name = os.environ.get("GEMINI_MODEL", "gemini-3.8-flash")
        self.client_type = None
        self.client = None

        if self.api_key and self.api_key != "your_gemini_api_key_here":
            self._init_gemini_client()
        else:
            print("[INFO] GEMINI_API_KEY not configured. Local grounded fallback active.")

    def _init_gemini_client(self):
        """Initializes either the modern google.genai client or legacy google.generativeai"""
        try:
            from google import genai
            self.client = genai.Client(api_key=self.api_key)
            self.client_type = "google-genai"
            print(f"[OK] Google Gemini Client initialized (SDK: google-genai, Model: {self.model_name})")
            return
        except Exception:
            pass

        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel(self.model_name)
            self.client_type = "google.generativeai"
            print(f"[OK] Google Gemini Client initialized (SDK: google.generativeai, Model: {self.model_name})")
        except Exception as e:
            print(f"[WARNING] Failed to initialize Gemini API client: {e}. Fallback active.")
            self.client = None

    def generate_classroom_insights(self, fused_data: Dict[str, Any]) -> StructuredAIInsights:
        """
        Receives fused multimodal session metrics and produces structured AI insights.
        """
        prompt = f"""
You are an expert pedagogical assistant analyzing real-time classroom multimodal telemetry.
Evaluate the following fused vision and audio metrics:

SESSION TELEMETRY:
- Session Duration: {fused_data.get('session_duration_seconds', 0)} seconds
- Presence / Attendance Rate: {int(fused_data.get('attendance_rate', 0.0) * 100)}%
- Average Visual Attention: {fused_data.get('average_attention', 0.0)}%
- Audio Speech Activity Ratio: {int(fused_data.get('average_audio_activity', 0.0) * 100)}%
- Ambient Noise Level: {fused_data.get('average_noise_level_db', 40.0)} dB
- Overall Multimodal Engagement Score: {fused_data.get('overall_engagement_score', 0.0)} / 100
- Low Engagement Periods: {fused_data.get('low_engagement_periods', [])}
- High Engagement Periods: {fused_data.get('high_engagement_periods', [])}

TASK:
Provide structured, assistive insights for the instructor.
Respond strictly in valid JSON matching this schema:
{{
  "session_summary": "Concise 2-sentence summary of the session dynamics.",
  "engagement_interpretation": "Objective analysis of student visual focus versus audio participation.",
  "teaching_suggestions": [
    "Actionable suggestion 1",
    "Actionable suggestion 2"
  ],
  "notable_periods": [
    "Observation of attention dip or peak"
  ]
}}
"""
        if self.client:
            try:
                raw_json = self._call_gemini_json(prompt)
                if raw_json:
                    data = json.loads(raw_json)
                    return StructuredAIInsights(**data)
            except Exception as e:
                print(f"[WARNING] Gemini API execution error: {e}. Falling back to deterministic reasoning.")

        return self._generate_grounded_fallback_insights(fused_data)

    def generate_student_reflection(self, student_data: Dict[str, Any]) -> StudentReflection:
        """
        Generates an encouraging, constructive reflection for an individual student (Epic 5.2).
        Non-judgmental, purely assistive.
        """
        pid = student_data.get('id', 'Participant')
        active_sec = student_data.get('active_duration', 0.0)
        presence_pct = student_data.get('presence_percentage', 0.0)
        status = student_data.get('attendance_status', 'N/A')
        attn = student_data.get('avg_attention', 0.0)

        prompt = f"""
You are an empathetic learning coach providing a private, non-judgmental session reflection for a student.
Student Data:
- ID: {pid}
- Time Active: {active_sec}s ({presence_pct}% of session)
- Attendance Status: {status}
- Average Attention Focus: {attn}%

Generate an encouraging reflection in valid JSON:
{{
  "participant_id": "{pid}",
  "presence_summary": "Brief summary of attendance presence.",
  "engagement_pattern": "Observation on focus and participation.",
  "constructive_reflection": "Encouraging, supportive tip for next class."
}}
"""
        if self.client:
            try:
                raw_json = self._call_gemini_json(prompt)
                if raw_json:
                    data = json.loads(raw_json)
                    return StudentReflection(**data)
            except Exception as e:
                print(f"[WARNING] Gemini student reflection error: {e}. Falling back.")

        # Grounded fallback
        return StudentReflection(
            participant_id=pid,
            presence_summary=f"Participated for {active_sec}s ({presence_pct}% session presence - {status}).",
            engagement_pattern=f"Maintained an average visual attention focus of {attn}%.",
            constructive_reflection="Consistent engagement observed. Consider active note-taking or asking questions during complex explanations."
        )

    def _call_gemini_json(self, prompt: str) -> Optional[str]:
        """Calls Gemini with JSON response constraint"""
        if self.client_type == "google-genai":
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={"response_mime_type": "application/json"}
            )
            return response.text
        elif self.client_type == "google.generativeai":
            response = self.client.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            return response.text
        return None

    def _generate_grounded_fallback_insights(self, fused_data: Dict[str, Any]) -> StructuredAIInsights:
        """
        Deterministic, rule-grounded fallback reasoning when API key is missing or network is offline.
        Uses REAL telemetry data rather than static fake strings.
        """
        attn = fused_data.get('average_attention', 70.0)
        noise = fused_data.get('average_noise_level_db', 45.0)
        score = fused_data.get('overall_engagement_score', 65.0)
        speech = fused_data.get('average_audio_activity', 0.3)
        low_p = fused_data.get('low_engagement_periods', [])

        suggestions = []
        if score < 50.0:
            summary = f"Session telemetry indicates reduced overall engagement ({score}/100) with attention averaging {attn}%."
            interpretation = "Visual attention drops coincided with low verbal activity. Participants may be fatigued or experiencing topic difficulty."
            suggestions.append("Introduce a short 2-minute active brainstorming break or interactive poll.")
            suggestions.append("Check for conceptual understanding by calling on volunteers for quick reactions.")
        elif noise > 70.0:
            summary = f"High energy session observed ({score}/100) with elevated classroom noise ({noise} dB)."
            interpretation = "Auditory telemetry indicates lively interaction, though background cross-talk may cause distraction."
            suggestions.append("Moderate group discussion volume to prevent cognitive fatigue.")
            suggestions.append("Summarize key takeaways on the whiteboard to refocus attention.")
        else:
            summary = f"Optimal session progress with engagement scoring {score}/100 and visual attention steady at {attn}%."
            interpretation = "Balanced multimodal harmony observed: visual tracking shows steady focus with normal discussion levels."
            suggestions.append("Maintain the current delivery pace; pacing aligns well with participant engagement.")
            suggestions.append("Introduce a challenging application problem to deepen retention.")

        notable = []
        if low_p:
            notable.append(f"Engagement dip detected between seconds {low_p[0]['start_seconds']} and {low_p[0]['end_seconds']}.")
        else:
            notable.append("Consistent, stable attention maintained throughout the observation window.")

        return StructuredAIInsights(
            session_summary=summary,
            engagement_interpretation=interpretation,
            teaching_suggestions=suggestions,
            notable_periods=notable
        )
