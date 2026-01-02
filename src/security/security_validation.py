"""
security_validation.py - Security Validation Functions
Version: 2025.10.22.01
Description: COMPLETE FILE - All validators including SecurityValidator class

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

import re
import math
from typing import Dict, Any


# ===== SECURITY VALIDATOR CLASS =====

class SecurityValidator:
    """Core security validator for requests, tokens, strings, emails, URLs."""
    
    def __init__(self):
        self._stats = {
            'validations_performed': 0,
            'validations_passed': 0,
            'validations_failed': 0
        }
    
    def validate_request(self, request: Dict[str, Any]) -> bool:
        """Validate HTTP request structure and content."""
        self._stats['validations_performed'] += 1
        
        try:
            if not isinstance(request, dict):
                self._stats['validations_failed'] += 1
                return False
            
            # Basic request validation
            if 'method' in request and not isinstance(request['method'], str):
                self._stats['validations_failed'] += 1
                return False
            
            if 'headers' in request and not isinstance(request['headers'], dict):
                self._stats['validations_failed'] += 1
                return False
            
            self._stats['validations_passed'] += 1
            return True
            
        except Exception:
            self._stats['validations_failed'] += 1
            return False
    
    def validate_token(self, token: str) -> bool:
        """Validate authentication token format."""
        self._stats['validations_performed'] += 1
        
        try:
            if not isinstance(token, str):
                self._stats['validations_failed'] += 1
                return False
            
            if not token or not token.strip():
                self._stats['validations_failed'] += 1
                return False
            
            if len(token) < 10:
                self._stats['validations_failed'] += 1
                return False
            
            self._stats['validations_passed'] += 1
            return True
            
        except Exception:
            self._stats['validations_failed'] += 1
            return False
    
    def validate_string(self, value: str, min_length: int = 0, max_length: int = 1000) -> bool:
        """Validate string length and content."""
        self._stats['validations_performed'] += 1
        
        try:
            if not isinstance(value, str):
                self._stats['validations_failed'] += 1
                return False
            
            if len(value) < min_length:
                self._stats['validations_failed'] += 1
                return False
            
            if len(value) > max_length:
                self._stats['validations_failed'] += 1
                return False
            
            self._stats['validations_passed'] += 1
            return True
            
        except Exception:
            self._stats['validations_failed'] += 1
            return False
    
    def validate_email(self, email: str) -> bool:
        """Validate email address format."""
        self._stats['validations_performed'] += 1
        
        try:
            if not isinstance(email, str):
                self._stats['validations_failed'] += 1
                return False
            
            # Basic email pattern
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                self._stats['validations_failed'] += 1
                return False
            
            self._stats['validations_passed'] += 1
            return True
            
        except Exception:
            self._stats['validations_failed'] += 1
            return False
    
    def validate_url(self, url: str) -> bool:
        """Validate URL format."""
        self._stats['validations_performed'] += 1
        
        try:
            if not isinstance(url, str):
                self._stats['validations_failed'] += 1
                return False
            
            if not url.startswith(('http://', 'https://')):
                self._stats['validations_failed'] += 1
                return False
            
            self._stats['validations_passed'] += 1
            return True
            
        except Exception:
            self._stats['validations_failed'] += 1
            return False
    
    def sanitize_input(self, data: Any) -> Any:
        """Sanitize input data for safe processing."""
        if isinstance(data, str):
            # Remove control characters
            return ''.join(char for char in data if ord(char) >= 32 or char in '\n\r\t')
        elif isinstance(data, dict):
            return {k: self.sanitize_input(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.sanitize_input(item) for item in data]
        else:
            return data
    
    def get_stats(self) -> Dict[str, int]:
        """Get validation statistics."""
        return self._stats.copy()


# ===== METRICS SECURITY VALIDATIONS =====

def validate_metric_name(name: str) -> None:
    """
    Validate metric name for security and sanity.
    
    Security Rules:
    - Length: 1-200 characters
    - Characters: [a-zA-Z0-9_.-] only
    - No path separators (/, \\)
    - No control characters
    - No leading/trailing whitespace
    - Cannot start/end with . or -
    
    Args:
        name: Metric name to validate
        
    Raises:
        ValueError: If name is invalid with specific reason
    """
    # Check empty/whitespace
    if not name or not name.strip():
        raise ValueError("Metric name cannot be empty or whitespace")
    
    # Auto-strip for safety
    name = name.strip()
    
    # Check length
    if len(name) > 200:
        raise ValueError(
            f"Metric name too long: {len(name)} characters (max: 200). "
            f"This may be a memory exhaustion attack."
        )
    
    if len(name) < 1:
        raise ValueError("Metric name must be at least 1 character")
    
    # Check character set
    if not re.match(r'^[a-zA-Z0-9_.\-]+$', name):
        raise ValueError(
            f"Metric name contains invalid characters: '{name}'. "
            f"Allowed characters: [a-zA-Z0-9_.-]"
        )
    
    # Check for path separators
    if '/' in name or '\\' in name:
        raise ValueError(
            f"Metric name cannot contain path separators: '{name}'. "
            f"This may be a path traversal attack."
        )
    
    # Check for leading/trailing special chars
    if name.startswith(('.', '-')) or name.endswith(('.', '-')):
        raise ValueError(
            f"Metric name cannot start or end with '.' or '-': '{name}'"
        )


def validate_dimension_value(value: str) -> None:
    """
    Validate metric dimension value for security.
    
    Security Rules:
    - Length: 1-100 characters
    - No control characters
    - No path separators
    - Must be printable
    
    Args:
        value: Dimension value to validate (will be converted to string)
        
    Raises:
        ValueError: If value is invalid with specific reason
    """
    # Convert to string if not already
    value = str(value)
    
    # Check empty/whitespace
    if not value or not value.strip():
        raise ValueError("Dimension value cannot be empty or whitespace")
    
    # Auto-strip for safety
    value = value.strip()
    
    # Check length
    if len(value) > 100:
        raise ValueError(
            f"Dimension value too long: {len(value)} characters (max: 100). "
            f"This may be a memory exhaustion attack."
        )
    
    # Check for control characters
    if not value.isprintable():
        raise ValueError(
            f"Dimension value contains non-printable characters. "
            f"This may be a control character injection attack."
        )
    
    # Check for path separators
    if '/' in value or '\\' in value:
        raise ValueError(
            f"Dimension value cannot contain path separators: '{value}'. "
            f"This may be a path traversal attack."
        )


def validate_metric_value(value: float, allow_negative: bool = True) -> None:
    """
    Validate metric numeric value is valid.
    
    Validates that metric values are valid floats:
    - Rejects: NaN (Not a Number)
    - Rejects: Infinity (positive or negative)
    - Optionally rejects: Negative values
    
    Args:
        value: Numeric value to validate
        allow_negative: Whether negative values are allowed (default: True)
        
    Raises:
        ValueError: If value is invalid with specific reason
    """
    # Check for NaN
    if math.isnan(value):
        raise ValueError(
            f"Metric value cannot be NaN (Not a Number). "
            f"This indicates a calculation error or invalid input."
        )
    
    # Check for infinity
    if math.isinf(value):
        raise ValueError(
            f"Metric value cannot be infinity. "
            f"Value: {value}. This may cause overflow or calculation errors."
        )
    
    # Check for negative (if not allowed)
    if not allow_negative and value < 0:
        raise ValueError(
            f"Metric value cannot be negative: {value}. "
            f"This is likely an error (e.g., negative duration)."
        )


# ===== EXPORTS =====

__all__ = [
    'SecurityValidator',
    'validate_metric_name',
    'validate_dimension_value',
    'validate_metric_value',
]

# EOF
