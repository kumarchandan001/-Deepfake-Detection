"""
Distributed Rate Limiter — AI Deepfake Detection Platform.

Production-grade sliding window + token bucket hybrid rate limiter with:
- Redis-backed distributed state (atomic Lua scripts)
- Thread-safe local fallback for development/testing
- Per-tenant, per-endpoint, and global rate limiting
- Burst allowance with configurable refill rates
- Rate limit headers (X-RateLimit-*) for API responses
"""

import time
import threading
import hashlib
from typing import Dict, Any, Optional, Tuple
from collections import defaultdict
from dataclasses import dataclass, field
from ai_engine.utils.logger import setup_logger

logger = setup_logger("rate_limiter")


# ─── Rate Limit Configuration ───────────────────────────────────────────────

@dataclass
class RateLimitPolicy:
    """Rate limit configuration for a specific scope."""
    name: str
    requests_per_second: float = 10.0
    requests_per_minute: float = 120.0
    burst_size: int = 20  # max instantaneous burst
    window_seconds: int = 60
    penalty_seconds: int = 60  # additional block time after limit hit


@dataclass
class RateLimitResult:
    """Result of a rate limit check."""
    allowed: bool
    remaining: int
    limit: int
    reset_at: float  # unix timestamp
    retry_after: Optional[int] = None  # seconds until next allowed request
    policy_name: str = ""

    def to_headers(self) -> Dict[str, str]:
        """Generate standard rate limit HTTP headers."""
        headers = {
            "X-RateLimit-Limit": str(self.limit),
            "X-RateLimit-Remaining": str(max(0, self.remaining)),
            "X-RateLimit-Reset": str(int(self.reset_at)),
            "X-RateLimit-Policy": self.policy_name,
        }
        if not self.allowed and self.retry_after:
            headers["Retry-After"] = str(self.retry_after)
        return headers


# ─── Sliding Window Counter (Local) ─────────────────────────────────────────

class LocalSlidingWindowCounter:
    """Thread-safe sliding window rate limiter for local/dev environments."""

    def __init__(self):
        self._windows: Dict[str, list] = defaultdict(list)
        self._lock = threading.Lock()
        self._penalties: Dict[str, float] = {}

    def check(self, key: str, policy: RateLimitPolicy) -> RateLimitResult:
        """
        Check if a request is allowed under the rate limit.

        Uses a sliding window over the last `window_seconds` to count requests.
        """
        now = time.time()
        window_start = now - policy.window_seconds

        with self._lock:
            # Check penalty
            if key in self._penalties:
                penalty_end = self._penalties[key]
                if now < penalty_end:
                    return RateLimitResult(
                        allowed=False,
                        remaining=0,
                        limit=int(policy.requests_per_minute),
                        reset_at=penalty_end,
                        retry_after=int(penalty_end - now) + 1,
                        policy_name=policy.name,
                    )
                else:
                    del self._penalties[key]

            # Clean expired entries
            self._windows[key] = [t for t in self._windows[key] if t > window_start]

            current_count = len(self._windows[key])
            max_requests = int(policy.requests_per_minute)

            if current_count >= max_requests:
                # Apply penalty
                penalty_end = now + policy.penalty_seconds
                self._penalties[key] = penalty_end

                logger.warning(f"Rate limit exceeded for {key}: {current_count}/{max_requests}")
                return RateLimitResult(
                    allowed=False,
                    remaining=0,
                    limit=max_requests,
                    reset_at=penalty_end,
                    retry_after=policy.penalty_seconds,
                    policy_name=policy.name,
                )

            # Check burst (requests in last 1 second)
            one_sec_ago = now - 1.0
            burst_count = sum(1 for t in self._windows[key] if t > one_sec_ago)
            if burst_count >= policy.burst_size:
                return RateLimitResult(
                    allowed=False,
                    remaining=max_requests - current_count,
                    limit=max_requests,
                    reset_at=now + 1.0,
                    retry_after=1,
                    policy_name=policy.name,
                )

            # Allow request
            self._windows[key].append(now)
            remaining = max_requests - current_count - 1

            return RateLimitResult(
                allowed=True,
                remaining=remaining,
                limit=max_requests,
                reset_at=now + policy.window_seconds,
                policy_name=policy.name,
            )

    def reset(self, key: str):
        """Reset rate limit state for a key."""
        with self._lock:
            self._windows.pop(key, None)
            self._penalties.pop(key, None)

    def get_stats(self) -> Dict[str, Any]:
        """Return rate limiter statistics."""
        with self._lock:
            return {
                "active_keys": len(self._windows),
                "active_penalties": len(self._penalties),
                "total_tracked_requests": sum(len(v) for v in self._windows.values()),
            }


