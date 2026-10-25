import unittest
from unittest.mock import MagicMock
import types
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock external vision dependencies if running in minimal environment
if 'cv2' not in sys.modules:
    sys.modules['cv2'] = MagicMock()

if 'mediapipe' not in sys.modules or 'mediapipe.tasks' not in sys.modules:
    m = types.ModuleType('mediapipe')
    t = types.ModuleType('tasks')
    p = MagicMock()
    v = MagicMock()
    setattr(t, 'python', p)
    setattr(p, 'vision', v)
    setattr(m, 'tasks', t)
    sys.modules['mediapipe'] = m
    sys.modules['mediapipe.tasks'] = t
    sys.modules['mediapipe.tasks.python'] = p
    sys.modules['mediapipe.tasks.python.vision'] = v

if 'deep_sort_realtime' not in sys.modules:
    ds = types.ModuleType('deep_sort_realtime')
    dst = types.ModuleType('deepsort_tracker')
    setattr(dst, 'DeepSort', MagicMock)
    setattr(ds, 'deepsort_tracker', dst)
    sys.modules['deep_sort_realtime'] = ds
    sys.modules['deep_sort_realtime.deepsort_tracker'] = dst

from core.database import init_db
from core.session_manager import (
    SessionManager,
    ATTENDANCE_PRESENT_THRESHOLD,
    ATTENDANCE_PARTIAL_THRESHOLD
)

class TestAttendanceLogic(unittest.TestCase):
    def setUp(self):
        init_db()
        self.manager = SessionManager()

    def test_anonymous_id_assignment(self):
        """Participants must be mapped to sequential anonymous labels (Rule 3)."""
        id1 = self.manager.get_anonymous_id(1)
        id2 = self.manager.get_anonymous_id(2)
        id1_again = self.manager.get_anonymous_id(1)

        self.assertEqual(id1, "Participant 01")
        self.assertEqual(id2, "Participant 02")
        self.assertEqual(id1_again, "Participant 01") # Consistency check

    def test_presence_threshold_constants(self):
        """Attendance thresholds must match required specification."""
        self.assertEqual(ATTENDANCE_PRESENT_THRESHOLD, 75.0)
        self.assertEqual(ATTENDANCE_PARTIAL_THRESHOLD, 40.0)

    def test_attendance_status_classification(self):
        """Verify attendance grading according to presence percentage."""
        def classify(pct):
            if pct >= ATTENDANCE_PRESENT_THRESHOLD:
                return "Present"
            elif pct >= ATTENDANCE_PARTIAL_THRESHOLD:
                return "Partial"
            return "Absent"

        self.assertEqual(classify(100.0), "Present")
        self.assertEqual(classify(75.0), "Present")
        self.assertEqual(classify(74.9), "Partial")
        self.assertEqual(classify(40.0), "Partial")
        self.assertEqual(classify(39.9), "Absent")
        self.assertEqual(classify(0.0), "Absent")

    def test_session_lifecycle(self):
        """Starting and stopping sessions must update manager state correctly."""
        start_res = self.manager.start_session("Teacher_A", "Room_101")
        self.assertEqual(start_res['status'], 'started')
        self.assertIsNotNone(self.manager.active_session_id)

        status = self.manager.get_status()
        self.assertTrue(status['session_active'])

        stop_res = self.manager.stop_session()
        self.assertEqual(stop_res['status'], 'stopped')
        self.assertIsNone(self.manager.active_session_id)

if __name__ == '__main__':
    unittest.main()
