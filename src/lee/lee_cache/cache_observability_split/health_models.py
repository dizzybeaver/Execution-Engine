"""cache_observability_split/health_models.py

Health recommendation and status dataclasses.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from lee.lee_cache.cache_observability_split.enums import HealthStatus

class HealthRecommendation:
    """Recommendation for improving cache health.

    Attributes:
        severity: Recommendation severity (info, warning, critical)
        category: Category of recommendation (performance, capacity, configuration)
        message: Human-readable recommendation
        action: Suggested action to take

    """

    severity: str
    category: str
    message: str
    action: str


@dataclass
class CacheHealthStatus:
    """Overall cache health status.

    Attributes:
        status: Health status (healthy, degraded, unhealthy, unknown)
        score: Health score (0-100, higher is better)
        warnings: List of health warnings
        recommendations: List of actionable recommendations
        checked_at: When health check was performed
        metrics_snapshot: Metrics at time of check

    """

    status: HealthStatus
    score: float
    warnings: list[str] = field(default_factory=list)
    recommendations: list[HealthRecommendation] = field(default_factory=list)
    checked_at: datetime = field(default_factory=datetime.now)
    metrics_snapshot: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization.

            Dict representation of health status

        """
        return {
            "status": self.status.value,
            "score": round(self.score, 2),
            "warnings": self.warnings,
            "recommendations": [
                {
                    "severity": r.severity,
                    "category": r.category,
                    "message": r.message,
                    "action": r.action,
                }
                for r in self.recommendations
            ],
            "checked_at": self.checked_at.isoformat(),
            "metrics": self.metrics_snapshot,
        }
