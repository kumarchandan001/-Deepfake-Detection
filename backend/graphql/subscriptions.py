"""
GraphQL Real-Time Subscriptions — AI Deepfake Detection & Enterprise Trust Platform.

Production-grade async event bus powering WebSocket-based GraphQL subscriptions
for live threat feeds, detection result streaming, and SOC dashboard updates.
Uses asyncio.Queue per subscriber with automatic cleanup and tenant isolation.
"""

import asyncio
import uuid
import time
from datetime import datetime
from typing import Dict, List, Optional, Set, AsyncGenerator, Any
from collections import defaultdict
from ai_engine.utils.logger import setup_logger

from backend.graphql.types import (
    ThreatEvent, DetectionResult, PlatformMetrics, AlertNotification,
)

logger = setup_logger("graphql_subscriptions")


# ─── Event Topics ────────────────────────────────────────────────────────────

class EventTopic:
    """Standard event topics for the subscription bus."""
    DETECTION_COMPLETED = "detection.completed"
    THREAT_DETECTED = "threat.detected"
    THREAT_ESCALATED = "threat.escalated"
    CAMPAIGN_IDENTIFIED = "campaign.identified"
    CASE_UPDATED = "case.updated"
    ALERT_FIRED = "alert.fired"
    PLATFORM_METRICS = "platform.metrics"
    TENANT_QUOTA_WARNING = "tenant.quota_warning"
    TENANT_QUOTA_EXCEEDED = "tenant.quota_exceeded"
    SYSTEM_HEALTH = "system.health"


# ─── Subscriber ──────────────────────────────────────────────────────────────

class Subscriber:
    """Individual WebSocket subscriber with isolated async queue."""

    def __init__(self, subscriber_id: str, tenant_id: str,
                 topics: Set[str], max_queue_size: int = 1000):
        self.id = subscriber_id
        self.tenant_id = tenant_id
        self.topics = topics
        self.queue: asyncio.Queue = asyncio.Queue(maxsize=max_queue_size)
        self.created_at = time.time()
        self.last_event_at: Optional[float] = None
        self.events_received = 0
        self.is_active = True

    async def push(self, event: Dict[str, Any]) -> bool:
        """Push an event to this subscriber's queue. Returns False if full."""
        if not self.is_active:
            return False
        try:
            self.queue.put_nowait(event)
            self.last_event_at = time.time()
            self.events_received += 1
            return True
        except asyncio.QueueFull:
            logger.warning(f"Subscriber {self.id} queue full, dropping event")
            return False

    async def pull(self, timeout: float = 30.0) -> Optional[Dict[str, Any]]:
        """Pull the next event from queue, with timeout."""
        try:
            return await asyncio.wait_for(self.queue.get(), timeout=timeout)
        except asyncio.TimeoutError:
            return None

    def deactivate(self):
        """Mark subscriber as inactive for cleanup."""
        self.is_active = False


# ─── Event Bus ───────────────────────────────────────────────────────────────

