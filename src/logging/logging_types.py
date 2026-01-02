"""
logging/logging_types.py
Version: 2025-12-08_1
Purpose: Logging type definitions and enumerations
License: Apache 2.0

CHANGES (2025-12-08_1):
- Moved to logging/ subdirectory
- Updated header to logging/ path
"""

from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional


# ===== LOGGING OPERATION ENUM =====

class LogOperation(Enum):
    """Enumeration of all logging operations."""
    LOG_INFO = "log_info"
    LOG_ERROR = "log_error"
    LOG_WARNING = "log_warning"
    LOG_DEBUG = "log_debug"
    LOG_OPERATION_START = "log_operation_start"
    LOG_OPERATION_SUCCESS = "log_operation_success"
    LOG_OPERATION_FAILURE = "log_operation_failure"
    LOG_WITH_TEMPLATE = "log_with_template"
    LOG_TEMPLATE_FAST = "log_template_fast"
    GET_ERROR_ENTRIES = "get_error_entries"
    GET_STATS = "get_stats"
    CLEAR_ERROR_ENTRIES = "clear_error_entries"
    LOG_ERROR_RESPONSE = "log_error_response"
    GET_ERROR_ANALYTICS = "get_error_analytics"
    CLEAR_ERROR_LOGS = "clear_error_logs"


class LogTemplate(Enum):
    """Pre-formatted log templates for optimal performance."""
    OPERATION_START = "[OP_START]"
    OPERATION_SUCCESS = "[OP_SUCCESS]"
    OPERATION_FAILURE = "[OP_FAIL]"
    CACHE_HIT = "[CACHE_HIT]"
    CACHE_MISS = "[CACHE_MISS]"


class ErrorLogLevel(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ===== ERROR ENTRY DATACLASSES =====

@dataclass
class ErrorEntry:
    """Simple error entry with metadata - used by logging_manager.py"""
    timestamp: datetime
    error_type: str
    message: str
    level: ErrorLogLevel
    details: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


@dataclass
class ErrorLogEntry:
    """Structured error response log entry - used by error response logging."""
    id: str
    timestamp: float
    datetime: datetime
    correlation_id: str
    source_module: Optional[str]
    error_type: str
    severity: ErrorLogLevel
    status_code: int
    error_response: Dict[str, Any]
    lambda_context_info: Optional[Dict[str, Any]]
    additional_context: Optional[Dict[str, Any]]
    
    @staticmethod
    def determine_severity(error_response: Dict[str, Any]) -> ErrorLogLevel:
        """Determine severity from error response."""
        error_code = error_response.get('error', {}).get('code', '')
        
        if 'critical' in error_code.lower() or 'fatal' in error_code.lower():
            return ErrorLogLevel.CRITICAL
        elif 'error' in error_code.lower():
            return ErrorLogLevel.HIGH
        elif 'warning' in error_code.lower():
            return ErrorLogLevel.MEDIUM
        else:
            return ErrorLogLevel.LOW


__all__ = [
    'LogOperation',
    'LogTemplate',
    'ErrorLogLevel',
    'ErrorEntry',
    'ErrorLogEntry',
]
