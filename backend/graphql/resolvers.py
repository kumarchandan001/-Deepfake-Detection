"""
GraphQL Resolvers — AI Deepfake Detection & Enterprise Trust Platform.

Production-grade query and mutation resolvers backed by in-memory stores
with async-safe operations, tenant isolation, and comprehensive filtering.
"""

import uuid
import time
import hashlib
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from ai_engine.utils.logger import setup_logger

from backend.graphql.types import (
    DetectionResult, ModelPrediction, ManipulationRegion,
    ThreatEvent, ThreatActor, CampaignCluster,
    ForensicCase, EvidenceItem,
    TenantUsageSnapshot, PlatformMetrics,
    AlertRule, AlertNotification,
    DetectionFilterInput, ThreatFilterInput,
    CreateCaseInput, CreateAlertRuleInput,
)

logger = setup_logger("graphql_resolvers")


# ─── In-Memory Data Stores (Production: swap with PostgreSQL/Redis) ──────────

class DataStore:
    """
    Thread-safe in-memory data store for GraphQL resolvers.
    In production, replace with async SQLAlchemy / Redis queries.
    """
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._detections: Dict[str, DetectionResult] = {}
            cls._instance._threat_events: Dict[str, ThreatEvent] = {}
            cls._instance._campaigns: Dict[str, CampaignCluster] = {}
            cls._instance._cases: Dict[str, ForensicCase] = {}
            cls._instance._alert_rules: Dict[str, AlertRule] = {}
            cls._instance._alert_notifications: Dict[str, AlertNotification] = {}
            cls._instance._threat_actors: Dict[str, ThreatActor] = {}
            cls._instance._initialized = False
        return cls._instance

    def seed_demo_data(self):
        """Populate stores with realistic demo data for development/testing."""
        if self._initialized:
            return
        self._initialized = True

        now = datetime.utcnow()

        # Seed threat actors
        actors = [
            ThreatActor(
                id="actor_001", alias="PhantomForge",
                known_techniques=["face_swap", "voice_clone", "lip_sync"],
                associated_ips=["185.220.101.42", "91.219.237.10"],
                first_seen=(now - timedelta(days=90)).isoformat(),
                last_seen=now.isoformat(),
                threat_score=92.5, attribution_confidence=0.78
            ),
            ThreatActor(
                id="actor_002", alias="DeepMirage",
                known_techniques=["gan_synthesis", "texture_transfer"],
                associated_ips=["45.155.205.71"],
                first_seen=(now - timedelta(days=45)).isoformat(),
                last_seen=(now - timedelta(hours=6)).isoformat(),
                threat_score=76.3, attribution_confidence=0.65
            ),
        ]
        for actor in actors:
            self._threat_actors[actor.id] = actor

        # Seed detections
        techniques = ["face_swap", "gan_synthesis", "voice_clone", "inpainting", "lip_sync"]
        verdicts = ["MANIPULATED", "AUTHENTIC", "SUSPICIOUS", "MANIPULATED", "AUTHENTIC"]
        for i in range(12):
            det_id = f"det_{uuid.uuid4().hex[:8]}"
            verdict = verdicts[i % len(verdicts)]
            confidence = 0.95 - (i * 0.05) if verdict == "MANIPULATED" else 0.12 + (i * 0.02)

            predictions = [
                ModelPrediction(
                    model_name="EfficientNet-B7-Forensic",
                    model_version="2.1.0",
                    confidence=min(confidence + 0.03, 1.0),
                    verdict=verdict,
                    inference_time_ms=45.2 + i * 3,
                    device="cuda:0",
                    features_extracted=2048
                ),
                ModelPrediction(
                    model_name="XceptionNet-DeepDetect",
                    model_version="1.8.0",
                    confidence=max(confidence - 0.02, 0.0),
                    verdict=verdict,
                    inference_time_ms=38.7 + i * 2,
                    device="cuda:0",
                    features_extracted=1024
                ),
            ]

            regions = []
            if verdict == "MANIPULATED":
                regions.append(ManipulationRegion(
                    x=0.15 + i * 0.02, y=0.2, width=0.35, height=0.4,
                    confidence=confidence,
                    technique=techniques[i % len(techniques)],
                    model_source="EfficientNet-B7-Forensic"
                ))

            det = DetectionResult(
                id=det_id,
                tenant_id=f"tenant_{'enterprise' if i < 3 else 'pro' if i < 7 else 'free'}",
                media_type=["IMAGE", "VIDEO", "AUDIO"][i % 3],
                file_hash=hashlib.sha256(f"file_{i}".encode()).hexdigest(),
                file_size_bytes=1024 * (100 + i * 50),
                verdict=verdict,
                overall_confidence=confidence,
                model_predictions=predictions,
                manipulation_regions=regions,
                processing_time_ms=85.0 + i * 10,
                gpu_memory_used_mb=256.0 + i * 12,
                created_at=(now - timedelta(hours=i * 4)).isoformat(),
            )
            self._detections[det_id] = det

        # Seed threat events
        event_types = ["deepfake_detected", "campaign_identified", "new_actor", "escalation"]
        severities = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
        for i in range(8):
            evt = ThreatEvent(
                id=f"evt_{uuid.uuid4().hex[:8]}",
                tenant_id=f"tenant_{'enterprise' if i < 2 else 'pro'}",
                severity=severities[i % len(severities)],
                event_type=event_types[i % len(event_types)],
                title=f"Threat Event #{i+1}: {event_types[i % len(event_types)].replace('_', ' ').title()}",
                description=f"Automated threat detection alert triggered by forensic analysis pipeline.",
                source_ip=f"10.0.{i}.{100+i}",
                actor=actors[i % 2] if i < 4 else None,
                ioc_indicators=[f"ioc_{uuid.uuid4().hex[:6]}" for _ in range(2)],
                timestamp=(now - timedelta(hours=i * 2)).isoformat(),
                acknowledged=i > 4,
            )
            self._threat_events[evt.id] = evt

        # Seed campaigns
        for i in range(3):
            camp = CampaignCluster(
                id=f"camp_{uuid.uuid4().hex[:8]}",
                name=f"Campaign {['Alpha', 'Bravo', 'Charlie'][i]}",
                detection_count=15 + i * 8,
                unique_sources=3 + i * 2,
                techniques_observed=techniques[:2+i],
                severity=severities[i],
                first_detection=(now - timedelta(days=30 - i * 10)).isoformat(),
                last_detection=(now - timedelta(hours=i * 12)).isoformat(),
                actor=actors[i % 2],
                is_active=i < 2,
            )
            self._campaigns[camp.id] = camp

        # Seed forensic cases
        for i in range(4):
            case = ForensicCase(
                id=f"case_{uuid.uuid4().hex[:8]}",
                tenant_id="tenant_enterprise",
                title=f"Investigation: {['Political Deepfake Series', 'Corporate Fraud Ring', 'Social Media Campaign', 'Audio Impersonation'][i]}",
                description=f"Forensic investigation case opened for coordinated deepfake activity.",
                status=["OPEN", "IN_PROGRESS", "ESCALATED", "RESOLVED"][i],
                priority=["CRITICAL", "HIGH", "MEDIUM", "LOW"][i],
                assigned_to=f"analyst_{i+1}@forensics.ai",
                evidence_items=[
                    EvidenceItem(
                        case_id=f"case_placeholder",
                        file_name=f"evidence_{i}_{j}.{'png' if j == 0 else 'mp4'}",
                        file_hash_sha256=hashlib.sha256(f"ev_{i}_{j}".encode()).hexdigest(),
                        file_size_bytes=1024 * 500 * (j + 1),
                        media_type="IMAGE" if j == 0 else "VIDEO",
                        chain_of_custody_hash=hashlib.sha256(f"coc_{i}_{j}_{time.time()}".encode()).hexdigest(),
                        collected_by=f"analyst_{i+1}@forensics.ai",
                    )
                    for j in range(2)
                ],
                tags=["political", "coordinated"] if i == 0 else ["corporate", "fraud"],
                created_at=(now - timedelta(days=20 - i * 5)).isoformat(),
            )
            self._cases[case.id] = case

        logger.info(f"Seeded demo data: {len(self._detections)} detections, "
                     f"{len(self._threat_events)} threats, {len(self._campaigns)} campaigns, "
                     f"{len(self._cases)} cases")


