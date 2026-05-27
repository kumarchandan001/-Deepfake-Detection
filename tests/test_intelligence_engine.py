import unittest
import os
import sys
import numpy as np

# Ensure workspace path imports resolve correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_engine.intelligence.threat_graph import ThreatGraph
from ai_engine.intelligence.misinformation_detector import MisinformationDetector
from ai_engine.intelligence.identity_risk_engine import IdentityRiskEngine
from ai_engine.intelligence.campaign_tracker import CampaignTracker
from ai_engine.intelligence.anomaly_correlation import AnomalyCorrelator

class TestIntelligenceEngine(unittest.TestCase):
    """
    Validates topological campaign graphs, average perceptual hashes, high-profile identity
    exposure scoring, and anomaly Pearson correlation algorithms.
    """
    def setUp(self):
        # Create a dummy 8x8 image as BGR numpy matrix for perceptual hash tests
        self.dummy_img = np.zeros((8, 8, 3), dtype=np.uint8)
        # Create a contrasting textured mock image for hamming distance checks
        self.contrasting_img = np.zeros((8, 8, 3), dtype=np.uint8)
        self.contrasting_img[0:4, 0:4] = 255 # half-and-half contrast pattern

    def test_threat_graph_attributions(self):
        """
        ThreatGraph should build network clusters of nodes and serialize to D3 format.
        """
        graph = ThreatGraph()
        
        # Register nodes
        graph.add_actor("BOT_A1", "Twitter", risk_score=0.92)
        graph.add_media_asset("ASSET_M1", "video", verdict="DEEPFAKE")
        graph.add_forensic_finding("FIND_F1", confidence=0.88, anomaly_type="LAPLACIAN")
        
        # Link nodes
        graph.link_nodes("BOT_A1", "ASSET_M1", "GENERATE")
        graph.link_nodes("ASSET_M1", "FIND_F1", "EVIDENT")

        # Cluster detection
        clusters = graph.detect_coordinated_clusters()
        self.assertEqual(len(clusters), 1)
        self.assertIn("BOT_A1", clusters[0])

        # Verify serialization formats
        json_data = graph.serialize_to_json_format()
        self.assertTrue(len(json_data["nodes"]) >= 3)
        self.assertEqual(json_data["links"][0]["source"], "BOT_A1")

    def test_misinformation_detector_hashes(self):
        """
        MisinformationDetector should generate 64-bit aHash signatures and scan duplicates.
        """
        detector = MisinformationDetector()
        
        # Test 1: average hash representation
        hash1 = detector.compute_average_hash(self.dummy_img)
        self.assertEqual(len(hash1), 16) # 16 characters representing 64-bits hex
        
        # Test 2: register and check matching duplicate within threshold
        detector.register_fake_fingerprint(self.dummy_img, "CASE-901")
        
        # Scanning same image should yield exact duplicate
        is_dup, cases = detector.scan_for_duplicates(self.dummy_img, distance_threshold=2)
        self.assertTrue(is_dup)
        self.assertIn("CASE-901", cases)

        # Scanning contrasting image should have Hamming distance > threshold
        is_dup_diff, _ = detector.scan_for_duplicates(self.contrasting_img, distance_threshold=2)
        self.assertFalse(is_dup_diff)

    def test_identity_risk_engine(self):
        """
        IdentityRiskEngine should assess high-profile profile exposure indices.
        """
        engine = IdentityRiskEngine()
        
        # Test High Exposure Case
        assessment = engine.assess_profile_compromise_risk(
            target_name="CEO John Doe",
            role_label="ceo",
            manipulation_confidence=95.0
        )
        self.assertEqual(assessment["threat_alert_level"], "CRITICAL_COMPROMISE")
        self.assertTrue(assessment["exposure_risk_index"] > 0.8)
        self.assertIn("Lock credential tokens", assessment["action_guideline"])

        # Test Low Exposure Case
        assessment_low = engine.assess_profile_compromise_risk(
            target_name="Standard Bot Node",
            role_label="regular_user",
            manipulation_confidence=10.0
        )
        self.assertEqual(assessment_low["threat_alert_level"], "INFORMATIONAL")
        self.assertTrue(assessment_low["exposure_risk_index"] < 0.3)

    def test_campaign_tracker_loops(self):
        """
        CampaignTracker should log cases under campaign identifiers and return summaries.
        """
        tracker = CampaignTracker()
        
        # Log case
        campaign_id = tracker.register_case_to_campaign(
            case_id="CASE-001",
            actor_account="Twitter_User_A",
            asset_fingerprint="hex_fingerprint_01",
            verdict="DEEPFAKE",
            confidence=94.0
        )
        
        brief = tracker.get_campaign_briefing(campaign_id)
        self.assertEqual(brief["campaign_id"], campaign_id)
        self.assertEqual(len(brief["cases_linked"]), 1)
        self.assertTrue(brief["threat_risk_level"] in ["WARNING", "CRITICAL_THREAT"])


    def test_anomaly_correlation_pearson(self):
        """
        AnomalyCorrelationAnalyzer should compute Pearson correlations.
        """
        analyzer = AnomalyCorrelator()
        
        series_a = [1.0, 2.0, 3.0, 4.0, 5.0]
        series_b = [2.0, 4.0, 6.0, 8.0, 10.0] # perfect correlation
        
        r = analyzer.calculate_pearson_correlation(series_a, series_b)
        self.assertAlmostEqual(r, 1.0, places=4)

        # Mismatched series sizes should return 0.0
        r_mismatch = analyzer.calculate_pearson_correlation(series_a, [1.0, 2.0])
        self.assertEqual(r_mismatch, 0.0)

if __name__ == "__main__":
    unittest.main()
