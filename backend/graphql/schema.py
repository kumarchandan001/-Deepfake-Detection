"""
GraphQL Schema & FastAPI Integration — AI Deepfake Detection & Enterprise Trust Platform.

Assembles the complete GraphQL schema from resolvers, wires subscriptions via WebSockets,
and exposes the GraphQL endpoint on FastAPI with authentication and tenant context.
"""

import json
from typing import Optional, Dict, Any, List
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from ai_engine.utils.logger import setup_logger

from backend.graphql.types import (
    DetectionFilterInput, ThreatFilterInput,
    CreateCaseInput, CreateAlertRuleInput,
)
from backend.graphql.resolvers import QueryResolvers, MutationResolvers
from backend.graphql.subscriptions import (
    SubscriptionEventBus, SubscriptionStreams, EventTopic,
)

logger = setup_logger("graphql_schema")

router = APIRouter(prefix="/api/v1/graphql", tags=["GraphQL"])

# Instantiate resolvers
_query = QueryResolvers()
_mutation = MutationResolvers()
_streams = SubscriptionStreams()
_bus = SubscriptionEventBus()


# ─── Query Dispatcher ────────────────────────────────────────────────────────

async def _dispatch_query(query_name: str, variables: Dict[str, Any],
                          tenant_id: str) -> Any:
    """Route a named query to the appropriate resolver."""

    if query_name == "detection":
        return await _query.get_detection(variables.get("id", ""))
    elif query_name == "detections":
        filters = DetectionFilterInput(
            tenant_id=variables.get("tenant_id", tenant_id),
            verdict=variables.get("verdict"),
            media_type=variables.get("media_type"),
            min_confidence=variables.get("min_confidence"),
            max_confidence=variables.get("max_confidence"),
            date_from=variables.get("date_from"),
            date_to=variables.get("date_to"),
            limit=variables.get("limit", 50),
            offset=variables.get("offset", 0),
        )
        return await _query.list_detections(filters)
    elif query_name == "threatEvent":
        return await _query.get_threat_event(variables.get("id", ""))
    elif query_name == "threatEvents":
        filters = ThreatFilterInput(
            tenant_id=variables.get("tenant_id", tenant_id),
            severity=variables.get("severity"),
            event_type=variables.get("event_type"),
            acknowledged=variables.get("acknowledged"),
            limit=variables.get("limit", 50),
            offset=variables.get("offset", 0),
        )
        return await _query.list_threat_events(filters)
    elif query_name == "campaigns":
        return await _query.list_campaigns(variables.get("active_only", False))
    elif query_name == "case":
        return await _query.get_case(variables.get("id", ""))
    elif query_name == "cases":
        return await _query.list_cases(
            tenant_id=variables.get("tenant_id", tenant_id),
            status=variables.get("status"),
        )
    elif query_name == "tenantUsage":
        return await _query.get_tenant_usage(variables.get("tenant_id", tenant_id))
    elif query_name == "platformMetrics":
        return await _query.get_platform_metrics()
    elif query_name == "alertRules":
        return await _query.list_alert_rules(variables.get("tenant_id", tenant_id))
    elif query_name == "threatActor":
        return await _query.get_threat_actor(variables.get("id", ""))
    elif query_name == "threatActors":
        return await _query.list_threat_actors()
    else:
        raise ValueError(f"Unknown query: {query_name}")


# ─── Mutation Dispatcher ─────────────────────────────────────────────────────

async def _dispatch_mutation(mutation_name: str, variables: Dict[str, Any],
                             tenant_id: str) -> Any:
    """Route a named mutation to the appropriate resolver."""

    if mutation_name == "submitDetection":
        result = await _mutation.submit_detection(
            tenant_id=variables.get("tenant_id", tenant_id),
            media_type=variables.get("media_type", "IMAGE"),
            file_hash=variables.get("file_hash", ""),
            file_size_bytes=variables.get("file_size_bytes", 0),
        )
        # Publish real-time event
        await _bus.publish_detection_result(result)
        return result
    elif mutation_name == "acknowledgeThreat":
        return await _mutation.acknowledge_threat(
            variables.get("event_id", ""),
            variables.get("analyst", "unknown"),
        )
    elif mutation_name == "escalateThreat":
        result = await _mutation.escalate_threat(
            variables.get("event_id", ""),
            variables.get("reason", ""),
        )
        if result:
            await _bus.publish(
                EventTopic.THREAT_ESCALATED,
                {"event_id": result.id, "severity": result.severity},
                tenant_id=result.tenant_id,
            )
        return result
    elif mutation_name == "createCase":
        input_data = CreateCaseInput(
            tenant_id=variables.get("tenant_id", tenant_id),
            title=variables.get("title", ""),
            description=variables.get("description", ""),
            priority=variables.get("priority", "MEDIUM"),
            assigned_to=variables.get("assigned_to", ""),
            tags=variables.get("tags", []),
        )
        return await _mutation.create_case(input_data)
    elif mutation_name == "updateCaseStatus":
        result = await _mutation.update_case_status(
            variables.get("case_id", ""),
            variables.get("status", ""),
        )
        if result:
            await _bus.publish(
                EventTopic.CASE_UPDATED,
                {"case_id": result.id, "status": result.status, "title": result.title},
                tenant_id=result.tenant_id,
            )
        return result
    elif mutation_name == "addEvidence":
        return await _mutation.add_evidence(
            case_id=variables.get("case_id", ""),
            file_name=variables.get("file_name", ""),
            file_hash=variables.get("file_hash", ""),
            media_type=variables.get("media_type", "IMAGE"),
            collected_by=variables.get("collected_by", ""),
        )
    elif mutation_name == "createAlertRule":
        input_data = CreateAlertRuleInput(
            tenant_id=variables.get("tenant_id", tenant_id),
            name=variables.get("name", ""),
            description=variables.get("description", ""),
            condition_type=variables.get("condition_type", "threshold"),
            condition_value=variables.get("condition_value", {}),
            channels=variables.get("channels", ["WEBHOOK"]),
            cooldown_seconds=variables.get("cooldown_seconds", 300),
        )
        return await _mutation.create_alert_rule(input_data)
    elif mutation_name == "toggleAlertRule":
        return await _mutation.toggle_alert_rule(
            variables.get("rule_id", ""),
            variables.get("enabled", True),
        )
    else:
        raise ValueError(f"Unknown mutation: {mutation_name}")


