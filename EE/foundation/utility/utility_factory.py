"""
Utility Factory - Foundation Domain

Helper functions implementation: JSON, UUID, validation.

UG-ISP Compliant:
- Factory contains actual implementation
- Receives logger, metrics, call_operation via DI
- Only uses stdlib imports
"""

import json
import uuid
import re
import logging
from typing import Any, Dict, Optional, Callable


class UtilityFactory:
    """Utility functions factory.

    Provides helper functions for:
    - JSON serialization/deserialization
    - UUID generation
    - Input validation
    - Input sanitization

    UG-ISP Compliance:
    - Only uses stdlib
    - Cross-domain calls via call_operation callback
    """

    def __init__(
        self,
        logger: Optional[Any] = None,
        metrics: Optional[Any] = None,
        call_operation: Optional[Callable] = None
    ):
        """Initialize utility factory.

        Args:
            logger: Logger instance
            metrics: Metrics instance
            call_operation: Callback for cross-domain operations
        """
        self.logger = logger or logging.getLogger(__name__)
        self.metrics = metrics
        self.call_operation = call_operation

    def json_to_string(self, data: Any, indent: int = 2, **kwargs) -> str:
        """Serialize data to JSON string.

        Args:
            data: Data to serialize
            indent: Indentation level
            **kwargs: Additional parameters

        Returns:
            JSON string

        Raises:
            TypeError: If data is not serializable
        """
        try:
            return json.dumps(data, indent=indent, default=str)
        except TypeError as e:
            self.logger.error(f"JSON serialization failed: {e}")
            raise

    def json_from_string(self, json_string: str, **kwargs) -> Any:
        """Deserialize JSON string to data.

        Args:
            json_string: JSON string to deserialize
            **kwargs: Additional parameters

        Returns:
            Deserialized data

        Raises:
            json.JSONDecodeError: If string is not valid JSON
        """
        try:
            return json.loads(json_string)
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON deserialization failed: {e}")
            raise

    def generate_uuid(self, version: int = 4, **kwargs) -> str:
        """Generate UUID.

        Args:
            version: UUID version (4 for random)
            **kwargs: Additional parameters

        Returns:
            UUID string
        """
        if version == 4:
            return str(uuid.uuid4())
        else:
            return str(uuid.uuid4())

    def validate_string(
        self,
        value: str,
        min_length: int = 0,
        max_length: int = 1000,
        pattern: Optional[str] = None,
        **kwargs
    ) -> bool:
        """Validate string input.

        Args:
            value: String to validate
            min_length: Minimum length
            max_length: Maximum length
            pattern: Optional regex pattern
            **kwargs: Additional parameters

        Returns:
            True if valid
        """
        if not isinstance(value, str):
            return False

        if len(value) < min_length or len(value) > max_length:
            return False

        if pattern and not re.match(pattern, value):
            return False

        return True

    def validate_dict(
        self,
        value: Any,
        required_keys: Optional[list] = None,
        **kwargs
    ) -> bool:
        """Validate dict input.

        Args:
            value: Value to validate
            required_keys: List of required keys
            **kwargs: Additional parameters

        Returns:
            True if valid
        """
        if not isinstance(value, dict):
            return False

        if required_keys:
            if not all(key in value for key in required_keys):
                return False

        return True

    def sanitize_input(self, value: str, **kwargs) -> str:
        """Sanitize string input.

        Args:
            value: String to sanitize
            **kwargs: Additional parameters

        Returns:
            Sanitized string
        """
        # Remove null bytes
        value = value.replace("\x00", "")

        # Strip whitespace
        value = value.strip()

        return value


__all__ = [
    "UtilityFactory",
]