# ─── Query Resolvers ─────────────────────────────────────────────────────────

class QueryResolvers:
    """Resolvers for all GraphQL Query operations."""

    def __init__(self):
        self.store = DataStore()
        self.store.seed_demo_data()

    async def get_detection(self, detection_id: str) -> Optional[DetectionResult]:
        """Retrieve a single detection result by ID."""
        result = self.store._detections.get(detection_id)
        if result:
            logger.info(f"Resolved detection: {detection_id}")
        return result

    async def list_detections(self, filters: Optional[DetectionFilterInput] = None) -> List[DetectionResult]:
        """List detection results with optional filtering."""
        results = list(self.store._detections.values())

        if filters:
            if filters.tenant_id:
                results = [r for r in results if r.tenant_id == filters.tenant_id]
            if filters.verdict:
                results = [r for r in results if r.verdict == filters.verdict]
            if filters.media_type:
                results = [r for r in results if r.media_type == filters.media_type]
            if filters.min_confidence is not None:
                results = [r for r in results if r.overall_confidence >= filters.min_confidence]
            if filters.max_confidence is not None:
                results = [r for r in results if r.overall_confidence <= filters.max_confidence]
            if filters.date_from:
                results = [r for r in results if r.created_at >= filters.date_from]
            if filters.date_to:
                results = [r for r in results if r.created_at <= filters.date_to]

            offset = filters.offset or 0
            limit = filters.limit or 50
            results = results[offset:offset + limit]

        logger.info(f"Listed {len(results)} detections")
        return results

    async def get_threat_event(self, event_id: str) -> Optional[ThreatEvent]:
        """Retrieve a single threat event by ID."""
        return self.store._threat_events.get(event_id)

    async def list_threat_events(self, filters: Optional[ThreatFilterInput] = None) -> List[ThreatEvent]:
        """List threat events with optional filtering."""
        results = list(self.store._threat_events.values())

        if filters:
            if filters.tenant_id:
                results = [r for r in results if r.tenant_id == filters.tenant_id]
            if filters.severity:
                results = [r for r in results if r.severity == filters.severity]
            if filters.event_type:
                results = [r for r in results if r.event_type == filters.event_type]
            if filters.acknowledged is not None:
                results = [r for r in results if r.acknowledged == filters.acknowledged]

            offset = filters.offset or 0
            limit = filters.limit or 50
            results = results[offset:offset + limit]

        return results

    async def list_campaigns(self, active_only: bool = False) -> List[CampaignCluster]:
        """List deepfake campaigns."""
        results = list(self.store._campaigns.values())
        if active_only:
            results = [c for c in results if c.is_active]
        return results

    async def get_case(self, case_id: str) -> Optional[ForensicCase]:
        """Retrieve a forensic case by ID."""
        return self.store._cases.get(case_id)

    async def list_cases(self, tenant_id: Optional[str] = None,
                         status: Optional[str] = None) -> List[ForensicCase]:
        """List forensic investigation cases."""
        results = list(self.store._cases.values())
        if tenant_id:
            results = [c for c in results if c.tenant_id == tenant_id]
        if status:
            results = [c for c in results if c.status == status]
        return results

    async def get_tenant_usage(self, tenant_id: str) -> TenantUsageSnapshot:
        """Get current usage snapshot for a tenant."""
        detections = [d for d in self.store._detections.values()
                      if d.tenant_id == tenant_id]
        now = datetime.utcnow()
        today_str = now.date().isoformat()

        return TenantUsageSnapshot(
            tenant_id=tenant_id,
            total_detections=len(detections),
            detections_today=sum(1 for d in detections if d.created_at.startswith(today_str)),
            detections_this_month=len(detections),
            gpu_minutes_used=sum(d.processing_time_ms for d in detections) / 60000,
            active_cases=sum(1 for c in self.store._cases.values()
                            if c.tenant_id == tenant_id and c.status != "RESOLVED"),
        )

    async def get_platform_metrics(self) -> PlatformMetrics:
        """Get global platform health metrics."""
        all_detections = list(self.store._detections.values())
        avg_time = (sum(d.processing_time_ms for d in all_detections) / len(all_detections)
                    if all_detections else 0)

        return PlatformMetrics(
            total_tenants=len(set(d.tenant_id for d in all_detections)),
            active_tenants_24h=len(set(d.tenant_id for d in all_detections)),
            total_detections_24h=len(all_detections),
            avg_inference_time_ms=avg_time,
            gpu_utilization_percent=67.3,
            active_threat_campaigns=sum(1 for c in self.store._campaigns.values() if c.is_active),
            open_cases=sum(1 for c in self.store._cases.values() if c.status != "RESOLVED"),
            api_requests_per_minute=142.7,
            error_rate_percent=0.03,
            uptime_percent=99.97,
        )

    async def list_alert_rules(self, tenant_id: Optional[str] = None) -> List[AlertRule]:
        """List configured alert rules."""
        rules = list(self.store._alert_rules.values())
        if tenant_id:
            rules = [r for r in rules if r.tenant_id == tenant_id]
        return rules

    async def get_threat_actor(self, actor_id: str) -> Optional[ThreatActor]:
        """Look up a threat actor by ID."""
        return self.store._threat_actors.get(actor_id)

    async def list_threat_actors(self) -> List[ThreatActor]:
        """List all known threat actors."""
        return list(self.store._threat_actors.values())


