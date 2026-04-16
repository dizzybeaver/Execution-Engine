# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-06 - Extract directive processing from ha_interconnect.py

"""directive.py - Alexa Directive Processing
Version: 2025-03-02_1
Purpose: Process Alexa Smart Home directives

This module handles:
- Alexa directive processing
- OAuth token extraction
- Input sanitization for security

Copyright 2025 Joseph Hersey
Licensed under Apache License, Version 2.0
"""

import os
import uuid
from typing import Any

from lee.gateway import GatewayInterface, execute_operation
from lee.home_assistant import ha_gateway
from lee.gateway.gateway_core import generate_correlation_id
from lee.lee_security.sanitize import DataSanitizer


def _is_debug_mode() -> bool:
    """Check if LEE_DEBUG is enabled."""
    return os.environ.get("LEE_DEBUG", "false").lower() == "true"


def log_debug(message: str, **context) -> None:
    """Log debug message through LEE gateway."""
    if _is_debug_mode():
        try:
            execute_operation(GatewayInterface.DEBUG, "log",
                            message=message, **context)
        except (AttributeError, RuntimeError):
            pass


def log_error(message: str, **context) -> None:
    """Log error message through LEE gateway."""
    try:
        execute_operation(GatewayInterface.LOGGING, "log_error",
                        message=message, **context)
    except (AttributeError, RuntimeError):
        if _is_debug_mode():
            try:
                execute_operation(GatewayInterface.DEBUG, "log",
                                message=f"[HA_ERROR] {message}", **context)
            except (AttributeError, RuntimeError):
                pass


def log_info(message: str, **context) -> None:
    """Log info message through LEE gateway."""
    try:
        execute_operation(GatewayInterface.LOGGING, "log_info",
                        message=message, **context)
    except (AttributeError, RuntimeError):
        if _is_debug_mode():
            try:
                execute_operation(GatewayInterface.DEBUG, "log",
                                message=f"[HA_INFO] {message}", **context)
            except (AttributeError, RuntimeError):
                pass


def metrics_increment(metric_name: str, value: float = 1.0, **tags) -> None:
    """Increment metric through LEE gateway."""
    try:
        execute_operation(GatewayInterface.OBSERVABILITY, "increment",
                        metric_name=metric_name, value=value, **tags)
    except (AttributeError, ImportError, RuntimeError):
        pass


def generate_ha_correlation_id() -> str:
    """Generate correlation ID for HA operations."""
    try:
        return execute_operation(GatewayInterface.UTILITY, "generate_correlation_id")
    except (AttributeError, ImportError, RuntimeError):
        return generate_correlation_id("ha")