# ─── Serialization Helper ────────────────────────────────────────────────────

def _serialize(obj: Any) -> Any:
    """Recursively convert dataclass objects to JSON-serializable dicts."""
    if obj is None:
        return None
    if isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, list):
        return [_serialize(item) for item in obj]
    if isinstance(obj, dict):
        return {k: _serialize(v) for k, v in obj.items()}
    if hasattr(obj, "__dataclass_fields__"):
        return {k: _serialize(v) for k, v in obj.__dict__.items()}
    return str(obj)


# ─── HTTP GraphQL Endpoint ───────────────────────────────────────────────────

@router.post("")
async def graphql_endpoint(request: Request):
    """
    Main GraphQL endpoint accepting JSON POST requests.

    Request body format:
    {
        "operation": "query" | "mutation",
        "name": "<operation_name>",
        "variables": { ... }
    }
    """
    tenant_id = request.headers.get("X-Tenant-ID", "default_tenant")

    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    operation = body.get("operation", "query")
    name = body.get("name", "")
    variables = body.get("variables", {})

    if not name:
        raise HTTPException(status_code=400, detail="Missing operation name")

    try:
        if operation == "query":
            result = await _dispatch_query(name, variables, tenant_id)
        elif operation == "mutation":
            result = await _dispatch_mutation(name, variables, tenant_id)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown operation: {operation}")

        return JSONResponse({
            "data": _serialize(result),
            "errors": None,
            "extensions": {
                "timestamp": datetime.utcnow().isoformat(),
                "tenant_id": tenant_id,
            }
        })

    except ValueError as e:
        return JSONResponse(
            status_code=400,
            content={"data": None, "errors": [{"message": str(e)}]}
        )
    except Exception as e:
        logger.error(f"GraphQL error: {e}")
        return JSONResponse(
            status_code=500,
            content={"data": None, "errors": [{"message": "Internal server error"}]}
        )


@router.get("/stats")
async def graphql_stats():
    """Return event bus and subscription statistics."""
    return JSONResponse({
        "event_bus": _bus.get_stats(),
        "timestamp": datetime.utcnow().isoformat(),
    })


# ─── WebSocket Subscription Endpoint ─────────────────────────────────────────