# ─── Redis-Backed Rate Limiter ───────────────────────────────────────────────

class RedisRateLimiter:
    """
    Redis-backed distributed rate limiter using atomic Lua scripts.
    Falls back to local counter if Redis is unavailable.
    """

    # Lua script for atomic sliding window check + increment
    SLIDING_WINDOW_LUA = """
    local key = KEYS[1]
    local window = tonumber(ARGV[1])
    local limit = tonumber(ARGV[2])
    local now = tonumber(ARGV[3])
    local window_start = now - window

    -- Remove expired entries
    redis.call('ZREMRANGEBYSCORE', key, '-inf', window_start)

    -- Count current entries
    local count = redis.call('ZCARD', key)

    if count >= limit then
        return {0, count, limit}
    end

    -- Add new entry
    redis.call('ZADD', key, now, now .. ':' .. math.random(1000000))
    redis.call('EXPIRE', key, window + 1)

    return {1, count + 1, limit}
    """

    def __init__(self):
        self._redis = None
        self._lua_sha = None
        self._local_fallback = LocalSlidingWindowCounter()
        self._use_redis = False
        self._connect_redis()

    def _connect_redis(self):
        """Attempt to connect to Redis."""
        try:
            import redis
            self._redis = redis.Redis(host="localhost", port=6379, socket_timeout=2)
            self._redis.ping()
            # Register Lua script
            self._lua_sha = self._redis.script_load(self.SLIDING_WINDOW_LUA)
            self._use_redis = True
            logger.info("Rate limiter connected to Redis (distributed mode)")
        except Exception:
            self._use_redis = False
            logger.warning("Redis unavailable for rate limiter - using local fallback")

    def check(self, key: str, policy: RateLimitPolicy) -> RateLimitResult:
        """
        Check rate limit, using Redis if available, local fallback otherwise.
        """
        if self._use_redis:
            return self._check_redis(key, policy)
        return self._local_fallback.check(key, policy)

    def _check_redis(self, key: str, policy: RateLimitPolicy) -> RateLimitResult:
        """Execute rate limit check via Redis Lua script."""
        try:
            now = time.time()
            redis_key = f"ratelimit:{key}"
            max_requests = int(policy.requests_per_minute)

            result = self._redis.evalsha(
                self._lua_sha,
                1,
                redis_key,
                str(policy.window_seconds),
                str(max_requests),
                str(now),
            )

            allowed = bool(result[0])
            current_count = int(result[1])
            limit = int(result[2])

            if not allowed:
                return RateLimitResult(
                    allowed=False,
                    remaining=0,
                    limit=limit,
                    reset_at=now + policy.window_seconds,
                    retry_after=policy.penalty_seconds,
                    policy_name=policy.name,
                )

            return RateLimitResult(
                allowed=True,
                remaining=limit - current_count,
                limit=limit,
                reset_at=now + policy.window_seconds,
                policy_name=policy.name,
            )

        except Exception as e:
            logger.error(f"Redis rate limit error: {e}, falling back to local")
            self._use_redis = False
            return self._local_fallback.check(key, policy)

    def reset(self, key: str):
        """Reset rate limit state."""
        if self._use_redis:
            try:
                self._redis.delete(f"ratelimit:{key}")
            except Exception:
                pass
        self._local_fallback.reset(key)

    def get_stats(self) -> Dict[str, Any]:
        stats = self._local_fallback.get_stats()
        stats["backend"] = "redis" if self._use_redis else "local"
        return stats


# ─── Rate Limit Manager ─────────────────────────────────────────────────────

