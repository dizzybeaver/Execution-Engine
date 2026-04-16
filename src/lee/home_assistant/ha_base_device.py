# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-04 - Create base device class for HA modules

"""ha_base_device.py

Base class for Home Assistant device module implementations.

Provides common functionality for all HA device modules:
- URL and token resolution from multiple sources
- Configuration validation
- Standard error handling
- HTTP client management
- Input sanitization

Reduces code duplication across 30+ HA device modules.
"""

from abc import ABC
from typing import Any, Optional

from lee.gateway import GatewayInterface, execute_operation


class HABaseDevice(ABC):
    """Base class for Home Assistant device modules.

    Provides common functionality for device operations including
    configuration resolution, validation, and standard error handling.
    """

    @staticmethod
    def resolve_ha_config(oauth_token: Optional[str] = None, **kwargs) -> tuple[Optional[str], Optional[str], Optional[dict[str, Any]]]:
        """Resolve Home Assistant URL and token from multiple sources.

        Priority order:
        1. oauth_token parameter
        2. kwargs['ha_token']
        3. get_ha_config() values

        Args:
            oauth_token: Home Assistant access token
            **kwargs: Additional parameters (may contain ha_url and ha_token)

        Returns:
            Tuple of (ha_url, ha_token, error_dict)
            error_dict is None if successful, contains error details otherwise
        """
        try:
            from lee.home_assistant.ha_config import get_ha_config  # pylint: disable=import-outside-toplevel
        except (ImportError, AttributeError) as e:
            return None, None, {
                "success": False,
                "error": f"HA config module unavailable: {e}",
                "error_code": "IMPORT_ERROR"
            }

        ha_url = kwargs.get("ha_url")
        ha_token = oauth_token or kwargs.get("ha_token")

        if not ha_url or not ha_token:
            config = get_ha_config()
            if config:
                if not ha_url:
                    config_url = getattr(config, 'HOME_ASSISTANT_URL', None)
                    if config_url:
                        ha_url = config_url
                if not ha_token:
                    config_token = getattr(config, 'HOME_ASSISTANT_API_KEY', None)
                    if config_token:
                        ha_token = config_token

        return ha_url, ha_token, None

    @staticmethod
    def validate_ha_config(ha_url: Optional[str], ha_token: Optional[str]) -> Optional[dict[str, Any]]:
        """Validate Home Assistant configuration.

        Args:
            ha_url: Home Assistant URL
            ha_token: Home Assistant token

        Returns:
            None if valid, error dict if invalid
        """
        if not ha_token:
            return {
                "success": False,
                "error": "No Home Assistant token provided",
                "error_code": "NO_TOKEN"
            }

        if not ha_url:
            return {
                "success": False,
                "error": "No Home Assistant URL configured",
                "error_code": "NO_URL"
            }

        return None

    @staticmethod
    def handle_network_error(operation: str, error: Exception) -> dict[str, Any]:
        """Handle network-related errors.

        Args:
            operation: Operation name for logging
            error: The exception that occurred

        Returns:
            Standard error response dict
        """
        execute_operation(GatewayInterface.LOGGING, "log_error",
                         message=f"{operation} network error: {str(error)}")
        return {
            "success": False,
            "error": f"Network error: {error}",
            "error_code": "NETWORK_ERROR"
        }

    @staticmethod
    def handle_validation_error(operation: str, error: Exception) -> dict[str, Any]:
        """Handle validation errors.

        Args:
            operation: Operation name for logging
            error: The exception that occurred

        Returns:
            Standard error response dict
        """
        execute_operation(GatewayInterface.LOGGING, "log_error",
                         message=f"{operation} validation error: {str(error)}")
        return {
            "success": False,
            "error": f"Invalid data: {error}",
            "error_code": "VALIDATION_ERROR"
        }

    @staticmethod
    def handle_config_error(operation: str, error: Exception) -> dict[str, Any]:
        """Handle configuration errors.

        Args:
            operation: Operation name for logging
            error: The exception that occurred

        Returns:
            Standard error response dict
        """
        execute_operation(GatewayInterface.LOGGING, "log_error",
                         message=f"{operation} config error: {str(error)}")
        return {
            "success": False,
            "error": f"Configuration error: {error}",
            "error_code": "CONFIG_ERROR"
        }

    @staticmethod
    def handle_generic_error(operation: str, error: Exception) -> dict[str, Any]:
        """Handle generic errors.

        Args:
            operation: Operation name for logging
            error: The exception that occurred

        Returns:
            Standard error response dict
        """
        execute_operation(GatewayInterface.LOGGING, "log_error",
                         message=f"{operation} failed: {str(error)}")
        return {
            "success": False,
            "error": str(error),
            "error_code": "UNKNOWN_ERROR"
        }

    @staticmethod
    def create_http_client(ha_url: str, ha_token: str) -> Any:
        """Create HomeAssistantHTTP client instance.

        Args:
            ha_url: Home Assistant URL
            ha_token: Home Assistant token

        Returns:
            HomeAssistantHTTP instance

        Raises:
            ValueError: If URL is invalid
        """
        from urllib.parse import urlparse  # pylint: disable=import-outside-toplevel

        from lee.home_assistant.http_client import HomeAssistantHTTP  # pylint: disable=import-outside-toplevel

        parsed_url = urlparse(ha_url)
        return HomeAssistantHTTP(
            host=parsed_url.hostname,
            port=parsed_url.port,
            token=ha_token,
            use_ssl=(parsed_url.scheme == "https")
        )

    @staticmethod
    def sanitize_input(input_data: str, level: str = "STRICT") -> str:
        """Sanitize user input using InputSanitizer.

        Args:
            input_data: Input string to sanitize
            level: Sanitization level (STRICT, MODERATE, PERMISSIVE)

        Returns:
            Sanitized string
        """
        from lee.lee_security import InputSanitizer, SanitizeLevel  # pylint: disable=import-outside-toplevel

        sanitize_level = getattr(SanitizeLevel, level, SanitizeLevel.STRICT)
        sanitizer = InputSanitizer(level=sanitize_level)
        return sanitizer.sanitize(input_data).sanitized


class HADeviceMixin:
    """Mixin class for device-specific operations.

    Provides helper methods for common device operations like
    filtering entities by domain, extracting device attributes, etc.
    """

    @staticmethod
    def filter_entities_by_domain(states: list[dict], domain: str) -> list[dict]:
        """Filter entities by domain prefix.

        Args:
            states: List of entity states
            domain: Domain prefix (e.g., 'light', 'switch')

        Returns:
            Filtered list of entities
        """
        return [s for s in states if s["entity_id"].startswith(f"{domain}.")]

    @staticmethod
    def extract_entity_attributes(entity: dict, attributes: list[str]) -> dict[str, Any]:
        """Extract specific attributes from entity state.

        Args:
            entity: Entity state dict
            attributes: List of attribute names to extract

        Returns:
            Dict with extracted attributes
        """
        result = {}
        entity_attrs = entity.get("attributes", {})
        for attr in attributes:
            if attr in entity_attrs:
                result[attr] = entity_attrs[attr]
        return result

    @staticmethod
    def get_entity_state(entity: dict) -> str:
        """Get entity state value.

        Args:
            entity: Entity state dict

        Returns:
            Entity state value
        """
        return entity.get("state", "unknown")

    @staticmethod
    def is_entity_on(entity: dict) -> bool:
        """Check if entity is in 'on' state.

        Args:
            entity: Entity state dict

        Returns:
            True if entity is on, False otherwise
        """
        return entity.get("state") == "on"
