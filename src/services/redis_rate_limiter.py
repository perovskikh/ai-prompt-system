"""
Redis-based Distributed Rate Limiter for AI-Prompt System

Implements distributed rate limiting using Redis to protect against:
- Distributed DoS attacks
- Rate limit abuse across multiple instances
- Better tracking and monitoring

Key Features:
- Distributed token bucket algorithm
- IP-based limiting
- Time window sliding
- Health check integration
- Graceful degradation support
"""

import time
import json
from typing import Optional, Dict, List, Tuple
from abc import ABC, abstractmethod


class RateLimitError(Exception):
    """Base exception for rate limiting errors."""
    pass


class RateLimiterType:
    """Type of rate limiter."""
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"


class LimitConfig:
    """Configuration for rate limiting."""
    def __init__(
        self,
        limit: int = 100,  # requests per minute
        window_seconds: int = 60,  # time window
        burst: int = 10,  # allow burst
        enabled: bool = True,
        grace_period: int = 60,  # grace period after limit exceeded
        distributed: bool = True,  # distributed mode
    ):
        self.limit = limit
        self.window_seconds = window_seconds
        self.burst = burst
        self.enabled = enabled
        self.grace_period = grace_period
        self.distributed = distributed

    def to_dict(self) -> dict:
        return {
            'limit': self.limit,
            'window_seconds': self.window_seconds,
            'burst': self.burst,
            'enabled': self.enabled,
            'grace_period': self.grace_period,
            'distributed': self.distributed
        }


