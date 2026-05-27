import time
import re
from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
from typing import Dict, Tuple
from ai_engine.utils.logger import setup_logger

logger = setup_logger("security_protection")

class SecurityProtectionMiddleware(BaseHTTPMiddleware):
    """
    Enterprise-grade security gatekeeper enforcing IP rate limits (DDoS throttling),
    injecting secure HTTP headers, and sanitizing payloads.
    """
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        # Bounded IP client request timestamp store: {IP: [timestamps]}
        self.ip_request_history: Dict[str, list] = defaultdict(list)
        # HTML tag sanitization regex pattern
        self.html_sanitizer = re.compile(r'<[^>]*>')

    async def dispatch(self, request: Request, call_next) -> Response:
        client_ip = request.client.host if request.client else "unknown_ip"
        current_time = time.time()

        # 1. DDoS Rate Limiting Throttling Filter
        ip_history = self.ip_request_history[client_ip]
        # Prune request history older than 60 seconds
        self.ip_request_history[client_ip] = [t for t in ip_history if current_time - t < 60.0]
        
        if len(self.ip_request_history[client_ip]) >= self.requests_per_minute:
            logger.warning(f"DDoS rate limit trigger: Client IP {client_ip} throttled.")
            return Response(
                content="API rate limit exceeded. Connection throttled for DDoS protection.",
                status_code=status.HTTP_429_TOO_MANY_REQUESTS
            )

        # Register current request timestamp
        self.ip_request_history[client_ip].append(current_time)

        # 2. Input Sanitization (Sanitize Query Parameters to block basic XSS/Injection scripts)
        for key, value in request.query_params.items():
            if isinstance(value, str) and self.html_sanitizer.search(value):
                logger.warning(f"Malicious input injection blocked from IP {client_ip} on key {key}.")
                return Response(
                    content="Malicious payload signature detected. Request blocked.",
                    status_code=status.HTTP_400_BAD_REQUEST
                )

        # 3. Proceed to application logic
        response: Response = await call_next(request)

        # 4. Inject OWASP Standard Hardened Security Headers
        response.headers["X-Frame-Options"] = "DENY" # Blocks Clickjacking exploits
        response.headers["X-Content-Type-Options"] = "nosniff" # Blocks MIME-sniffing exploits
        response.headers["X-XSS-Protection"] = "1; mode=block" # Blocks XSS
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response