class RateLimitManager:
    """
    High-level rate limit manager supporting per-tenant, per-endpoint,
    and global rate limiting with configurable policies.
    """
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._limiter = RedisRateLimiter()
            cls._instance._policies: Dict[str, RateLimitPolicy] = {}
            cls._instance._seed_default_policies()
        return cls._instance

    def _seed_default_policies(self):
        """Install default rate limit policies."""
        self._policies = {
            "global": RateLimitPolicy(
                name="global",
                requests_per_second=100.0,
                requests_per_minute=5000.0,
                burst_size=200,
                window_seconds=60,
                penalty_seconds=30,
            ),
            "free_tier": RateLimitPolicy(
                name="free_tier",
                requests_per_second=2.0,
                requests_per_minute=10.0,
                burst_size=5,
                window_seconds=60,
                penalty_seconds=60,
            ),
            "pro_tier": RateLimitPolicy(
                name="pro_tier",
                requests_per_second=20.0,
                requests_per_minute=500.0,
                burst_size=50,
                window_seconds=60,
                penalty_seconds=30,
            ),
            "enterprise_tier": RateLimitPolicy(
                name="enterprise_tier",
                requests_per_second=100.0,
                requests_per_minute=5000.0,
                burst_size=200,
                window_seconds=60,
                penalty_seconds=10,
            ),
            "detection_endpoint": RateLimitPolicy(
                name="detection_endpoint",
                requests_per_second=5.0,
                requests_per_minute=100.0,
                burst_size=10,
                window_seconds=60,
                penalty_seconds=30,
            ),
            "graphql_endpoint": RateLimitPolicy(
                name="graphql_endpoint",
                requests_per_second=30.0,
                requests_per_minute=1000.0,
                burst_size=50,
                window_seconds=60,
                penalty_seconds=15,
            ),
            "webhook_endpoint": RateLimitPolicy(
                name="webhook_endpoint",
                requests_per_second=50.0,
                requests_per_minute=2000.0,
                burst_size=100,
                window_seconds=60,
                penalty_seconds=5,
            ),
        }
        logger.info(f"Seeded {len(self._policies)} default rate limit policies")

    def get_policy(self, name: str) -> Optional[RateLimitPolicy]:
        return self._policies.get(name)

    def register_policy(self, policy: RateLimitPolicy):
        self._policies[policy.name] = policy
        logger.info(f"Registered rate limit policy: {policy.name}")

    def _build_key(self, tenant_id: str, endpoint: str = "",
                    ip_address: str = "") -> str:
        """Build a composite rate limit key."""
        parts = [p for p in [tenant_id, endpoint, ip_address] if p]
        raw = ":".join(parts)
        return hashlib.md5(raw.encode()).hexdigest()

    def check_tenant_limit(self, tenant_id: str, plan_key: str) -> RateLimitResult:
        """Check rate limit for a tenant based on their plan."""
        policy_name = f"{plan_key}_tier"
        policy = self._policies.get(policy_name, self._policies["free_tier"])
        key = self._build_key(tenant_id)
        return self._limiter.check(key, policy)

    def check_endpoint_limit(self, tenant_id: str,
                              endpoint: str) -> RateLimitResult:
        """Check rate limit for a specific endpoint."""
        policy = self._policies.get(f"{endpoint}_endpoint",
                                     self._policies.get("global"))
        if not policy:
            policy = self._policies["global"]
        key = self._build_key(tenant_id, endpoint)
        return self._limiter.check(key, policy)

    def check_global_limit(self, ip_address: str) -> RateLimitResult:
        """Check global rate limit by IP address."""
        policy = self._policies["global"]
        key = self._build_key("", "", ip_address)
        return self._limiter.check(key, policy)

    def check_composite(self, tenant_id: str, plan_key: str,
                         endpoint: str, ip_address: str) -> Tuple[RateLimitResult, str]:
        """
        Check all applicable rate limits and return the most restrictive result.

        Returns:
            Tuple of (RateLimitResult, limiting_policy_name)
        """
        checks = [
            ("tenant", self.check_tenant_limit(tenant_id, plan_key)),
            ("endpoint", self.check_endpoint_limit(tenant_id, endpoint)),
            ("global", self.check_global_limit(ip_address)),
        ]

        # Return the first denied result, or the most restrictive allowed result
        for name, result in checks:
            if not result.allowed:
                return result, name

        # All allowed - return the one with fewest remaining
        most_restrictive = min(checks, key=lambda x: x[1].remaining)
        return most_restrictive[1], most_restrictive[0]

    def reset_tenant(self, tenant_id: str):
        """Reset all rate limits for a tenant."""
        key = self._build_key(tenant_id)
        self._limiter.reset(key)
        logger.info(f"Reset rate limits for tenant: {tenant_id}")

    def get_stats(self) -> Dict[str, Any]:
        """Return rate limiter statistics."""
        return {
            "policies": {k: v.requests_per_minute for k, v in self._policies.items()},
            "limiter": self._limiter.get_stats(),
        }
