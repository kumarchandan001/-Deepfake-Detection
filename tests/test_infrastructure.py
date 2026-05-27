import unittest
import os
import re
import json
import asyncio
from datetime import datetime

# Attempt to import yaml for config testing; fallback to regex/basic parsing if not installed
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

from backend.monitoring.alerting_rules import (
    AlertRulesEngine, AlertRuleConfig, AlertCondition, AlertSeverity, AlertInstance
)
from backend.monitoring.health_checks import DeepHealthChecker, HealthStatus


class TestInfrastructure(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.k8s_dir = os.path.join(os.getcwd(), "k8s")
        cls.workflows_dir = os.path.join(os.getcwd(), ".github", "workflows")
        cls.health_checker = DeepHealthChecker()
        cls.alert_engine = AlertRulesEngine()

    def test_kubernetes_yaml_files_exist(self):
        """Verify that all standard Kubernetes deployment YAML configurations are present."""
        expected_files = [
            "namespace.yaml",
            "configmap.yaml",
            "secrets.yaml",
            "service.yaml",
            "hpa.yaml",
            "ingress.yaml",
            "redis-deployment.yaml",
            "gpu-worker-deployment.yaml"
        ]
        for filename in expected_files:
            filepath = os.path.join(self.k8s_dir, filename)
            self.assertTrue(os.path.exists(filepath), f"Kubernetes configuration {filename} is missing at {filepath}")

    def test_kubernetes_yaml_syntax_and_schemas(self):
        """Validate YAML syntax and critical Kubernetes fields for k8s resources."""
        if not HAS_YAML:
            self.skipTest("PyYAML package not installed, skipping strict YAML structure validation.")

        k8s_files = [f for f in os.listdir(self.k8s_dir) if f.endswith(".yaml") or f.endswith(".yml")]
        for filename in k8s_files:
            filepath = os.path.join(self.k8s_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                try:
                    # YAML files can contain multiple documents separated by ---
                    docs = list(yaml.safe_load_all(f))
                    for doc in docs:
                        if doc is None:
                            continue
                        self.assertIn("apiVersion", doc, f"Missing apiVersion in {filename}")
                        self.assertIn("kind", doc, f"Missing kind in {filename}")
                        self.assertIn("metadata", doc, f"Missing metadata in {filename}")
                        
                        metadata = doc["metadata"]
                        self.assertIn("name", metadata, f"Missing metadata.name in {filename}")
                        
                        # Component-specific checks
                        kind = doc["kind"]
                        if kind == "Deployment":
                            spec = doc.get("spec", {})
                            self.assertIn("selector", spec, f"Missing spec.selector in deployment {filename}")
                            self.assertIn("template", spec, f"Missing spec.template in deployment {filename}")
                            
                            pod_template = spec["template"]
                            self.assertIn("spec", pod_template, f"Missing template spec in deployment {filename}")
                            
                            containers = pod_template["spec"].get("containers", [])
                            self.assertGreater(len(containers), 0, f"No containers defined in deployment {filename}")
                            for container in containers:
                                self.assertIn("name", container, f"Container missing name in deployment {filename}")

                        elif kind == "Service":
                            spec = doc.get("spec", {})
                            self.assertIn("ports", spec, f"Service missing ports specification in {filename}")

                except Exception as e:
                    self.fail(f"Failed to parse Kubernetes YAML file {filename}: {e}")

    def test_gpu_worker_kubernetes_configuration(self):
        """Ensure the GPU worker Kubernetes configuration includes required GPU limits and sidecars."""
        if not HAS_YAML:
            self.skipTest("PyYAML package not installed, skipping strict GPU config parsing.")

        gpu_filepath = os.path.join(self.k8s_dir, "gpu-worker-deployment.yaml")
        self.assertTrue(os.path.exists(gpu_filepath))

        with open(gpu_filepath, "r", encoding="utf-8") as f:
            docs = list(yaml.safe_load_all(f))
            gpu_deployment = None
            for doc in docs:
                if doc and doc.get("kind") == "Deployment":
                    gpu_deployment = doc
                    break
            
            self.assertIsNotNone(gpu_deployment, "Could not find Deployment spec in gpu-worker-deployment.yaml")
            
            spec = gpu_deployment.get("spec", {})
            containers = spec.get("template", {}).get("spec", {}).get("containers", [])
            
            # Find the primary GPU worker container and sidecars
            gpu_worker_container = None
            dcgm_sidecar = None
            
            for container in containers:
                if container.get("name") == "gpu-inference-worker":
                    gpu_worker_container = container
                elif container.get("name") == "dcgm-exporter":
                    dcgm_sidecar = container
                    
            self.assertIsNotNone(gpu_worker_container, "Missing gpu-inference-worker container definition.")
            
            # Verify NVIDIA GPU Resource Limits are declared
            resources = gpu_worker_container.get("resources", {})
            limits = resources.get("limits", {})
            self.assertIn("nvidia.com/gpu", limits, "GPU worker is missing NVIDIA resource limits specification ('nvidia.com/gpu').")
            
            # Verify shared memory (shm) is configured for PyTorch
            volumes = spec.get("template", {}).get("spec", {}).get("volumes", [])
            shm_volume_exists = any(vol.get("name") == "shm" for vol in volumes)
            self.assertTrue(shm_volume_exists, "Missing shared memory volume (shm) for high-performance PyTorch DataLoader.")

    def test_cicd_workflow_files_exist_and_parse(self):
        """Verify GitHub actions CI/CD workflows are defined and syntax compliant."""
        expected_workflows = ["ci.yaml", "cd.yaml"]
        for workflow in expected_workflows:
            filepath = os.path.join(self.workflows_dir, workflow)
            self.assertTrue(os.path.exists(filepath), f"Workflow {workflow} is missing at {filepath}")
            
            if HAS_YAML:
                with open(filepath, "r", encoding="utf-8") as f:
                    try:
                        doc = yaml.safe_load(f)
                        self.assertIsNotNone(doc)
                        self.assertIn("name", doc, f"Workflow {workflow} is missing name")
                        self.assertTrue("on" in doc or True in doc, f"Workflow {workflow} is missing trigger triggers (on)")
                        self.assertIn("jobs", doc, f"Workflow {workflow} is missing jobs specification")
                    except Exception as e:
                        self.fail(f"Failed parsing workflow YAML {workflow}: {e}")

    def test_alert_rules_engine_flow(self):
        """Test alerting rules evaluation, deduplication, acknowledging, and resolving flows."""
        # Setup custom test alert rule
        test_rule = AlertRuleConfig(
            id="rule_test_infrastructure_alert",
            tenant_id="infra_test_tenant",
            name="Infrastructure Test Metric Warning",
            description="Fires when test metric exceeds 100",
            severity=AlertSeverity.HIGH,
            conditions=[AlertCondition(
                condition_type="threshold",
                metric_name="test_infra_metric",
                operator="gt",
                threshold_value=100.0,
                window_seconds=60
            )],
            channels=["webhook", "slack"],
            cooldown_seconds=10  # Low cooldown for rapid test runs
        )
        
        self.alert_engine.register_rule(test_rule)
        
        # Scenario 1: Metric is below threshold -> No alert should trigger
        fired_1 = asyncio.run(self.alert_engine.evaluate_and_fire("test_infra_metric", 85.0, "infra_test_tenant"))
        self.assertEqual(len(fired_1), 0, "Alert fired when metric was below threshold limit.")
        
        # Scenario 2: Metric exceeds threshold -> Alert fires
        fired_2 = asyncio.run(self.alert_engine.evaluate_and_fire("test_infra_metric", 120.0, "infra_test_tenant"))
        self.assertEqual(len(fired_2), 1, "Alert failed to fire when metric exceeded threshold limits.")
        alert_instance = fired_2[0]
        self.assertEqual(alert_instance.rule_id, test_rule.id)
        self.assertEqual(alert_instance.severity, AlertSeverity.HIGH)
        self.assertIn("webhook", alert_instance.channels_notified)
        
        # Scenario 3: Quench/Cooldown -> Consecutive metric triggers should be throttled
        fired_3 = asyncio.run(self.alert_engine.evaluate_and_fire("test_infra_metric", 130.0, "infra_test_tenant"))
        self.assertEqual(len(fired_3), 0, "Alert fired during cooldown throttling period.")
        
        # Test alert Acknowledgment
        acknowledged_alert = asyncio.run(self.alert_engine.acknowledge_alert(alert_instance.id, "operator_test"))
        self.assertIsNotNone(acknowledged_alert)
        self.assertTrue(acknowledged_alert.acknowledged)
        self.assertEqual(acknowledged_alert.acknowledged_by, "operator_test")
        
        # Test alert Resolution
        resolved_alert = asyncio.run(self.alert_engine.resolve_alert(alert_instance.id))
        self.assertIsNotNone(resolved_alert)
        self.assertTrue(resolved_alert.resolved)
        self.assertIsNotNone(resolved_alert.resolved_at)
        
        # Cleanup
        self.alert_engine.deregister_rule(test_rule.id)

    def test_deep_health_checks(self):
        """Validate health check endpoints diagnostic outputs for K8s probes."""
        # 1. Shallow Check (Liveness Probe)
        shallow_report = asyncio.run(self.health_checker.shallow_check())
        self.assertEqual(shallow_report["status"], HealthStatus.HEALTHY)
        self.assertIn("uptime_seconds", shallow_report)
        self.assertIn("timestamp", shallow_report)
        
        # 2. Readiness Check (Readiness Probe)
        readiness_report = asyncio.run(self.health_checker.readiness_check())
        self.assertIn(readiness_report["status"], [HealthStatus.HEALTHY, HealthStatus.DEGRADED, HealthStatus.UNHEALTHY])
        self.assertIn("components", readiness_report)
        self.assertIn("API Gateway", readiness_report["components"])
        
        # 3. Full Diagnostic Report
        full_report = asyncio.run(self.health_checker.full_diagnostic())
        self.assertIn(full_report.overall_status, [HealthStatus.HEALTHY, HealthStatus.DEGRADED, HealthStatus.UNHEALTHY])
        self.assertGreater(full_report.total_checks, 0)
        self.assertEqual(len(full_report.components), full_report.total_checks)
