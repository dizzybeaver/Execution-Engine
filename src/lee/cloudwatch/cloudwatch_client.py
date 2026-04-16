"""cloudwatch/cloudwatch_client.py - CloudWatch Metrics Client
Version: 2025-03-03_3
Purpose: CloudWatch metrics integration using boto3 only
License: Apache 2.0

Design Principles:
- Uses only boto3 (pre-installed in Lambda)
- Batches metrics for efficient PutMetricData calls (max 20 per call)
- Non-blocking async design
- Graceful failure (don't break Lambda if CW fails)
- Singleton pattern for client reuse

Performance:
- Lazy boto3 import (only when first metric is recorded)
- Buffered metrics with configurable auto-flush threshold
- Async flush on Lambda shutdown
"""
from __future__ import annotations

import os
import re
import time
from collections.abc import Sequence
from dataclasses import dataclass, field
from enum import Enum
from threading import Lock
from typing import TYPE_CHECKING, Any, Optional

# Import shared security patterns
from lee.cloudwatch.security_patterns import sanitize_cloudwatch_error

from lee.gateway import GatewayInterface, execute_operation

# Import performance configuration
from lee.lee_config.variables import (
    CLOUDWATCH_AUTO_FLUSH_THRESHOLD,
    CLOUDWATCH_MAX_BUFFER_SIZE,
    CLOUDWATCH_MAX_DATUM_SIZE_BYTES,
    CLOUDWATCH_MAX_FLUSH_FAILURES,
    CLOUDWATCH_MAX_METRICS_PER_BATCH,
    CLOUDWATCH_MAX_METRICS_PER_MINUTE,
)

# Type hint for boto3 client (lazy import to avoid dependency)
if TYPE_CHECKING:
    from botocore.client import BaseClient


class MetricUnit(Enum):
    """CloudWatch metric units."""

    None_ = "None"
    Seconds = "Seconds"
    Microseconds = "Microseconds"
    Milliseconds = "Milliseconds"
    Bytes = "Bytes"
    Kilobytes = "Kilobytes"
    Megabytes = "Megabytes"
    Gigabytes = "Gigabytes"
    Terabytes = "Terabytes"
    Bits = "Bits"
    Kilobits = "Kilobits"
    Megabits = "Megabits"
    Gigabits = "Gigabits"
    Terabits = "Terabits"
    Percent = "Percent"
    Count = "Count"
    Bytes_Second = "Bytes/Second"
    Kilobytes_Second = "Kilobytes/Second"
    Megabytes_Second = "Megabytes/Second"
    Gigabytes_Second = "Gigabytes/Second"
    Terabytes_Second = "Terabytes/Second"
    Bits_Second = "Bits/Second"
    Kilobits_Second = "Kilobits/Second"
    Megabits_Second = "Megabits/Second"
    Gigabits_Second = "Gigabits/Second"
    Terabits_Second = "Terabits/Second"
    Count_Second = "Count/Second"


@dataclass
class MetricDimension:
    """CloudWatch metric dimension."""

    name: str
    value: str

    def to_cloudwatch_dict(self) -> dict[str, str]:
        """Convert to CloudWatch API format."""
        return {
            "Name": self.name,
            "Value": self.value,
        }

    def _calculate_datum_size(self) -> int:
        """Calculate the size of this dimension in bytes.

        LOW SEVERITY: Prevents buffer overflow by ensuring dimensions
        don't exceed CloudWatch's 2048 byte limit per metric datum.

            Size in bytes (UTF-8 encoded)

        """
        name_bytes = len(self.name.encode("utf-8"))
        value_bytes = len(self.value.encode("utf-8"))
        # CloudWatch format: {"Name": "...", "Value": "..."}
        return name_bytes + value_bytes + 20  # 20 for JSON overhead


