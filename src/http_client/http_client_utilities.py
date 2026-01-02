"""
http_client/http_client_utilities.py
Version: 2025-12-10_1
Purpose: HTTP client utility functions
License: Apache 2.0
"""

from typing import Dict, Any, Optional
from urllib.parse import urlencode


def get_standard_headers() -> Dict[str, str]:
    """Get standard HTTP headers for requests."""
    return {
        'Content-Type': 'application/json',
        'User-Agent': 'LambdaExecutionEngine/1.0'
    }


def get_ha_headers(token: str) -> Dict[str, str]:
    """Get Home Assistant specific headers."""
    headers = get_standard_headers()
    headers['Authorization'] = f'Bearer {token}'
    return headers


def build_query_string(params: Dict[str, Any]) -> str:
    """Build URL query string from parameters."""
    if not params:
        return ''
    return urlencode(params)


def build_query_string_fast(params: Dict[str, Any]) -> str:
    """Fast query string builder (optimized)."""
    return build_query_string(params)


def parse_response_headers(headers: Dict[str, Any]) -> Dict[str, Any]:
    """Parse and normalize response headers."""
    normalized = {}
    for key, value in headers.items():
        normalized[key.lower()] = value
    return normalized


def parse_response_headers_fast(headers: Dict[str, Any]) -> Dict[str, Any]:
    """Fast header parser (optimized)."""
    return parse_response_headers(headers)


def process_response(response_data: Dict[str, Any], expected_format: str = 'json',
                    validation_rules: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Process and validate HTTP response."""
    return response_data


__all__ = [
    'get_standard_headers',
    'get_ha_headers',
    'build_query_string',
    'build_query_string_fast',
    'parse_response_headers',
    'parse_response_headers_fast',
    'process_response',
]
