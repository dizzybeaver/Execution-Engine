# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-03-23 - Error response factory to eliminate duplication

"""Error Response Factory for Home Assistant

Provides standardized error response creation to eliminate code duplication
across HA device implementations (1,215-1,620 line savings potential).
"""

from typing import Any


def missing_parameter(param_name: str) -> dict[str, Any]:
    """Create a missing parameter error response.

    Args:
        param_name: Name of the missing parameter

    Returns:
        Error response dictionary

    Example:
        >>> missing_parameter("entity_id")
        {'success': False, 'error_code': 'MISSING_PARAMETER', 'error_message': 'entity_id is required'}
    """
    return {
        "success": False,
        "error_code": "MISSING_PARAMETER",
        "error_message": f"{param_name} is required"
    }


def create_error_response(
    error_code: str,
    error_message: str
) -> dict[str, Any]:
    """Create a standardized error response.

    Args:
        error_code: Error code (e.g., 'MISSING_PARAMETER', 'INVALID_VALUE')
        error_message: Human-readable error message

    Returns:
        Error response dictionary

    Example:
        >>> create_error_response("INVALID_VALUE", "brightness must be between 0 and 255")
        {'success': False, 'error_code': 'INVALID_VALUE', 'error_message': 'brightness must be between 0 and 255'}
    """
    return {
        "success": False,
        "error_code": error_code,
        "error_message": error_message
    }