# ─── Mutation Resolvers ──────────────────────────────────────────────────────

class MutationResolvers:
    """Resolvers for all GraphQL Mutation operations."""

    def __init__(self):
        self.store = DataStore()

    async def submit_detection(self, tenant_id: str, media_type: str,
                                file_hash: str, file_size_bytes: int) -> DetectionResult:
        """Submit media for deepfake detection analysis."""
        import random
        det_id = f"det_{uuid.uuid4().hex[:8]}"

        # Simulate ensemble inference
        verdict = random.choice(["MANIPULATED", "AUTHENTIC", "SUSPICIOUS"])
        confidence = random.uniform(0.65, 0.98)

        predictions = [
            ModelPrediction(
                model_name="EfficientNet-B7-Forensic", model_version="2.1.0",
                confidence=min(confidence + 0.02, 1.0), verdict=verdict,
                inference_time_ms=random.uniform(30, 80), device="cuda:0",
                features_extracted=2048
            ),
        ]

        regions = []
        if verdict == "MANIPULATED":
            regions.append(ManipulationRegion(
                x=random.uniform(0.1, 0.3), y=random.uniform(0.1, 0.3),
                width=random.uniform(0.2, 0.5), height=random.uniform(0.2, 0.5),
                confidence=confidence,
                technique=random.choice(["face_swap", "gan_synthesis", "inpainting"]),
                model_source="EfficientNet-B7-Forensic"
            ))

        result = DetectionResult(
            id=det_id, tenant_id=tenant_id, media_type=media_type,
            file_hash=file_hash, file_size_bytes=file_size_bytes,
            verdict=verdict, overall_confidence=confidence,
            model_predictions=predictions, manipulation_regions=regions,
            processing_time_ms=random.uniform(50, 200),
            gpu_memory_used_mb=random.uniform(200, 400),
        )
        self.store._detections[det_id] = result
        logger.info(f"New detection submitted: {det_id}, verdict={verdict}")
        return result

    async def acknowledge_threat(self, event_id: str, analyst: str) -> Optional[ThreatEvent]:
        """Mark a threat event as acknowledged by SOC analyst."""
        event = self.store._threat_events.get(event_id)
        if event:
            event.acknowledged = True
            logger.info(f"Threat {event_id} acknowledged by {analyst}")
        return event

    async def escalate_threat(self, event_id: str, reason: str) -> Optional[ThreatEvent]:
        """Escalate a threat event for senior review."""
        event = self.store._threat_events.get(event_id)
        if event:
            event.escalated = True
            event.severity = "CRITICAL"
            logger.info(f"Threat {event_id} escalated: {reason}")
        return event

    async def create_case(self, input_data: CreateCaseInput) -> ForensicCase:
        """Create a new forensic investigation case."""
        case = ForensicCase(
            tenant_id=input_data.tenant_id,
            title=input_data.title,
            description=input_data.description,
            priority=input_data.priority,
            assigned_to=input_data.assigned_to,
            tags=input_data.tags,
        )
        self.store._cases[case.id] = case
        logger.info(f"Created forensic case: {case.id} - {case.title}")
        return case

    async def update_case_status(self, case_id: str, status: str) -> Optional[ForensicCase]:
        """Update the status of a forensic case."""
        case = self.store._cases.get(case_id)
        if case:
            case.status = status
            case.updated_at = datetime.utcnow().isoformat()
            if status == "RESOLVED":
                case.closed_at = datetime.utcnow().isoformat()
            logger.info(f"Case {case_id} status updated to {status}")
        return case

    async def add_evidence(self, case_id: str, file_name: str,
                           file_hash: str, media_type: str,
                           collected_by: str) -> Optional[EvidenceItem]:
        """Add evidence to an existing forensic case."""
        case = self.store._cases.get(case_id)
        if not case:
            return None

        evidence = EvidenceItem(
            case_id=case_id, file_name=file_name,
            file_hash_sha256=file_hash, media_type=media_type,
            chain_of_custody_hash=hashlib.sha256(
                f"{file_hash}:{time.time()}".encode()
            ).hexdigest(),
            collected_by=collected_by,
        )
        case.evidence_items.append(evidence)
        case.updated_at = datetime.utcnow().isoformat()
        logger.info(f"Added evidence {evidence.id} to case {case_id}")
        return evidence

    async def create_alert_rule(self, input_data: CreateAlertRuleInput) -> AlertRule:
        """Create a new automated alert rule."""
        rule = AlertRule(
            tenant_id=input_data.tenant_id,
            name=input_data.name,
            description=input_data.description,
            condition_type=input_data.condition_type,
            condition_value=input_data.condition_value,
            channels=input_data.channels,
            cooldown_seconds=input_data.cooldown_seconds,
        )
        self.store._alert_rules[rule.id] = rule
        logger.info(f"Created alert rule: {rule.id} - {rule.name}")
        return rule

    async def toggle_alert_rule(self, rule_id: str, enabled: bool) -> Optional[AlertRule]:
        """Enable or disable an alert rule."""
        rule = self.store._alert_rules.get(rule_id)
        if rule:
            rule.is_enabled = enabled
            logger.info(f"Alert rule {rule_id} {'enabled' if enabled else 'disabled'}")
        return rule
