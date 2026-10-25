import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.gemini_agent import GeminiMultimodalAgent, StructuredAIInsights, StudentReflection

class TestGeminiAgent(unittest.TestCase):
    def setUp(self):
        self.agent = GeminiMultimodalAgent()

    def test_structured_ai_insights_schema(self):
        """StructuredAIInsights schema must enforce required attributes."""
        insights = StructuredAIInsights(
            session_summary="Test summary of session progress.",
            engagement_interpretation="Telemetry indicates sustained focus.",
            teaching_suggestions=["Provide interactive checkpoint.", "Maintain pacing."],
            notable_periods=["Peak attention at second 45."]
        )
        self.assertEqual(insights.session_summary, "Test summary of session progress.")
        self.assertEqual(len(insights.teaching_suggestions), 2)

    def test_student_reflection_schema(self):
        """StudentReflection schema must enforce anonymous participant coaching format."""
        reflection = StudentReflection(
            participant_id="Participant 01",
            presence_summary="Present for 90% of session.",
            engagement_pattern="High visual attention observed.",
            constructive_reflection="Keep engaging with complex derivations."
        )
        self.assertEqual(reflection.participant_id, "Participant 01")
        self.assertTrue(reflection.participant_id.startswith("Participant"))

    def test_grounded_fallback_insights_generation(self):
        """When API key is offline, agent must return deterministic grounded insights from real data."""
        telemetry = {
            'session_duration_seconds': 120.0,
            'attendance_rate': 0.85,
            'average_attention': 78.5,
            'average_audio_activity': 0.32,
            'average_noise_level_db': 54.0,
            'overall_engagement_score': 81.2,
            'low_engagement_periods': [],
            'high_engagement_periods': [{'start_seconds': 10, 'end_seconds': 60}]
        }
        result = self.agent.generate_classroom_insights(telemetry)
        
        self.assertIsInstance(result, StructuredAIInsights)
        self.assertIn("81.2", result.session_summary)
        self.assertGreater(len(result.teaching_suggestions), 0)

    def test_student_reflection_generation(self):
        """Student reflection must produce non-judgmental explainable insights."""
        student_data = {
            'id': 'Participant 03',
            'presence_percentage': 88.0,
            'active_duration': 140.0,
            'attendance_status': 'Present',
            'avg_attention': 76.0
        }
        reflection = self.agent.generate_student_reflection(student_data)
        
        self.assertIsInstance(reflection, StudentReflection)
        self.assertEqual(reflection.participant_id, "Participant 03")
        self.assertIn("Present", reflection.presence_summary)
        self.assertGreater(len(reflection.constructive_reflection), 10)

if __name__ == '__main__':
    unittest.main()
