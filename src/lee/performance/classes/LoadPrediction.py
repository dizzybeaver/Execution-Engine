"""Load Prediction Data Class for LEE Lambda Performance

Prediction result for future load analysis.
Zero external dependencies - uses only Python stdlib.
"""

from dataclasses import dataclass

# Day names for pattern descriptions
DAY_NAMES = [
    "Monday", "Tuesday", "Wednesday", "Thursday",
    "Friday", "Saturday", "Sunday",
]


@dataclass
class LoadPrediction:
    """Prediction result for future load.

    Attributes:
        predicted_requests_per_minute: Expected request rate
        confidence: Confidence score (0.0 to 1.0)
        sample_size: Number of samples used for prediction
        time_slot: (day_of_week, hour) tuple
        predicted_duration_ms: Predicted average request duration
        pattern_description: Human-readable description

    """

    predicted_requests_per_minute: float
    confidence: float  # 0.0 to 1.0
    sample_size: int
    time_slot: tuple[int, int]  # (day_of_week, hour)
    predicted_duration_ms: float
    pattern_description: str  # Human-readable description

    def to_dict(self) -> dict:
        """Convert prediction to dictionary for logging/metrics."""
        return {
            "predicted_requests_per_minute": self.predicted_requests_per_minute,
            "confidence": self.confidence,
            "sample_size": self.sample_size,
            "time_slot": {
                "day_of_week": self.time_slot[0],
                "hour": self.time_slot[1],
                "day_name": DAY_NAMES[self.time_slot[0]],
            },
            "predicted_duration_ms": self.predicted_duration_ms,
            "pattern_description": self.pattern_description,
        }


__all__ = [
    "LoadPrediction",
    "DAY_NAMES",
]
