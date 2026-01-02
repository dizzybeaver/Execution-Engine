"""
utility_types.py - Utility Types and Constants (Internal)
Version: 2025.10.16.04
Description: Core types, enums, and constants for utility interface

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from enum import Enum
from dataclasses import dataclass

# ===== CONFIGURATION =====

# These can be overridden via environment variables
DEFAULT_USE_TEMPLATES = True
DEFAULT_USE_GENERIC_OPERATIONS = True
DEFAULT_MAX_JSON_CACHE_SIZE = 100

# ===== JSON RESPONSE TEMPLATES =====

SUCCESS_TEMPLATE = '{"success":true,"message":"%s","timestamp":%d,"data":%s}'
SUCCESS_WITH_CORRELATION = '{"success":true,"message":"%s","timestamp":%d,"data":%s,"correlation_id":"%s"}'
ERROR_TEMPLATE = '{"success":false,"error":"%s","timestamp":%d}'
ERROR_WITH_CODE = '{"success":false,"error":"%s","error_code":"%s","timestamp":%d,"details":%s}'
ERROR_WITH_CORRELATION = '{"success":false,"error":"%s","error_code":"%s","timestamp":%d,"details":%s,"correlation_id":"%s"}'
LAMBDA_RESPONSE = '{"statusCode":%d,"body":%s,"headers":%s}'
DEFAULT_HEADERS_JSON = '{"Content-Type":"application/json","Access-Control-Allow-Origin":"*"}'
EMPTY_DATA = '{}'

DEFAULT_HEADERS_DICT = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*"
}

# ===== UTILITY OPERATION ENUM =====

class UtilityOperation(Enum):
    """Enumeration of all utility operations."""
    
    # UUID and Timestamp
    GENERATE_UUID = "generate_uuid"
    GET_TIMESTAMP = "get_timestamp"
    GENERATE_CORRELATION_ID = "generate_correlation_id"
    
    # Response Formatting
    FORMAT_RESPONSE = "format_response"
    FORMAT_RESPONSE_FAST = "format_response_fast"
    CREATE_SUCCESS_RESPONSE = "create_success_response"
    CREATE_ERROR_RESPONSE = "create_error_response"
    
    # Data Operations
    PARSE_JSON = "parse_json"
    PARSE_JSON_SAFELY = "parse_json_safely"
    DEEP_MERGE = "deep_merge"
    SAFE_GET = "safe_get"
    FORMAT_BYTES = "format_bytes"
    
    # Validation
    VALIDATE_STRING = "validate_string"
    VALIDATE_DATA_STRUCTURE = "validate_data_structure"
    VALIDATE_OPERATION_PARAMETERS = "validate_operation_parameters"
    
    # Sanitization
    SANITIZE_DATA = "sanitize_data"
    SANITIZE_RESPONSE_DATA = "sanitize_response_data"
    SAFE_STRING_CONVERSION = "safe_string_conversion"
    
    # Utilities
    MERGE_DICTIONARIES = "merge_dictionaries"
    EXTRACT_ERROR_DETAILS = "extract_error_details"
    FORMAT_DATA_FOR_RESPONSE = "format_data_for_response"
    
    # Performance
    CLEANUP_CACHE = "cleanup_cache"
    GET_PERFORMANCE_STATS = "get_performance_stats"
    OPTIMIZE_PERFORMANCE = "optimize_performance"
    CONFIGURE_CACHING = "configure_caching"


# ===== METRICS TRACKING =====

@dataclass
class UtilityMetrics:
    """Metrics for utility operations."""
    operation_type: str
    call_count: int = 0
    total_duration_ms: float = 0.0
    avg_duration_ms: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    error_count: int = 0
    template_usage: int = 0


# ===== MODULE EXPORTS =====

__all__ = [
    # Configuration
    'DEFAULT_USE_TEMPLATES',
    'DEFAULT_USE_GENERIC_OPERATIONS',
    'DEFAULT_MAX_JSON_CACHE_SIZE',
    
    # Templates
    'SUCCESS_TEMPLATE',
    'SUCCESS_WITH_CORRELATION',
    'ERROR_TEMPLATE',
    'ERROR_WITH_CODE',
    'ERROR_WITH_CORRELATION',
    'LAMBDA_RESPONSE',
    'DEFAULT_HEADERS_JSON',
    'DEFAULT_HEADERS_DICT',
    'EMPTY_DATA',
    
    # Types
    'UtilityOperation',
    'UtilityMetrics',
]

# EOF
