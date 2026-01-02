"""
Serialization Factory - Operations Domain

Data serialization implementation (JSON, pickle).

UG-ISP Compliant:
- Factory contains actual implementation
- Receives logger, metrics, call_operation via DI
- NO imports outside operations domain (except stdlib)
- All cross-domain calls via call_operation callback
"""

import json
import pickle
import logging
from typing import Any, Dict, Optional, Callable


class SerializationFactory:
    """Serialization operations factory.

    Provides data serialization for JSON and pickle formats.

    UG-ISP Compliance:
    - Factory contains actual implementation
    - Cross-domain calls via call_operation callback
    """

    def __init__(
        self,
        logger: Optional[Any] = None,
        metrics: Optional[Any] = None,
        call_operation: Optional[Callable] = None
    ):
        """Initialize serialization factory.

        Args:
            logger: Logger instance
            metrics: Metrics instance
            call_operation: Callback for cross-domain operations
        """
        self.logger = logger or logging.getLogger(__name__)
        self.metrics = metrics
        self.call_operation = call_operation

    def to_json(self, obj: Any, indent: int = 2, **kwargs) -> Optional[str]:
        """Serialize object to JSON string.

        Args:
            obj: Object to serialize
            indent: JSON indentation
            **kwargs: Additional parameters

        Returns:
            JSON string or None if error
        """
        try:
            return json.dumps(obj, indent=indent, default=str)
        except Exception as e:
            self.logger.error(f"Error serializing to JSON: {e}")
            return None

    def from_json(self, json_str: str, **kwargs) -> Optional[Any]:
        """Deserialize JSON string to object.

        Args:
            json_str: JSON string to deserialize
            **kwargs: Additional parameters

        Returns:
            Deserialized object or None if error
        """
        try:
            return json.loads(json_str)
        except Exception as e:
            self.logger.error(f"Error deserializing from JSON: {e}")
            return None

    def to_pickle(self, obj: Any, **kwargs) -> Optional[bytes]:
        """Serialize object to pickle bytes.

        Args:
            obj: Object to serialize
            **kwargs: Additional parameters

        Returns:
            Pickle bytes or None if error
        """
        try:
            return pickle.dumps(obj)
        except Exception as e:
            self.logger.error(f"Error serializing to pickle: {e}")
            return None

    def from_pickle(self, pickle_bytes: bytes, **kwargs) -> Optional[Any]:
        """Deserialize pickle bytes to object.

        Args:
            pickle_bytes: Pickle bytes to deserialize
            **kwargs: Additional parameters

        Returns:
            Deserialized object or None if error
        """
        try:
            return pickle.loads(pickle_bytes)
        except Exception as e:
            self.logger.error(f"Error deserializing from pickle: {e}")
            return None


__all__ = [
    "SerializationFactory",
]
