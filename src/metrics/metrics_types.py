"""
metrics/metrics_types.py

Version: 2025-12-11_1
Purpose: Metrics type definitions and data structures
Project: LEE
License: Apache 2.0
"""

from dataclasses import dataclass, field
from typing import Dict
from collections import defaultdict


@dataclass
class ResponseMetrics:
    """Response metrics data structure."""
    total_responses: int = 0
    successful_responses: int = 0
    error_responses: int = 0
    timeout_responses: int = 0
    cached_responses: int = 0
    fallback_responses: int = 0
    avg_response_time_ms: float = 0.0
    fastest_response_ms: float = float('inf')
    slowest_response_ms: float = 0.0
    cache_hit_rate: float = 0.0
    
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        from metrics.metrics_helper import safe_divide
        return safe_divide(self.successful_responses, self.total_responses, multiply_by=100.0)


@dataclass
class HTTPClientMetrics:
    """HTTP client metrics data structure."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_time_ms: float = 0.0
    total_response_time_ms: float = 0.0
    requests_by_method: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    requests_by_status: Dict[int, int] = field(default_factory=lambda: defaultdict(int))


@dataclass
class CircuitBreakerMetrics:
    """Circuit breaker metrics data structure."""
    circuit_name: str = ""
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    circuit_opens: int = 0
    half_open_attempts: int = 0
    current_state: str = "closed"
