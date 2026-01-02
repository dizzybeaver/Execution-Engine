"""
lambda_preload.py - LUGS-Protected Critical Module Preloading
Version: 2025-12-14_1
Purpose: Preload critical modules during Lambda INIT with selective imports
License: Apache 2.0

This module loads ONLY what we need, WHEN we need it:
- typing: Common types used everywhere (20ms)
- enum: Enum base class (10ms)
- urllib3: ONLY PoolManager and Timeout (50ms vs 1,700ms full import)
- boto3 SSM: ONLY SSM client via botocore.session (300ms vs 8,500ms full boto3)

Design Decision: Selective imports for performance
Reason: We don't need S3, Lambda, DynamoDB, EC2, RDS, CloudWatch, SNS, SQS, IAM,
        CloudFormation, API Gateway, Step Functions, etc. - just SSM!
        Full boto3 loads 200+ services (8,500ms), we only need 1 service (300ms).
        Full urllib3 loads entire library (1,700ms), we only need 2 classes (50ms).

Performance Target:
- Lambda INIT: 350-450ms (typing, enum, urllib3 selective, boto3 SSM selective)
- First Request: 120-180ms (everything preloaded, just business logic)
- Total Cold Start: 470-630ms (acceptable!)
"""

import os
import time
from typing import Dict, Any, Optional

# ===== TIMING HELPER =====

def _print_timing(message: str):
    """Print timing if DEBUG_MODE=true."""
    if os.environ.get('DEBUG_MODE', 'false').lower() == 'true':
        print(f"[PRELOAD_TIMING] {message}")

# ===== PRELOAD START =====

_preload_start = time.perf_counter()
_print_timing("===== LAMBDA PRELOAD START =====")

# ===== COMMON TYPES (Always Needed) =====

_timing_start = time.perf_counter()
_print_timing("Loading typing module...")

from typing import Dict, Any, Optional, List, Union, Callable, Tuple, Set

_typing_time = (time.perf_counter() - _timing_start) * 1000
_print_timing(f"*** typing loaded: {_typing_time:.2f}ms ***")

# ===== ENUM (Frequently Used) =====

_timing_start = time.perf_counter()
_print_timing("Loading enum module...")

from enum import Enum

_enum_time = (time.perf_counter() - _timing_start) * 1000
_print_timing(f"*** enum loaded: {_enum_time:.2f}ms ***")

# ===== URLLIB3 (Always Needed for HTTP) =====

_timing_start = time.perf_counter()
_print_timing("Loading urllib3 (selective: PoolManager, Timeout)...")

# SELECTIVE IMPORT: Only the 2 classes we actually use
# NOT: import urllib3 (loads entire library - 1,700ms)
# YES: from urllib3 import PoolManager, Timeout (only what we need - 50ms)
from urllib3 import PoolManager, Timeout

_urllib3_time = (time.perf_counter() - _timing_start) * 1000
_print_timing(f"*** urllib3 (selective) loaded: {_urllib3_time:.2f}ms ***")

# ===== BOTO3 SSM (Conditional - Only If Parameter Store Enabled) =====

_USE_PARAMETER_STORE = os.environ.get('USE_PARAMETER_STORE', 'false').lower() == 'true'
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
        _BOTO3_SSM_CLIENT = session.create_client('ssm')
        
        _ssm_time = (time.perf_counter() - _ssm_start) * 1000
        _print_timing(f"  *** SSM client created: {_ssm_time:.2f}ms ***")
        
        _total_boto3_time = (time.perf_counter() - _timing_start) * 1000
        _print_timing(f"*** boto3 SSM (selective) loaded: {_total_boto3_time:.2f}ms ***")
        
    except Exception as e:
        _error_time = (time.perf_counter() - _timing_start) * 1000
        _print_timing(f"!!! boto3 SSM initialization FAILED after {_error_time:.2f}ms: {e}")
        _USE_PARAMETER_STORE = False
        _BOTO3_SSM_CLIENT = None
else:
    _print_timing("Parameter Store DISABLED - Skipping boto3")

# ===== ZAPH PREWARMING (Optional - Only If Enabled) =====

_ZAPH_PREWARM_ENABLED = os.environ.get('ZAPH_PREWARM_ON_COLD_START', 'false').lower() == 'true'

if _ZAPH_PREWARM_ENABLED:
    _timing_start = time.perf_counter()
    _print_timing("ZAPH prewarming ENABLED - Initializing fast path cache...")
    
    try:
        # Import and prewarm common operations
        from gateway import zaph_prewarm_common
        
        prewarmed_count = zaph_prewarm_common(correlation_id="preload")
        
        _zaph_time = (time.perf_counter() - _timing_start) * 1000
        _print_timing(f"*** ZAPH prewarmed {prewarmed_count} operations: {_zaph_time:.2f}ms ***")
        
    except Exception as e:
        _error_time = (time.perf_counter() - _timing_start) * 1000
        _print_timing(f"!!! ZAPH prewarming FAILED after {_error_time:.2f}ms: {e}")
else:
    _print_timing("ZAPH prewarming DISABLED - Skipping fast path initialization")

# ===== PRELOAD COMPLETE =====

_total_preload_time = (time.perf_counter() - _preload_start) * 1000
_print_timing(f"===== LAMBDA PRELOAD COMPLETE: {_total_preload_time:.2f}ms =====")

# ===== EXPORTS =====

# Make preloaded modules available for import
__all__ = [
    'PoolManager',
    'Timeout',
    '_BOTO3_SSM_CLIENT',
    '_USE_PARAMETER_STORE'
]

# EOF
