"""Cache compression module for LEE.

Compresses cache values larger than threshold to reduce memory usage.
Uses gzip compression with pickle or JSON serialization.

Version: 2026-03-03_1
License: Apache 2.0
"""

from __future__ import annotations

import gzip
import json
import pickle
import sys
import threading
import time
from collections.abc import Collection
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

try:
    from lee.gateway import GatewayInterface, execute_operation
    from lee.gateway.gateway_core import generate_correlation_id
    _GATEWAY_AVAILABLE = True
except ImportError:
    _GATEWAY_AVAILABLE = False

from lee.singleton import SingletonFactory

# Import SecurePickle for safe serialization
try:
    from lee.lee_security import safe_dumps, safe_loads
    _SECURE_PICKLE_AVAILABLE = True
except ImportError:
    _SECURE_PICKLE_AVAILABLE = False

# Import observability for metrics tracking
try:
    from lee.lee_cache.cache_observability import get_cache_observability
    _OBSERVABILITY_AVAILABLE = True
except ImportError:
    _OBSERVABILITY_AVAILABLE = False


class SerializationFormat(Enum):
    """Serialization format options."""

    PICKLE = "pickle"
    JSON = "json"


@dataclass
class CompressionConfig:
    """Compression configuration."""

    threshold_bytes: int = 1024  # Compress values > 1KB
    compression_level: int = 6    # 1-9 (default 6)
    algorithm: str = "gzip"
    serialization: SerializationFormat = SerializationFormat.PICKLE
    enable_timing: bool = True


@dataclass
class CompressionMetadata:
    """Metadata for compressed values."""

    original_size: int
    compressed_size: int
    compression_ratio: float
    algorithm: str
    serialization: str
    timestamp: float

    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            "original_size": self.original_size,
            "compressed_size": self.compressed_size,
            "compression_ratio": self.compression_ratio,
            "algorithm": self.algorithm,
            "serialization": self.serialization,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict) -> CompressionMetadata:
        """Create from dictionary."""
        return cls(
            original_size=data["original_size"],
            compressed_size=data["compressed_size"],
            compression_ratio=data["compression_ratio"],
            algorithm=data["algorithm"],
            serialization=data["serialization"],
            timestamp=data["timestamp"],
        )


@dataclass
class CompressionStatistics:
    """Compression statistics tracking."""

    total_compressions: int = 0
    total_decompressions: int = 0
    bytes_saved: int = 0
    total_original_bytes: int = 0
    total_compressed_bytes: int = 0
    compression_failures: int = 0
    decompression_failures: int = 0
    skip_count: int = 0
    skip_bytes_saved: int = 0
    compression_time_total_ms: float = 0.0
    compression_count_for_time: int = 0

    @property
    def space_saving_rate(self) -> float:
        """Calculate space saving rate (0-1)."""
        if self.total_original_bytes == 0:
            return 0.0
        return self.bytes_saved / self.total_original_bytes

    @property
    def average_compression_ratio(self) -> float:
        """Calculate average compression ratio."""
        if self.total_original_bytes == 0:
            return 1.0
        return self.total_original_bytes / self.total_compressed_bytes if self.total_compressed_bytes > 0 else 1.0

    @property
    def skip_rate(self) -> float:
        """Calculate skip rate (0-1)."""
        total_attempts = self.total_compressions + self.skip_count
        if total_attempts == 0:
            return 0.0
        return self.skip_count / total_attempts

    @property
    def average_compression_time_ms(self) -> float:
        """Calculate average compression time in milliseconds."""
        if self.compression_count_for_time == 0:
            return 0.0
        return self.compression_time_total_ms / self.compression_count_for_time

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "total_compressions": self.total_compressions,
            "total_decompressions": self.total_decompressions,
            "bytes_saved": self.bytes_saved,
            "total_original_bytes": self.total_original_bytes,
            "total_compressed_bytes": self.total_compressed_bytes,
            "compression_failures": self.compression_failures,
            "decompression_failures": self.decompression_failures,
            "space_saving_rate": self.space_saving_rate,
            "average_compression_ratio": self.average_compression_ratio,
            "skip_count": self.skip_count,
            "skip_bytes_saved": self.skip_bytes_saved,
            "skip_rate": self.skip_rate,
            "average_compression_time_ms": self.average_compression_time_ms,
        }


