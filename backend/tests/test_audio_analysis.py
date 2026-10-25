import unittest
import numpy as np
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.audio_analysis import AudioAnalyzer

class TestAudioAnalysis(unittest.TestCase):
    def setUp(self):
        self.analyzer = AudioAnalyzer(sample_rate=16000)

    def test_silence_input(self):
        """Zero input signal should yield quiet ambient dB and zero speech ratio."""
        silence = np.zeros(8000, dtype=np.float32)
        metrics = self.analyzer.analyze_audio_chunk(silence)
        
        self.assertIsNotNone(metrics)
        self.assertAlmostEqual(metrics['noise_db'], 30.0, delta=1.0) # Lower bound 30 dB SPL
        self.assertFalse(metrics['is_speaking'])
        self.assertEqual(metrics['speech_ratio'], 0.0)

    def test_synthetic_speech_signal(self):
        """Active oscillating signal with typical speech frequency should be recognized."""
        sample_rate = 16000
        t = np.linspace(0, 0.5, int(sample_rate * 0.5), endpoint=False)
        # Synthetic speech-like harmonic signal with typical speech RMS amplitude
        signal = (0.12 * np.sin(2 * np.pi * 300 * t)).astype(np.float32)

        metrics = self.analyzer.analyze_audio_chunk(signal)
        self.assertIsNotNone(metrics)
        self.assertGreater(metrics['noise_db'], 40.0)
        self.assertTrue(metrics['is_speaking'])
        self.assertGreater(metrics['speech_ratio'], 0.0)

    def test_decibel_clamping_limits(self):
        """Noise level must remain calibrated within the physical classroom scale (30 - 95 dB SPL)."""
        # Very quiet input
        quiet = np.full(8000, 1e-8, dtype=np.float32)
        m_quiet = self.analyzer.analyze_audio_chunk(quiet)
        self.assertGreaterEqual(m_quiet['noise_db'], 30.0)

        # Extremely loud clipping input
        loud = np.ones(8000, dtype=np.float32)
        m_loud = self.analyzer.analyze_audio_chunk(loud)
        self.assertLessEqual(m_loud['noise_db'], 95.0)

    def test_session_reset(self):
        """Reset should clear chunk counters and rolling history."""
        signal = np.random.uniform(-0.3, 0.3, 8000).astype(np.float32)
        self.analyzer.analyze_audio_chunk(signal)
        self.assertGreater(len(self.analyzer.history_samples), 0)

        self.analyzer.reset_session()
        summary = self.analyzer.get_session_summary()
        self.assertEqual(summary['total_audio_frames'], 0)
        self.assertEqual(len(self.analyzer.history_samples), 0)

if __name__ == '__main__':
    unittest.main()
