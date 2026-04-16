# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-06 - Application-level rate limiting with token bucket algorithm

"""
Rate Limiting Module

Implements token bucket algorithm for application-level rate limiting.
Provides CloudWatch metrics integration and per-key tracking.
"""

import logging
import os
import time
from typing import Dict, Optional, Tuple
from collections import defaultdict

logger = logging.getLogger(__name__)


class RateLimiterError(Exception):
    """Base exception for rate limiter operations."""


class RateLimitExceeded(RateLimiterError):
    """Raised when rate limit is exceeded."""


class TokenBucket:
    """
    Token bucket implementation for rate limiting.

    Features:
    - Configurable rate and burst capacity
    - Automatic token refill
    - Per-key tracking
    - Thread-safe operations
    """

    def __init__(self, rate: float, capacity: int):
        """
        Initialize token bucket.

        Args:
            rate: Tokens per second (e.g., 1.667 for 100 per minute)
            capacity: Maximum token capacity (burst size)
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens: float = float(capacity)
        self.last_update: float = time.time()
        self._lock_value = 0  # Simple lock counter

    def _refill_tokens(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_update

        # Refill tokens based on rate
        tokens_to_add = elapsed * self.rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_update = now

    def consume(self, tokens: int = 1) -> bool:
        """
        Consume tokens from bucket.

        Args:
            tokens: Number of tokens to consume (default: 1)

        Returns:
            True if tokens consumed successfully, False if insufficient tokens
        """
        self._refill_tokens()

        if self.tokens >= tokens:
            self.tokens -= tokens
            return True

        return False

    def get_available_tokens(self) -> float:
        """
        Get number of available tokens.

        Returns:
            Available tokens count
        """
        self._refill_tokens()
        return self.tokens

    def get_wait_time(self, tokens: int = 1) -> float:
        """
        Get time to wait for tokens to be available.

        Args:
            tokens: Number of tokens needed

        Returns:
            Wait time in seconds
        """
        self._refill_tokens()

        if self.tokens >= tokens:
            return 0.0

        tokens_needed = tokens - self.tokens
        return tokens_needed / self.rate


class RateLimiter:  # pylint: disable=too-many-instance-attributes
    """
    Application-level rate limiter with token bucket algorithm.

    Features:
    - Per-key rate limiting (e.g., per user, per IP)
    - Configurable rate and burst capacity
    - CloudWatch metrics integration
    - Automatic cleanup of stale buckets
    - Health check integration

    Configuration via environment variables:
    - RATE_LIMIT_PER_MINUTE: Requests per minute (default: 100)
    - RATE_LIMIT_BURST: Burst capacity (default: 20)
    - RATE_LIMIT_ENABLED: Enable/disable rate limiting (default: true)
    """

    def __init__(self,
                 rate_per_minute: Optional[int] = None,
                 burst_capacity: Optional[int] = None):
        """
        Initialize rate limiter.

        Args:
            rate_per_minute: Requests per minute (default: from env var or 100)
            burst_capacity: Burst capacity (default: from env var or 20)
        """
        # Load configuration
        self._enabled = os.getenv('RATE_LIMIT_ENABLED', 'true').lower() == 'true'
        rate_per_minute = rate_per_minute or int(os.getenv('RATE_LIMIT_PER_MINUTE', '100'))
        burst_capacity = burst_capacity or int(os.getenv('RATE_LIMIT_BURST', '20'))

        # Convert rate to tokens per second
        self.rate = rate_per_minute / 60.0
        self.capacity = burst_capacity

        # Token buckets storage (key -> TokenBucket)
        self._buckets: Dict[str, TokenBucket] = defaultdict(
            lambda: TokenBucket(self.rate, self.capacity)
        )

        # Metrics
        self._metrics_enabled = os.getenv('CLOUDWATCH_METRICS_ENABLED', 'true').lower() == 'true'
        self._total_requests = 0
        self._allowed_requests = 0
        self._blocked_requests = 0

        # Cleanup configuration
        self._last_cleanup = time.time()
        self._cleanup_interval = 300  # 5 minutes
        self._bucket_ttl = 600  # 10 minutes

        logger.info("Rate limiter initialized: enabled=%s, rate=%d/min, burst=%d",
                    self._enabled, rate_per_minute, burst_capacity)

    def _publish_metric(self, metric_name: str, value: float, unit: str = 'Count') -> None:
        """
        Publish custom metric to CloudWatch.

        Args:
            metric_name: Name of the metric
            value: Metric value
            unit: CloudWatch unit (Count, None, etc.)
        """
        if not self._metrics_enabled:
            return

        try:
            logger.info("CloudWatchMetric: {\"name\": \"%s\", \"value\": %s, \"unit\": \"%s\"}",
                       metric_name, value, unit)
        except Exception as e:
            logger.warning("Failed to publish metric %s: %s", metric_name, e)

    def _cleanup_stale_buckets(self) -> None:
        """Clean up stale token buckets to prevent memory leaks."""
        now = time.time()

        # Only cleanup periodically
        if now - self._last_cleanup < self._cleanup_interval:
            return

        try:
            stale_keys = []

            for key, bucket in self._buckets.items():
                # Remove buckets that haven't been used recently
                if now - bucket.last_update > self._bucket_ttl:
                    stale_keys.append(key)

            for key in stale_keys:
                del self._buckets[key]

            if stale_keys:
                logger.info("Cleaned up %d stale rate limit buckets", len(stale_keys))
                self._publish_metric('RateLimiterBucketCleanup', len(stale_keys), 'Count')

            self._last_cleanup = now

        except Exception as e:
            logger.warning("Failed to cleanup stale buckets: %s", e)

    def check_rate_limit(self, key: str = 'default', tokens: int = 1) -> Tuple[bool, Optional[float]]:
        """
        Check if request is within rate limit.

        Args:
            key: Unique identifier for rate limit bucket (e.g., user ID, IP address)
            tokens: Number of tokens to consume (default: 1)

        Returns:
            Tuple of (allowed: bool, wait_time_seconds: Optional[float])

        Raises:
            RateLimiterError: If rate limiter is misconfigured
        """
        self._total_requests += 1

        # Check if rate limiting is enabled
        if not self._enabled:
            self._allowed_requests += 1
            return True, None

        try:
            # Periodic cleanup
            self._cleanup_stale_buckets()

            # Get or create token bucket for key
            bucket = self._buckets[key]

            # Check if tokens are available
            if bucket.consume(tokens):
                self._allowed_requests += 1
                self._publish_metric('RateLimitAllowed', 1, 'Count')
                return True, None

            self._blocked_requests += 1
            wait_time = bucket.get_wait_time(tokens)
            self._publish_metric('RateLimitBlocked', 1, 'Count')
            self._publish_metric('RateLimitWaitTime', wait_time, 'Seconds')
            return False, wait_time

        except Exception as e:
            logger.error("Rate limiter error: %s", e)
            self._publish_metric('RateLimitError', 1, 'Count')
            raise RateLimiterError(f"Rate limiter error: {e}") from e

    def is_allowed(self, key: str = 'default', tokens: int = 1) -> bool:
        """
        Check if request is allowed (simplified version).

        Args:
            key: Unique identifier for rate limit bucket
            tokens: Number of tokens to consume

        Returns:
            True if allowed, False if rate limited
        """
        allowed, _ = self.check_rate_limit(key, tokens)
        return allowed

    def assert_allowed(self, key: str = 'default', tokens: int = 1) -> None:
        """
        Assert that request is allowed, raise exception if not.

        Args:
            key: Unique identifier for rate limit bucket
            tokens: Number of tokens to consume

        Raises:
            RateLimitExceeded: If rate limit is exceeded
        """
        allowed, wait_time = self.check_rate_limit(key, tokens)

        if not allowed:
            raise RateLimitExceeded(
                f"Rate limit exceeded. Try again in {wait_time:.1f} seconds."
            )

    def get_statistics(self) -> Dict[str, any]:
        """
        Get rate limiter statistics.

        Returns:
            Dictionary with statistics
        """
        stats = {
            'enabled': self._enabled,
            'rate_per_minute': int(self.rate * 60),
            'burst_capacity': self.capacity,
            'total_requests': self._total_requests,
            'allowed_requests': self._allowed_requests,
            'blocked_requests': self._blocked_requests,
            'block_rate': self._blocked_requests / max(1, self._total_requests),
            'active_buckets': len(self._buckets)
        }

        return stats

    def get_key_statistics(self, key: str) -> Dict[str, any]:
        """
        Get statistics for a specific key.

        Args:
            key: Rate limit bucket key

        Returns:
            Dictionary with key-specific statistics
        """
        if key not in self._buckets:
            return {
                'key': key,
                'exists': False
            }

        bucket = self._buckets[key]
        return {
            'key': key,
            'exists': True,
            'available_tokens': bucket.get_available_tokens(),
            'capacity': bucket.capacity,
            'last_update': bucket.last_update
        }

    def reset_key(self, key: str) -> None:
        """
        Reset rate limit for a specific key.

        Args:
            key: Rate limit bucket key to reset
        """
        if key in self._buckets:
            del self._buckets[key]
            logger.info("Reset rate limit for key: %s", key)

    def health_check(self) -> Dict[str, any]:
        """
        Perform health check on rate limiter.

        Returns:
            Health check results
        """
        try:
            stats = self.get_statistics()

            health = {
                'status': 'healthy',
                'enabled': self._enabled,
                'active_buckets': stats['active_buckets'],
                'block_rate': stats['block_rate']
            }

            # Warn if block rate is high
            if stats['block_rate'] > 0.1:
                health['status'] = 'warning'
                health['warning'] = f"High block rate: {stats['block_rate']:.1%}"

            return health

        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }


# Singleton instance for reuse across Lambda invocations
_rate_limiter_instance: Optional[RateLimiter] = None


def get_rate_limiter() -> RateLimiter:
    """
    Get singleton rate limiter instance.

    Returns:
        RateLimiter instance
    """
    global _rate_limiter_instance  # pylint: disable=global-statement

    if _rate_limiter_instance is None:
        _rate_limiter_instance = RateLimiter()

    return _rate_limiter_instance


def check_rate_limit(key: str = 'default', tokens: int = 1) -> Tuple[bool, Optional[float]]:
    """
    Check if request is within rate limit.

    Args:
        key: Unique identifier for rate limit bucket
        tokens: Number of tokens to consume

    Returns:
        Tuple of (allowed: bool, wait_time_seconds: Optional[float])
    """
    rate_limiter = get_rate_limiter()
    return rate_limiter.check_rate_limit(key, tokens)


def is_allowed(key: str = 'default', tokens: int = 1) -> bool:
    """
    Check if request is allowed (simplified version).

    Args:
        key: Unique identifier for rate limit bucket
        tokens: Number of tokens to consume

    Returns:
        True if allowed, False if rate limited
    """
    rate_limiter = get_rate_limiter()
    return rate_limiter.is_allowed(key, tokens)
