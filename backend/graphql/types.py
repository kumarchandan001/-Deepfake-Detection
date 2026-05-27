"""
GraphQL Type Definitions — AI Deepfake Detection & Enterprise Trust Platform.

Defines all Strawberry-compatible GraphQL types for detection results, threat events,
tenant analytics, forensic cases, and real-time SOC dashboard feeds.
"""

import enum
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field


# ─── Enums ───────────────────────────────────────────────────────────────────

class DetectionVerdict(enum.Enum):
    AUTHENTIC = "AUTHENTIC"
    MANIPULATED = "MANIPULATED"
    SUSPICIOUS = "SUSPICIOUS"
    INCONCLUSIVE = "INCONCLUSIVE"


class MediaType(enum.Enum):
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"
    AUDIO = "AUDIO"
    DOCUMENT = "DOCUMENT"
    LIVESTREAM = "LIVESTREAM"


class ThreatSeverity(enum.Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class CaseStatus(enum.Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    ESCALATED = "ESCALATED"
    RESOLVED = "RESOLVED"
    ARCHIVED = "ARCHIVED"


class AlertChannel(enum.Enum):
    WEBHOOK = "WEBHOOK"
    EMAIL = "EMAIL"
    SLACK = "SLACK"
    DISCORD = "DISCORD"
    SMS = "SMS"
    PAGERDUTY = "PAGERDUTY"


# ─── Detection Types ────────────────────────────────────────────────────────

@dataclass
class ManipulationRegion:
    """Spatial region flagged as manipulated within media."""
    x: float
    y: float
    width: float
    height: float
    confidence: float
    technique: str  # e.g. "face_swap", "inpainting", "splicing"
    model_source: str  # which model detected it


@dataclass
class ModelPrediction:
    """Individual model prediction within the ensemble."""
    model_name: str
    model_version: str
    confidence: float
    verdict: str
    inference_time_ms: float
    device: str  # "cpu", "cuda:0", etc.
    features_extracted: int


@dataclass
class DetectionResult:
    """Complete deepfake detection analysis result."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str = ""
    media_type: str = "IMAGE"
    file_hash: str = ""
    file_size_bytes: int = 0
    verdict: str = "INCONCLUSIVE"
    overall_confidence: float = 0.0
    model_predictions: List[ModelPrediction] = field(default_factory=list)
    manipulation_regions: List[ManipulationRegion] = field(default_factory=list)
    processing_time_ms: float = 0.0
    gpu_memory_used_mb: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    explainability_map_url: Optional[str] = None


# ─── Threat Intelligence Types ───────────────────────────────────────────────

@dataclass
class ThreatActor:
    """Identified or suspected threat actor behind deepfake campaigns."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    alias: str = ""
    known_techniques: List[str] = field(default_factory=list)
    associated_ips: List[str] = field(default_factory=list)
    first_seen: str = ""
    last_seen: str = ""
    threat_score: float = 0.0
    attribution_confidence: float = 0.0


@dataclass
class ThreatEvent:
    """Real-time threat event for SOC dashboard streaming."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str = ""
    severity: str = "MEDIUM"
    event_type: str = ""  # "deepfake_detected", "campaign_identified", "new_actor"
    title: str = ""
    description: str = ""
    source_ip: Optional[str] = None
    detection_id: Optional[str] = None
    actor: Optional[ThreatActor] = None
    ioc_indicators: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    acknowledged: bool = False
    escalated: bool = False


@dataclass
class CampaignCluster:
    """Cluster of related deepfake detections forming a campaign."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    detection_count: int = 0
    unique_sources: int = 0
    techniques_observed: List[str] = field(default_factory=list)
    severity: str = "MEDIUM"
    first_detection: str = ""
    last_detection: str = ""
    actor: Optional[ThreatActor] = None
    is_active: bool = True


# ─── Forensic Investigation Types ────────────────────────────────────────────

@dataclass
class EvidenceItem:
    """Digital evidence artifact within a forensic case."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    case_id: str = ""
    file_name: str = ""
    file_hash_sha256: str = ""
    file_size_bytes: int = 0
    media_type: str = "IMAGE"
    chain_of_custody_hash: str = ""  # cryptographic integrity
    detection_result_id: Optional[str] = None
    collected_by: str = ""
    collected_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    notes: str = ""


@dataclass
class ForensicCase:
    """Full forensic investigation case."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str = ""
    title: str = ""
    description: str = ""
    status: str = "OPEN"
    priority: str = "MEDIUM"
    assigned_to: str = ""
    evidence_items: List[EvidenceItem] = field(default_factory=list)
    related_threat_events: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    closed_at: Optional[str] = None


# ─── Tenant & Analytics Types ────────────────────────────────────────────────

@dataclass
class TenantUsageSnapshot:
    """Point-in-time usage metrics for a tenant."""
    tenant_id: str = ""
    plan_key: str = "free"
    total_detections: int = 0
    detections_today: int = 0
    detections_this_month: int = 0
    quota_remaining: int = 0
    gpu_minutes_used: float = 0.0
    api_calls_today: int = 0
    storage_used_mb: float = 0.0
    active_cases: int = 0
    snapshot_time: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class PlatformMetrics:
    """Global platform health and performance metrics."""
    total_tenants: int = 0
    active_tenants_24h: int = 0
    total_detections_24h: int = 0
    avg_inference_time_ms: float = 0.0
    gpu_utilization_percent: float = 0.0
    active_threat_campaigns: int = 0
    open_cases: int = 0
    api_requests_per_minute: float = 0.0
    error_rate_percent: float = 0.0
    uptime_percent: float = 99.99
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


# ─── Alert & Notification Types ──────────────────────────────────────────────

@dataclass
class AlertRule:
    """Configurable alert rule for automated SOC notifications."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str = ""
    name: str = ""
    description: str = ""
    condition_type: str = ""  # "threshold", "pattern", "anomaly"
    condition_value: Dict[str, Any] = field(default_factory=dict)
    channels: List[str] = field(default_factory=list)
    is_enabled: bool = True
    cooldown_seconds: int = 300
    last_triggered: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class AlertNotification:
    """Dispatched alert notification record."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    rule_id: str = ""
    tenant_id: str = ""
    channel: str = "WEBHOOK"
    title: str = ""
    message: str = ""
    severity: str = "MEDIUM"
    delivered: bool = False
    delivered_at: Optional[str] = None
    error: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


# ─── Input Types ─────────────────────────────────────────────────────────────

@dataclass
class DetectionFilterInput:
    """Filter criteria for querying detection results."""
    tenant_id: Optional[str] = None
    verdict: Optional[str] = None
    media_type: Optional[str] = None
    min_confidence: Optional[float] = None
    max_confidence: Optional[float] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    limit: int = 50
    offset: int = 0


@dataclass
class ThreatFilterInput:
    """Filter criteria for querying threat events."""
    tenant_id: Optional[str] = None
    severity: Optional[str] = None
    event_type: Optional[str] = None
    acknowledged: Optional[bool] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    limit: int = 50
    offset: int = 0


@dataclass
class CreateCaseInput:
    """Input for creating a new forensic case."""
    tenant_id: str = ""
    title: str = ""
    description: str = ""
    priority: str = "MEDIUM"
    assigned_to: str = ""
    related_detection_ids: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)


@dataclass
class CreateAlertRuleInput:
    """Input for creating an alert rule."""
    tenant_id: str = ""
    name: str = ""
    description: str = ""
    condition_type: str = "threshold"
    condition_value: Dict[str, Any] = field(default_factory=dict)
    channels: List[str] = field(default_factory=lambda: ["WEBHOOK"])
    cooldown_seconds: int = 300