class SubscriptionEventBus:
    """
    Async event bus managing pub/sub for GraphQL subscriptions.

    Features:
    - Per-tenant event isolation
    - Topic-based routing
    - Automatic subscriber cleanup
    - Backpressure handling via bounded queues
    - Event history for late joiners
    """
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._subscribers: Dict[str, Subscriber] = {}
            cls._instance._topic_subscribers: Dict[str, Set[str]] = defaultdict(set)
            cls._instance._event_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
            cls._instance._max_history = 100
            cls._instance._stats = {
                "total_events_published": 0,
                "total_events_delivered": 0,
                "total_events_dropped": 0,
                "total_subscribers_created": 0,
                "total_subscribers_removed": 0,
            }
            cls._instance._cleanup_task = None
        return cls._instance

    def subscribe(self, tenant_id: str, topics: Set[str],
                  replay_last: int = 0) -> Subscriber:
        """
        Register a new subscriber for specified topics.

        Args:
            tenant_id: Tenant isolation scope
            topics: Set of event topics to subscribe to
            replay_last: Number of recent events to replay on connect

        Returns:
            Subscriber instance with async event queue
        """
        sub_id = f"sub_{uuid.uuid4().hex[:12]}"
        subscriber = Subscriber(sub_id, tenant_id, topics)

        self._subscribers[sub_id] = subscriber
        for topic in topics:
            self._topic_subscribers[topic].add(sub_id)

        self._stats["total_subscribers_created"] += 1

        # Replay recent events if requested
        if replay_last > 0:
            for topic in topics:
                history = self._event_history.get(topic, [])
                for event in history[-replay_last:]:
                    # Only replay tenant-scoped events
                    if event.get("tenant_id") in (tenant_id, None, "*"):
                        asyncio.ensure_future(subscriber.push(event))

        logger.info(f"New subscriber {sub_id} for tenant {tenant_id}, "
                     f"topics={topics}, replay={replay_last}")
        return subscriber

    def unsubscribe(self, subscriber_id: str):
        """Remove a subscriber and clean up topic registrations."""
        subscriber = self._subscribers.pop(subscriber_id, None)
        if subscriber:
            subscriber.deactivate()
            for topic in subscriber.topics:
                self._topic_subscribers[topic].discard(subscriber_id)
            self._stats["total_subscribers_removed"] += 1
            logger.info(f"Removed subscriber {subscriber_id}")

    async def publish(self, topic: str, payload: Dict[str, Any],
                      tenant_id: Optional[str] = None):
        """
        Publish an event to all subscribers of the given topic.

        Args:
            topic: Event topic string
            payload: Event payload data
            tenant_id: If set, only deliver to matching tenant subscribers
        """
        event = {
            "id": str(uuid.uuid4()),
            "topic": topic,
            "tenant_id": tenant_id,
            "payload": payload,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Store in history
        self._event_history[topic].append(event)
        if len(self._event_history[topic]) > self._max_history:
            self._event_history[topic] = self._event_history[topic][-self._max_history:]

        self._stats["total_events_published"] += 1

        # Fan out to matching subscribers
        subscriber_ids = self._topic_subscribers.get(topic, set()).copy()
        delivered = 0
        dropped = 0

        for sub_id in subscriber_ids:
            subscriber = self._subscribers.get(sub_id)
            if not subscriber or not subscriber.is_active:
                continue

            # Tenant isolation: only deliver if tenant matches or is global
            if tenant_id and subscriber.tenant_id != tenant_id and tenant_id != "*":
                continue

            success = await subscriber.push(event)
            if success:
                delivered += 1
            else:
                dropped += 1

        self._stats["total_events_delivered"] += delivered
        self._stats["total_events_dropped"] += dropped

        if delivered > 0:
            logger.debug(f"Published {topic}: delivered={delivered}, dropped={dropped}")

    async def publish_detection_result(self, result: DetectionResult):
        """Convenience: publish a detection completion event."""
        await self.publish(
            EventTopic.DETECTION_COMPLETED,
            {
                "detection_id": result.id,
                "verdict": result.verdict,
                "confidence": result.overall_confidence,
                "media_type": result.media_type,
                "processing_time_ms": result.processing_time_ms,
                "model_count": len(result.model_predictions),
            },
            tenant_id=result.tenant_id,
        )

    async def publish_threat_event(self, event: ThreatEvent):
        """Convenience: publish a real-time threat event."""
        await self.publish(
            EventTopic.THREAT_DETECTED,
            {
                "event_id": event.id,
                "severity": event.severity,
                "event_type": event.event_type,
                "title": event.title,
                "description": event.description,
                "source_ip": event.source_ip,
                "actor_alias": event.actor.alias if event.actor else None,
            },
            tenant_id=event.tenant_id,
        )

    async def publish_platform_metrics(self, metrics: PlatformMetrics):
        """Convenience: publish platform health metrics (global broadcast)."""
        await self.publish(
            EventTopic.PLATFORM_METRICS,
            {
                "total_tenants": metrics.total_tenants,
                "active_tenants_24h": metrics.active_tenants_24h,
                "total_detections_24h": metrics.total_detections_24h,
                "avg_inference_time_ms": metrics.avg_inference_time_ms,
                "gpu_utilization_percent": metrics.gpu_utilization_percent,
                "uptime_percent": metrics.uptime_percent,
                "error_rate_percent": metrics.error_rate_percent,
            },
            tenant_id="*",
        )

    async def publish_alert(self, notification: AlertNotification):
        """Convenience: publish an alert notification."""
        await self.publish(
            EventTopic.ALERT_FIRED,
            {
                "notification_id": notification.id,
                "rule_id": notification.rule_id,
                "title": notification.title,
                "message": notification.message,
                "severity": notification.severity,
                "channel": notification.channel,
            },
            tenant_id=notification.tenant_id,
        )

    async def cleanup_stale_subscribers(self, max_idle_seconds: float = 3600):
        """Remove subscribers that haven't received events recently."""
        now = time.time()
        stale = []
        for sub_id, subscriber in self._subscribers.items():
            if not subscriber.is_active:
                stale.append(sub_id)
            elif subscriber.last_event_at and (now - subscriber.last_event_at) > max_idle_seconds:
                stale.append(sub_id)
            elif (now - subscriber.created_at) > max_idle_seconds and subscriber.events_received == 0:
                stale.append(sub_id)

        for sub_id in stale:
            self.unsubscribe(sub_id)

        if stale:
            logger.info(f"Cleaned up {len(stale)} stale subscribers")

    def get_stats(self) -> Dict[str, Any]:
        """Return event bus statistics."""
        return {
            **self._stats,
            "active_subscribers": len([s for s in self._subscribers.values() if s.is_active]),
            "topics_active": len(self._topic_subscribers),
            "history_size": sum(len(v) for v in self._event_history.values()),
        }


# ─── Subscription Stream Generators ─────────────────────────────────────────

class SubscriptionStreams:
    """
    Async generators for GraphQL subscription fields.
    Each generator yields events from the event bus filtered by topic/tenant.
    """

    def __init__(self):
        self.bus = SubscriptionEventBus()

    async def detection_stream(self, tenant_id: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream new detection results for a tenant."""
        subscriber = self.bus.subscribe(
            tenant_id, {EventTopic.DETECTION_COMPLETED}, replay_last=5
        )
        try:
            while subscriber.is_active:
                event = await subscriber.pull(timeout=30.0)
                if event:
                    yield event["payload"]
                else:
                    # Send keepalive
                    yield {"type": "keepalive", "timestamp": datetime.utcnow().isoformat()}
        finally:
            self.bus.unsubscribe(subscriber.id)

    async def threat_feed(self, tenant_id: str,
                          min_severity: Optional[str] = None) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream real-time threat events for SOC dashboard."""
        severity_order = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1, "INFO": 0}
        min_level = severity_order.get(min_severity, 0) if min_severity else 0

        subscriber = self.bus.subscribe(
            tenant_id,
            {EventTopic.THREAT_DETECTED, EventTopic.THREAT_ESCALATED,
             EventTopic.CAMPAIGN_IDENTIFIED},
            replay_last=10,
        )
        try:
            while subscriber.is_active:
                event = await subscriber.pull(timeout=30.0)
                if event:
                    payload = event["payload"]
                    event_severity = severity_order.get(payload.get("severity", "INFO"), 0)
                    if event_severity >= min_level:
                        yield payload
                else:
                    yield {"type": "keepalive", "timestamp": datetime.utcnow().isoformat()}
        finally:
            self.bus.unsubscribe(subscriber.id)

    async def platform_health_stream(self) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream platform-wide health metrics (admin only)."""
        subscriber = self.bus.subscribe(
            "*", {EventTopic.PLATFORM_METRICS, EventTopic.SYSTEM_HEALTH}
        )
        try:
            while subscriber.is_active:
                event = await subscriber.pull(timeout=30.0)
                if event:
                    yield event["payload"]
                else:
                    yield {"type": "keepalive", "timestamp": datetime.utcnow().isoformat()}
        finally:
            self.bus.unsubscribe(subscriber.id)

    async def alert_stream(self, tenant_id: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream alert notifications for a tenant."""
        subscriber = self.bus.subscribe(
            tenant_id, {EventTopic.ALERT_FIRED}, replay_last=5
        )
        try:
            while subscriber.is_active:
                event = await subscriber.pull(timeout=30.0)
                if event:
                    yield event["payload"]
                else:
                    yield {"type": "keepalive", "timestamp": datetime.utcnow().isoformat()}
        finally:
            self.bus.unsubscribe(subscriber.id)

    async def case_updates_stream(self, tenant_id: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream forensic case status updates."""
        subscriber = self.bus.subscribe(
            tenant_id, {EventTopic.CASE_UPDATED}, replay_last=3
        )
        try:
            while subscriber.is_active:
                event = await subscriber.pull(timeout=30.0)
                if event:
                    yield event["payload"]
                else:
                    yield {"type": "keepalive", "timestamp": datetime.utcnow().isoformat()}
        finally:
            self.bus.unsubscribe(subscriber.id)
