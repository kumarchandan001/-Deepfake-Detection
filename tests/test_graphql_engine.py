import unittest
import json
import asyncio
from fastapi import FastAPI
from fastapi.testclient import TestClient
from backend.graphql.schema import router as graphql_router
from backend.graphql.resolvers import DataStore
from backend.graphql.subscriptions import EventTopic

# Construct test FastAPI app
app = FastAPI()
app.include_router(graphql_router)

class TestGraphQLEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.store = DataStore()
        cls.store.seed_demo_data()

    def test_graphql_endpoint_invalid_json(self):
        """Verify the GraphQL endpoint returns 400 for malformed JSON request bodies."""
        response = self.client.post("/api/v1/graphql", content="malformed json string", headers={"Content-Type": "application/json"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid JSON body", response.json()["detail"])

    def test_graphql_endpoint_missing_operation_name(self):
        """Verify the GraphQL endpoint returns 400 when operation name is missing."""
        payload = {
            "operation": "query",
            "variables": {}
        }
        response = self.client.post("/api/v1/graphql", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Missing operation name", response.json()["detail"])

    def test_graphql_endpoint_unknown_operation(self):
        """Verify the GraphQL endpoint returns 400 for unknown operations."""
        payload = {
            "operation": "invalid_operation",
            "name": "detections",
            "variables": {}
        }
        response = self.client.post("/api/v1/graphql", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Unknown operation", response.json()["detail"])

    def test_graphql_query_detections(self):
        """Test retrieving a list of detections using a GraphQL query."""
        payload = {
            "operation": "query",
            "name": "detections",
            "variables": {
                "limit": 5,
                "offset": 0
            }
        }
        response = self.client.post("/api/v1/graphql", json=payload, headers={"X-Tenant-ID": "tenant_pro"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNone(data["errors"])
        self.assertIsNotNone(data["data"])
        self.assertGreaterEqual(len(data["data"]), 0)

    def test_graphql_query_detection_by_id(self):
        """Test retrieving a specific detection result by ID."""
        # Find a real detection ID first
        detection_id = list(self.store._detections.keys())[0]
        payload = {
            "operation": "query",
            "name": "detection",
            "variables": {
                "id": detection_id
            }
        }
        response = self.client.post("/api/v1/graphql", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNone(data["errors"])
        self.assertEqual(data["data"]["id"], detection_id)

    def test_graphql_query_threat_events(self):
        """Test listing threat events with filters."""
        payload = {
            "operation": "query",
            "name": "threatEvents",
            "variables": {
                "severity": "CRITICAL",
                "limit": 2
            }
        }
        response = self.client.post("/api/v1/graphql", json=payload, headers={"X-Tenant-ID": "tenant_enterprise"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNone(data["errors"])
        self.assertIsNotNone(data["data"])

    def test_graphql_query_threat_event_by_id(self):
        """Test retrieving a threat event by ID."""
        event_id = list(self.store._threat_events.keys())[0]
        payload = {
            "operation": "query",
            "name": "threatEvent",
            "variables": {
                "id": event_id
            }
        }
        response = self.client.post("/api/v1/graphql", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNone(data["errors"])
        self.assertEqual(data["data"]["id"], event_id)

    def test_graphql_query_campaigns(self):
        """Test listing threat campaigns."""
        payload = {
            "operation": "query",
            "name": "campaigns",
            "variables": {
                "active_only": True
            }
        }
        response = self.client.post("/api/v1/graphql", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNone(data["errors"])
        self.assertIsNotNone(data["data"])

    def test_graphql_query_cases(self):
        """Test listing forensic investigation cases."""
        payload = {
            "operation": "query",
            "name": "cases",
            "variables": {
                "status": "OPEN"
            }
        }
        response = self.client.post("/api/v1/graphql", json=payload, headers={"X-Tenant-ID": "tenant_enterprise"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNone(data["errors"])
        self.assertIsNotNone(data["data"])

    def test_graphql_query_case_by_id(self):
        """Test retrieving a single forensic case by ID."""
        case_id = list(self.store._cases.keys())[0]
        payload = {
            "operation": "query",
            "name": "case",
            "variables": {
                "id": case_id
            }
        }
        response = self.client.post("/api/v1/graphql", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNone(data["errors"])
        self.assertEqual(data["data"]["id"], case_id)

    def test_graphql_query_tenant_usage(self):
        """Test getting a tenant's metered usage snapshot."""
        payload = {
            "operation": "query",
            "name": "tenantUsage",
            "variables": {
                "tenant_id": "tenant_pro"
            }
        }
        response = self.client.post("/api/v1/graphql", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNone(data["errors"])
        self.assertEqual(data["data"]["tenant_id"], "tenant_pro")

    def test_graphql_query_platform_metrics(self):
        """Test resolving global platform status and performance metrics."""
        payload = {
            "operation": "query",
            "name": "platformMetrics",
            "variables": {}
        }
        response = self.client.post("/api/v1/graphql", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNone(data["errors"])
        self.assertIn("gpu_utilization_percent", data["data"])

    def test_graphql_query_alert_rules(self):
        """Test listing configured alert rules."""
        payload = {
            "operation": "query",
            "name": "alertRules",
            "variables": {
                "tenant_id": "tenant_enterprise"
            }
        }
        response = self.client.post("/api/v1/graphql", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNone(data["errors"])

    def test_graphql_query_threat_actors(self):
        """Test listing threat actors and retrieving details."""
        payload = {
            "operation": "query",
            "name": "threatActors",
            "variables": {}
        }
        response = self.client.post("/api/v1/graphql", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNone(data["errors"])
        self.assertGreater(len(data["data"]), 0)

        # Query single actor
        actor_id = data["data"][0]["id"]
        actor_payload = {
            "operation": "query",
            "name": "threatActor",
            "variables": {
                "id": actor_id
            }
        }
        actor_response = self.client.post("/api/v1/graphql", json=actor_payload)
        self.assertEqual(actor_response.status_code, 200)
        actor_data = actor_response.json()
        self.assertEqual(actor_data["data"]["id"], actor_id)

    def test_graphql_mutation_submit_detection(self):
        """Test mutation to submit media for processing."""
        payload = {
            "operation": "mutation",
            "name": "submitDetection",
            "variables": {
                "tenant_id": "tenant_pro",
                "media_type": "VIDEO",
                "file_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                "file_size_bytes": 4820300
            }
        }
        response = self.client.post("/api/v1/graphql", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNone(data["errors"])
        self.assertEqual(data["data"]["verdict"] in ["MANIPULATED", "AUTHENTIC", "SUSPICIOUS"], True)
        self.assertEqual(data["data"]["media_type"], "VIDEO")

    def test_graphql_mutation_acknowledge_threat(self):
        """Test mutation to acknowledge high-severity events."""
        event_id = list(self.store._threat_events.keys())[0]
        payload = {
            "operation": "mutation",
            "name": "acknowledgeThreat",
            "variables": {
                "event_id": event_id,
                "analyst": "analyst_jones"
            }
        }
        response = self.client.post("/api/v1/graphql", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNone(data["errors"])
        self.assertTrue(data["data"]["acknowledged"])

    def test_graphql_mutation_escalate_threat(self):
        """Test mutation to escalate threat alerts."""
        event_id = list(self.store._threat_events.keys())[0]
        payload = {
            "operation": "mutation",
            "name": "escalateThreat",
            "variables": {
                "event_id": event_id,
                "reason": "Coordinated GAN injection suspected across multiple enterprise assets."
            }
        }
        response = self.client.post("/api/v1/graphql", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNone(data["errors"])
        self.assertEqual(data["data"]["severity"], "CRITICAL")

    def test_graphql_mutation_create_case(self):
        """Test mutation to open a new forensic case."""
        payload = {
            "operation": "mutation",
            "name": "createCase",
            "variables": {
                "title": "Deepfake Impersonation of Executive officers",
                "description": "Voice clones generated to bypass corporate vocal identity verification systems.",
                "priority": "HIGH",
                "assigned_to": "analyst_sarah@forensics.ai",
                "tags": ["audio", "fraud", "executive"]
            }
        }
        response = self.client.post("/api/v1/graphql", json=payload, headers={"X-Tenant-ID": "tenant_enterprise"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNone(data["errors"])
        self.assertEqual(data["data"]["title"], "Deepfake Impersonation of Executive officers")
        self.assertEqual(data["data"]["status"], "OPEN")

    def test_graphql_mutation_update_case_status(self):
        """Test case status modifications."""
        case_id = list(self.store._cases.keys())[0]
        payload = {
            "operation": "mutation",
            "name": "updateCaseStatus",
            "variables": {
                "case_id": case_id,
                "status": "RESOLVED"
            }
        }
        response = self.client.post("/api/v1/graphql", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNone(data["errors"])
        self.assertEqual(data["data"]["status"], "RESOLVED")
        self.assertIsNotNone(data["data"]["closed_at"])

    def test_graphql_mutation_add_evidence(self):
        """Test adding evidence files with chain-of-custody tracking."""
        case_id = list(self.store._cases.keys())[0]
        payload = {
            "operation": "mutation",
            "name": "addEvidence",
            "variables": {
                "case_id": case_id,
                "file_name": "manipulated_audio_intercept.mp3",
                "file_hash": "a1f9e8a8b8c7d6e5f433221100abcdef1234567890abcdef1234567890abcdef",
                "media_type": "AUDIO",
                "collected_by": "officer_davis"
            }
        }
        response = self.client.post("/api/v1/graphql", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNone(data["errors"])
        self.assertEqual(data["data"]["file_name"], "manipulated_audio_intercept.mp3")
        self.assertIsNotNone(data["data"]["chain_of_custody_hash"])

    def test_graphql_mutation_create_alert_rule(self):
        """Test creating an automated alert rule."""
        payload = {
            "operation": "mutation",
            "name": "createAlertRule",
            "variables": {
                "name": "High Volume Manipulations Warning",
                "description": "Trigger alert if overall confidence of MANIPULATED verdict exceeds 85% twice in 5 mins",
                "condition_type": "threshold",
                "condition_value": {"threshold": 2, "time_window_seconds": 300},
                "channels": ["WEBHOOK", "SLACK"],
                "cooldown_seconds": 600
            }
        }
        response = self.client.post("/api/v1/graphql", json=payload, headers={"X-Tenant-ID": "tenant_enterprise"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNone(data["errors"])
        self.assertEqual(data["data"]["name"], "High Volume Manipulations Warning")

    def test_graphql_mutation_toggle_alert_rule(self):
        """Test rule enablement toggle."""
        payload = {
            "operation": "mutation",
            "name": "createAlertRule",
            "variables": {
                "name": "Temporary Silent Rule",
                "description": "Silent rule.",
                "condition_type": "threshold",
                "condition_value": {"threshold": 1},
                "channels": ["WEBHOOK"],
                "cooldown_seconds": 60
            }
        }
        create_resp = self.client.post("/api/v1/graphql", json=payload, headers={"X-Tenant-ID": "tenant_enterprise"})
        rule_id = create_resp.json()["data"]["id"]

        toggle_payload = {
            "operation": "mutation",
            "name": "toggleAlertRule",
            "variables": {
                "rule_id": rule_id,
                "enabled": False
            }
        }
        response = self.client.post("/api/v1/graphql", json=toggle_payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNone(data["errors"])
        self.assertFalse(data["data"]["is_enabled"])

    def test_graphql_websocket_ping(self):
        """Verify WebSocket subscription channels ping-pong sequence."""
        with self.client.websocket_connect("/api/v1/graphql/ws") as ws:
            ws.send_json({"type": "ping"})
            resp = ws.receive_json()
            self.assertEqual(resp["type"], "pong")
            self.assertIsNotNone(resp["timestamp"])

    def test_graphql_websocket_subscription_lifecycle(self):
        """Verify standard WebSocket subscribing, listening, and unsubscribing operations."""
        with self.client.websocket_connect("/api/v1/graphql/ws") as ws:
            # Subscribe to platform health stream
            ws.send_json({
                "type": "subscribe",
                "stream": "platform_health"
            })
            sub_resp = ws.receive_json()
            self.assertEqual(sub_resp["type"], "subscribed")
            self.assertEqual(sub_resp["stream"], "platform_health")

            # Receive initial or subsequent data event
            data_resp = ws.receive_json()
            self.assertEqual(data_resp["type"], "data")
            self.assertEqual(data_resp["stream"], "platform_health")
            self.assertIsNotNone(data_resp["payload"])

            # Unsubscribe
            ws.send_json({
                "type": "unsubscribe",
                "stream": "platform_health"
            })
            unsub_resp = ws.receive_json()
            self.assertEqual(unsub_resp["type"], "unsubscribed")
            self.assertEqual(unsub_resp["stream"], "platform_health")

    def test_graphql_websocket_subscription_invalid_stream(self):
        """Verify that subscribing to an invalid stream returns an error message."""
        with self.client.websocket_connect("/api/v1/graphql/ws") as ws:
            ws.send_json({
                "type": "subscribe",
                "stream": "invalid_nonexistent_stream"
            })
            resp = ws.receive_json()
            self.assertIn("error", resp)
            self.assertIn("Unknown stream", resp["error"])

    def test_graphql_stats_endpoint(self):
        """Test getting stats from the Event Bus."""
        response = self.client.get("/api/v1/graphql/stats")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("event_bus", data)
        self.assertIn("topics", data["event_bus"])
