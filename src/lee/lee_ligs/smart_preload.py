# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-03-31 - Smart preload prediction system

"""smart_preload.py - Request Pattern-Based Smart Preloading
Version: 1.0.0
Date: 2026-03-31
Purpose: Predictive module preloading based on request patterns

Reduces cold start latency by tracking which modules are commonly
accessed together and preloading them proactively.

Key Features:
    - RequestPatternTracker: Track module access patterns
    - PreloadPredictor: Predict likely module needs based on request type
    - SmartPreloader: Execute preloads with timing tracking
    - Pattern-based optimization: Discovery vs Control requests

Pattern Tracking:
    - Discovery requests: ha_gateway, ha_devices (high correlation)
    - Control requests: ha_gateway, ha_http_client, ha_websocket_client
    - State queries: ha_gateway, ha_devices, ha_cache

Performance Impact:
    - First Request: 50-80ms (lazy loading overhead)
    - Subsequent: <5ms (all cached)
    - Smart Preload: 20-30ms (predictive, reduces first request latency)

Usage:
    from lee.lee_ligs.smart_preload import get_smart_preloader

    preloader = get_smart_preloader()

    # Preload for discovery request
    preloader.preload_for_request_type('discovery')

    # Preload for control request
    preloader.preload_for_request_type('control')

    # Record module access (for pattern learning)
    preloader.record_access('ha_gateway', 'discovery')

Copyright 2026 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

from __future__ import annotations

import os
import threading
import time
from collections import defaultdict
from typing import Any

# Import gateway for logging
from lee.gateway import GatewayInterface, execute_operation
from lee.singleton import ThreadSafeSingleton

# Cache debug mode check at module load time
_DEBUG_ENABLED = os.getenv("LEE_DEBUG", "false").lower() == "true"


def _is_debug_mode() -> bool:
    """Check if debug mode is enabled.

    Returns:
        True if LEE_DEBUG environment variable is set to 'true'
    """
    return _DEBUG_ENABLED


class RequestPatternTracker:
    """Track module access patterns by request type.

    Learns which modules are commonly accessed together for different
    request types (discovery, control, query, etc.).

    Attributes:
        _access_counts: Dict tracking module access counts by request type
        _coaccess_counts: Dict tracking module co-access patterns
        _lock: Thread lock for thread-safe updates

    Example:
        tracker = RequestPatternTracker()

        # Record that ha_gateway was accessed during discovery
        tracker.record_access('ha_gateway', 'discovery')

        # Record that ha_gateway and ha_devices were accessed together
        tracker.record_coaccess(['ha_gateway', 'ha_devices'], 'discovery')

        # Get predicted modules for discovery
        predicted = tracker.predict_modules('discovery')
    """

    def __init__(self):
        """Initialize RequestPatternTracker."""
        self._access_counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self._coaccess_counts: dict[str, dict[tuple[str, ...], int]] = defaultdict(lambda: defaultdict(int))
        self._lock = threading.Lock()

        # Initialize with known patterns (baseline knowledge)
        self._initialize_baseline_patterns()

    def _initialize_baseline_patterns(self):
        """Initialize with known request patterns.

        These patterns are based on typical Alexa Smart Home request flows:
        - Discovery: Needs ha_gateway, ha_devices
        - Control: Needs ha_gateway, ha_http_client, ha_websocket_client
        - Query: Needs ha_gateway, ha_devices
        - Authorization: Needs NO modules (AcceptGrant is lightweight)
        """
        # Discovery request patterns
        self._access_counts['discovery']['ha_gateway'] = 100
        self._access_counts['discovery']['ha_devices'] = 95
        self._access_counts['discovery']['ha_http_client'] = 80

        # Control request patterns
        self._access_counts['control']['ha_gateway'] = 100
        self._access_counts['control']['ha_http_client'] = 90
        self._access_counts['control']['ha_websocket_client'] = 85
        self._access_counts['control']['ha_devices'] = 60

        # Query request patterns
        self._access_counts['query']['ha_gateway'] = 100
        self._access_counts['query']['ha_devices'] = 95
        self._access_counts['query']['ha_http_client'] = 40

        # Authorization request patterns (AcceptGrant - NO preload needed)
        self._access_counts['authorization'] = {}

    def record_access(self, module_name: str, request_type: str) -> None:
        """Record module access for a request type.

        Args:
            module_name: Name of module accessed
            request_type: Type of request (discovery, control, query, etc.)
        """
        with self._lock:
            self._access_counts[request_type][module_name] += 1

    def record_coaccess(self, module_names: list[str], request_type: str) -> None:
        """Record modules accessed together.

        Args:
            module_names: List of module names accessed together
            request_type: Type of request
        """
        if len(module_names) < 2:
            return

        # Sort for consistent key
        module_tuple = tuple(sorted(module_names))

        with self._lock:
            self._coaccess_counts[request_type][module_tuple] += 1

    def predict_modules(self, request_type: str, threshold: int = 50) -> list[str]:
        """Predict which modules will be needed for a request type.

        Args:
            request_type: Type of request
            threshold: Minimum access count to include in prediction

        Returns:
            List of module names predicted to be needed

        """
        with self._lock:
            # Get access counts for this request type
            access_counts = self._access_counts.get(request_type, {})

            # Filter by threshold and sort by frequency
            predicted = [
                module for module, count in access_counts.items()
                if count >= threshold
            ]

            # Sort by access frequency (most common first)
            predicted.sort(key=lambda m: access_counts[m], reverse=True)

            return predicted

    def get_stats(self) -> dict[str, Any]:
        """Get pattern tracking statistics.

        Returns:
            Dictionary with tracking statistics

        """
        with self._lock:
            return {
                "request_types": list(self._access_counts.keys()),
                "total_modules": sum(len(modules) for modules in self._access_counts.values()),
                "access_patterns": {
                    req_type: list(modules.keys())
                    for req_type, modules in self._access_counts.items()
                },
            }


class PreloadPredictor:
    """Predictive preloading based on request patterns.

    Uses RequestPatternTracker to determine which modules to preload
    for optimal performance.

    Attributes:
        _tracker: RequestPatternTracker instance
        _ligs_registry: LazyImportRegistry instance

    Example:
        predictor = PreloadPredictor()

        # Get preload list for discovery request
        modules = predictor.predict_for_namespace('Alexa.Discovery')

        # Get preload list for control request
        modules = predictor.predict_for_namespace('Alexa.PowerController')
    """

    def __init__(self):
        """Initialize PreloadPredictor."""
        self._tracker = RequestPatternTracker()

        # Get LIGS registry for actual preloading
        try:
            from lee.lee_ligs import get_lazy_import_registry  # pylint: disable=import-outside-toplevel
            self._ligs_registry = get_lazy_import_registry()
        except ImportError:
            self._ligs_registry = None

    def predict_for_namespace(self, namespace: str, name: str = "") -> list[str]:
        """Predict modules needed for Alexa namespace/name.

        Args:
            namespace: Alexa namespace (e.g., 'Alexa.Discovery')
            name: Alexa operation name (e.g., 'TurnOn')

        Returns:
            List of module names to preload

        """
        # Map Alexa namespaces to request types
        request_type = self._map_namespace_to_request_type(namespace, name)

        # Get predicted modules
        return self._tracker.predict_modules(request_type)

    def _map_namespace_to_request_type(self, namespace: str, name: str) -> str:  # pylint: disable=unused-argument
        """Map Alexa namespace to request type.

        Args:
            namespace: Alexa namespace
            name: Alexa operation name (unused, reserved for future use)

        Returns:
            Request type string (discovery, control, query, authorization)

        """
        if namespace == "Alexa.Discovery":
            return "discovery"

        # Authorization/AcceptGrant - skip preloading to prevent timeout
        if namespace == "Alexa.Authorization":
            return "authorization"

        # Control namespaces
        control_namespaces = [
            "Alexa.PowerController",
            "Alexa.BrightnessController",
            "Alexa.ColorController",
            "Alexa.ThermostatController",
            "Alexa.LockController",
            "Alexa.SceneController",
        ]

        if namespace in control_namespaces:
            return "control"

        # Query namespaces
        query_namespaces = [
            "Alexa.TemperatureSensor",
            "Alexa.PercentageController",
            "Alexa.ModeController",
            "Alexa.RangeController",
        ]

        if namespace in query_namespaces:
            return "query"

        # Default: assume control
        return "control"


class SmartPreloader(ThreadSafeSingleton):
    """Execute smart preloading with timing tracking.

    Coordinates predictive preloading with actual module loading
    and performance tracking.

    Attributes:
        _predictor: PreloadPredictor instance
        _preload_cache: Cache of preloaded modules by request type
        _lock: Thread lock for thread-safe operations

    Example:
        preloader = SmartPreloader()

        # Preload for discovery request
        timing = preloader.preload_for_request_type('discovery')

        # Preload for specific namespace
        timing = preloader.preload_for_namespace('Alexa.Discovery')

    """

    def __init__(self):
        """Initialize SmartPreloader (use get_instance() instead)."""
        self._predictor = PreloadPredictor()
        self._preload_cache: dict[str, set[str]] = defaultdict(set)
        self._lock = threading.Lock()

    def preload_for_request_type(self, request_type: str) -> dict[str, Any]:
        """Preload modules for a request type.

        Args:
            request_type: Type of request (discovery, control, query, authorization)

        Returns:
            Dictionary with timing and status information

        """
        start_time = time.perf_counter()

        if _is_debug_mode():
            execute_operation(
                GatewayInterface.DEBUG, 'log',
                message="[SmartPreloader] preload_for_request_type START",
                scope='LIGS',
                request_type=request_type,
            )

        try:
            # Get predicted modules
            predictor = self._predictor._tracker  # pylint: disable=protected-access
            module_names = predictor.predict_modules(request_type)

            if _is_debug_mode():
                execute_operation(
                    GatewayInterface.DEBUG, 'log',
                    message="[SmartPreloader] Predicted modules",
                    scope='LIGS',
                    request_type=request_type,
                    module_names=module_names,
                )

            if not module_names:
                if _is_debug_mode():
                    execute_operation(
                        GatewayInterface.DEBUG, 'log',
                        message="[SmartPreloader] No modules to preload",
                        scope='LIGS',
                        request_type=request_type,
                    )
                return {
                    "success": True,
                    "request_type": request_type,
                    "modules_preloaded": [],
                    "total_time_ms": 0.0,
                    "message": "No modules to preload",
                }

            # Preload modules
            results = self._preload_modules(module_names, request_type)

            total_time = (time.perf_counter() - start_time) * 1000

            if _is_debug_mode():
                execute_operation(
                    GatewayInterface.DEBUG, 'log',
                    message="[SmartPreloader] Preload complete",
                    scope='LIGS',
                    request_type=request_type,
                    loaded=results["loaded"],
                    skipped=results["skipped"],
                    failed=results["failed"],
                    total_time_ms=total_time,
                )

            return {
                "success": True,
                "request_type": request_type,
                "modules_preloaded": results["loaded"],
                "total_time_ms": total_time,
                "message": f"Preloaded {len(results['loaded'])} modules in {total_time:.2f}ms",
            }

        except (ImportError, ModuleNotFoundError, AttributeError, TypeError, ValueError, RuntimeError, ConnectionError, TimeoutError) as e:
            total_time = (time.perf_counter() - start_time) * 1000

            if _is_debug_mode():
                execute_operation(
                    GatewayInterface.DEBUG, 'log',
                    message="[SmartPreloader] Preload FAILED",
                    scope='LIGS',
                    request_type=request_type,
                    error=str(e),
                    error_type=type(e).__name__,
                )

            try:
                execute_operation(
                    GatewayInterface.LOGGING,
                    "log_error",
                    message=f"[SmartPreloader] Preload failed for {request_type}: {e}",
                )
            except (ImportError, AttributeError):
                ...

            return {
                "success": False,
                "request_type": request_type,
                "modules_preloaded": [],
                "total_time_ms": total_time,
                "error": str(e),
            }

    def preload_for_namespace(self, namespace: str, name: str = "") -> dict[str, Any]:
        """Preload modules for Alexa namespace.

        Args:
            namespace: Alexa namespace (e.g., 'Alexa.Discovery')
            name: Alexa operation name (e.g., 'TurnOn')

        Returns:
            Dictionary with timing and status information

        """
        if _is_debug_mode():
            execute_operation(
                GatewayInterface.DEBUG, 'log',
                message="[SmartPreloader] preload_for_namespace START",
                scope='LIGS',
                namespace=namespace,
                name=name,
            )

        # Map namespace to request type
        request_type = self._predictor._map_namespace_to_request_type(namespace, name)  # pylint: disable=protected-access

        if _is_debug_mode():
            execute_operation(
                GatewayInterface.DEBUG, 'log',
                message="[SmartPreloader] Mapped namespace to request type",
                scope='LIGS',
                namespace=namespace,
                name=name,
                request_type=request_type,
            )

        # Preload for request type
        return self.preload_for_request_type(request_type)

    def _preload_modules(self, module_names: list[str], request_type: str) -> dict[str, Any]:
        """Preload list of modules.

        Args:
            module_names: List of module names to preload
            request_type: Request type for caching

        Returns:
            Dictionary with preload results

        """
        loaded = []
        skipped = []
        failed = []

        registry = self._predictor._ligs_registry  # pylint: disable=protected-access

        if registry is None:
            if _is_debug_mode():
                execute_operation(
                    GatewayInterface.DEBUG, 'log',
                    message="[SmartPreloader] Registry is None, skipping preload",
                    scope='LIGS',
                    request_type=request_type,
                )
            return {"loaded": [], "skipped": [], "failed": []}

        if _is_debug_mode():
            execute_operation(
                GatewayInterface.DEBUG, 'log',
                message="[SmartPreloader] _preload_modules START",
                scope='LIGS',
                request_type=request_type,
                module_count=len(module_names),
            )

        for module_name in module_names:
            if _is_debug_mode():
                execute_operation(
                    GatewayInterface.DEBUG, 'log',
                    message="[SmartPreloader] Checking module",
                    scope='LIGS',
                    module_name=module_name,
                )

            # Check if already loaded
            try:
                if registry.is_loaded(module_name):
                    if _is_debug_mode():
                        execute_operation(
                            GatewayInterface.DEBUG, 'log',
                            message="[SmartPreloader] Module already loaded, skipping",
                            scope='LIGS',
                            module_name=module_name,
                        )
                    skipped.append(module_name)
                    continue
            except ValueError:
                # Module not registered
                if _is_debug_mode():
                    execute_operation(
                        GatewayInterface.DEBUG, 'log',
                        message="[SmartPreloader] Module not registered",
                        scope='LIGS',
                        module_name=module_name,
                    )
                failed.append(module_name)
                continue

            # Preload module
            try:
                module_start = time.perf_counter()
                registry.get(module_name)
                module_time = (time.perf_counter() - module_start) * 1000

                loaded.append(module_name)

                # Add to preload cache
                with self._lock:
                    self._preload_cache[request_type].add(module_name)

                if _is_debug_mode():
                    execute_operation(
                        GatewayInterface.DEBUG, 'log',
                        message="[SmartPreloader] Preloaded module successfully",
                        scope='LIGS',
                        module_name=module_name,
                        load_time_ms=module_time,
                    )

                # Log preload
                try:
                    execute_operation(
                        GatewayInterface.LOGGING,
                        "log_debug",
                        message=f"[SmartPreloader] Preloaded {module_name} for {request_type} ({module_time:.2f}ms)",
                    )
                except (ImportError, AttributeError):
                    ...

            except (ImportError, ModuleNotFoundError, AttributeError, TypeError, ValueError, RuntimeError, ConnectionError, TimeoutError) as e:
                if _is_debug_mode():
                    execute_operation(
                        GatewayInterface.DEBUG, 'log',
                        message="[SmartPreloader] Failed to preload module",
                        scope='LIGS',
                        module_name=module_name,
                        error=str(e),
                        error_type=type(e).__name__,
                    )

                failed.append(module_name)

                try:
                    execute_operation(
                        GatewayInterface.LOGGING,
                        "log_error",
                        message=f"[SmartPreloader] Failed to preload {module_name}: {e}",
                    )
                except (ImportError, AttributeError):
                    ...

        if _is_debug_mode():
            execute_operation(
                GatewayInterface.DEBUG, 'log',
                message="[SmartPreloader] _preload_modules COMPLETE",
                scope='LIGS',
                request_type=request_type,
                loaded_count=len(loaded),
                skipped_count=len(skipped),
                failed_count=len(failed),
            )

        return {"loaded": loaded, "skipped": skipped, "failed": failed}

    def get_stats(self) -> dict[str, Any]:
        """Get preloading statistics.

        Returns:
            Dictionary with preloading statistics

        """
        with self._lock:
            return {
                "cached_request_types": list(self._preload_cache.keys()),
                "cached_modules": {
                    req_type: list(modules)
                    for req_type, modules in self._preload_cache.items()
                },
                "pattern_stats": self._predictor._tracker.get_stats(),  # pylint: disable=protected-access
            }


def get_smart_preloader() -> SmartPreloader:
    """Convenience function to get singleton SmartPreloader.

    Returns:
        Shared SmartPreloader instance

    Example:
        from lee.lee_ligs.smart_preload import get_smart_preloader

        preloader = get_smart_preloader()
        result = preloader.preload_for_namespace('Alexa.Discovery')

    """
    return SmartPreloader.get_instance()


__all__ = [
    "RequestPatternTracker",
    "PreloadPredictor",
    "SmartPreloader",
    "get_smart_preloader",
]
