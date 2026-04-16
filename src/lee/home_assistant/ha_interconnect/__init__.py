# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-06 - Create __init__.py for ha_interconnect package

"""ha_interconnect - LEE to HA-SUGA Bridge Layer

This package provides the interface that lambda_function.py expects:
    result = ha_interconnect.alexa_process_directive(event)

Architecture:
- Imports LEE gateway for cross-cutting concerns (logging, metrics, etc.)
- Imports HA-SUGA gateway for Home Assistant operations
- Extracts and manages OAuth token flow
- Provides convenience functions for common operations

Copyright 2025 Joseph Hersey
Licensed under Apache License, Version 2.0
"""

# Import main functions
from lee.home_assistant.ha_interconnect.directive import (
    alexa_process_directive,
    extract_oauth_token,
)
from lee.home_assistant.ha_interconnect.gateway_functions import (
    alexa_handle_discovery,
    assist_send_message,
    config_get_ha_config,
    devices_call_service,
    devices_get_by_id,
    devices_get_ha_entities,
    devices_get_states,
    health_check_system,
)
from lee.home_assistant.ha_interconnect.ha_api import (
    devices_call_ha_api,
)
from lee.home_assistant.ha_interconnect.http_handlers import (
    HTTP_METHOD_HANDLERS,
)
from lee.home_assistant.ha_interconnect.utils import (
    generate_ha_correlation_id,
    log_debug,
    log_error,
    log_info,
    metrics_increment,
    metrics_record,
)

__all__ = [
    # Main entry point
    "alexa_process_directive",
    "extract_oauth_token",
    # Gateway convenience functions
    "alexa_handle_discovery",
    "devices_call_service",
    "devices_get_states",
    "devices_get_by_id",
    "assist_send_message",
    "config_get_ha_config",
    "health_check_system",
    "devices_get_ha_entities",
    "devices_call_ha_api",
    # Utilities
    "log_info",
    "log_error",
    "log_debug",
    "metrics_increment",
    "metrics_record",
    "generate_ha_correlation_id",
    # HTTP handlers
    "HTTP_METHOD_HANDLERS",
]
