from lee.gateway import GatewayInterface, execute_operation
from lee.gateway.gateway_core import generate_correlation_id

# ha_websocket_entities.py
"""
ha_websocket_entities.py - Entity Registry Operations via WebSocket
Version: 3.0.0
Description: Entity registry and filtering operations with WebSocket communication

Split from ha_websocket.py (498 lines) to meet AWS Lambda 350-line limit.

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

from contextlib import contextmanager, nullcontext
from typing import Any, Optional

# ===== SUGA-ISP COMPLIANT DEBUG FUNCTIONS =====


def _check_entity_registry_cache(cache_key: str, correlation_id: str) -> Optional[dict[str, Any]]:
    """Check cache for entity registry.

    Args:
        cache_key: Cache key to check
        correlation_id: Correlation ID for tracking

    Returns:
        Cached registry data or None if not found
    """
    cached_registry = execute_operation(GatewayInterface.CACHE, "get", key=cache_key)
    if cached_registry and isinstance(cached_registry, dict):
        try:
            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="HOME_ASSISTANT",
                             message="get_entity_registry_via_websocket COMPLETE (CACHE)")
            execute_operation(GatewayInterface.OBSERVABILITY, "increment", metric_name="ha_entity_registry_cache_hit")
            return execute_operation(GatewayInterface.SECURITY, "create_success_response",
                                    message="Entity registry retrieved from cache",
                                    data=cached_registry)
        except ImportError:
            # Optional dependency - continue if unavailable
            ...
    return None


def _establish_websocket_connection(ws_url: str, access_token: str, correlation_id: str) -> Optional[tuple[bool, Any, dict[str, Any]]]:
    """Establish WebSocket connection for entity registry.

    Args:
        ws_url: WebSocket URL
        access_token: Home Assistant access token
        correlation_id: Correlation ID for tracking

    Returns:
        Tuple of (success, connection, error_details)
    """
    from lee.home_assistant.ha_websocket_core import establish_websocket_connection

    # Pass config dict with url and token for proper pool management
    ha_config = {
        "url": ws_url,
        "token": access_token
    }

    conn_result = establish_websocket_connection(ha_config, timeout=10)

    if not conn_result.get("success"):
        try:
            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="HOME_ASSISTANT",
                             message="get_entity_registry_via_websocket FAILED - Connection failed")
            execute_operation(GatewayInterface.OBSERVABILITY, "increment", metric_name="ha_entity_registry_connection_failed")
        except ImportError:
            # Optional dependency - continue if unavailable
            ...
        return False, None, conn_result

    return True, conn_result.get("connection"), None


def _authenticate_websocket(connection, access_token: str, correlation_id: str) -> Optional[tuple[bool, dict[str, Any]]]:
    """Authenticate WebSocket connection.

    Args:
        connection: WebSocket connection object
        access_token: Home Assistant access token
        correlation_id: Correlation ID for tracking

    Returns:
        Tuple of (success, error_details)
    """
    from lee.home_assistant.ha_websocket_core import authenticate_websocket

    # Pass ha_config dict with token for proper authentication
    ha_config = {"token": access_token}
    auth_result = authenticate_websocket(connection, ha_config)

    if not auth_result.get("success"):
        try:
            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="HOME_ASSISTANT",
                             message="get_entity_registry_via_websocket FAILED - Auth failed")
            execute_operation(GatewayInterface.OBSERVABILITY, "increment", metric_name="ha_entity_registry_auth_failed")
        except ImportError:
            # Optional dependency - continue if unavailable
            ...
        return False, auth_result

    return True, None


def _request_entity_registry(connection, correlation_id: str) -> Optional[tuple[bool, list, dict[str, Any]]]:
    """Request entity registry via WebSocket.

    Args:
        connection: Authenticated WebSocket connection
        correlation_id: Correlation ID for tracking

    Returns:
        Tuple of (success, registry_data, error_details)
    """
    from lee.home_assistant.ha_websocket_core import websocket_request

    registry_result = websocket_request(
        connection,
        "config/entity_registry/get",
        timeout=30,
    )

    if not registry_result.get("success"):
        try:
            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="HOME_ASSISTANT",
                             message="get_entity_registry_via_websocket FAILED - Request failed")
            execute_operation(GatewayInterface.OBSERVABILITY, "increment", metric_name="ha_entity_registry_request_failed")
        except ImportError:
            # Optional dependency - continue if unavailable
            ...
        return False, [], registry_result

    # Extract registry data
    response_data = registry_result.get("response", {})
    registry_data = response_data.get("result", [])

    execute_operation(GatewayInterface.LOGGING, "log_info", message=f"[{correlation_id}] Retrieved {len(registry_data)} entities from registry")

    return True, registry_data, None


@contextmanager
def _websocket_connection_context(ws_url: str, access_token: str, correlation_id: str):
    """Context manager for WebSocket connection with automatic cleanup.

    Args:
        ws_url: WebSocket URL
        access_token: Home Assistant access token
        correlation_id: Correlation ID for tracking

    Yields:
        WebSocket connection object

    Example:
        with _websocket_connection_context(ws_url, token, corr_id) as conn:
            # Use connection
            pass
        # Connection automatically cleaned up
    """
    from lee.home_assistant.ha_websocket_core import close_websocket_connection

    connection = None
    try:
        # Establish connection
        success, connection, error_details = _establish_websocket_connection(ws_url, access_token, correlation_id)
        if not success:
            raise RuntimeError(f"Failed to establish WebSocket connection: {error_details}")

        # Yield connection for use
        yield connection

    finally:
        # Always cleanup connection - pass URL for proper pool management
        if connection:
            close_result = close_websocket_connection(connection, url=ws_url)
            if not close_result.get("success"):
                try:
                    execute_operation(GatewayInterface.LOGGING, "log_warning",
                                   message=f"[{correlation_id}] Failed to close WebSocket connection cleanly")
                except (AttributeError, RuntimeError):
                    # Logging unavailable - silent fail
                    ...


def _cache_and_log_registry(registry_data: list, cache_key: str, use_cache: bool,
                           correlation_id: str, duration_ms: float) -> dict[str, Any]:
    """Cache entity registry and log metrics.

    Args:
        registry_data: Entity registry data
        cache_key: Cache key for storage
        use_cache: Whether to cache the result
        correlation_id: Correlation ID for tracking
        duration_ms: Request duration in milliseconds

    Returns:
        Success response dict
    """
    # Cache the result
    if use_cache and registry_data:
        execute_operation(GatewayInterface.CACHE, "set", key=cache_key, value=registry_data, ttl=3600)
        try:
            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="HOME_ASSISTANT",
                             message="Entity registry cached")
        except ImportError:
            # Optional dependency - continue if unavailable
            ...

    try:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="get_entity_registry_via_websocket SUCCESS",
                         entity_count=len(registry_data))
    except ImportError:
        # Optional dependency - continue if unavailable
        ...

    execute_operation(GatewayInterface.OBSERVABILITY, "increment", metric_name="ha_entity_registry_success")
    execute_operation(GatewayInterface.OBSERVABILITY, "record", name="ha_entity_registry_count", value=len(registry_data))
    execute_operation(GatewayInterface.OBSERVABILITY, "record", name="ha_entity_registry_duration_ms", value=duration_ms)

    return execute_operation(GatewayInterface.SECURITY, "create_success_response",
                            message="Entity registry retrieved",
                            data=registry_data)


def get_entity_registry_via_websocket(use_cache: bool = True) -> dict[str, Any]:
    """Get Home Assistant entity registry via WebSocket.

    Args:
        use_cache: Whether to use cached data if available

    Returns:
        Response dict with entity registry data
    """
    from lee.home_assistant.ha_config import get_ha_config

    correlation_id = generate_correlation_id("ws")

    try:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="get_entity_registry_via_websocket START", use_cache=use_cache)
    except ImportError:
        # Optional dependency - continue if unavailable
        ...

    cache_key = "ha_entity_registry"

    # Check cache first
    if use_cache:
        cached_result = _check_entity_registry_cache(cache_key, correlation_id)
        if cached_result:
            return cached_result

    # Get HA configuration
    config = get_ha_config()
    base_url = config.get("base_url", "")
    # Import shared utility for protocol conversion
    from lee.home_assistant.ha_protocol_utils import convert_to_websocket_url

    # Convert HTTP protocol to WebSocket protocol
    ws_url = convert_to_websocket_url(base_url) + "/api/websocket"

    execute_operation(GatewayInterface.LOGGING, "log_info", message=f"[{correlation_id}] Getting entity registry via WebSocket: {ws_url}")

    try:
        try:
            timing_ctx = execute_operation(GatewayInterface.DEBUG, "timing",
                                          corr_id=correlation_id,
                                          operation_name="get_entity_registry_via_websocket")
        except ImportError:
            timing_ctx = nullcontext()

        with timing_ctx:
            # Use context manager for automatic connection cleanup
            with _websocket_connection_context(ws_url, config.get("access_token"), correlation_id) as connection:
                # Authenticate
                success, auth_error = _authenticate_websocket(connection, config.get("access_token"), correlation_id)
                if not success:
                    return execute_operation(GatewayInterface.SECURITY, "create_error_response",
                                            message="WebSocket authentication failed",
                                            code="WEBSOCKET_AUTH_FAILED",
                                            details=auth_error)

                # Request entity registry
                success, registry_data, request_error = _request_entity_registry(connection, correlation_id)
                if not success:
                    return execute_operation(GatewayInterface.SECURITY, "create_error_response",
                                            message="Failed to get entity registry",
                                            code="ENTITY_REGISTRY_REQUEST_FAILED",
                                            details=request_error)

                # Cache and log results
                duration_ms = request_error.get("duration_ms", 0) if request_error else 0
                return _cache_and_log_registry(registry_data, cache_key, use_cache, correlation_id, duration_ms)

    except (ConnectionError, TimeoutError, OSError, ValueError, KeyError, TypeError) as e:
        # Expected entity registry errors
        try:
            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="HOME_ASSISTANT",
                             message="get_entity_registry_via_websocket FAILED", error=str(e))
        except ImportError:
            # Optional dependency - continue if unavailable
            ...

        try:
            execute_operation(GatewayInterface.LOGGING, "log_error",
                           message=f"[{correlation_id}] Entity registry WebSocket request failed: {e!s}",
                           corr_id=correlation_id)
            execute_operation(GatewayInterface.OBSERVABILITY, "increment", metric_name="ha_entity_registry_exception")
        except (AttributeError, RuntimeError):
            # Logging/observability unavailable - silent fail
            ...
        return execute_operation(GatewayInterface.SECURITY, "create_error_response",
                                message="Entity registry request failed",
                                code="ENTITY_REGISTRY_EXCEPTION",
                                details={"error": str(e)})
    except Exception as e:
        # Unexpected errors
        try:
            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="HOME_ASSISTANT",
                             message="get_entity_registry_via_websocket FAILED", error=str(e))
        except ImportError:
            # Optional dependency - continue if unavailable
            ...

        try:
            execute_operation(GatewayInterface.LOGGING, "log_error",
                           message=f"[{correlation_id}] Entity registry WebSocket request failed: {e!s}",
                           corr_id=correlation_id)
            execute_operation(GatewayInterface.OBSERVABILITY, "increment", metric_name="ha_entity_registry_exception")
        except (AttributeError, RuntimeError):
            # Logging/observability unavailable - silent fail
            ...
        return execute_operation(GatewayInterface.SECURITY, "create_error_response",
                                message="Entity registry request failed",
                                code="ENTITY_REGISTRY_EXCEPTION",
                                details={"error": str(e)})


def filter_exposed_entities(entities: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Filter entities for Alexa exposure based on entity registry data.

        entities: List of entity registry dictionaries

        List of entities that should be exposed to Alexa

    """
    correlation_id = generate_correlation_id("ws")

    try:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="filter_exposed_entities START", total_entities=len(entities))
    except ImportError:
        # Optional dependency - continue if unavailable
        ...

    try:
        if not entities:
            try:
                execute_operation(GatewayInterface.DEBUG, "log",
                                 corr_id=correlation_id, scope="HOME_ASSISTANT",
                                 message="filter_exposed_entities COMPLETE - No entities")
            except ImportError:
                # Optional dependency - continue if unavailable
                ...
            return []

        filtered_entities = []
        hidden_count = 0
        exposed_count = 0

        try:
            timing_ctx = execute_operation(GatewayInterface.DEBUG, "timing",
                                          corr_id=correlation_id,
                                          operation_name="filter_exposed_entities")
        except ImportError:
            timing_ctx = nullcontext()

        with timing_ctx:
            for entity in entities:
                if not isinstance(entity, dict):
                    continue

                _ = entity.get("entity_id", "")  # Entity ID used for logging/debugging
                disabled = entity.get("disabled_by", None)
                hidden = entity.get("hidden_by", None)
                entity_category = entity.get("entity_category", None)

                # Skip disabled entities
                if disabled:
                    hidden_count += 1
                    continue

                # Skip hidden entities (unless explicitly configured)
                if hidden and hidden != "integration":
                    hidden_count += 1
                    continue

                # Skip configuration entities (diagnostic entities)
                if entity_category == "config":
                    hidden_count += 1
                    continue

                # Include entity if it passes all filters
                filtered_entities.append(entity)
                exposed_count += 1

        execute_operation(GatewayInterface.LOGGING, "log_info", message=f"[{correlation_id}] Entity filtering complete: {exposed_count} exposed, {hidden_count} hidden")

        try:
            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="HOME_ASSISTANT",
                             message="filter_exposed_entities SUCCESS",
                             exposed_count=exposed_count, hidden_count=hidden_count)
        except ImportError:
            # Optional dependency - continue if unavailable
            ...

        execute_operation(GatewayInterface.OBSERVABILITY, "increment", metric_name="ha_entity_filter_success")
        execute_operation(GatewayInterface.OBSERVABILITY, "record", name="ha_entities_exposed_count", value=exposed_count)
        execute_operation(GatewayInterface.OBSERVABILITY, "record", name="ha_entities_hidden_count", value=hidden_count)
        execute_operation(GatewayInterface.OBSERVABILITY, "record", name="ha_entity_filter_duration_ms", value=0)

        return filtered_entities

    except (ValueError, TypeError, KeyError, AttributeError) as e:
        # Expected entity filtering errors
        try:
            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="HOME_ASSISTANT",
                             message="filter_exposed_entities FAILED", error=str(e))
        except ImportError:
            # Optional dependency - continue if unavailable
            ...

        try:
            execute_operation(GatewayInterface.LOGGING, "error", message=f"[{correlation_id}] Entity filtering failed: {e!s}")
            execute_operation(GatewayInterface.OBSERVABILITY, "increment", metric_name="ha_entity_filter_exception")
        except ImportError:
            # Optional dependency - continue if unavailable
            ...

        # Return empty list on error to be safe
        return []
    except Exception as e:
        # Unexpected errors
        try:
            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="HOME_ASSISTANT",
                             message="filter_exposed_entities FAILED", error=str(e))
        except ImportError:
            # Optional dependency - continue if unavailable
            ...

        try:
            execute_operation(GatewayInterface.LOGGING, "error", message=f"[{correlation_id}] Entity filtering failed: {e!s}")
            execute_operation(GatewayInterface.OBSERVABILITY, "increment", metric_name="ha_entity_filter_exception")
        except ImportError:
            # Optional dependency - continue if unavailable
            ...

        # Return empty list on error to be safe
        return []