@dataclass
class CloudWatchMetric:
    """CloudWatch metric data."""

    namespace: str
    metric_name: str
    value: float
    unit: MetricUnit = MetricUnit.Count
    dimensions: list[MetricDimension] = field(default_factory=list)
    timestamp: Optional[float] = None

    def __post_init__(self):
        """Set default timestamp and validate types."""
        if self.timestamp is None:
            self.timestamp = time.time()

        # LOW SEVERITY: Type validation for safe serialization
        self._validate_types()

    def _validate_types(self) -> None:
        """Validate metric data types for safe serialization.

        LOW SEVERITY: Prevents unsafe serialization issues by validating
        all metric data types before CloudWatch API calls.

        Raises:
            TypeError: If any field has an invalid type
            ValueError: If timestamp is out of valid range

        """
        if not isinstance(self.namespace, str):
            raise TypeError("namespace must be a string")

        if not isinstance(self.metric_name, str):
            raise TypeError("metric_name must be a string")

        if not isinstance(self.value, (int, float)):
            raise TypeError("value must be numeric")

        if not isinstance(self.unit, MetricUnit):
            raise TypeError("unit must be a MetricUnit enum")

        if not isinstance(self.dimensions, Sequence):
            raise TypeError("dimensions must be a sequence")

        for dim in self.dimensions:
            if not isinstance(dim, MetricDimension):
                raise TypeError(
                    "each dimension must be a MetricDimension object",
                )

        # Validate timestamp is numeric and in reasonable range
        if self.timestamp is not None:
            if not isinstance(self.timestamp, (int, float)):
                raise TypeError("timestamp must be numeric")
            # Check timestamp is between year 2000 and year 2100
            if self.timestamp < 946684800 or self.timestamp > 4102444800:
                raise ValueError("timestamp is out of valid range")

    def _calculate_datum_size(self) -> int:
        """Calculate the total size of this metric datum in bytes.

        LOW SEVERITY: Prevents API rejection by checking against
        CloudWatch's 2048 byte limit per metric datum.

            Size in bytes (estimated UTF-8 encoded)

        """
        namespace_bytes = len(self.namespace.encode("utf-8"))
        metric_name_bytes = len(self.metric_name.encode("utf-8"))
        value_bytes = len(str(self.value).encode("utf-8"))
        unit_bytes = len(self.unit.value.encode("utf-8"))

        # Calculate dimension sizes
        dimensions_bytes = sum(
            dim._calculate_datum_size()  # pylint: disable=protected-access
            for dim in self.dimensions
        )

        # Base JSON overhead
        overhead = 60  # Approximate JSON structure overhead

        return (namespace_bytes + metric_name_bytes + value_bytes + unit_bytes
                + dimensions_bytes + overhead)

    def to_cloudwatch_dict(self) -> dict[str, Any]:
        """Convert to CloudWatch API format."""
        metric_data = {
            "MetricName": self.metric_name,
            "Value": self.value,
            "Unit": self.unit.value,
            "Timestamp": self.timestamp,
        }

        if self.dimensions:
            metric_data["Dimensions"] = [
                dim.to_cloudwatch_dict() for dim in self.dimensions
            ]

        return metric_data


