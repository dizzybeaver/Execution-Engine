"""
utility/utility_validation.py
Version: 2025-12-13_1
Purpose: Validation operations for utility interface
License: Apache 2.0
"""

from typing import Dict, Any, Optional, List
import logging as stdlib_logging

logger = stdlib_logging.getLogger(__name__)


class UtilityValidationOperations:
    """Validation operations for strings, data structures, and parameters."""
    
    def __init__(self, manager):
        """Initialize with reference to SharedUtilityCore manager."""
        self._manager = manager
    
    def validate_string(self, value: str, min_length: int = 0, max_length: int = 1000,
                       correlation_id: str = None) -> Dict[str, Any]:
        """Validate string input."""
        from gateway import debug_log, generate_correlation_id
        
        if correlation_id is None:
            correlation_id = generate_correlation_id()
        
        if not isinstance(value, str):
            debug_log(correlation_id, "UTILITY", "String validation failed: not a string",
                     value_type=type(value).__name__)
            return {"valid": False, "error": "Value must be a string"}
        
        if len(value) < min_length:
            debug_log(correlation_id, "UTILITY", "String validation failed: too short",
                     length=len(value), min_length=min_length)
            return {"valid": False, "error": f"String too short (min: {min_length})"}
        
        if len(value) > max_length:
            debug_log(correlation_id, "UTILITY", "String validation failed: too long",
                     length=len(value), max_length=max_length)
            return {"valid": False, "error": f"String too long (max: {max_length})"}
        
        debug_log(correlation_id, "UTILITY", "String validation passed",
                 length=len(value))
        return {"valid": True}
    
    def validate_data_structure(self, data: Any, expected_type: type,
                               required_fields: Optional[List[str]] = None,
                               correlation_id: str = None) -> bool:
        """Validate data structure."""
        from gateway import debug_log, generate_correlation_id
        
        if correlation_id is None:
            correlation_id = generate_correlation_id()
        
        if not isinstance(data, expected_type):
            debug_log(correlation_id, "UTILITY", "Data structure validation failed: wrong type",
                     expected_type=expected_type.__name__, actual_type=type(data).__name__)
            return False
        
        if required_fields and isinstance(data, dict):
            for field in required_fields:
                if field not in data:
                    debug_log(correlation_id, "UTILITY", "Data structure validation failed: missing field",
                             field=field)
                    return False
        
        debug_log(correlation_id, "UTILITY", "Data structure validation passed",
                 expected_type=expected_type.__name__)
        return True
    
    def validate_operation_parameters(self, required_params: List[str], 
                                     optional_params: Optional[List[str]] = None,
                                     correlation_id: str = None,
                                     **kwargs) -> Dict[str, Any]:
        """Generic parameter validation for any interface operation."""
        from gateway import debug_log, generate_correlation_id
        
        if correlation_id is None:
            correlation_id = generate_correlation_id()
        
        missing = [param for param in required_params if param not in kwargs]
        
        if missing:
            debug_log(correlation_id, "UTILITY", "Parameter validation failed: missing params",
                     missing_params=missing)
            return {
                "valid": False,
                "missing_params": missing,
                "error": f"Missing required parameters: {', '.join(missing)}"
            }
        
        if optional_params:
            all_params = set(required_params + optional_params)
            unexpected = [k for k in kwargs.keys() if k not in all_params]
            
            if unexpected:
                debug_log(correlation_id, "UTILITY", "Parameter validation passed with warnings",
                         unexpected_params=unexpected)
                return {
                    "valid": True,
                    "warning": f"Unexpected parameters: {', '.join(unexpected)}"
                }
        
        debug_log(correlation_id, "UTILITY", "Parameter validation passed",
                 required_count=len(required_params))
        return {"valid": True}


__all__ = [
    'UtilityValidationOperations',
]
