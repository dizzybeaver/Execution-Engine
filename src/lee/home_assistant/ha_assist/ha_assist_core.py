# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-03-28 - Implement HA Assist conversation API wrappers

"""ha_assist_core.py

Core implementations for Home Assistant Conversation API (Assist interface).

Provides conversation processing functionality through HA's /api/conversation/process endpoint.
Allows natural language interaction with Home Assistant.
"""

from typing import Any, Optional

from lee.home_assistant.http_client import HomeAssistantHTTP
from lee.home_assistant.ha_gateway_convenience import (
    ha_log_error,
    ha_log_warning,
)
from lee.lee_security import InputSanitizer, SanitizeLevel


def _resolve_ha_config(oauth_token: Optional[str] = None, **kwargs) -> tuple[Optional[str], Optional[str], dict[str, Any]]:  # pylint: disable=too-many-return-statements
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


def _validate_ha_config(ha_url: Optional[str], ha_token: Optional[str]) -> Optional[dict[str, Any]]:
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


def _sanitize_assist_message(message: str) -> str:
    """Sanitize user message for Assist conversation API.

    Uses InputSanitizer with STRICT level to prevent:
    - XSS attacks (script injection, HTML injection)
    - SQL injection attacks
    - Command injection attacks
    - Path traversal attacks
    - SSRF attacks

    Args:
        message: User message to sanitize

    Returns:
        Sanitized message string

    Raises:
        TypeError: If message is not a string
        ValueError: If message contains threats that cannot be safely sanitized
    """
    # Check type FIRST (before checking if empty)
    if not isinstance(message, str):
        raise TypeError(f"Message must be string, got {type(message).__name__}")

    # Check for empty message
    if not message:
        return ""

    # Limit message length before sanitization (prevent DoS via huge payloads)
    if len(message) > 10000:
        raise ValueError("Message too long (max 10000 characters)")

    # Use InputSanitizer with STRICT level for maximum security
    sanitizer = InputSanitizer(level=SanitizeLevel.STRICT)
    result = sanitizer.sanitize(message, context="general")

    # Check if threats were detected
    if not result.is_safe:
        # Log detected threats for security monitoring
        threat_summary = ", ".join(
            f"{t.threat_type.value} at position {t.position}"
            for t in result.threats
        )
        ha_log_warning(
            message=f"Assist message contained security threats: {threat_summary}",
            corr_id=None,
        )

    # Return sanitized message (threats removed/neutralized)
    return result.sanitized.strip()


def get_assist_response_impl(conversation_id: str, oauth_token: str = None, **kwargs) -> dict[str, Any]:  # pylint: disable=too-many-return-statements
    """Get response from active conversation.

    Args:
        conversation_id: Conversation ID to retrieve
        oauth_token: Home Assistant access token
        **kwargs: Additional parameters

    Returns:
        Conversation response or error
    """
    try:
        ha_url, ha_token, error = _resolve_ha_config(oauth_token, **kwargs)
        if error:
            return error

        validation_error = _validate_ha_config(ha_url, ha_token)
        if validation_error:
            return validation_error

        # Note: Conversation history retrieval not supported via HTTP
        # This is a limitation of HA's conversation API
        return {
            "success": False,
            "error": "Conversation history retrieval not supported via HTTP API. Use WebSocket connection for conversation tracking.",
            "error_code": "NOT_SUPPORTED",
            "conversation_id": conversation_id
        }

    except (ConnectionError, TimeoutError) as e:
        # Network error
        ha_log_error(
                         message=f"get_assist_response network error: {str(e)}")
        return {
            "success": False,
            "error": f"Network error: {e}",
            "error_code": "NETWORK_ERROR"
        }
    except (ValueError, TypeError, KeyError) as e:
        # Data validation error
        ha_log_error(
                         message=f"get_assist_response validation error: {str(e)}")
        return {
            "success": False,
            "error": f"Invalid data: {e}",
            "error_code": "VALIDATION_ERROR"
        }
    except (ImportError, AttributeError) as e:
        # Configuration error
        ha_log_error(
                         message=f"get_assist_response config error: {str(e)}")
        return {
            "success": False,
            "error": f"Configuration error: {e}",
            "error_code": "CONFIG_ERROR"
        }
    except Exception:  # pylint: disable=broad-except
        # Other unexpected errors
        ha_log_error(
                         message="get_assist_response failed")
        return {
            "success": False,
            "error": "Unknown error",
            "error_code": "GET_ASSIST_RESPONSE_ERROR"
        }


