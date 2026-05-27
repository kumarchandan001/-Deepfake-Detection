import unittest
import os
import sys
import numpy as np
import time

# Ensure workspace path imports resolve correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_engine.realtime.frame_queue import ThreadSafeFrameQueue
from ai_engine.realtime.fps_monitor import FPSMonitor

class TestRealtimePipeline(unittest.TestCase):
    """
    Validates ThreadSafeFrameQueue overflow handling and FPS sliding window calculations.
    """
    def test_frame_queue_dropping(self):
        """
        ThreadSafeFrameQueue should drop oldest frames when pushing past max size.
        """
        # Create a queue of max size 3
        queue = ThreadSafeFrameQueue(maxsize=3)
        
        # Push 4 frames
        queue.put("frame_1")
        queue.put("frame_2")
        queue.put("frame_3")
        queue.put("frame_4")  # This should cause frame_1 to be dropped
        
        self.assertEqual(queue.size(), 3)
        
        # Pop frames and verify frame_1 was indeed dropped (First-In-First-Out)
        f2 = queue.get(block=False)
        f3 = queue.get(block=False)
        f4 = queue.get(block=False)
        
        self.assertEqual(f2, "frame_2")
        self.assertEqual(f3, "frame_3")
        self.assertEqual(f4, "frame_4")
        
        nil_val = queue.get(block=False) # Queue should be empty now
        self.assertIsNone(nil_val)

    def test_fps_monitor_calculation(self):
        """
        FPSMonitor should accurately report sliding-window frame frequencies.
        """
        monitor = FPSMonitor(window_size=5)
        
        # Simulate rendering 5 frames over 1 second total (approx 5 FPS)
        for _ in range(5):
            monitor.tick()
            time.sleep(0.05) # Sleep 50ms per frame update

        fps = monitor.get_fps()
        # Verify FPS is calculated and non-zero
        self.assertTrue(fps > 0)
        self.assertTrue(fps <= 100) # realistic upper bound

if __name__ == "__main__":
    unittest.main()
