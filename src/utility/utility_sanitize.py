"""
utility/utility_sanitize.py
Version: 2025-12-13_1
Purpose: Sanitization operations for utility interface
License: Apache 2.0
"""

import traceback
from typing import Dict, Any
import logging as stdlib_logging

logger = stdlib_logging.getLogger(__name__)


class UtilitySanitizeOperations:
    """Sanitization operations for data cleaning and error extraction."""
    
    def __init__(self, manager):
        """Initialize with reference to SharedUtilityCore manager."""
        self._manager = manager
    
    def sanitize_data(self, data: Dict[str, Any], correlation_id: str = None) -> Dict[str, Any]:
        """Sanitize response data by removing sensitive fields."""
        from gateway import debug_log, generate_correlation_id
        
        if correlation_id is None:
            correlation_id = generate_correlation_id()
        
        sensitive_keys = ['password', 'secret', 'token', 'api_key', 'private_key']
        
        if not isinstance(data, dict):
            debug_log(correlation_id, "UTILITY", "Sanitize skipped: not a dict",
                     data_type=type(data).__name__)
            return data
        
        sanitized = {}
        redacted_count = 0
        
        for key, value in data.items():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                sanitized[key] = "***REDACTED***"
                redacted_count += 1
            elif isinstance(value, dict):
                sanitized[key] = self.sanitize_data(value, correlation_id)
            else:
                sanitized[key] = value
        
        debug_log(correlation_id, "UTILITY", "Data sanitized",
                 redacted_count=redacted_count, total_keys=len(data))
        
        return sanitized
    
    def safe_string_conversion(self, data: Any, max_length: int = 10000,
                              correlation_id: str = None) -> str:
        """Safely convert data to string with length limits."""
        from gateway import debug_log, generate_correlation_id
        
        if correlation_id is None:
            correlation_id = generate_correlation_id()
        
        try:
            result = str(data)
            if len(result) > max_length:
                truncated = result[:max_length] + "... [TRUNCATED]"
                debug_log(correlation_id, "UTILITY", "String conversion truncated",
                         original_length=len(result), max_length=max_length)
                return truncated
            
            debug_log(correlation_id, "UTILITY", "String conversion successful",
                     result_length=len(result))
            return result
        except Exception as e:
            debug_log(correlation_id, "UTILITY", "String conversion failed", error=str(e))
            return "[conversion_error]"
    
    def extract_error_details(self, error: Exception, correlation_id: str = None) -> Dict[str, Any]:
        """Extract detailed error information with stack trace."""
        from gateway import debug_log, generate_correlation_id
        
        if correlation_id is None:
            correlation_id = generate_correlation_id()
        
        try:
            details = {
                "type": type(error).__name__,
                "message": str(error),
                "args": error.args if hasattr(error, 'args') else [],
                "traceback": traceback.format_exc()
            }
            
            debug_log(correlation_id, "UTILITY", "Error details extracted",
                     error_type=details["type"])
            
            return details
        except Exception as e:
            debug_log(correlation_id, "UTILITY", "Error detail extraction failed",
                     error=str(e))
            return {
                "type": "UnknownError", 
                "message": "Failed to extract error details",
                "traceback": None
            }


__all__ = [
    'UtilitySanitizeOperations',
]
