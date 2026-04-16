#!/usr/bin/env python3
"""Error occurrence data model for diagnosis system."""

from dataclasses import dataclass, field

from lee.diagnosis.classes.ErrorSignature import ErrorSignature


@dataclass
class ErrorOccurrence:
    """Single error occurrence record.

    Attributes:
        signature: Error signature for pattern matching
        timestamp: Unix timestamp when error occurred
        correlation_id: Request correlation ID
        message: Error message
        severity: Error severity level ("low", "medium", "high", "critical")
        context: Additional context dictionary
    """

    signature: ErrorSignature
    timestamp: float
    correlation_id: str
    message: str
    severity: str
    context: dict = field(default_factory=dict)
