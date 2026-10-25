import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.multimodal_fusion import MultimodalFusionEngine

class TestMultimodalFusion(unittest.TestCase):
    def setUp(self):
        self.engine = MultimodalFusionEngine()

    def test_high_engagement_conditions(self):
        """High visual attention + high presence + moderate audio should yield High Engagement."""
        vision = {
            'people': [
                {'id': 'Participant 01', 'attention': 90.0},
                {'id': 'Participant 02', 'attention': 85.0}
            ]
        }
        audio = {
            'speech_ratio': 0.35,
            'noise_db': 55.0,
            'activity_type': 'lecture'
        }
        result = self.engine.fuse_signals(vision, audio)
        
        self.assertIn('engagement_score', result)
        self.assertGreaterEqual(result['engagement_score'], 75.0)
        self.assertEqual(result['engagement_state'], 'High Engagement')

    def test_low_attention_conditions(self):
        """Distracted participants + silent or noisy room should drop score."""
        vision = {
            'people': [
                {'id': 'Participant 01', 'attention': 20.0},
                {'id': 'Participant 02', 'attention': 25.0}
            ]
        }
        audio = {
            'speech_ratio': 0.05,
            'noise_db': 88.0,
            'activity_type': 'excessive_noise'
        }
        result = self.engine.fuse_signals(vision, audio)
        
        self.assertLess(result['engagement_score'], 50.0)
        self.assertIn(result['engagement_state'], ['Low Attention', 'Inactive / Distracted'])

    def test_score_bounded_between_0_and_100(self):
        """Engagement score must always stay strictly within [0, 100]."""
        # Worst case
        worst_vis = {'people': []}
        worst_aud = {'speech_ratio': 0.0, 'noise_db': 95.0}
        r_worst = self.engine.fuse_signals(worst_vis, worst_aud)
        self.assertGreaterEqual(r_worst['engagement_score'], 0.0)

        # Best case
        best_vis = {'people': [{'attention': 100.0} for _ in range(5)]}
        best_aud = {'speech_ratio': 0.45, 'noise_db': 52.0}
        r_best = self.engine.fuse_signals(best_vis, best_aud)
        self.assertLessEqual(r_best['engagement_score'], 100.0)

    def test_gemini_summary_payload_structure(self):
        """Rule 5: Aggregation must return compact numerical telemetry, never raw video."""
        for _ in range(5):
            self.engine.fuse_signals(
                {'people': [{'id': 'Participant 01', 'attention': 80.0}]},
                {'speech_ratio': 0.3, 'noise_db': 50.0}
            )

        summary = self.engine.get_session_summary_for_gemini(total_duration_seconds=30.0)
        self.assertIn('session_duration_seconds', summary)
        self.assertIn('overall_engagement_score', summary)
        self.assertIn('average_attention', summary)
        self.assertIn('average_noise_level_db', summary)
        # Ensure no binary or frame data is leaked
        for key, val in summary.items():
            self.assertNotIsInstance(val, bytes)

if __name__ == '__main__':
    unittest.main()