class Boto3CloudWatchClient:  # pylint: disable=too-many-instance-attributes
    """CloudWatch client using boto3 only.

    Features:
    - Singleton pattern for client reuse
    - Metric buffering (max 20 per batch)
    - Async non-blocking design
    - Graceful failure handling

    Usage:
        client = Boto3CloudWatchClient.get_instance()
        client.put_metric(
            namespace='LEE/Lambda',
            metric_name='InvocationCount',
            value=1.0,
            unit=MetricUnit.Count,
            dimensions=[MetricDimension('Function', 'lambda_handler')]
        )
        client.flush_on_shutdown()
    """

    _instance: Optional["Boto3CloudWatchClient"] = None
    _lock: Lock = Lock()

    # CloudWatch API limits (from config)
    _MAX_METRICS_PER_BATCH = CLOUDWATCH_MAX_METRICS_PER_BATCH
    _MAX_DATUM_SIZE = CLOUDWATCH_MAX_DATUM_SIZE_BYTES
    _MAX_METRICS_PER_MINUTE = CLOUDWATCH_MAX_METRICS_PER_MINUTE
    _MAX_BUFFER_SIZE = CLOUDWATCH_MAX_BUFFER_SIZE

    def __init__(self):
        """Initialize CloudWatch client."""
        if Boto3CloudWatchClient._instance is not None:
            raise RuntimeError(
                "Use get_instance() to get Boto3CloudWatchClient singleton",
            )

        # Type hint for boto3 client (lazy loaded)
        self._client: Optional[BaseClient] = None
        self._metric_buffer: list[CloudWatchMetric] = []
        self._buffer_lock: Lock = Lock()
        self._enabled: bool = True
        self._dry_run: bool = False
        self._default_namespace: str = "LEE/Lambda"
        self._auto_flush_threshold: int = CLOUDWATCH_AUTO_FLUSH_THRESHOLD
        self._flush_failure_count: int = 0
        self._max_flush_failures: int = CLOUDWATCH_MAX_FLUSH_FAILURES

        # MEDIUM SEVERITY: Rate limiting to prevent metric flooding
        self._metrics_recorded_minute: int = 0
        self._rate_limit_reset_time: float = time.time()
        self._dropped_metrics_count: int = 0
        self._rate_limit_lock: Lock = Lock()  # Thread safety for rate limiting

        # Configuration from environment
        self._load_config()

    @classmethod
    def get_instance(cls) -> "Boto3CloudWatchClient":
        """Get singleton instance.

            Boto3CloudWatchClient instance

        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def _load_config(self):
        """Load configuration from environment variables with validation.

        INFO SEVERITY: Validates boolean environment variables and namespace
        format to prevent configuration issues.
        """
        # Enable/disable CloudWatch metrics with validation
        # For AWS Lambda: Read from environment variable
        # For local testing: .env file should set this via environment variable
        enabled_str = os.getenv("CLOUDWATCH_ENABLED", "true").lower()
        if enabled_str in ("true", "1", "yes", "on"):
            self._enabled = True
        elif enabled_str in ("false", "0", "no", "off"):
            self._enabled = False
        else:
            # Invalid value, default to enabled
            self._enabled = True

        # Dry run mode (log but don't send) with validation
        dry_run_str = os.getenv("CLOUDWATCH_DRY_RUN", "false").lower()
        if dry_run_str in ("true", "1", "yes", "on"):
            self._dry_run = True
        elif dry_run_str in ("false", "0", "no", "off"):
            self._dry_run = False
        else:
            self._dry_run = False

        # Default namespace with validation
        namespace = os.getenv("CLOUDWATCH_NAMESPACE", "LEE/Lambda")
        if not isinstance(namespace, str):
            namespace = "LEE/Lambda"
        # Remove control characters
        namespace = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", namespace)
        # Enforce 255 character limit
        if len(namespace) > 255:
            namespace = namespace[:255]
        self._default_namespace = namespace

        # Auto-flush threshold (buffer size before auto-flush)
        # For AWS Lambda: Read from environment variable
        # For local testing: .env file should set this via environment variable
        try:
            threshold = int(os.getenv("CLOUDWATCH_FLUSH_THRESHOLD", "15"))
            self._auto_flush_threshold = max(1, min(threshold, self._MAX_METRICS_PER_BATCH))
        except ValueError:
            self._auto_flush_threshold = 15

    def _check_rate_limit(self) -> bool:
        """Check if rate limit has been exceeded.

        MEDIUM SEVERITY: Prevents metric flooding attacks by enforcing
        a maximum number of metrics per minute.

        Thread-safe: Uses lock to prevent race conditions in rate limit checking.

            True if within rate limit, False if limit exceeded

        """
        with self._rate_limit_lock:
            current_time = time.time()

            # Reset counter if minute has passed
            if current_time - self._rate_limit_reset_time > 60:
                self._metrics_recorded_minute = 0
                self._rate_limit_reset_time = current_time

            # Check if limit exceeded
            if self._metrics_recorded_minute >= self._MAX_METRICS_PER_MINUTE:
                self._dropped_metrics_count += 1
                # Record dropped metrics counter
                try:
                    self._record_dropped_metrics()
                except (OSError, ImportError, AttributeError, ConnectionError) as e:
                    try:
                        execute_operation(
                            GatewayInterface.LOGGING,
                            'log_error',
                            message=f'(ImportError, AttributeError, ConnectionError, IOError) occurred: {e}',
                            corr_id=None
                        )
                    except (ImportError, AttributeError, RuntimeError):
                        pass  # Gateway not available
                return False

            self._metrics_recorded_minute += 1
            return True

    def _record_dropped_metrics(self) -> None:
        """Record dropped metrics as a counter metric.

        This helps track when metrics are being dropped due to rate limiting
        or buffer overflow, providing visibility into metric loss.
        """
        # Only record if we have dropped metrics
        if self._dropped_metrics_count > 0:
            # Use a special namespace for dropped metrics to avoid recursion
            try:
                # Create metric directly without going through put_metric
                # to avoid infinite recursion
                dropped_metric = CloudWatchMetric(
                    namespace="LEE/Lambda/Dropped",
                    metric_name="DroppedMetrics",
                    value=float(self._dropped_metrics_count),
                    unit=MetricUnit.Count,
                    dimensions=[MetricDimension(name="Reason", value="RateLimit")],
                )
                # Add to buffer if there's space
                with self._buffer_lock:
                    if len(self._metric_buffer) < self._MAX_BUFFER_SIZE:
                        self._metric_buffer.append(dropped_metric)
                # Reset counter after recording
                self._dropped_metrics_count = 0
            except (OSError, ImportError, AttributeError, ConnectionError):
                # Don't fail if we can't record dropped metrics
                ...

    def _get_client(self) -> "BaseClient":
        """Lazy load boto3 CloudWatch client.

            boto3 CloudWatch client (BaseClient from botocore)

        Raises:
            RuntimeError: If boto3 is not available or client creation fails

        """
        if self._client is None:
            try:
                import boto3  # pylint: disable=import-outside-toplevel
                self._client = boto3.client("cloudwatch")
            except ImportError as e:
                self._enabled = False
                raise RuntimeError(
                    f"boto3 not available for CloudWatch metrics: {e}",
                ) from e
            except Exception as e:
                self._enabled = False
                raise RuntimeError(
                    f"Failed to create CloudWatch client: {e}",
                ) from e

        return self._client

    def put_metric(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        metric_name: str,
        value: float,
        unit: MetricUnit = MetricUnit.Count,
        dimensions: Optional[list[MetricDimension]] = None,
        namespace: Optional[str] = None,
        timestamp: Optional[float] = None,
    ) -> bool:
        """Record a metric (buffered, async) with rate limiting.

            metric_name: Metric name
            value: Metric value
            unit: Metric unit
            dimensions: Optional metric dimensions
            namespace: Optional namespace (uses default if not provided)
            timestamp: Optional timestamp (uses current time if not provided)

            bool: True if metric buffered successfully, False if:
                - CloudWatch metrics are disabled
                - Too many flush failures have occurred
                - Rate limit has been exceeded
                - Metric size exceeds CloudWatch limit
                - An error occurred during buffering

        """
        if not self._enabled:
            return False

        if self._flush_failure_count >= self._max_flush_failures:
            # Too many failures, disable metrics
            self._enabled = False
            return False

        # MEDIUM SEVERITY: Check rate limit (silent fail if exceeded)
        if not self._check_rate_limit():
            return False

        try:
            # Create metric
            metric = CloudWatchMetric(
                namespace=namespace or self._default_namespace,
                metric_name=metric_name,
                value=value,
                unit=unit,
                dimensions=dimensions or [],
                timestamp=timestamp,
            )

            # LOW SEVERITY: Check datum size limit
            if metric._calculate_datum_size() > self._MAX_DATUM_SIZE:  # pylint: disable=protected-access
                return False

            # Add to buffer with size limit
            with self._buffer_lock:
                # MEDIUM SEVERITY: Enforce max buffer size
                if len(self._metric_buffer) >= self._MAX_BUFFER_SIZE:
                    # Drop oldest metric (FIFO)
                    self._metric_buffer.pop(0)
                    self._dropped_metrics_count += 1
                    # Record dropped metrics counter
                    try:
                        self._record_dropped_metrics()
                    except (OSError, ImportError, AttributeError, ConnectionError) as e:
                        try:
                            execute_operation(
                                GatewayInterface.LOGGING,
                                'log_error',
                                message=f'(ImportError, AttributeError, ConnectionError, IOError) occurred: {e}',
                                corr_id=None
                            )
                        except (ImportError, AttributeError, RuntimeError):
                            pass  # Gateway not available

                self._metric_buffer.append(metric)

                # Auto-flush if threshold reached
                if len(self._metric_buffer) >= self._auto_flush_threshold:
                    self._flush_unlocked()

            return True

        except (OSError, ImportError, AttributeError, ConnectionError, IOError) as e:
            # MEDIUM SEVERITY: Sanitize error message
            sanitized_error = sanitize_cloudwatch_error(str(e))
            try:
                from lee.interface.interface_logging import execute_logging_operation  # pylint: disable=import-outside-toplevel
                execute_logging_operation(
                    "log_warning",
                    message=f"CloudWatch put_metric failed: {sanitized_error}",
                )
            except ImportError:
                # Optional dependency - continue if unavailable
                pass
            return False

    def put_metric_data(
        self,
        namespace: str,
        metric_data: list[dict[str, Any]],
    ) -> bool:
        """Put multiple metrics in a single call.

            namespace: CloudWatch namespace
            metric_data: List of metric data dictionaries

            bool: True if all metrics were sent successfully,
                False if:
                    - CloudWatch metrics are disabled
                    - Too many flush failures have occurred
                    - An error occurred during sending

        """
        if not self._enabled:
            return False

        if self._dry_run:
            return True

        if self._flush_failure_count >= self._max_flush_failures:
            self._enabled = False
            return False

        try:
            client = self._get_client()

            # CloudWatch PutMetricData accepts max 20 metrics
            for i in range(
                0,
                len(metric_data),
                self._MAX_METRICS_PER_BATCH,
            ):
                batch = metric_data[i:i + self._MAX_METRICS_PER_BATCH]
                client.put_metric_data(
                    Namespace=namespace,
                    MetricData=batch,
                )

            # Reset failure count on success
            self._flush_failure_count = 0
            return True

        except (OSError, ImportError, AttributeError, ConnectionError, IOError) as e:
            self._flush_failure_count += 1

            # MEDIUM SEVERITY: Sanitize error message
            sanitized_error = sanitize_cloudwatch_error(str(e))
            try:
                execute_operation(
                    GatewayInterface.LOGGING,
                    "log_warning",
                    message=(
                        f"CloudWatch put_metric_data failed: "
                        f"{sanitized_error}"
                    ),
                )
            except ImportError:
                # Optional dependency - continue if unavailable
                pass

            return False

    def increment_counter(
        self,
        metric_name: str,
        value: float = 1.0,
        dimensions: Optional[list[MetricDimension]] = None,
        namespace: Optional[str] = None,
    ) -> bool:
        """Increment a counter metric.

            metric_name: Metric name
            value: Value to increment by (default 1.0)
            dimensions: Optional metric dimensions
            namespace: Optional namespace

            bool: True if counter incremented successfully, False otherwise

        """
        return self.put_metric(
            metric_name=metric_name,
            value=value,
            unit=MetricUnit.Count,
            dimensions=dimensions,
            namespace=namespace,
        )

    def record_timing(
        self,
        metric_name: str,
        duration_ms: float,
        dimensions: Optional[list[MetricDimension]] = None,
        namespace: Optional[str] = None,
    ) -> bool:
        """Record a timing metric.

            metric_name: Metric name
            duration_ms: Duration in milliseconds
            dimensions: Optional metric dimensions
            namespace: Optional namespace

            bool: True if timing recorded successfully, False otherwise

        """
        return self.put_metric(
            metric_name=metric_name,
            value=duration_ms,
            unit=MetricUnit.Milliseconds,
            dimensions=dimensions,
            namespace=namespace,
        )

    def _flush_unlocked(self) -> bool:
        """Flush metric buffer (assumes lock is held) with size validation.

        This method must only be called while holding _buffer_lock to prevent
        concurrent modifications to the metric buffer.

            bool: True if all metrics were flushed successfully, False if any
                namespace batch failed to send

        """
        if not self._metric_buffer:
            return True

        # Convert metrics to CloudWatch format
        # LOW SEVERITY: Filter out metrics that exceed size limit
        valid_metrics = []
        for metric in self._metric_buffer:
            if metric._calculate_datum_size() <= self._MAX_DATUM_SIZE:  # pylint: disable=protected-access
                valid_metrics.append(metric)

        metric_data = [
            metric.to_cloudwatch_dict() for metric in valid_metrics
        ]

        # Group by namespace
        by_namespace: dict[str, list[dict[str, Any]]] = {}
        for datum in metric_data:
            namespace = datum.get("Namespace", self._default_namespace)
            # Remove Namespace from datum (it's a parameter, not in MetricData)
            datum_copy = datum.copy()
            datum_copy.pop("Namespace", None)
            by_namespace.setdefault(namespace, []).append(datum_copy)

        # Clear buffer
        self._metric_buffer.clear()

        # Send metrics by namespace
        success = True
        for namespace, data in by_namespace.items():
            if not self.put_metric_data(namespace, data):
                success = False

        return success

    def flush(self) -> bool:
        """Flush buffered metrics to CloudWatch.

        Thread-safe: Acquires buffer lock before flushing.

            bool: True if all metrics were flushed successfully, False if:
                - CloudWatch metrics are disabled
                - Any namespace batch failed to send

        """
        if not self._enabled:
            return False

        with self._buffer_lock:
            return self._flush_unlocked()

    def flush_on_shutdown(self) -> bool:
        """Flush metrics on Lambda shutdown.

        This should be called in the Lambda pre-stop hook to ensure
        all buffered metrics are sent before the function terminates.

            bool: True if all metrics were flushed successfully, False otherwise

        """
        return self.flush()

    def get_buffer_size(self) -> int:
        """Get current buffer size.

        Thread-safe: Acquires buffer lock before reading.

            int: Number of metrics currently in the buffer

        """
        with self._buffer_lock:
            return len(self._metric_buffer)

    def is_enabled(self) -> bool:
        """Check if CloudWatch metrics are enabled.

            bool: True if CloudWatch metrics are currently enabled,
                False if disabled or too many flush failures have occurred

        """
        return self._enabled

    def reset_failure_count(self):
        """Reset flush failure count (re-enable metrics after failures)."""
        self._flush_failure_count = 0
        self._enabled = True


def get_cloudwatch_client() -> Boto3CloudWatchClient:
    """Get CloudWatch client singleton.

        Boto3CloudWatchClient instance

    """
    return Boto3CloudWatchClient.get_instance()


__all__ = [
    "Boto3CloudWatchClient",
    "CloudWatchMetric",
    "MetricDimension",
    "MetricUnit",
    "get_cloudwatch_client",
]
