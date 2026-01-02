"""
utility_response.py - Response Formatting (Internal)
Version: 2025.10.18.01 - RECURSION FIX
Description: Response formatting methods for success/error responses and Lambda responses

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

import json
import time
import os
from typing import Dict, Any, Optional
import logging as stdlib_logging

from utility_types import (
    SUCCESS_TEMPLATE,
    SUCCESS_WITH_CORRELATION,
    ERROR_TEMPLATE,
    ERROR_WITH_CODE,
    ERROR_WITH_CORRELATION,
    LAMBDA_RESPONSE,
    DEFAULT_HEADERS_JSON,
    DEFAULT_HEADERS_DICT,
    EMPTY_DATA,
    DEFAULT_USE_TEMPLATES
)

logger = stdlib_logging.getLogger(__name__)

# Runtime configuration
_USE_TEMPLATES = os.environ.get('USE_JSON_TEMPLATES', 'true').lower() == 'true'


# ===== HELPER FUNCTIONS =====

def _sanitize_for_json(obj: Any, max_depth: int = 10) -> Any:
    """
    Sanitize object for JSON serialization.
    Converts tuples to lists, removes non-JSON-serializable keys.
    """
    if max_depth <= 0:
        return str(obj)[:100]  # Prevent infinite recursion
    
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj
    
    if isinstance(obj, (list, tuple)):
        return [_sanitize_for_json(item, max_depth - 1) for item in obj]
    
    if isinstance(obj, dict):
        sanitized = {}
        for key, value in obj.items():
            # Convert tuple keys to strings
            if isinstance(key, tuple):
                key = str(key)
            # Only allow JSON-safe key types
            elif not isinstance(key, (str, int, float, bool)):
                key = str(key)
            
            sanitized[key] = _sanitize_for_json(value, max_depth - 1)
        return sanitized
    
    # For other types, convert to string
    return str(obj)


def _safe_json_dumps(obj: Any) -> str:
    """Safely convert object to JSON string."""
    try:
        # First attempt normal JSON serialization
        return json.dumps(obj)
    except (TypeError, ValueError) as e:
        # If that fails, sanitize and try again
        try:
            sanitized = _sanitize_for_json(obj)
            return json.dumps(sanitized)
        except Exception as inner_e:
            # Last resort: return string representation
            logger.error(f"JSON serialization failed even after sanitization: {inner_e}")
            return json.dumps({"error": "Serialization failed", "details": str(obj)[:200]})


# ===== RESPONSE FORMATTING =====

class ResponseFormatter:
    """Response formatting utilities for Lambda and API responses."""
    
    @staticmethod
    def format_response_fast(status_code: int, body: Any, 
                           headers: Optional[str] = None) -> Dict:
        """Fast Lambda response formatting using template."""
        try:
            # Use safe JSON dumps to handle problematic data
            body_json = body if isinstance(body, str) else _safe_json_dumps(body)
            headers_json = headers or DEFAULT_HEADERS_JSON
            
            json_str = LAMBDA_RESPONSE % (status_code, body_json, headers_json)
            return json.loads(json_str)
        except Exception as e:
            logger.error(f"Fast response formatting error: {str(e)}")
            # CRITICAL FIX: Use _format_response_fallback instead of recursing
            return ResponseFormatter._format_response_fallback(status_code, body)
    
    @staticmethod
    def _format_response_fallback(status_code: int, body: Any) -> Dict:
        """
        Fallback response formatter that NEVER calls format_response_fast.
        Breaks the recursion cycle.
        """
        try:
            # Sanitize body for JSON
            sanitized_body = _sanitize_for_json(body)
            
            return {
                "statusCode": status_code,
                "body": _safe_json_dumps(sanitized_body),
                "headers": DEFAULT_HEADERS_DICT
            }
        except Exception as e:
            logger.error(f"Fallback response formatting error: {str(e)}")
            # Absolute last resort - hardcoded safe response
            return {
                "statusCode": 500,
                "body": '{"error": "Response formatting failed completely"}',
                "headers": DEFAULT_HEADERS_DICT
            }
    
    @staticmethod
    def format_response(status_code: int, body: Any, headers: Optional[Dict] = None) -> Dict:
        """Format Lambda response (standard path)."""
        # Use fast path only if headers are default/None AND templates enabled
        if _USE_TEMPLATES and (headers is None or headers == DEFAULT_HEADERS_DICT):
            return ResponseFormatter.format_response_fast(status_code, body)
        
        try:
            # Sanitize body for JSON
            sanitized_body = _sanitize_for_json(body)
            
            return {
                "statusCode": status_code,
                "body": _safe_json_dumps(sanitized_body),
                "headers": headers or DEFAULT_HEADERS_DICT
            }
        except Exception as e:
            logger.error(f"Response formatting error: {str(e)}")
            # Use fallback instead of recursing
            return ResponseFormatter._format_response_fallback(status_code, body)
    
    @staticmethod
    def create_success_response(message: str, data: Any = None, 
                               correlation_id: Optional[str] = None) -> Dict[str, Any]:
        """Create success response with template optimization."""
        try:
            if _USE_TEMPLATES:
                timestamp = int(time.time())
                # Sanitize data before JSON conversion
                sanitized_data = _sanitize_for_json(data) if data is not None else None
                data_json = _safe_json_dumps(sanitized_data) if sanitized_data is not None else EMPTY_DATA
                
                if correlation_id:
                    json_str = SUCCESS_WITH_CORRELATION % (message, timestamp, data_json, correlation_id)
                else:
                    json_str = SUCCESS_TEMPLATE % (message, timestamp, data_json)
                
                return json.loads(json_str)
            
            # Standard path
            response = {
                "success": True,
                "message": message,
                "timestamp": int(time.time())
            }
            
            if data is not None:
                response["data"] = _sanitize_for_json(data)
            
            if correlation_id:
                response["correlation_id"] = correlation_id
            
            return response
            
        except Exception as e:
            logger.error(f"Success response creation error: {str(e)}")
            return {
                "success": True,
                "message": message,
                "timestamp": int(time.time())
            }
    
    @staticmethod
    def create_error_response(message: str, error_code: str = "UNKNOWN_ERROR",
                             details: Any = None, correlation_id: Optional[str] = None) -> Dict[str, Any]:
        """Create error response with template optimization."""
        try:
            if _USE_TEMPLATES:
                timestamp = int(time.time())
                # Sanitize details before JSON conversion
                sanitized_details = _sanitize_for_json(details) if details is not None else None
                details_json = _safe_json_dumps(sanitized_details) if sanitized_details is not None else EMPTY_DATA
                
                if correlation_id:
                    json_str = ERROR_WITH_CORRELATION % (message, error_code, timestamp, details_json, correlation_id)
                else:
                    json_str = ERROR_WITH_CODE % (message, error_code, timestamp, details_json)
                
                return json.loads(json_str)
            
            # Standard path
            response = {
                "success": False,
                "error": message,
                "error_code": error_code,
                "timestamp": int(time.time())
            }
            
            if details is not None:
                response["details"] = _sanitize_for_json(details)
            
            if correlation_id:
                response["correlation_id"] = correlation_id
            
            return response
            
        except Exception as e:
            logger.error(f"Error response creation error: {str(e)}")
            return {
                "success": False,
                "error": message,
                "error_code": error_code,
                "timestamp": int(time.time())
            }


# ===== SINGLETON INSTANCE =====

_RESPONSE_FORMATTER = ResponseFormatter()


# ===== PUBLIC FUNCTIONS =====

def format_response_fast(status_code: int, body: Any, 
                        headers: Optional[str] = None) -> Dict:
    """Fast Lambda response formatting using template."""
    return _RESPONSE_FORMATTER.format_response_fast(status_code, body, headers)


def format_response(status_code: int, body: Any, headers: Optional[Dict] = None) -> Dict:
    """Format Lambda response."""
    return _RESPONSE_FORMATTER.format_response(status_code, body, headers)


def create_success_response(message: str, data: Any = None, 
                           correlation_id: Optional[str] = None) -> Dict[str, Any]:
    """Create success response."""
    return _RESPONSE_FORMATTER.create_success_response(message, data, correlation_id)


def create_error_response(message: str, error_code: str = "UNKNOWN_ERROR",
                         details: Any = None, correlation_id: Optional[str] = None) -> Dict[str, Any]:
    """Create error response."""
    return _RESPONSE_FORMATTER.create_error_response(message, error_code, details, correlation_id)


# ===== MODULE EXPORTS =====

__all__ = [
    'ResponseFormatter',
    'format_response_fast',
    'format_response',
    'create_success_response',
    'create_error_response',
]

# EOF
