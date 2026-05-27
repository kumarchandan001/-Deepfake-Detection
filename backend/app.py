from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from backend.routes.detection_routes import router as detection_router
from backend.routes.video_routes import router as video_router
from backend.routes.realtime_routes import router as realtime_router
from backend.routes.auth_routes import router as auth_router
from backend.routes.investigation_routes import router as investigation_router
from backend.routes.intelligence_routes import router as intelligence_router
from backend.routes.threat_routes import router as threat_router

# Import Enterprise GraphQL Realtime Engine
from backend.graphql.schema import router as graphql_router

# Import Enterprise SaaS billing, pricing, subscriptions, and routing components
from enterprise.saas.billing_routes import router as billing_router
from enterprise.saas.tenant_routes import router as tenant_router
from enterprise.saas.subscription_routes import router as subscription_router
from enterprise.saas.tenant_middleware import TenantContextMiddleware
from enterprise.saas.quota_middleware import QuotaEnforcementMiddleware

from backend.security.protection_middleware import SecurityProtectionMiddleware
from backend.monitoring.prometheus_metrics import instrument_app
from backend.db.config import init_database
from ai_engine.utils.logger import setup_logger

logger = setup_logger("app_main")

app = FastAPI(
    title="AI Deepfake Detection & Autonomous Forensics Platform Gateway",
    description="Enterprise ASGI cybersecurity verification gateway mapping neural layers and campaign intelligence graphs.",
    version="1.0.0"
)

# 1. Register secure DDoS IP rate limiting & security headers middleware
app.add_middleware(SecurityProtectionMiddleware, requests_per_minute=120)

# 2. Register multi-tenant billing contexts and usage quota enforcement middleware
app.add_middleware(QuotaEnforcementMiddleware)
app.add_middleware(TenantContextMiddleware)

# 3. Configure Cross-Origin Resource Sharing (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Setup lifecycle events to auto-initialize database schemas
@app.on_event("startup")
async def startup_db_initialization():
    logger.info("Initializing relational metadata schemas...")
    await init_database()

# 5. Include REST, real-time WebSockets, autonomous intelligence, and GraphQL routes
app.include_router(detection_router)
app.include_router(video_router)
app.include_router(realtime_router)
app.include_router(auth_router)
app.include_router(investigation_router)
app.include_router(intelligence_router)
app.include_router(threat_router)

# 6. Include GraphQL and Enterprise SaaS Subscription Routers
app.include_router(graphql_router)
app.include_router(billing_router)
app.include_router(tenant_router)
app.include_router(subscription_router)

# 7. Instrument ASGI gateway with Prometheus active telemetry scraping
instrument_app(app)

@app.get("/health", status_code=status.HTTP_200_OK, tags=["System Health"])
async def system_health_check():
    """
    Standard heartbeat check endpoint.
    """
    return {
        "status": "HEALTHY",
        "message": "AI Deepfake Detection Platform is online and responsive."
    }

logger.info("ASGI API Gateway initialized successfully with security middleware, auth, and telemetry metrics.")