class CacheCompressor:
    """Cache compression manager.

    Compresses values larger than threshold to reduce memory usage.
    Thread-safe singleton pattern.
    """

    def __init__(self, config: Optional[CompressionConfig] = None):
        """Initialize cache compressor.

            config: Compression configuration (uses defaults if None)

        """
        self._config = config or CompressionConfig()
        self._stats = CompressionStatistics()
        self._lock = threading.RLock()

    def configure(self, **kwargs) -> None:
        """Update compressor configuration.

        Args:
            **kwargs: Configuration options to update
        """
        with self._lock:
            for key, value in kwargs.items():
                if hasattr(self._config, key):
                    setattr(self._config, key, value)

    def get_config(self) -> CompressionConfig:
        """Get current compressor configuration.

        Returns:
            Current configuration
        """
        return self._config

    def _estimate_size_fast(self, value: Any, correlation_id: Optional[str] = None) -> int:
        """Fast size estimation without serialization.

        Args:
            value: Value to estimate size for
            correlation_id: Optional correlation ID for tracking

        Returns:
            Estimated size in bytes (conservative estimate)
        """
        # For simple types, use direct measurement
        if value is None:
            return 0
        elif isinstance(value, (str, bytes, bytearray)):
            return len(value)
        elif isinstance(value, (int, float, bool)):
            return 8  # Conservative estimate for primitives
        elif isinstance(value, Collection):
            # Estimate collection size
            try:
                # Count elements and estimate string content size
                element_count = len(value)
                total_size = element_count * 64  # Base overhead per element
                # Add estimated content size for strings
                for item in value:
                    if isinstance(item, str):
                        total_size += len(item)
                return total_size
            except TypeError:
                return self._config.threshold_bytes + 1  # Force compression
        elif isinstance(value, dict):
            # Estimate dict size: keys + values + overhead
            try:
                total_size = len(value) * 128  # Higher overhead for dict entries
                # Add estimated content size for strings
                for k, v in value.items():
                    if isinstance(k, str):
                        total_size += len(k)
                    if isinstance(v, str):
                        total_size += len(v)
                return total_size
            except (ValueError, TypeError, OverflowError, MemoryError) as original_error:
                try:
                    from lee.lee_cache.exception_handler import handle_cache_exception
                    handle_cache_exception(
                        exception=original_error,
                        operation_name="estimate_size_dict",
                        context="Dict size estimation failed, forcing compression",
                        correlation_id=correlation_id
                    )
                except (ImportError, AttributeError, RuntimeError):
                    try:
                        execute_operation(
                            GatewayInterface.LOGGING,
                            'log_error',
                            message=f'(ImportError, AttributeError, RuntimeError) occurred: {original_error}',
                            corr_id=None
                        )
                    except (ImportError, AttributeError, RuntimeError):
                        pass  # Gateway not available
                return self._config.threshold_bytes + 1  # Force compression
        else:
            # For complex objects, use sys.getsizeof as heuristic
            # This is much faster than serialization
            try:
                return sys.getsizeof(value)
            except (TypeError, ValueError, OverflowError, MemoryError) as original_error:
                try:
                    from lee.lee_cache.exception_handler import handle_cache_exception
                    handle_cache_exception(
                        exception=original_error,
                        operation_name="estimate_size_complex",
                        context="Size estimation failed, forcing compression",
                        correlation_id=correlation_id
                    )
                except (ImportError, AttributeError, RuntimeError):
                    try:
                        execute_operation(
                            GatewayInterface.LOGGING,
                            'log_error',
                            message=f'(ImportError, AttributeError, RuntimeError) occurred: {original_error}',
                            corr_id=None
                        )
                    except (ImportError, AttributeError, RuntimeError):
                        pass  # Gateway not available
                return self._config.threshold_bytes + 1

    def compress(self, value: Any, correlation_id: Optional[str] = None) -> tuple[bytes, CompressionMetadata]:
        """Compress a value if it exceeds threshold.

        Args:
            value: Value to compress
            correlation_id: Optional correlation ID for tracking

        Returns:
            Tuple of (compressed_data, metadata)

        Raises:
            ValueError: If compression fails
            TypeError: If value cannot be serialized
        """
        # Inline correlation ID generation (SUGA-ISP compliant)
        if correlation_id is None:
            correlation_id = generate_correlation_id("cmp")

        # FAST PATH: Check estimated size BEFORE expensive serialization
        estimated_size = self._estimate_size_fast(value, correlation_id)
        if estimated_size < self._config.threshold_bytes:
            # Small value: skip compression entirely (15-20ms savings)
            with self._lock:
                self._stats.skip_count += 1
                # Estimate bytes saved by avoiding compression overhead
                # Compression overhead is typically 15-20ms + metadata
                self._stats.skip_bytes_saved += estimated_size

            # Record compression skip to observability
            if _OBSERVABILITY_AVAILABLE:
                try:
                    observability = get_cache_observability()
                    observability.record_compression_skip(
                        key="skipped_value",
                        correlation_id=correlation_id,
                    )
                except (ImportError, AttributeError):
                    # Observability unavailable - skip recording
                    ...

            # Still need to serialize for storage, but return with None metadata
            if self._config.serialization == SerializationFormat.PICKLE:
                if _SECURE_PICKLE_AVAILABLE:
                    serialized = safe_dumps(value)
                else:
                    raise ValueError(
                        "Secure pickle not available - cannot use pickle serialization. "
                        "SerializationFormat.PICKLE requires lee_security.safe_pickle module."
                    )
            else:
                serialized = json.dumps(value).encode("utf-8")
            return serialized, None

        # Start timing (only for large values that might be compressed)
        start_time = None
        if self._config.enable_timing:
            start_time = time.perf_counter()

        if _GATEWAY_AVAILABLE:
            timing_ctx = execute_operation(
                GatewayInterface.DEBUG, "timing",
                correlation_id=correlation_id,
                operation_name="compression.compress",
            )
            with timing_ctx:
                pass  # Context manager will auto-exit

        try:
            with self._lock:
                # Serialize value (use secure pickle if available)
                if self._config.serialization == SerializationFormat.PICKLE:
                    if _SECURE_PICKLE_AVAILABLE:
                        serialized = safe_dumps(value)
                    else:
                        # Fallback to standard pickle (less safe)
                        serialized = pickle.dumps(value)
                else:
                    # JSON requires dict/list/string types
                    serialized = json.dumps(value).encode("utf-8")

                original_size = len(serialized)

                # Check if compression is needed (actual size check)
                if original_size < self._config.threshold_bytes:
                    # Skip compression for small data even after serialization
                    self._stats.skip_count += 1
                    self._stats.skip_bytes_saved += original_size

                    # Record compression skip to observability
                    if _OBSERVABILITY_AVAILABLE:
                        try:
                            observability = get_cache_observability()
                            observability.record_compression_skip(
                                key="skipped_value",
                                correlation_id=correlation_id,
                            )
                        except (ImportError, AttributeError):
                            # Observability unavailable - skip recording
                            ...

                    # End timing early
                    if self._config.enable_timing and start_time is not None:
                        duration_ms = (time.perf_counter() - start_time) * 1000

                    if self._config.enable_timing and _GATEWAY_AVAILABLE:
                        timing_ctx.__exit__(None, None, None)

                    return serialized, None

                # Compress
                compressed_data = gzip.compress(
                    serialized,
                    compresslevel=self._config.compression_level,
                )
                compressed_size = len(compressed_data)
                compression_ratio = original_size / compressed_size if compressed_size > 0 else 1.0

                # Create metadata
                metadata = CompressionMetadata(
                    original_size=original_size,
                    compressed_size=compressed_size,
                    compression_ratio=compression_ratio,
                    algorithm=self._config.algorithm,
                    serialization=self._config.serialization.value,
                    timestamp=time.time(),
                )

                # Update statistics
                self._stats.total_compressions += 1
                self._stats.total_original_bytes += original_size
                self._stats.total_compressed_bytes += compressed_size
                self._stats.bytes_saved += (original_size - compressed_size)

                # Track timing
                duration_ms = 0.0
                if self._config.enable_timing and start_time is not None:
                    duration_ms = (time.perf_counter() - start_time) * 1000
                    self._stats.compression_time_total_ms += duration_ms
                    self._stats.compression_count_for_time += 1

                # Record compression metrics to observability
                if _OBSERVABILITY_AVAILABLE:
                    try:
                        observability = get_cache_observability()
                        observability.record_compression(
                            key="compressed_value",
                            compression_ratio=compression_ratio,
                            compression_time_ms=duration_ms,
                            bytes_saved=(original_size - compressed_size),
                            original_bytes=original_size,
                            compressed_bytes=compressed_size,
                            correlation_id=correlation_id,
                        )
                    except (ImportError, AttributeError):
                        # Observability unavailable - skip recording
                        ...

                # End timing
                if self._config.enable_timing and _GATEWAY_AVAILABLE:
                    timing_ctx.__exit__(None, None, None)

                return compressed_data, metadata

        except Exception as e:
            with self._lock:
                self._stats.compression_failures += 1

            if self._config.enable_timing and _GATEWAY_AVAILABLE:
                timing_ctx.__exit__(type(e), e, None)

            # Re-raise for caller to handle
            raise

    def decompress(self, data: bytes, metadata: CompressionMetadata, correlation_id: Optional[str] = None) -> Any:
        """Decompress compressed data.

        Args:
            data: Compressed data
            metadata: Compression metadata from compression
            correlation_id: Optional correlation ID for tracking

        Returns:
            Decompressed value

        Raises:
            ValueError: If decompression fails
        """
        # Inline correlation ID generation
        if correlation_id is None:
            correlation_id = generate_correlation_id("cmp")

        # Start timing
        timing_ctx = None
        if self._config.enable_timing and _GATEWAY_AVAILABLE:
            timing_ctx = execute_operation(
                GatewayInterface.DEBUG, "timing",
                correlation_id=correlation_id,
                operation_name="compression.decompress",
            )
            timing_ctx.__enter__()

        try:
            # If no metadata, data wasn't compressed
            if metadata is None:
                if timing_ctx is not None:
                    timing_ctx.__exit__(None, None, None)
                # Try to unpickle/deserialize anyway (use secure pickle if available)
                try:
                    if _SECURE_PICKLE_AVAILABLE:
                        return safe_loads(data)
                    raise ValueError("Secure pickle not available - cannot deserialize pickle data safely")
                except (ValueError, TypeError, pickle.UnpicklingError):
                    try:
                        return json.loads(data.decode("utf-8"))
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        return data.decode("utf-8")

            with self._lock:
                # Decompress
                decompressed = gzip.decompress(data)

                # Deserialize (use secure pickle if available)
                if metadata.serialization == SerializationFormat.PICKLE.value:
                    if _SECURE_PICKLE_AVAILABLE:
                        value = safe_loads(decompressed)
                    else:
                        raise ValueError("Secure pickle not available - cannot deserialize pickle data safely")
                else:
                    value = json.loads(decompressed.decode("utf-8"))

                # Update statistics
                self._stats.total_decompressions += 1

                # End timing
                if timing_ctx is not None:
                    timing_ctx.__exit__(None, None, None)

                return value

        except Exception as e:
            with self._lock:
                self._stats.decompression_failures += 1

            if timing_ctx is not None:
                timing_ctx.__exit__(type(e), e, None)

            raise ValueError(f"Decompression failed: {e}") from e

    def get_stats(self) -> CompressionStatistics:
        """Alias for get_statistics() for backwards compatibility."""
        return self.get_statistics()

    def get_statistics(self) -> CompressionStatistics:
        """Get current compression statistics."""
        with self._lock:
            # Return a copy to prevent external modification
            return CompressionStatistics(
                total_compressions=self._stats.total_compressions,
                total_decompressions=self._stats.total_decompressions,
                bytes_saved=self._stats.bytes_saved,
                total_original_bytes=self._stats.total_original_bytes,
                total_compressed_bytes=self._stats.total_compressed_bytes,
                compression_failures=self._stats.compression_failures,
                decompression_failures=self._stats.decompression_failures,
                skip_count=self._stats.skip_count,
                skip_bytes_saved=self._stats.skip_bytes_saved,
                compression_time_total_ms=self._stats.compression_time_total_ms,
                compression_count_for_time=self._stats.compression_count_for_time,
            )

    def reset_statistics(self) -> None:
        """Reset compression statistics."""
        with self._lock:
            self._stats = CompressionStatistics()


# Singleton factory for cache compressor
_compressor_factory: Optional[SingletonFactory[CacheCompressor]] = None


def _get_compressor_factory() -> SingletonFactory[CacheCompressor]:
    """Get or create the compressor singleton factory."""
    global _compressor_factory  # pylint: disable=global-statement
    if _compressor_factory is None:
        _compressor_factory = SingletonFactory(lambda: CacheCompressor())
    return _compressor_factory


def get_cache_compressor(config: Optional[CompressionConfig] = None) -> CacheCompressor:
    """Get singleton cache compressor instance.

    Args:
        config: Optional configuration (only used on first call)

    Returns:
        CacheCompressor singleton instance
    """
    compressor = _get_compressor_factory().get_instance()

    # Apply config if provided
    if config is not None:
        compressor.configure(**dict(config.__dict__.items()))

    return compressor


def reset_cache_compressor() -> None:
    """Reset compressor singleton (for testing)."""
    _get_compressor_factory().reset_instance()


__all__ = [
    "CacheCompressor",
    "CompressionConfig",
    "CompressionMetadata",
    "CompressionStatistics",
    "SerializationFormat",
    "get_cache_compressor",
    "reset_cache_compressor",
]
