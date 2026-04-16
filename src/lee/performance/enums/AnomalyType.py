#!/usr/bin/env python3
"""Anomaly type enumeration for performance system."""

from enum import Enum


class AnomalyType(Enum):
    """Types of anomaly detection algorithms.

    Types:
        Z_SCORE: Z-score based detection
        SPIKE: Spike detection
        IQR: Interquartile range detection
    """

    Z_SCORE = "z_score"
    SPIKE = "spike"
    IQR = "iqr"
