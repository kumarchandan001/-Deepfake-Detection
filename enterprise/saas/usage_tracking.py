import time
import threading
from typing import Dict, Any, Optional
from ai_engine.utils.logger import setup_logger

logger = setup_logger("usage_tracking")

class UsageTracker:
    _instance: Optional["UsageTracker"] = None
    _lock = threading.Lock()
    
    # High-performance thread-safe memory fallback store
    _memory_counters: Dict[str, Dict[str, int]] = {}
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(UsageTracker, cls).__new__(cls, *args, **kwargs)
                    cls._instance._init_connections()
        return cls._instance

    def _init_connections(self):
        self.redis_client = None
        self.use_redis = False
        
        # Proactively check if redis is available inside environment
        try:
            import redis
            redis_host = "localhost"
            redis_port = 6379
            self.redis_client = redis.Redis(
                host=redis_host, 
                port=redis_port, 
                db=0, 
                socket_connect_timeout=1
            )
            # Ping to verify active connection
            self.redis_client.ping()
            self.use_redis = True
            logger.info("Redis atomic usage counters successfully connected.")
        except Exception:
            logger.warning("Redis is not running. Usage tracker falling back to thread-safe local memory counters.")

    def _get_redis_key(self, tenant_id: str, metric: str) -> str:
        # e.g. saas:usage:tenant_abc:daily_checks
        return f"saas:usage:{tenant_id}:{metric}"

    async def increment_usage(self, tenant_id: str, metric: str, amount: int = 1) -> int:
        """
        Atomically increments the target metric usage for tenant.
        """
        if self.use_redis:
            try:
                # Direct atomic redis increment operation
                key = self._get_redis_key(tenant_id, metric)
                new_val = self.redis_client.incrby(key, amount)
                return int(new_val)
            except Exception as e:
                logger.error(f"Redis usage increment error: {e}. Falling back to memory increment.")
        
        # Local Thread-safe Memory Fallback
        with self._lock:
            if tenant_id not in self._memory_counters:
                self._memory_counters[tenant_id] = {}
            current = self._memory_counters[tenant_id].get(metric, 0)
            new_val = current + amount
            self._memory_counters[tenant_id][metric] = new_val
            return new_val

    async def get_usage(self, tenant_id: str, metric: str) -> int:
        """
        Retrieves current usage count for metric.
        """
        if self.use_redis:
            try:
                key = self._get_redis_key(tenant_id, metric)
                val = self.redis_client.get(key)
                return int(val) if val else 0
            except Exception as e:
                logger.error(f"Redis usage fetch error: {e}. Falling back to memory lookup.")

        with self._lock:
            return self._memory_counters.get(tenant_id, {}).get(metric, 0)

    async def reset_usage(self, tenant_id: str, metric: str) -> None:
        """
        Resets target usage metric to 0.
        """
        if self.use_redis:
            try:
                key = self._get_redis_key(tenant_id, metric)
                self.redis_client.delete(key)
                return
            except Exception as e:
                logger.error(f"Redis usage reset error: {e}")

        with self._lock:
            if tenant_id in self._memory_counters and metric in self._memory_counters[tenant_id]:
                self._memory_counters[tenant_id][metric] = 0

    async def record_compute_footprint(self, tenant_id: str, inference_count: int, execution_time_sec: float):
        """
        Utility logging raw execution time metrics for billing rollups.
        """
        await self.increment_usage(tenant_id, "inference_count", inference_count)
        # Convert float seconds to integer milliseconds to prevent rounding inaccuracies in atomic counts
        execution_ms = int(execution_time_sec * 1000)
        await self.increment_usage(tenant_id, "compute_time_ms", execution_ms)
        logger.info(f"Recorded compute footprint for Tenant: {tenant_id}: Inferences={inference_count}, Duration={execution_time_sec:.4f}s")