@router.websocket("/ws")
async def graphql_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for GraphQL subscriptions.

    Client sends JSON messages to subscribe/unsubscribe:
    {
        "type": "subscribe",
        "stream": "threat_feed" | "detection_stream" | "platform_health" | "alerts" | "case_updates",
        "variables": { "tenant_id": "...", "min_severity": "HIGH" }
    }
    """
    await websocket.accept()
    tenant_id = websocket.headers.get("x-tenant-id", "default_tenant")
    logger.info(f"WebSocket connection opened for tenant: {tenant_id}")

    active_tasks: Dict[str, Any] = {}

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                message = json.loads(raw)
            except json.JSONDecodeError:
                await websocket.send_json({"error": "Invalid JSON"})
                continue

            msg_type = message.get("type", "")
            stream_name = message.get("stream", "")
            variables = message.get("variables", {})
            stream_tenant = variables.get("tenant_id", tenant_id)

            if msg_type == "subscribe":
                if stream_name in active_tasks:
                    await websocket.send_json(
                        {"error": f"Already subscribed to {stream_name}"}
                    )
                    continue

                # Map stream name to generator
                generator = None
                if stream_name == "detection_stream":
                    generator = _streams.detection_stream(stream_tenant)
                elif stream_name == "threat_feed":
                    generator = _streams.threat_feed(
                        stream_tenant,
                        min_severity=variables.get("min_severity"),
                    )
                elif stream_name == "platform_health":
                    generator = _streams.platform_health_stream()
                elif stream_name == "alerts":
                    generator = _streams.alert_stream(stream_tenant)
                elif stream_name == "case_updates":
                    generator = _streams.case_updates_stream(stream_tenant)
                else:
                    await websocket.send_json(
                        {"error": f"Unknown stream: {stream_name}"}
                    )
                    continue

                async def _stream_task(ws, gen, name):
                    try:
                        async for event in gen:
                            await ws.send_json({
                                "type": "data",
                                "stream": name,
                                "payload": event,
                            })
                    except WebSocketDisconnect:
                        pass
                    except Exception as e:
                        logger.error(f"Stream error [{name}]: {e}")

                import asyncio
                task = asyncio.create_task(_stream_task(websocket, generator, stream_name))
                active_tasks[stream_name] = task

                await websocket.send_json({
                    "type": "subscribed",
                    "stream": stream_name,
                    "timestamp": datetime.utcnow().isoformat(),
                })

            elif msg_type == "unsubscribe":
                task = active_tasks.pop(stream_name, None)
                if task:
                    task.cancel()
                    await websocket.send_json({
                        "type": "unsubscribed",
                        "stream": stream_name,
                    })

            elif msg_type == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat(),
                })

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for tenant: {tenant_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        # Cancel all active streaming tasks
        for task in active_tasks.values():
            task.cancel()
        logger.info(f"Cleaned up {len(active_tasks)} active streams for tenant {tenant_id}")


# ─── GraphQL Playground (Development) ────────────────────────────────────────

PLAYGROUND_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>DeepGuard AI — GraphQL Playground</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Inter', system-ui, sans-serif; background: #0a0e17; color: #e1e5ee; }
        .header { background: linear-gradient(135deg, #1a1f2e 0%, #0d1117 100%);
                  padding: 20px 32px; border-bottom: 1px solid #21262d; }
        .header h1 { font-size: 18px; color: #58a6ff; }
        .header p { font-size: 13px; color: #8b949e; margin-top: 4px; }
        .container { display: grid; grid-template-columns: 1fr 1fr; height: calc(100vh - 80px); }
        .panel { padding: 16px; }
        .editor { width: 100%; height: calc(100% - 60px); background: #0d1117;
                  border: 1px solid #21262d; border-radius: 8px; color: #c9d1d9;
                  font-family: 'Fira Code', monospace; font-size: 13px; padding: 16px;
                  resize: none; outline: none; }
        .result { width: 100%; height: calc(100% - 40px); background: #0d1117;
                  border: 1px solid #21262d; border-radius: 8px; color: #7ee787;
                  font-family: 'Fira Code', monospace; font-size: 13px; padding: 16px;
                  overflow: auto; white-space: pre-wrap; }
        .btn { background: linear-gradient(135deg, #238636, #2ea043); color: white;
               border: none; padding: 10px 24px; border-radius: 6px; cursor: pointer;
               font-weight: 600; font-size: 14px; margin-top: 12px; }
        .btn:hover { filter: brightness(1.1); }
        .label { font-size: 12px; color: #8b949e; margin-bottom: 8px; text-transform: uppercase;
                 letter-spacing: 1px; font-weight: 600; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🛡️ DeepGuard AI — GraphQL Playground</h1>
        <p>Enterprise Deepfake Detection & Forensics Intelligence API</p>
    </div>
    <div class="container">
        <div class="panel">
            <div class="label">Query / Mutation</div>
            <textarea class="editor" id="query">{
  "operation": "query",
  "name": "detections",
  "variables": {
    "verdict": "MANIPULATED",
    "limit": 5
  }
}</textarea>
            <button class="btn" onclick="executeQuery()">▶ Execute</button>
        </div>
        <div class="panel">
            <div class="label">Response</div>
            <div class="result" id="result">// Results will appear here...</div>
        </div>
    </div>
    <script>
        async function executeQuery() {
            const query = document.getElementById('query').value;
            const resultEl = document.getElementById('result');
            try {
                const body = JSON.parse(query);
                const resp = await fetch('/api/v1/graphql', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'X-Tenant-ID': 'playground_tenant' },
                    body: JSON.stringify(body)
                });
                const data = await resp.json();
                resultEl.textContent = JSON.stringify(data, null, 2);
                resultEl.style.color = data.errors ? '#f85149' : '#7ee787';
            } catch (e) {
                resultEl.textContent = 'Error: ' + e.message;
                resultEl.style.color = '#f85149';
            }
        }
    </script>
</body>
</html>
"""


@router.get("/playground", response_class=HTMLResponse)
async def graphql_playground():
    """Interactive GraphQL playground for development and testing."""
    return HTMLResponse(content=PLAYGROUND_HTML)