def alexa_process_directive(event: dict[str, Any]) -> dict[str, Any]:
    """Process Alexa Smart Home directive.

    Called by lambda_function.py with event containing:
    - event['directive']: Alexa directive
    - event['oauth_token']: LWA OAuth token (added by lambda_function.py)

    Args:
        event: Lambda event dictionary

    Returns:
        Alexa response dictionary
    """
    import os
    import time

    corr_id = generate_ha_correlation_id()

    directive_start = None
    if os.environ.get("LEE_DEBUG", "false").lower() == "true":
        directive_start = time.perf_counter()
        header = event.get("directive", {}).get("header", {})
        namespace = header.get("namespace", "Unknown")
        name = header.get("name", "Unknown")
        if _is_debug_mode():
            execute_operation(GatewayInterface.DEBUG, "log",
                            message="alexa_process_directive ENTRY",
                            corr_id=corr_id, directive=f"{namespace}.{name}",
                            scope="ALEXA_DIRECTIVE")

    try:
        # Check if forwarding to Home Assistant /api/alexa/smart_home
        use_ha_endpoint = os.environ.get("USE_HA_ALEXA_ENDPOINT", "false").lower() == "true"

        if use_ha_endpoint:
            # Forward to Home Assistant /api/alexa/smart_home
            from lee.home_assistant.ha_alexa_proxy import forward_to_home_assistant_alexa

            directive = event.get("directive", {})

            # Extract OAuth token
            try:
                token = event.get("oauth_token")
                if not token:
                    token = extract_oauth_token(event)
            except (ValueError, AttributeError, KeyError):
                # Fallback to HOME_ASSISTANT_API_KEY
                token = os.environ.get("HOME_ASSISTANT_API_KEY")

            if not token:
                directive_header = directive.get("header", {})
                return {
                    "event": {
                        "header": {
                            "namespace": "Alexa",
                            "name": "ErrorResponse",
                            "messageId": str(uuid.uuid4()),
                            "correlationToken": directive_header.get("correlationToken", ""),
                            "payloadVersion": "3",
                        },
                        "payload": {
                            "type": "INVALID_AUTHORIZATION_CREDENTIAL",
                            "message": "Could not get access token"
                        }
                    }
                }

            log_info(f"[{corr_id}] Forwarding to Home Assistant /api/alexa/smart_home")
            return forward_to_home_assistant_alexa(directive, token)

        # Original implementation using LEE's directive handlers
        # SECURITY: Sanitize user input from directive
        directive = event.get("directive", {})
        if directive:
            # Sanitize directive fields to prevent XSS attacks
            safe_directive = DataSanitizer.sanitize_directive_input(directive)
            event["directive"] = safe_directive
            directive = safe_directive

        # Check if HOME_ASSISTANT_API_KEY is set (long-lived access token)
        # If set, we don't need OAuth token extraction for Home Assistant authentication
        use_long_lived_token = False
        try:
            ha_api_key = execute_operation(GatewayInterface.CONFIG, "get", key="HOME_ASSISTANT_API_KEY")
            if ha_api_key:
                use_long_lived_token = True
                log_debug(f"[{corr_id}] HOME_ASSISTANT_API_KEY is set - using long-lived token for HA authentication")
        except (KeyError, AttributeError, NameError):
            pass  # HOME_ASSISTANT_API_KEY not set, fall through to OAuth

        # Extract OAuth token (lambda_function.py already added it)
        # Only extract if we're not using long-lived token
        oauth_token = None
        if not use_long_lived_token:
            oauth_token = event.get("oauth_token")
            if not oauth_token:
                # Fallback extraction if lambda didn't add it
                try:
                    oauth_token = extract_oauth_token(event)
                except ValueError:
                    # OAuth token not found, but this might be OK if using long-lived token
                    if not use_long_lived_token:
                        log_error(f"[{corr_id}] No OAuth token found and HOME_ASSISTANT_API_KEY not set")
                        raise

        # Log incoming directive
        header = directive.get("header", {})
        namespace = header.get("namespace", "Unknown")
        name = header.get("name", "Unknown")

        log_info(f"[{corr_id}] Processing Alexa directive: {namespace}.{name}")

        # Route to HA-SUGA
        result = ha_gateway.ha_alexa_process_directive(
            event=event,
            oauth_token=oauth_token,
            correlation_id=corr_id,
        )

        # Log completion
        metrics_increment("alexa_directive_processed")
        log_debug(f"[{corr_id}] Directive processed successfully")

        if _is_debug_mode() and directive_start is not None:
            duration_ms = (time.perf_counter() - directive_start) * 1000
            execute_operation(GatewayInterface.DEBUG, "log",
                            message="alexa_process_directive EXIT (success)",
                            corr_id=corr_id, directive=f"{namespace}.{name}",
                            duration_ms=f"{duration_ms:.2f}",
                            scope="ALEXA_DIRECTIVE")

        return result

    except (ConnectionError, TimeoutError, OSError) as e:
        # Network or system errors
        log_error(f"[{corr_id}] Network error during directive processing: {e!s}")
        metrics_increment("alexa_directive_error")
        directive = event.get("directive", {})
        header = directive.get("header", {})
        namespace = header.get("namespace", "Unknown")
        name = header.get("name", "Unknown")

        if _is_debug_mode() and directive_start is not None:
            duration_ms = (time.perf_counter() - directive_start) * 1000
            execute_operation(GatewayInterface.DEBUG, "log",
                            message="alexa_process_directive EXIT (Network error)",
                            corr_id=corr_id, directive=f"{namespace}.{name}",
                            duration_ms=f"{duration_ms:.2f}",
                            error_type=f"Network:{type(e).__name__}",
                            scope="ALEXA_DIRECTIVE")

        return {
            "event": {
                "header": {
                    "namespace": "Alexa",
                    "name": "ErrorResponse",
                    "messageId": str(uuid.uuid4()),
                    "correlationToken": header.get("correlationToken", ""),
                    "payloadVersion": "3",
                },
                "payload": {
                    "type": "INTERNAL_ERROR",
                    "message": "Network error",
                },
            },
        }
    except (ValueError, TypeError, KeyError) as e:
        # Invalid directive format or parameters
        log_error(f"[{corr_id}] Invalid directive format: {e!s}")
        metrics_increment("alexa_directive_error")
        directive = event.get("directive", {})
        header = directive.get("header", {})
        namespace = header.get("namespace", "Unknown")
        name = header.get("name", "Unknown")

        if _is_debug_mode() and directive_start is not None:
            duration_ms = (time.perf_counter() - directive_start) * 1000
            execute_operation(GatewayInterface.DEBUG, "log",
                            message="alexa_process_directive EXIT (Validation error)",
                            corr_id=corr_id, directive=f"{namespace}.{name}",
                            duration_ms=f"{duration_ms:.2f}",
                            error_type=f"Validation:{type(e).__name__}",
                            scope="ALEXA_DIRECTIVE")

        return {
            "event": {
                "header": {
                    "namespace": "Alexa",
                    "name": "ErrorResponse",
                    "messageId": str(uuid.uuid4()),
                    "correlationToken": header.get("correlationToken", ""),
                    "payloadVersion": "3",
                },
                "payload": {
                    "type": "INVALID_VALUE",
                    "message": "Invalid directive format",
                },
            },
        }
    except (AttributeError, NameError) as e:
        # Gateway or module interface errors
        log_error(f"[{corr_id}] Gateway interface error: {e!s}")
        metrics_increment("alexa_directive_error")
        directive = event.get("directive", {})
        header = directive.get("header", {})
        namespace = header.get("namespace", "Unknown")
        name = header.get("name", "Unknown")

        if _is_debug_mode() and directive_start is not None:
            duration_ms = (time.perf_counter() - directive_start) * 1000
            execute_operation(GatewayInterface.DEBUG, "log",
                            message="alexa_process_directive EXIT (Gateway error)",
                            corr_id=corr_id, directive=f"{namespace}.{name}",
                            duration_ms=f"{duration_ms:.2f}",
                            error_type=f"Gateway:{type(e).__name__}",
                            scope="ALEXA_DIRECTIVE")

        return {
            "event": {
                "header": {
                    "namespace": "Alexa",
                    "name": "ErrorResponse",
                    "messageId": str(uuid.uuid4()),
                    "correlationToken": header.get("correlationToken", ""),
                    "payloadVersion": "3",
                },
                "payload": {
                    "type": "INTERNAL_ERROR",
                    "message": "Gateway interface error",
                },
            },
        }
    except (RuntimeError,) as e:
        # Other unexpected errors
        log_error(f"[{corr_id}] Directive processing failed: {e!s}")
        metrics_increment("alexa_directive_error")

        # Return Alexa error response
        directive = event.get("directive", {})
        header = directive.get("header", {})
        namespace = header.get("namespace", "Unknown")
        name = header.get("name", "Unknown")

        if _is_debug_mode() and directive_start is not None:
            duration_ms = (time.perf_counter() - directive_start) * 1000
            execute_operation(GatewayInterface.DEBUG, "log",
                            message="alexa_process_directive EXIT (Runtime error)",
                            corr_id=corr_id, directive=f"{namespace}.{name}",
                            duration_ms=f"{duration_ms:.2f}",
                            error_type=f"Runtime:{type(e).__name__}",
                            scope="ALEXA_DIRECTIVE")

        # Generic error message in production to avoid leaking internal state
        import os  # noqa: C0415
        is_production = os.environ.get('PRODUCTION', 'false').lower() == 'true'
        error_msg = "Internal error" if is_production else str(e)

        return {
            "event": {
                "header": {
                    "namespace": "Alexa",
                    "name": "ErrorResponse",
                    "messageId": str(uuid.uuid4()),
                    "correlationToken": header.get("correlationToken", ""),
                    "payloadVersion": "3",
                },
                "payload": {
                    "type": "INTERNAL_ERROR",
                    "message": error_msg,
                },
            },
        }


