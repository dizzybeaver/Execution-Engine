# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-01 - Correlation ID generation utilities

"""correlation_id_utils.py - Centralized Correlation ID Generation

Provides standardized correlation ID generation for tracking and debugging
across the LEE codebase. Replaces duplicate correlation ID patterns in 30+ files.

Usage:
    from lee.utils.correlation_id_utils import generate_correlation_id

    cid = generate_correlation_id(prefix="svc")
    # Returns: "svc_1712345678_abc123"
"""

import secrets
import time


def generate_correlation_id(prefix: str = "op", entropy_bytes: int = 4) -> str:
    """Generate a unique correlation ID for tracing operations.

    Args:
        prefix: Operation prefix (e.g., "svc", "http", "cache")
        entropy_bytes: Number of random bytes (default: 4)

    Returns:
        Correlation ID string in format: "{prefix}_{timestamp}_{random}"
        Example: "svc_1712345678_abc123"

    Code Quality: Replaces duplicate correlation ID generation across 30+ files
    """
    timestamp = int(time.time() * 1000)
    random_part = secrets.token_hex(entropy_bytes)
    return f"{prefix}_{timestamp}_{random_part}"


def generate_correlation_id_with_context(prefix: str, context: dict[str, str]) -> str:
    """Generate correlation ID with embedded context information.

    Args:
        prefix: Operation prefix
        context: Dictionary of context key-value pairs

    Returns:
        Correlation ID with encoded context

    Code Quality: Enables richer tracing without changing function signatures
    """
    base_id = generate_correlation_id(prefix)
    if context:
        context_str = "_".join(f"{k}:{v}" for k, v in context.items())
        return f"{base_id}_{context_str}"
    return base_id


def parse_correlation_id(correlation_id: str) -> dict[str, str]:
    """Parse correlation ID to extract components.

    Args:
        correlation_id: Correlation ID string to parse

    Returns:
        Dictionary with components: prefix, timestamp, random, context

    Code Quality: Enables reverse-lookup of correlation ID information
    """
    parts = correlation_id.split("_")
    result = {"prefix": parts[0] if len(parts) > 0 else "",
              "timestamp": parts[1] if len(parts) > 1 else "",
              "random": parts[2] if len(parts) > 2 else ""}

    if len(parts) > 3:
        result["context"] = "_".join(parts[3:])

    return result
