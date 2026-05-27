import unittest
import os
import sys
import numpy as np
from PIL import Image

# Ensure workspace path imports resolve correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_engine.advanced_forensics.exif_scanner import EXIFForensicScanner
from ai_engine.advanced_forensics.visual_consistency import VisualConsistencyAnalyzer

class TestAdvancedForensics(unittest.TestCase):
    """
    Validates EXIF metadata scanners and spatial-temporal blink/lip speech metrics.
    """
    def setUp(self):
        # Create a temporary dummy image to test EXIF parsing
        self.test_img_path = "temp_dummy_exif_test.png"
        img = Image.new('RGB', (10, 10), color = 'red')
        img.save(self.test_img_path)

    def tearDown(self):
        if os.path.exists(self.test_img_path):
            os.remove(self.test_img_path)

    def test_exif_scanner_execution(self):
        """
        EXIFForensicScanner should ingest files and parse formats and EXIF tags cleanly.
        """
        report = EXIFForensicScanner.scan_image_metadata(self.test_img_path)
        self.assertTrue(report["success"])
        self.assertEqual(report["extracted_tags"]["format"], "PNG")
        self.assertFalse(report["has_exif"]) # PNGs saved this way lack EXIF metadata
        self.assertEqual(report["risk_verdict"], "SUSPICIOUS_STRIPPED")

    def test_eye_aspect_ratio_calculation(self):
        """
        VisualConsistencyAnalyzer should compute standard Eye Aspect Ratio (EAR).
        """
        # Create standard eye coordinate points: P1-P6
        # Open eye geometry
        eye_open = np.array([
            [1.0, 2.0], [2.0, 3.0], [3.0, 3.0], 
            [4.0, 2.0], [3.0, 1.0], [2.0, 1.0]
        ])
        
        ear_open = VisualConsistencyAnalyzer.calculate_eye_aspect_ratio(eye_open)
        self.assertTrue(ear_open > 0.0)

        # Closed eye geometry (vertical distances are smaller)
        eye_closed = np.array([
            [1.0, 2.0], [2.0, 2.1], [3.0, 2.1], 
            [4.0, 2.0], [3.0, 1.9], [2.0, 1.9]
        ])
        ear_closed = VisualConsistencyAnalyzer.calculate_eye_aspect_ratio(eye_closed)
        
        # EAR should decrease when the eye closes
        self.assertTrue(ear_closed < ear_open)

    def test_blink_timeline_sequence(self):
        """
        Blink analyzer should count dips in EAR timeline representing closed eyes.
        """
        # Generate timeline representing 30 frames: normal EAR is 0.35, blinking dips to 0.15
        timeline = [0.35] * 10 + [0.15] * 3 + [0.35] * 17
        report = VisualConsistencyAnalyzer.analyze_blink_sequence(timeline, fps=30.0)
        
        self.assertEqual(report["blink_count"], 1)
        self.assertFalse(report["absence_of_blinking"])
        self.assertFalse(report["anomalous_blink_speed"])

    def test_lipsync_alignment_cross_correlation(self):
        """
        Speech lip check should measure cross-correlation coefficient of facial motion.
        """
        # Scenario A: Correlated movement (mouth opening matches audio peaks perfectly)
        mouth_amp = np.sin(np.linspace(0, 10, 50))
        audio_env = np.sin(np.linspace(0, 10, 50))
        
        report_aligned = VisualConsistencyAnalyzer.check_lipsync_alignment(mouth_amp, audio_env)
        self.assertTrue(report_aligned["is_synchronized"])
        self.assertTrue(report_aligned["correlation_coefficient"] > 0.9)

        # Scenario B: Mismatched movement
        audio_mismatch = np.cos(np.linspace(0, 40, 50)) # different frequency entirely
        report_misaligned = VisualConsistencyAnalyzer.check_lipsync_alignment(mouth_amp, audio_mismatch)
        self.assertFalse(report_misaligned["is_synchronized"])
        self.assertTrue(report_misaligned["lipsync_risk_score"] > 0.0)

if __name__ == "__main__":
    unittest.main()