def extract_oauth_token(event: dict[str, Any]) -> str:
    """Extract OAuth token from Lambda event.

    Priority order (matches lambda_function.py logic):
    1. event['oauth_token'] (pre-extracted by lambda)
    2. directive.endpoint.scope.token (control directives)
    3. directive.payload.scope.token (discovery/grant)
    4. directive.payload.grantee.token (AcceptGrant)

    Args:
        event: Lambda event dictionary

    Returns:
        OAuth token string

    Raises:
        ValueError: If token not found
    """
    # Check 1: Already extracted by lambda_function.py
    if "oauth_token" in event:
        return event["oauth_token"]

    directive = event.get("directive", {})

    # Check 2: directive.endpoint.scope.token
    endpoint = directive.get("endpoint", {})
    if endpoint:
        scope = endpoint.get("scope", {})
        if scope and "token" in scope:
            return scope["token"]

    # Check 3: directive.payload.scope.token
    payload = directive.get("payload", {})
    if payload:
        scope = payload.get("scope", {})
        if scope and "token" in scope:
            return scope["token"]

    # Check 4: directive.payload.grantee.token
    if payload:
        grantee = payload.get("grantee", {})
        if grantee and "token" in grantee:
            return grantee["token"]

    raise ValueError("No OAuth token found in event")


__all__ = [
    "alexa_process_directive",
    "extract_oauth_token",
    "generate_ha_correlation_id",
]