def get_alexa_exposed_entities(use_cache: bool = True) -> dict[str, Any]:
    """Get entities that should be exposed to Alexa.

    This combines getting the entity registry via WebSocket and filtering for exposure.

        use_cache: Whether to use cached results

        Response with filtered list of entities for Alexa exposure

    """
    correlation_id = generate_correlation_id("ws")

    try:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="get_alexa_exposed_entities START", use_cache=use_cache)
    except ImportError:
        # Optional dependency - continue if unavailable
        ...

    try:
        try:
            timing_ctx = execute_operation(GatewayInterface.DEBUG, "timing",
                                          corr_id=correlation_id,
                                          operation_name="get_alexa_exposed_entities")
        except ImportError:
            timing_ctx = nullcontext()

        with timing_ctx:
            # Get full entity registry
            registry_result = get_entity_registry_via_websocket(use_cache)

            if not registry_result.get("success"):
                try:
                    execute_operation(GatewayInterface.DEBUG, "log",
                                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                                     message="get_alexa_exposed_entities FAILED - Registry failed")
                    execute_operation(GatewayInterface.OBSERVABILITY, "increment", metric_name="ha_alexa_entities_registry_failed")
                except ImportError:
                    # Optional dependency - continue if unavailable
                    ...
                return execute_operation(GatewayInterface.SECURITY, "create_error_response",
                                       message="Failed to get entity registry",
                                       code="ENTITY_REGISTRY_FAILED",
                                       details=registry_result)

            # Filter for Alexa exposure
            all_entities = registry_result.get("data", [])
            exposed_entities = filter_exposed_entities(all_entities)

            try:
                execute_operation(GatewayInterface.DEBUG, "log",
                                 corr_id=correlation_id, scope="HOME_ASSISTANT",
                                 message="get_alexa_exposed_entities SUCCESS",
                                 total_entities=len(all_entities), exposed_entities=len(exposed_entities))
            except ImportError:
                # Optional dependency - continue if unavailable
                ...

            execute_operation(GatewayInterface.OBSERVABILITY, "increment", metric_name="ha_alexa_entities_success")
            execute_operation(GatewayInterface.OBSERVABILITY, "record", name="ha_alexa_entities_count", value=len(exposed_entities))
            execute_operation(GatewayInterface.OBSERVABILITY, "record", name="ha_alexa_entities_duration_ms", value=0)

            return execute_operation(GatewayInterface.SECURITY, "create_success_response",
                                   message="Alexa-exposed entities retrieved",
                                   data={
                                       "total_entities": len(all_entities),
                                       "exposed_entities": len(exposed_entities),
                                       "entities": exposed_entities,
                                   })

    except (ConnectionError, TimeoutError, OSError, ValueError, KeyError, TypeError) as e:
        # Expected Alexa entity operations errors
        try:
            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="HOME_ASSISTANT",
                             message="get_alexa_exposed_entities FAILED", error=str(e))
        except ImportError:
            # Optional dependency - continue if unavailable
            ...

        try:
            execute_operation(GatewayInterface.LOGGING, "error", message=f"[{correlation_id}] Get Alexa exposed entities failed: {e!s}")
            execute_operation(GatewayInterface.OBSERVABILITY, "increment", metric_name="ha_alexa_entities_exception")
        except ImportError:
            # Optional dependency - continue if unavailable
            ...

        return execute_operation(GatewayInterface.SECURITY, "create_error_response",
                               message=str(e),
                               code="ALEXA_ENTITIES_EXCEPTION")
    except Exception as e:
        # Unexpected errors
        try:
            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="HOME_ASSISTANT",
                             message="get_alexa_exposed_entities FAILED", error=str(e))
        except ImportError:
            # Optional dependency - continue if unavailable
            ...

        try:
            execute_operation(GatewayInterface.LOGGING, "error", message=f"[{correlation_id}] Get Alexa exposed entities failed: {e!s}")
            execute_operation(GatewayInterface.OBSERVABILITY, "increment", metric_name="ha_alexa_entities_exception")
        except ImportError:
            # Optional dependency - continue if unavailable
            ...

        return execute_operation(GatewayInterface.SECURITY, "create_error_response",
                               message=str(e),
                               code="ALEXA_ENTITIES_EXCEPTION")


__all__ = [
    "filter_exposed_entities",
    "get_alexa_exposed_entities",
    "get_entity_registry_via_websocket",
]

# EOF
