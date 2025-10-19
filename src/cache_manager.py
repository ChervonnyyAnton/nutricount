"""
Cache Manager Module
Handles Redis caching and performance optimization
"""

import json
import logging
import time
from typing import Any, Optional
from functools import wraps

try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

logger = logging.getLogger(__name__)


class CacheManager:
    """Redis-based cache manager with fallback to in-memory cache"""

    def __init__(
        self, redis_url: str = "redis://localhost:6379/0", fallback_cache_size: int = 1000
    ):
        self.redis_client = None
        self.fallback_cache = {}
        self.fallback_cache_size = fallback_cache_size
        self.use_redis = False

        if REDIS_AVAILABLE:
            try:
                self.redis_client = redis.from_url(redis_url, decode_responses=True)
                # Test connection
                self.redis_client.ping()
                self.use_redis = True
                logger.info("Redis cache initialized successfully")
            except Exception as e:
                logger.warning(f"Redis not available, using fallback cache: {e}")
                self.use_redis = False
        else:
            logger.warning("Redis not installed, using fallback cache")

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            if self.use_redis and self.redis_client:
                value = self.redis_client.get(key)
                if value:
                    return json.loads(value)
            else:
                # Fallback to in-memory cache
                if key in self.fallback_cache:
                    cached_item = self.fallback_cache[key]
                    if cached_item["expires"] > time.time():
                        return cached_item["value"]
                    else:
                        del self.fallback_cache[key]
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")

        return None

    def set(self, key: str, value: Any, expire: int = 300) -> bool:
        """Set value in cache with expiration"""
        try:
            if self.use_redis and self.redis_client:
                return self.redis_client.setex(key, expire, json.dumps(value))
            else:
                # Fallback to in-memory cache
                if len(self.fallback_cache) >= self.fallback_cache_size:
                    # Remove oldest item
                    oldest_key = min(
                        self.fallback_cache.keys(), key=lambda k: self.fallback_cache[k]["expires"]
                    )
                    del self.fallback_cache[oldest_key]

                self.fallback_cache[key] = {"value": value, "expires": time.time() + expire}
                return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            if self.use_redis and self.redis_client:
                return bool(self.redis_client.delete(key))
            else:
                if key in self.fallback_cache:
                    del self.fallback_cache[key]
                    return True
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")

        return False

    def clear(self) -> bool:
        """Clear all cache"""
        try:
            if self.use_redis and self.redis_client:
                return self.redis_client.flushdb()
            else:
                self.fallback_cache.clear()
                return True
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return False

    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            if self.use_redis and self.redis_client:
                return bool(self.redis_client.exists(key))
            else:
                if key in self.fallback_cache:
                    cached_item = self.fallback_cache[key]
                    if cached_item["expires"] > time.time():
                        return True
                    else:
                        del self.fallback_cache[key]
        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {e}")

        return False

    def get_stats(self) -> dict:
        """Get cache statistics"""
        try:
            if self.use_redis and self.redis_client:
                info = self.redis_client.info()
                return {
                    "type": "redis",
                    "connected_clients": info.get("connected_clients", 0),
                    "used_memory": info.get("used_memory_human", "0B"),
                    "keyspace_hits": info.get("keyspace_hits", 0),
                    "keyspace_misses": info.get("keyspace_misses", 0),
                    "hit_rate": self._calculate_hit_rate(
                        info.get("keyspace_hits", 0), info.get("keyspace_misses", 0)
                    ),
                }
            else:
                return {
                    "type": "fallback",
                    "cache_size": len(self.fallback_cache),
                    "max_size": self.fallback_cache_size,
                    "usage_percentage": (len(self.fallback_cache) / self.fallback_cache_size) * 100,
                }
        except Exception as e:
            logger.error(f"Cache stats error: {e}")
            return {"type": "error", "error": str(e)}

    def delete_pattern(self, pattern: str) -> int:
        """Delete keys matching pattern"""
        try:
            if self.use_redis and self.redis_client:
                keys = self.redis_client.keys(pattern)
                if keys:
                    return self.redis_client.delete(*keys)
                return 0
            else:
                # For fallback cache, we can't pattern match easily
                # Return 0 as we can't implement pattern matching efficiently
                return 0
        except Exception as e:
            logger.error(f"Cache delete pattern error for pattern {pattern}: {e}")
            return 0

    def _calculate_hit_rate(self, hits: int, misses: int) -> float:
        """Calculate cache hit rate percentage"""
        total = hits + misses
        if total == 0:
            return 0.0
        return (hits / total) * 100

    def health_check(self) -> bool:
        """Check if cache is healthy"""
        try:
            if self.use_redis and self.redis_client:
                return self.redis_client.ping()
            else:
                return True  # Fallback cache is always "healthy"
        except Exception as e:
            logger.error(f"Cache health check error: {e}")
            return False


# Global cache instance
cache_manager = CacheManager()


def cached(timeout: int = 300, key_prefix: str = ""):
    """Decorator for caching function results"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = (
                f"{key_prefix}:{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            )

            # Try to get from cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_result

            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, timeout)
            logger.debug(f"Cached result for {cache_key}")

            return result

        return wrapper

    return decorator


def cache_invalidate(pattern: str = None):
    """Decorator to invalidate cache entries matching pattern"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Execute function first
            result = func(*args, **kwargs)

            # Then invalidate cache
            try:
                if cache_manager.use_redis and cache_manager.redis_client:
                    if pattern:
                        keys = cache_manager.redis_client.keys(pattern)
                        if keys:
                            cache_manager.redis_client.delete(*keys)
                    else:
                        cache_manager.redis_client.flushdb()
                else:
                    # For fallback cache, we can't pattern match easily
                    # So we'll clear all if no pattern specified
                    if not pattern:
                        cache_manager.fallback_cache.clear()
            except Exception as e:
                logger.error(f"Cache invalidation error: {e}")

            return result

        return wrapper

    return decorator


class CacheMetrics:
    """Cache performance metrics"""

    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.sets = 0
        self.deletes = 0

    def record_hit(self):
        self.hits += 1

    def record_miss(self):
        self.misses += 1

    def record_set(self):
        self.sets += 1

    def record_delete(self):
        self.deletes += 1

    def get_stats(self) -> dict:
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0

        return {
            "hits": self.hits,
            "misses": self.misses,
            "sets": self.sets,
            "deletes": self.deletes,
            "hit_rate": hit_rate,
            "total_requests": total_requests,
        }


# Global metrics instance
cache_metrics = CacheMetrics()
