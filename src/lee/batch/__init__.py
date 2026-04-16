# LEE Project Code File
# ASCII ONLY
# Modified: 2026-03-25 - Batch module init

"""Batch operations module for LEE project.

This module provides batch processing capabilities for Home Assistant operations,
including batching multiple API calls, parallel execution, and batch processing.

Exports:
    batch_ha_calls_implementation: Batch multiple HA API calls
    batch_process_implementation: Process items in batches
    parallel_execute_implementation: Execute operations in parallel
"""

from lee.batch.batch_generic import (
    batch_ha_calls_implementation,
    batch_process_implementation,
    parallel_execute_implementation,
)

__all__ = [
    "batch_ha_calls_implementation",
    "batch_process_implementation",
    "parallel_execute_implementation",
]
