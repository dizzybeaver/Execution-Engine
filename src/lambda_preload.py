"""lambda_preload.py - LUGS-Protected Critical Module Preloading
Version: 2025-03-02_2
Description: Preload critical modules during Lambda INIT with selective imports

This module loads ONLY what we need, WHEN we need it:
- typing: Common types used everywhere (20ms)
- enum: Enum base class (10ms)
- urllib3: ONLY PoolManager and Timeout (50ms vs 1,700ms full import)
- boto3 SSM: ONLY SSM client via botocore.session (300ms vs 8,500ms full boto3)
- HA-SUGA: LAZY import via LIGS (0ms INIT time, loads on first use)

Design Decision: Selective imports for performance
Reason: We don't need S3, Lambda, DynamoDB, EC2, RDS, CloudWatch, SNS, SQS, IAM,
        CloudFormation, API Gateway, Step Functions, etc. - just SSM!
        Full boto3 loads 200+ services (8,500ms), we only need 1 service (300ms).
        Full urllib3 loads entire library (1,700ms), we only need 2 classes (50ms).
        HA-SUGA modules load lazily via LIGS (0ms INIT impact).

Performance Target:
- Lambda INIT: 350-450ms (typing, enum, urllib3 selective, boto3 SSM selective)
- First Request: 120-180ms (everything preloaded, just business logic)
- Total Cold Start: 470-630ms (acceptable!)
- HA-SUGA Load: 0ms INIT (lazy loads on first Alexa request)

CHANGES (2025-03-02_2):
- ADDED: LIGS (Lazy Import Gateway System) support for HA-SUGA modules
- REMOVED: Eager HA-SUGA imports (now load lazily via home_assistant.__init__)

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import os
import time

# ===== GATEWAY DEBUG SYSTEM (Earliest Initialization) =====
# Gateway debug system (initialized when LEE_DEBUG=true)
# This must be initialized before any debug operations
_LEE_DEBUG = os.environ.get("LEE_DEBUG", "false").lower() == "true"
_execute_operation = None
_GatewayInterface = None


def _init_debug_system() -> None:
    """Initialize gateway debug system if available."""
    global _execute_operation, _GatewayInterface

    if not _LEE_DEBUG:
        return

    try:
        from lee.gateway import execute_operation, GatewayInterface
        _execute_operation = execute_operation
        _GatewayInterface = GatewayInterface
    except (ImportError, AttributeError):
        pass


# Initialize debug system on module load
_init_debug_system()

# ===== TIMING HELPER =====

def _print_timing(message: str):
    """Print timing if LEE_DEBUG=true."""
    if _LEE_DEBUG:
        print(f"[PRELOAD_TIMING] {message}")

# ===== URLLIB3 IMPORT =====
# Import urllib3 at module level (required for Lambda cold start optimization)
from urllib3 import PoolManager, Timeout  # noqa: E402

# ===== BOOTSTRAP LOGGING (EARLIEST INITIALIZATION) =====
# Bootstrap logging must be initialized FIRST, before any other imports
# This provides logging capability before gateway is available

_timing_start = time.perf_counter()
_print_timing("Initializing bootstrap logging...")

try:
    from lee.lee_logging.bootstrap_logging import setup_lambda_bootstrap_logging
    bootstrap_log = setup_lambda_bootstrap_logging("PRELOAD")
    bootstrap_log.info("Bootstrap logging initialized for Lambda preload")
    _bootstrap_time = (time.perf_counter() - _timing_start) * 1000
    _print_timing(f"*** Bootstrap logging initialized: {_bootstrap_time:.2f}ms ***")
except ImportError as e:
    # Bootstrap logging not available, use print
    print(f"[PRELOAD_WARNING] Bootstrap logging not available: {e}")
    bootstrap_log = None
    _bootstrap_time = (time.perf_counter() - _timing_start) * 1000
    _print_timing(f"*** Bootstrap logging skipped: {_bootstrap_time:.2f}ms ***")

# ===== PRELOAD START =====

_preload_start = time.perf_counter()
_print_timing("===== LAMBDA PRELOAD START =====")

# ===== URLLIB3 (Always Needed for HTTP) =====

_timing_start = time.perf_counter()
_print_timing("Loading urllib3 (selective: PoolManager, Timeout)...")

# SELECTIVE IMPORT: Only the 2 classes we actually use
# NOT: import urllib3 (loads entire library - 1,700ms)
# YES: from urllib3 import PoolManager, Timeout (only what we need - 50ms)
# Already imported at module level for cold start optimization

_urllib3_time = (time.perf_counter() - _timing_start) * 1000
_print_timing(f"*** urllib3 (selective) loaded: {_urllib3_time:.2f}ms ***")

# ===== BOTO3 SSM (Conditional - Only If Parameter Store Enabled) =====

_USE_PARAMETER_STORE = os.environ.get("USE_PARAMETER_STORE", "false").lower() == "true"
_BOTO3_SSM_CLIENT = None

if _USE_PARAMETER_STORE:
    _timing_start = time.perf_counter()
    _print_timing("Parameter Store ENABLED - Loading boto3 SSM client (selective)...")

    try:
        # SELECTIVE IMPORT: Only SSM client, not entire boto3
        # NOT: import boto3; boto3.client('ssm') (loads 200+ services - 8,500ms!)
        # YES: botocore.session.Session().create_client('ssm') (only SSM - 300ms)
        _print_timing("  Step 1: Importing botocore.session...")
        _botocore_start = time.perf_counter()

        from botocore.session import Session

        _botocore_import_time = (time.perf_counter() - _botocore_start) * 1000
        _print_timing(f"  *** botocore.session imported: {_botocore_import_time:.2f}ms ***")

        # Create SSM client directly (bypasses full boto3 initialization)
        _print_timing("  Step 2: Creating SSM client...")
        _ssm_start = time.perf_counter()

        session = Session()
        _BOTO3_SSM_CLIENT = session.create_client("ssm")

        _ssm_time = (time.perf_counter() - _ssm_start) * 1000
        _print_timing(f"  *** SSM client created: {_ssm_time:.2f}ms ***")

        _total_boto3_time = (time.perf_counter() - _timing_start) * 1000
        _print_timing(f"*** boto3 SSM (selective) loaded: {_total_boto3_time:.2f}ms ***")

    except (ImportError, AttributeError) as e:
        # Import or attribute error during boto3 initialization
        _error_time = (time.perf_counter() - _timing_start) * 1000
        _print_timing(f"!!! boto3 SSM initialization FAILED after {_error_time:.2f}ms: {e}")
        _USE_PARAMETER_STORE = False
        _BOTO3_SSM_CLIENT = None
    except (OSError, ConnectionError) as e:
        # Network or system error during SSM client creation
        _error_time = (time.perf_counter() - _timing_start) * 1000
        _print_timing(f"!!! boto3 SSM network error after {_error_time:.2f}ms: {e}")
        _USE_PARAMETER_STORE = False
        _BOTO3_SSM_CLIENT = None
    except (RuntimeError, ValueError, TypeError) as e:
        # Other unexpected errors during boto3 initialization
        _error_time = (time.perf_counter() - _timing_start) * 1000
        _print_timing(f"!!! boto3 SSM initialization FAILED after {_error_time:.2f}ms: {e}")
        _USE_PARAMETER_STORE = False
        _BOTO3_SSM_CLIENT = None
else:
    _print_timing("Parameter Store DISABLED - Skipping boto3")

# ===== PRELOAD COMPLETE =====

_total_preload_time = (time.perf_counter() - _preload_start) * 1000
_print_timing(f"===== LAMBDA PRELOAD COMPLETE: {_total_preload_time:.2f}ms =====")

# Gateway availability flag
_GATEWAY_AVAILABLE = True

# Gateway debug verification (LEE_DEBUG mode)
if _LEE_DEBUG and _execute_operation and _GatewayInterface:
    _timing_start = time.perf_counter()
    _print_timing("Verifying gateway debug interface...")

    try:
        _debug_test = _execute_operation(_GatewayInterface.DEBUG, 'generate_trace_id')
        _debug_test_time = (time.perf_counter() - _timing_start) * 1000
        _print_timing(f"*** Gateway debug interface verified: {_debug_test_time:.2f}ms ***")
    except (AttributeError, TypeError, RuntimeError) as e:
        _gateway_init_time = (time.perf_counter() - _timing_start) * 1000
        _print_timing(f"!!! Gateway debug verification FAILED after {_gateway_init_time:.2f}ms: {e}")


# ===== EXPORTS =====

# Make preloaded modules available for import
__all__ = [
    "_BOTO3_SSM_CLIENT",
    "_USE_PARAMETER_STORE",
    "PoolManager",
    "Timeout",
]

# ===== CACHE CONFIGURATION =====

# Cache configuration for Lambda environment
cache_l2_disable = True  # Disable L2 disk cache in Lambda
cache_warming_threads = 1  # Use single thread for cache warming in Lambda

# ===== COLD START TRACKING INTEGRATION =====

# Only initialize performance tracking if explicitly enabled
_ENABLE_PERFORMANCE_TRACKING = os.environ.get(
    "ENABLE_PERFORMANCE_TRACKING", "true",
).lower() == "true"

if _ENABLE_PERFORMANCE_TRACKING:
    try:
        # pylint: disable=ungrouped-imports
        from lee.performance.cold_start_tracker import get_cold_start_tracker

        if _LEE_DEBUG and _execute_operation and _GatewayInterface:
            try:
                _execute_operation(_GatewayInterface.DEBUG, 'log',
                                 message="[COLD_START] About to get cold start tracker",
                                 scope="PRELOAD")
            except (AttributeError, TypeError, RuntimeError):
                pass

        tracker = get_cold_start_tracker()

        if _LEE_DEBUG and _execute_operation and _GatewayInterface:
            try:
                _execute_operation(_GatewayInterface.DEBUG, 'log',
                                 message="[COLD_START] Tracker obtained, recording imports",
                                 scope="PRELOAD")
            except (AttributeError, TypeError, RuntimeError):
                pass

        tracker.record_import(
            "urllib3",
            _urllib3_time if "_urllib3_time" in dir() else 0.0,
        )

        if _USE_PARAMETER_STORE and "_total_boto3_time" in dir():
            tracker.record_import("boto3_ssm", _total_boto3_time)

        if _LEE_DEBUG and _execute_operation and _GatewayInterface:
            try:
                _execute_operation(_GatewayInterface.DEBUG, 'log',
                                 message="[COLD_START] About to finalize cold start",
                                 scope="PRELOAD")
            except (AttributeError, TypeError, RuntimeError):
                pass

        tracker.finalize_cold_start()

        if _LEE_DEBUG and _execute_operation and _GatewayInterface:
            try:
                _execute_operation(_GatewayInterface.DEBUG, 'log',
                                 message="[COLD_START] Tracking initialized - PRELOAD COMPLETE",
                                 scope="PRELOAD")
            except (AttributeError, TypeError, RuntimeError):
                pass

        _print_timing("[COLD_START] Tracking initialized")
    except ImportError:
        _print_timing("[COLD_START] Performance tracking not available")
    except (AttributeError, TypeError) as e:
        # Attribute or type error during tracking initialization
        _print_timing(f"[COLD_START] Tracking init error: {e}")
    except (ValueError, KeyError, RuntimeError, OSError) as e:
        # Other unexpected errors during tracking initialization
        _print_timing(f"[COLD_START] Tracking init failed: {e}")
else:
    _print_timing("[COLD_START] Performance tracking disabled via "
                 "ENABLE_PERFORMANCE_TRACKING")

if _LEE_DEBUG and _execute_operation and _GatewayInterface:
    try:
        _execute_operation(_GatewayInterface.DEBUG, 'log',
                         message="[PRELOAD] Lambda preload module ending, returning to lambda_function.py",
                         scope="PRELOAD")
    except (AttributeError, TypeError, RuntimeError):
        pass

# EOF