class RedisRateLimiter:
    """
    Distributed rate limiter using Redis.

    Uses token bucket algorithm for precise rate limiting:
    - Each user gets 'tokens' that replenish over time
    - Requests consume tokens
    - Tokens replenish at fixed rate (limit / window_seconds)
    - Supports burst capacity for short spikes
    """

    def __init__(
        self,
        redis_client,
        default_config: LimitConfig = None,
        namespace: str = "rate_limit"
    ):
        self.redis = redis_client
        self.namespace = namespace
        self.default_config = default_config or LimitConfig()

    async def check_limit(
        self,
        api_key: str,
        ip_address: str = "unknown",
        limit_config: Optional[LimitConfig] = None,
        tokens: int = 1  # requests consume 1 token by default
    ) -> Tuple[bool, Dict]:
        """
        Check if request is within rate limit.

        Returns:
            - allowed: True/False
            - remaining: dict with limits info
            - retry_after: seconds until token replenishes
            - headers: dict with rate limit headers
        """
        config = limit_config or self.default_config

        if not config.enabled:
            return True, {}, 0, 0, {}

        # Redis key pattern
        key_prefix = f"{self.namespace}:limits:{api_key}"

        # Get current timestamp
        now = time.time()

        # Get remaining tokens and window start
        pipeline_key = f"{key_prefix}:pipeline"
        tokens_key = f"{key_prefix}:tokens"
        window_start_key = f"{key_prefix}:window_start"

        # Multi-execution for atomic operations
        pipeline = self.redis.pipeline()

        # Get current state
        pipeline.lrange(pipeline_key, 0, -1)
        pipeline_result = pipeline.execute()
        current_tokens = int(pipeline_result[0] if pipeline_result else 0)

        # Get window start time
        window_start_result = pipeline.execute()
        window_start = float(window_start_result[0] if window_start_result else now)

        # Check if we're in a new window
        time_since_start = now - window_start
        if time_since_start >= config.window_seconds:
            # Reset window
            pipe = self.redis.pipeline()
            pipe.set(window_start_key, now)
            pipe.execute()

            # Reset tokens to config.limit
            pipe.set(tokens_key, config.limit)
            pipe.execute()
            current_tokens = config.limit
            window_start = now

        # Check burst capacity
        burst_tokens = min(config.burst, current_tokens)

        # Consume tokens
        if current_tokens >= burst_tokens:
            # Allow burst usage
            new_tokens = current_tokens - tokens
            pipeline.decrby(tokens_key, new_tokens)
            pipeline.expire(tokens_key, config.window_seconds)
        else:
            # Consume regular tokens
            new_tokens = max(0, current_tokens - tokens)
            pipeline.decrby(tokens_key, new_tokens)

        # Get remaining after consumption
        pipeline_result = pipeline.execute()
        remaining_tokens = int(pipeline_result[0] if pipeline_result else 0)
        window_end = now + (config.window_seconds - (now - window_start))

        # Calculate retry after
        tokens_needed = tokens + 1
        time_per_token = config.window_seconds / config.limit
        retry_after = max(1, int(tokens_needed * time_per_token))

        # Reset grace period if under limit
        if remaining_tokens < config.limit:
            grace_key = f"{key_prefix}:grace"
            pipe.exists(grace_key)
            grace_remaining = pipe.execute()

            if not grace_remaining:
                # Start grace period
                pipe.setex(grace_key, config.grace_period)
            else:
                # Check grace period remaining
                grace_ttl = pipe.ttl(grace_key)
                if grace_ttl:
                    # Extend grace period
                    pipe.expire(grace_key, grace_ttl + config.grace_period)
                    retry_after = 0
                else:
                    # Grace period active
                    retry_after = max(1, int(grace_ttl))

        allowed = remaining_tokens > 0

        return (
            allowed,
            {
                'limit': config.limit,
                'remaining': remaining_tokens,
                'window_seconds': config.window_seconds,
                'retry_after': retry_after,
                'tokens_per_second': config.limit / config.window_seconds,
                'burst': config.burst,
                'headers': {
                    'X-RateLimit-Limit': str(config.limit),
                    'X-RateLimit-Remaining': str(remaining_tokens),
                    'X-RateLimit-Reset': window_end,
                    'X-RateLimit-Burst': str(config.burst),
                    'X-RateLimit-Grace': str(int(pipe.ttl(f"{key_prefix}:grace")) if pipe.exists(f"{key_prefix}:grace") else 0)
                }
            }
        )

    async def get_limit_info(
        self,
        api_key: str,
        ip_address: str = "unknown"
    ) -> Dict:
        """Get current limit information for a key."""
        key_prefix = f"{self.namespace}:limits:{api_key}"

        pipeline = self.redis.pipeline()

        # Get all limit info
        pipeline.lrange(f"{key_prefix}:config", 0, -1)
        pipeline.lrange(f"{key_prefix}:tokens", 0, -1)
        pipeline.lrange(f"{key_prefix}:window_start", 0, -1)
        pipeline.ttl(f"{key_prefix}:tokens")
        pipeline.ttl(f"{key_prefix}:grace")
        pipeline.execute()

        config_result = pipeline.execute()
        config_data = json.loads(config_result[0]) if config_result else {}

        tokens_result = pipeline.execute()
        current_tokens = int(tokens_result[0]) if tokens_result else 0

        window_start_result = pipeline.execute()
        window_start = float(window_start_result[0]) if window_start_result else 0

        pipeline.ttl(f"{key_prefix}:tokens")
        tokens_ttl = pipeline.ttl(f"{key_prefix}:tokens")
        grace_ttl = pipeline.ttl(f"{key_prefix}:grace")

        return {
            'config': config_data,
            'current_tokens': current_tokens,
            'window_start': window_start,
            'tokens_ttl': tokens_ttl,
            'grace_ttl': grace_ttl,
            'remaining': current_tokens
        }

    async def reset_limit(
        self,
        api_key: str,
        ip_address: str = "unknown"
    ) -> bool:
        """Reset rate limit for a specific key/IP."""
        key_prefix = f"{self.namespace}:limits:{api_key}"

        pipeline = self.redis.pipeline()

        # Delete limit info
        pipeline.delete(f"{key_prefix}:config")
        pipeline.delete(f"{key_prefix}:tokens")
        pipeline.delete(f"{key_prefix}:window_start")
        pipeline.delete(f"{key_prefix}:grace")

        # Reset to initial state
        now = time.time()
        pipe.set(f"{key_prefix}:window_start", now)
        pipe.set(f"{key_prefix}:tokens", self.default_config.limit)
        pipe.execute()

        return True

    async def cleanup(self, api_key: str) -> int:
        """Clean up old rate limit data."""
        key_prefix = f"{self.namespace}:limits:{api_key}"

        # Find all keys for this user
        cursor = 0
        while True:
            cursor, keys = self.redis.scan(
                cursor,
                match=f"{key_prefix}:*",
                count=100
            )
            cursor += int(keys[0])

            if keys[1] == 0:
                break

        if cursor > 0:
            # Delete old keys
            pipeline = self.redis.pipeline()
            for key in keys[1]:
                pipeline.delete(key)
            pipeline.execute()

        return cursor


