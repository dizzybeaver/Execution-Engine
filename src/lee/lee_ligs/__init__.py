"""lee_ligs - Lazy Import Gateway System for LEE
Version: 1.0.0
Date: 2026-03-05
Description: Lazy module loading to reduce cold start time and memory usage

Based on UGA's LIGS pattern (gateway.omms.ligs).

Benefits:
    - 40-60% reduction in cold start time for HA-SUGA modules
    - Lower memory footprint (modules load only when used)
    - Faster Lambda INIT phase
    - Better resource utilization

Architecture:
    - LazyModule: Wrapper for lazy-loaded modules
    - LazyImportRegistry: Thread-safe singleton registry
    - Factory pattern for consistent module creation

Usage:
    from lee.lee_ligs import get_lazy_import_registry

    registry = get_lazy_import_registry()
    registry.register(
        name='ha_gateway',
        module_path='home_assistant.ha_gateway',
        factory=lambda: __import__('home_assistant.ha_gateway')
    )

    # Module loads on first access
    ha_gateway = registry.get('ha_gateway')

Copyright 2026 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

from lee.lee_ligs.lazy_import_system import (
    LazyImportRegistry,
    LazyModule,
    get_lazy_import_registry,
)

__all__ = [
    "LazyImportRegistry",
    "LazyModule",
    "get_lazy_import_registry",
]

__version__ = "1.0.0"
__ligs_version__ = "COMPLETE"
