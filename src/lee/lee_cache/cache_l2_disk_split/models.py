"""cache_l2_disk_split/models.py

Data models for L2 disk cache.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, asdict
from typing import Any, Optional


# Constants
DEFAULT_CACHE_DIR = "/tmp/lee_cache_l2"
DEFAULT_MAX_SIZE_MB = 100
DEFAULT_MAX_ENTRIES = 1000
DEFAULT_TTL = 3600
CLEANUP_INTERVAL_SECONDS = 60
HASH_ALGORITHM = "sha256"


@dataclass
class L2CacheEntry:
    """Represents a single cache entry with metadata."""

    key: str
    value: Any
    created_at: float
    expires_at: float
    size_bytes: int
    access_count: int = 0
    last_accessed: float = 0.0

    def is_expired(self, current_time: Optional[float] = None) -> bool:
        """Check if entry has expired."""
        if current_time is None:
            current_time = time.time()
        return current_time >= self.expires_at

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> L2CacheEntry:
        """Create from dictionary."""
        return cls(**data)


@dataclass
class L2CacheConfig:
    """Configuration for L2 disk cache."""

    cache_dir: str = DEFAULT_CACHE_DIR
    max_size_mb: int = DEFAULT_MAX_SIZE_MB
    max_entries: int = DEFAULT_MAX_ENTRIES
    default_ttl: int = DEFAULT_TTL
    cleanup_interval: int = CLEANUP_INTERVAL_SECONDS

    def validate(self) -> None:
        """Validate configuration parameters."""
        if self.max_size_mb <= 0:
            raise ValueError("max_size_mb must be positive")
        if self.max_entries <= 0:
            raise ValueError("max_entries must be positive")
        if self.default_ttl <= 0:
            raise ValueError("default_ttl must be positive")
        if self.cleanup_interval <= 0:
            raise ValueError("cleanup_interval must be positive")
