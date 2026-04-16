"""Anomaly Result Data Class for LEE Lambda Performance

Structured result from anomaly detection operations.
Zero external dependencies - uses only Python stdlib.
"""

from dataclasses import dataclass, field
from typing import Optional

from lee.performance.enums.AnomalySeverity import AnomalySeverity
from lee.performance.enums.AnomalyType import AnomalyType


@dataclass
class AnomalyResult:
    """Structured result from anomaly detection.

    Attributes:
        is_anomaly: Whether an anomaly was detected
        severity: Severity level if anomaly detected (None otherwise)
        anomaly_type: Type of detection algorithm used
        value: The value that was checked
        threshold: Threshold used for detection
        message: Human-readable description of the result
        confidence: Confidence score (0.0 to 1.0)
        context: Additional context information

    """
    # pylint: disable=too-many-instance-attributes
    # All 8 attributes are necessary for complete anomaly detection results

    is_anomaly: bool
    severity: Optional[AnomalySeverity]
    anomaly_type: AnomalyType
    value: float
    threshold: float
    message: str
    confidence: float = 0.0
    context: dict[str, any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, any]:
        """Convert result to dictionary for logging/metrics."""
        return {
            "is_anomaly": self.is_anomaly,
            "severity": self.severity.value if self.severity else None,
            "anomaly_type": self.anomaly_type.value,
            "value": self.value,
            "threshold": self.threshold,
            "message": self.message,
            "confidence": self.confidence,
            "context": self.context,
        }


__all__ = [
    "AnomalyResult",
    "AnomalySeverity",
    "AnomalyType",
]
