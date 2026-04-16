"""lee_cache/cache_key_optimizer.py

Version: 2026-03-31_1
Purpose: Cache key optimization with normalization and hashing
Project: LEE
License: Apache 2.0

Provides cache key optimization features:
- Key normalization for consistent lookups
- Key hashing for faster comparisons
- Key pattern analysis
- Key size optimization

Classes:
    CacheKeyOptimizer: Main key optimization orchestrator
    KeyPattern: Analyzer for key usage patterns

"""

import hashlib
import re
import threading
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class KeyPatternStats:
    """Statistics for a key pattern.

    Attributes:
        pattern: Regular expression pattern
        count: Number of keys matching this pattern
        avg_length: Average key length
        total_accesses: Total access count
        hit_rate: Cache hit rate for this pattern

    """

    pattern: str
    count: int = 0
    avg_length: float = 0.0
    total_accesses: int = 0
    hit_count: int = 0
    miss_count: int = 0

    @property
    def hit_rate(self) -> float:
        """Cache hit rate as percentage (0-100)."""
        if self.total_accesses == 0:
            return 0.0
        return (self.hit_count / self.total_accesses) * 100


class CacheKeyOptimizer:
    """Cache key optimization with normalization and hashing.

    Thread-safe singleton implementation.
    """

    _instance = None  # type: Optional[CacheKeyOptimizer]
    _initialized = False  # type: bool
    _lock = threading.RLock()

    # Key normalization rules
    NORMALIZATION_RULES = [
        # Convert to lowercase
        (r"[A-Z]", lambda m: m.group(0).lower()),
        # Replace multiple spaces with single space
        (r"\s+", "_"),
        # Remove special characters except underscore, colon, dot, dash
        (r"[^a-zA-Z0-9_:.-]", ""),
        # Remove leading/trailing underscores
        (r"^_+|_+$", ""),
    ]

    def __new__(cls) -> "CacheKeyOptimizer":
        """Get or create singleton instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize key optimizer (only once)."""
        if self._initialized:
            return

        self._key_hashes: dict[str, str] = {}
        self._hash_to_key: dict[str, str] = {}
        self._key_patterns: dict[str, KeyPatternStats] = defaultdict(KeyPatternStats)
        self._key_access_count: dict[str, int] = defaultdict(int)
        self._normalization_cache: dict[str, str] = {}
        self._max_cache_size: int = 10000
        self._initialized = True

    def normalize_key(self, key: str, _correlation_id: Optional[str] = None) -> str:
        """Normalize cache key for consistent lookups.

            key: Cache key to normalize
            _correlation_id: Optional correlation ID for tracking

            Normalized cache key

        """
        # Check cache first
        if key in self._normalization_cache:
            return self._normalization_cache[key]

        normalized = key

        # Apply normalization rules
        for rule in self.NORMALIZATION_RULES:
            if isinstance(rule, tuple):
                if len(rule) == 2 and callable(rule[1]):
                    # Pattern with replacement function
                    normalized = re.sub(rule[0], rule[1], normalized)
                else:
                    # Simple string replacement
                    normalized = re.sub(rule[0], rule[1], normalized)
            else:
                # String replacement
                normalized = re.sub(rule, "_", normalized)

        # Cache result
        with self._lock:
            if len(self._normalization_cache) >= self._max_cache_size:
                # Clear oldest entries (simple approach)
                self._normalization_cache.clear()
            self._normalization_cache[key] = normalized

        return normalized

    def hash_key(self, key: str, algorithm: str = "sha256", correlation_id: Optional[str] = None) -> str:
        """Generate hash of cache key for faster comparisons.

            key: Cache key to hash
            algorithm: Hash algorithm (md5, sha1, sha256)
            correlation_id: Optional correlation ID for tracking

            Hexadecimal hash string

        """
        # Normalize first
        normalized = self.normalize_key(key, correlation_id)

        # Check cache
        if normalized in self._key_hashes:
            return self._key_hashes[normalized]

        # Generate hash
        # Dictionary dispatch for O(1) algorithm lookup
        # MD5 and SHA-1 deprecated for security - use SHA-256
        # Cache key hashing is not security-critical, but SHA-256 is recommended
        HASH_ALGORITHMS = {
            # "md5": hashlib.md5,      # Deprecated - use SHA-256
            # "sha1": hashlib.sha1,    # Deprecated - use SHA-256
            "sha256": hashlib.sha256,  # Recommended - secure and widely supported
        }
        hash_constructor = HASH_ALGORITHMS.get(algorithm, hashlib.sha256)
        hash_obj = hash_constructor()

        hash_obj.update(normalized.encode("utf-8"))
        hash_hex = hash_obj.hexdigest()

        # Cache bidirectional mapping
        with self._lock:
            self._key_hashes[normalized] = hash_hex
            self._hash_to_key[hash_hex] = normalized

        return hash_hex

    def optimize_key(self, key: str, use_hash: bool = False, correlation_id: Optional[str] = None) -> str:
        """Optimize cache key with normalization and optional hashing.

            key: Cache key to optimize
            use_hash: Whether to use hashed key
            correlation_id: Optional correlation ID for tracking

            Optimized cache key

        """
        normalized = self.normalize_key(key, correlation_id)

        if use_hash:
            return self.hash_key(key, correlation_id=correlation_id)

        return normalized

    def record_key_access(self, key: str, hit: bool = False, correlation_id: Optional[str] = None) -> None:
        """Record cache key access for pattern analysis.

            key: Cache key that was accessed
            hit: Whether this was a cache hit
            correlation_id: Optional correlation ID for tracking

        """
        normalized = self.normalize_key(key, correlation_id)

        with self._lock:
            self._key_access_count[normalized] += 1

            # Update pattern stats
            pattern = self._detect_pattern(normalized)
            if pattern not in self._key_patterns:
                self._key_patterns[pattern] = KeyPatternStats(pattern=pattern)

            stats = self._key_patterns[pattern]
            stats.total_accesses += 1
            if hit:
                stats.hit_count += 1
            else:
                stats.miss_count += 1
            stats.count += 1
            stats.avg_length = (stats.avg_length * (stats.count - 1) + len(normalized)) / stats.count

    def _detect_pattern(self, key: str) -> str:
        """Detect pattern in cache key.

            key: Normalized cache key

            Pattern string

        """
        # Common patterns
        if key.startswith("entity:"):
            return "entity:*"
        if key.startswith("config:"):
            return "config:*"
        if key.startswith("state:"):
            return "state:*"
        if ":" in key:
            parts = key.split(":")
            if len(parts) >= 2:
                return f"{parts[0]}:*"
        if "." in key:
            return "*.*"
        return "*"

    def get_key_stats(self, key: Optional[str] = None, correlation_id: Optional[str] = None) -> dict[str, Any] | dict[str, Any]:
        """Get statistics for cache key(s).

            key: Optional specific key to query (None for all keys)
            correlation_id: Optional correlation ID for tracking

            Dict with key statistics

        """
        with self._lock:
            if key:
                normalized = self.normalize_key(key, correlation_id)
                access_count = self._key_access_count.get(normalized, 0)
                hash_value = self._key_hashes.get(normalized, "")

                return {
                    "key": key,
                    "normalized_key": normalized,
                    "hash": hash_value,
                    "access_count": access_count,
                }
            # Return all keys stats
            return {
                "total_keys": len(self._key_access_count),
                "total_hashed_keys": len(self._key_hashes),
                "normalization_cache_size": len(self._normalization_cache),
                "top_keys": list(self._key_access_count.items()),
            }

    def get_pattern_stats(self, _correlation_id: Optional[str] = None) -> list[dict[str, Any]]:
        """Get statistics by key pattern.

            _correlation_id: Optional correlation ID for tracking

            List of pattern statistics sorted by access count

        """
        with self._lock:
            patterns = []
            for pattern, stats in self._key_patterns.items():
                patterns.append({
                    "pattern": pattern,
                    "count": stats.count,
                    "avg_length": round(stats.avg_length, 2),
                    "total_accesses": stats.total_accesses,
                    "hit_rate": round(stats.hit_rate, 2),
                })

            return sorted(patterns, key=lambda x: x["total_accesses"], reverse=True)

    def clear_cache(self, _correlation_id: Optional[str] = None) -> None:
        """Clear optimization caches.

            _correlation_id: Optional correlation ID for tracking

        """
        with self._lock:
            self._key_hashes.clear()
            self._hash_to_key.clear()
            self._normalization_cache.clear()

    def get_optimization_recommendations(self, correlation_id: Optional[str] = None) -> list[dict[str, Any]]:
        """Get optimization recommendations based on key analysis.

            correlation_id: Optional correlation ID for tracking

            List of optimization recommendations

        """
        recommendations = []
        pattern_stats = self.get_pattern_stats(correlation_id)

        # Check for long keys
        for pattern in pattern_stats:
            if pattern["avg_length"] > 100:
                recommendations.append({
                    "type": "key_length",
                    "severity": "info",
                    "pattern": pattern["pattern"],
                    "message": f"Pattern '{pattern['pattern']}' has average key length of {pattern['avg_length']:.1f} characters",
                    "action": "Consider using hashed keys for this pattern",
                })

        # Check for low hit rate patterns
        for pattern in pattern_stats:
            if pattern["total_accesses"] > 100 and pattern["hit_rate"] < 50:
                recommendations.append({
                    "type": "hit_rate",
                    "severity": "warning",
                    "pattern": pattern["pattern"],
                    "message": f"Pattern '{pattern['pattern']}' has low hit rate of {pattern['hit_rate']:.1f}%",
                    "action": "Consider adjusting TTL or cache strategy for this pattern",
                })

        return recommendations


def get_cache_key_optimizer() -> CacheKeyOptimizer:
    """Get singleton CacheKeyOptimizer instance.

        CacheKeyOptimizer singleton instance

    """
    return CacheKeyOptimizer()


__all__ = [
    "CacheKeyOptimizer",
    "KeyPatternStats",
    "get_cache_key_optimizer",
]

# EOF