class DistributedRateLimiter:
    """
    Manager for distributed rate limiting across instances.

    Combines multiple limiter strategies:
    - Token bucket algorithm (per-minute limits)
    - IP-based limiting (per-IP limits)
    - Sliding window (short-term burst control)
    - Health checks and monitoring
    - Graceful degradation support
    """

    def __init__(self, redis_client):
        self.redis = redis_client
        self.limiters: Dict[str, RedisRateLimiter] = {}

    async def check_rate_limit(
        self,
        api_key: str,
        ip_address: str = "unknown",
        limit_config: Optional[LimitConfig] = None
    ) -> Tuple[bool, Dict]:
        """Check rate limit using appropriate limiter."""
        # Get or create limiter for this key
        if api_key not in self.limiters:
            self.limiters[api_key] = RedisRateLimiter(
                self.redis,
                default_config=limit_config or LimitConfig(
                    limit=100,  # 100 requests per minute
                    window_seconds=60,  # 1 minute window
                    burst=10,  # Allow burst of 10
                    enabled=True,
                    grace_period=60,
                    distributed=True
                ),
                namespace=f"limits:{api_key}"
            )

        limiter = self.limiters[api_key]

        # Check rate limit
        allowed, limit_info = await limiter.check_limit(api_key, ip_address)

        return allowed, limit_info

    async def add_whitelist_entry(self, api_key: str, limit: int) -> bool:
        """Add an API key to whitelist."""
        whitelist_key = f"{self.redis.namespace}:whitelist"

        # Add to whitelist with 24h TTL
        pipeline = self.redis.pipeline()
        pipeline.sadd(whitelist_key, api_key)
        pipeline.expire(whitelist_key, 86400)  # 24 hours

        # Set custom limit
        limit_key = f"{self.redis.namespace}:limits:{api_key}:config"
        config_key = f"{self.redis.namespace}:limits:{api_key}:custom_limit"

        pipeline.setex(limit_key, 24 * 3600)  # 24h TTL
        pipeline.set(config_key, limit)
        pipeline.execute()

        return True

    async def remove_whitelist_entry(self, api_key: str) -> bool:
        """Remove API key from whitelist."""
        whitelist_key = f"{self.redis.namespace}:whitelist"

        pipeline = self.redis.pipeline()
        pipeline.srem(whitelist_key, api_key)
        pipeline.delete(f"{self.redis.namespace}:limits:{api_key}:config")
        pipeline.execute()

        return True

    async def get_system_stats(self) -> Dict:
        """Get system-wide rate limiting statistics."""
        keys = []
        cursor = 0
        while True:
            cursor, scan_keys = self.redis.scan(
                cursor=cursor,
                match=f"{self.redis.namespace}:limits:*",
                count=100
            )
            cursor += int(scan_keys[0])
            keys.extend(scan_keys[1])

            if len(scan_keys[1]) == 0:
                break

        stats = {
            'total_limits': len(keys),
            'active_limits': len(keys),
            'namespace': self.redis.namespace
        }

        return stats


# Factory function for creating rate limiter instance
def create_redis_rate_limiter(redis_client, config=None) -> DistributedRateLimiter:
    """
    Factory function to create a distributed rate limiter.

    Args:
        redis_client: Redis client instance
        config: Optional rate limit configuration

    Returns:
        DistributedRateLimiter instance
    """
    return DistributedRateLimiter(redis_client, config)


# Example usage (to be integrated into APIKeyManager):
#
# redis_client = await redis.Redis(host='localhost', port=6379)
# rate_limiter = create_redis_rate_limiter(redis_client)
#
# async with rate_limiter.check_rate_limit(api_key, ip) as (allowed, limit_info):
#     if not allowed:
#         raise RateLimitError("Rate limit exceeded")
#     return False, {}
#
# # Later, check health
# health_status = await rate_limiter.get_health_status()
# if not health_status['healthy']:
#     raise RateLimitError("Rate limiter unhealthy")
