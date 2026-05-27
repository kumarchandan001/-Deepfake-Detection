import unittest
import os
import sys
import asyncio
from typing import Dict, Any, List

# Ensure workspace path imports resolve correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_engine.agents.agent_memory import AgentMemory
from ai_engine.agents.forensic_agent import ForensicAgent
from ai_engine.agents.orchestration_agent import OrchestrationAgent
from ai_engine.agents.threat_agent import ThreatAgent
from ai_engine.agents.report_agent import ReportAgent
from ai_engine.agents.multimodal_agent import MultimodalAgent

class TestAgentsLayer(unittest.TestCase):
    """
    Validates autonomous forensic agents, incident timeline memories, threat analysis scoring, 
    and cross-modal correlation algorithms.
    """
    def setUp(self):
        self.memory = AgentMemory()
        self.case_id = "CASE-TEST-881"
        self.dummy_img = "mock_agents_image.jpg"
        self.dummy_audio = "mock_agents_audio.wav"
        
        # Create small blank placeholder files for agent upload routing tests
        with open(self.dummy_img, "wb") as f:
            f.write(b"MOCK_IMAGE_DATA_TENSOR")
        with open(self.dummy_audio, "wb") as f:
            f.write(b"MOCK_AUDIO_DATA_TENSOR")

    def tearDown(self):
        if os.path.exists(self.dummy_img):
            os.remove(self.dummy_img)
        if os.path.exists(self.dummy_audio):
            os.remove(self.dummy_audio)

    def test_agent_memory_timeline_and_lookup(self):
        """
        AgentMemory should persist observations and allow keyword query filters.
        """
        self.memory.record_observation(
            case_id=self.case_id,
            source="LaplacianCheck",
            observation="Variance was 0.0028 indicating static printed mask spoofing.",
            metadata={"kernel_size": 3}
        )
        self.memory.record_observation(
            case_id=self.case_id,
            source="FFTAnalyzer",
            observation="Found spatial power spikes at (350, 480).",
            metadata={"threshold": 0.05}
        )

        # Verify timeline count
        timeline = self.memory.get_case_timeline(self.case_id)
        self.assertEqual(len(timeline), 2)
        self.assertEqual(timeline[0]["source"], "LaplacianCheck")

        # Verify keyword search
        matches = self.memory.query_semantic_keywords(self.case_id, "spoofing")
        self.assertEqual(len(matches), 1)
        self.assertIn("LaplacianCheck", matches[0]["source"])

        # Verify context cache
        context = {"target_profile": "@VIP_Account", "risk_index": 0.94}
        self.memory.cache_case_context(self.case_id, context)
        self.assertEqual(self.memory.get_case_context(self.case_id), context)

        # Clear memory
        self.memory.clear_memory(self.case_id)
        self.assertEqual(len(self.memory.get_case_timeline(self.case_id)), 0)

    def test_threat_agent_severity_calculations(self):
        """
        ThreatAgent should compute risk index scores and select appropriate advisories.
        """
        agent = ThreatAgent(memory=self.memory)
        
        # Test Critical Case Scenario
        report = agent.analyze_threat_severity(
            case_id=self.case_id,
            analysis_verdict="FAKE_VOICE",
            confidence=96.0,
            source_account="@FakeVIP_Bot"
        )
        self.assertEqual(report["case_id"], self.case_id)
        self.assertEqual(report["threat_severity"], "CRITICAL")
        self.assertTrue(report["risk_score"] >= 0.8)
        self.assertIn("cryptographic blocks", report["actionable_defense_advisory"])

        # Test Moderate Warning Scenario
        report_warn = agent.analyze_threat_severity(
            case_id=self.case_id,
            analysis_verdict="CLEAN_MEDIA",
            confidence=55.0
        )
        self.assertEqual(report_warn["threat_severity"], "LOW")
        self.assertTrue(report_warn["risk_score"] < 0.5)

    def test_report_agent_dossier_compilation(self):
        """
        ReportAgent should synthesize structured JSON report briefs.
        """
        agent = ReportAgent(memory=self.memory)
        results = [
            {"file": "ceo_mock.mp4", "verdict": "FAKE", "confidence": 92.0},
            {"file": "speech.wav", "verdict": "FAKE_VOICE", "confidence": 88.0}
        ]
        threat_report = {
            "threat_severity": "CRITICAL",
            "risk_score": 0.94,
            "actionable_defense_advisory": "Escalate immediate verification hold."
        }

        dossier = agent.generate_investigation_report(
            case_id=self.case_id,
            case_title="CEO Corporate Extortion Campaign",
            results=results,
            threat_report=threat_report
        )

        self.assertEqual(dossier["case_id"], self.case_id)
        self.assertEqual(dossier["forensic_verdict"], "MANIPULATED")
        self.assertEqual(dossier["evidence_count"], 2)
        self.assertTrue(len(dossier["investigation_timeline"]) >= 0)

    def test_multimodal_agent_cross_modal_correlation(self):
        """
        MultimodalAgent should correlate timing coefficients across spatial and acoustic frames.
        """
        agent = MultimodalAgent(memory=self.memory)
        
        # Test highly correlated visual/voice syntheses (typical of high-end deepfakes)
        visual_anomalies = [(1.2, 3.5), (4.5, 6.0)]
        audio_anomalies = [(1.5, 3.2), (6.8, 8.0)]

        report = agent.cross_correlate_modalities(
            case_id=self.case_id,
            visual_anomalies=visual_anomalies,
            audio_anomalies=audio_anomalies
        )

        self.assertTrue(report["has_overlap"])
        self.assertTrue(report["fusion_risk_score"] > 0.0)
        self.assertTrue(report["total_overlap_duration_sec"] > 0.0)
        self.assertEqual(report["correlation_verdict"], "TEMPORAL_OVERLAP")

    def test_forensic_agent_routing(self):
        """
        ForensicAgent should asynchronously audit media types and trigger sub-model workflows.
        """
        from unittest.mock import patch
        
        async def run_forensic_agent_test():
            agent = ForensicAgent(memory=self.memory)
            
            # Mock engine results to bypass raw model load and cv2 read requirements
            with patch.object(agent.image_engine, 'predict_image', return_value={
                "success": True, "prediction": "FAKE", "confidence": 92.4, "raw_score": 0.92, "processing_time": 0.12
            }), patch.object(agent.audio_engine, 'predict_audio_file', return_value={
                "success": True, "prediction": "FAKE_VOICE", "confidence": 88.5, "processing_time": 0.08
            }):
                # Test image routing
                img_report = await agent.investigate_media(self.case_id, self.dummy_img)
                self.assertTrue(img_report["success"])
                self.assertEqual(img_report["verdict"], "FAKE")
                self.assertEqual(img_report["confidence"], 92.4)

                # Test audio routing
                aud_report = await agent.investigate_media(self.case_id, self.dummy_audio)
                self.assertTrue(aud_report["success"])
                self.assertEqual(aud_report["verdict"], "FAKE_VOICE")
                self.assertEqual(aud_report["confidence"], 88.5)

        asyncio.run(run_forensic_agent_test())

    def test_orchestration_agent_workflow(self):
        """
        OrchestrationAgent should schedules cases runs and aggregates multi-node metrics.
        """
        from unittest.mock import patch
        
        async def run_orchestration_test():
            orchestrator = OrchestrationAgent(memory=self.memory)
            case_id = orchestrator.create_case("Ecrime Stock Manipulation Sweep")
            self.assertTrue(case_id.startswith("case_"))

            # Mock forensic agent to return successful deepfake verdict dictionary
            with patch.object(orchestrator.forensic_agent, 'investigate_media', return_value={
                "success": True, "verdict": "FAKE", "confidence": 94.2, "processing_time": 0.15
            }):
                res = await orchestrator.add_and_analyze_asset(case_id, self.dummy_img)
                self.assertTrue(res["success"])
                self.assertEqual(res["verdict"], "FAKE")

                # Compile case report
                summary = orchestrator.get_case_summary(case_id)
                self.assertEqual(summary["case_id"], case_id)
                self.assertEqual(summary["assets_analyzed"], 1)
                self.assertEqual(summary["overall_verdict"], "MANIPULATED")

        asyncio.run(run_orchestration_test())

if __name__ == "__main__":
    unittest.main()