def handle_assist_pipeline_impl(pipeline_id: str, message: str,  # pylint: disable=too-many-return-statements
                                oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Handle Assist pipeline conversation.

    Args:
        pipeline_id: Pipeline/agent ID to use
        message: User message text
        oauth_token: Home Assistant access token
        **kwargs: Additional parameters

    Returns:
        Pipeline conversation result
    """
    try:
        from urllib.parse import urlparse  # pylint: disable=import-outside-toplevel

        ha_url, ha_token, error = _resolve_ha_config(oauth_token, **kwargs)
        if error:
            return error

        validation_error = _validate_ha_config(ha_url, ha_token)
        if validation_error:
            return validation_error

        parsed_url = urlparse(ha_url)
        with HomeAssistantHTTP(host=parsed_url.hostname, port=parsed_url.port,
                             token=ha_token, use_ssl=parsed_url.scheme == "https") as ha_http:
            # Sanitize user message for security
            sanitized_message = _sanitize_assist_message(message)
            # Process conversation through specific agent/pipeline
            response_data = ha_http.post_json(
                "conversation/process",
                {
                    "text": sanitized_message,
                    "agent_id": pipeline_id,
                    "language": kwargs.get("language", "en")
                }
            )

        return {
            "success": True,
            "response": response_data,
            "pipeline_id": pipeline_id
        }

    except (ConnectionError, TimeoutError) as e:
        # Network error
        ha_log_error(
                         message=f"handle_assist_pipeline network error: {str(e)}")
        return {
            "success": False,
            "error": f"Network error: {e}",
            "error_code": "NETWORK_ERROR"
        }
    except (ValueError, TypeError, KeyError) as e:
        # Data validation error
        ha_log_error(
                         message=f"handle_assist_pipeline validation error: {str(e)}")
        return {
            "success": False,
            "error": f"Invalid data: {e}",
            "error_code": "VALIDATION_ERROR"
        }
    except (ImportError, AttributeError) as e:
        # Configuration error
        ha_log_error(
                         message=f"handle_assist_pipeline config error: {str(e)}")
        return {
            "success": False,
            "error": f"Configuration error: {e}",
            "error_code": "CONFIG_ERROR"
        }
    except Exception:  # pylint: disable=broad-except
        # Other unexpected errors
        ha_log_error(
                         message="handle_assist_pipeline failed")
        return {
            "success": False,
            "error": "Unknown error",
            "error_code": "HANDLE_PIPELINE_ERROR"
        }


def process_assist_conversation_impl(message: str, context: Optional[dict[str, Any]] = None,  # pylint: disable=too-many-return-statements
                                     oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Process conversation with Assist.

    Args:
        message: User message text
        context: Optional conversation context (conversation_id, etc.)
        oauth_token: Home Assistant access token
        **kwargs: Additional parameters (language, agent_id, etc.)

    Returns:
        Conversation result with response and metadata
    """
    try:
        from urllib.parse import urlparse  # pylint: disable=import-outside-toplevel

        ha_url, ha_token, error = _resolve_ha_config(oauth_token, **kwargs)
        if error:
            return error

        validation_error = _validate_ha_config(ha_url, ha_token)
        if validation_error:
            return validation_error

        parsed_url = urlparse(ha_url)
        with HomeAssistantHTTP(host=parsed_url.hostname, port=parsed_url.port,
                             token=ha_token, use_ssl=parsed_url.scheme == "https") as ha_http:
            # Sanitize user message for security
            sanitized_message = _sanitize_assist_message(message)
            # Build request payload
            payload = {
                "text": sanitized_message,
                "language": kwargs.get("language", "en")
            }

            # Add context if provided
            if context:
                if "conversation_id" in context:
                    payload["conversation_id"] = context["conversation_id"]
                if "agent_id" in context:
                    payload["agent_id"] = context["agent_id"]

            response_data = ha_http.post_json("conversation/process", payload)

        return {
            "success": True,
            "response": response_data,
            "message": message
        }

    except (ConnectionError, TimeoutError) as e:
        # Network error
        ha_log_error(
                         message=f"process_assist_conversation network error: {str(e)}")
        return {
            "success": False,
            "error": f"Network error: {e}",
            "error_code": "NETWORK_ERROR"
        }
    except (ValueError, TypeError, KeyError) as e:
        # Data validation error
        ha_log_error(
                         message=f"process_assist_conversation validation error: {str(e)}")
        return {
            "success": False,
            "error": f"Invalid data: {e}",
            "error_code": "VALIDATION_ERROR"
        }
    except (ImportError, AttributeError) as e:
        # Configuration error
        ha_log_error(
                         message=f"process_assist_conversation config error: {str(e)}")
        return {
            "success": False,
            "error": f"Configuration error: {e}",
            "error_code": "CONFIG_ERROR"
        }
    except Exception:  # pylint: disable=broad-except
        # Other unexpected errors
        ha_log_error(
                         message="process_assist_conversation failed")
        return {
            "success": False,
            "error": "Unknown error",
            "error_code": "PROCESS_CONVERSATION_ERROR"
        }


def send_assist_message_impl(message: str, conversation_id: Optional[str] = None,  # pylint: disable=too-many-return-statements,too-many-locals
                             language: str = "en", oauth_token: str = None,
                             **kwargs) -> dict[str, Any]:
    """Send message to Assist conversation.

    Args:
        message: User message text
        conversation_id: Optional conversation ID for context
        language: Language code (default: 'en')
        oauth_token: Home Assistant access token
        **kwargs: Additional parameters (agent_id, etc.)

    Returns:
        Assist response dictionary
    """
    try:
        from urllib.parse import urlparse  # pylint: disable=import-outside-toplevel

        ha_url, ha_token, error = _resolve_ha_config(oauth_token, **kwargs)
        if error:
            return error

        validation_error = _validate_ha_config(ha_url, ha_token)
        if validation_error:
            return validation_error

        parsed_url = urlparse(ha_url)
        with HomeAssistantHTTP(host=parsed_url.hostname, port=parsed_url.port,
                             token=ha_token, use_ssl=parsed_url.scheme == "https") as ha_http:
            # Sanitize user message for security
            sanitized_message = _sanitize_assist_message(message)
            # Build request payload
            payload = {
                "text": sanitized_message,
                "language": language
            }

            # Add conversation_id if tracking conversation
            if conversation_id:
                payload["conversation_id"] = conversation_id

            # Add agent_id if specified
            if "agent_id" in kwargs:
                payload["agent_id"] = kwargs["agent_id"]

            response_data = ha_http.post_json("conversation/process", payload)

        return {
            "success": True,
            "response": response_data,
            "message": message,
            "conversation_id": response_data.get("conversation_id")
        }

    except (ConnectionError, TimeoutError) as e:
        # Network error
        ha_log_error(
                         message=f"send_assist_message network error: {str(e)}")
        return {
            "success": False,
            "error": f"Network error: {e}",
            "error_code": "NETWORK_ERROR"
        }
    except (ValueError, TypeError, KeyError) as e:
        # Data validation error
        ha_log_error(
                         message=f"send_assist_message validation error: {str(e)}")
        return {
            "success": False,
            "error": f"Invalid data: {e}",
            "error_code": "VALIDATION_ERROR"
        }
    except (ImportError, AttributeError) as e:
        # Configuration error
        ha_log_error(
                         message=f"send_assist_message config error: {str(e)}")
        return {
            "success": False,
            "error": f"Configuration error: {e}",
            "error_code": "CONFIG_ERROR"
        }
    except Exception:  # pylint: disable=broad-except
        # Other unexpected errors
        ha_log_error(
                         message="send_assist_message failed")
        return {
            "success": False,
            "error": "Unknown error",
            "error_code": "SEND_MESSAGE_ERROR"
        }
