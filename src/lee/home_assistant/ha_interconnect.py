# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-06 - DEPRECATED: Module split into package

"""ha_interconnect.py - LEE to HA-SUGA Bridge Layer

DEPRECATED (2026-04-06): This module has been split into a package for better maintainability.

New import location:
    from lee.home_assistant.ha_interconnect import (
        alexa_process_directive,
        extract_oauth_token,
        devices_call_service,
        # ... etc
    )

This file now imports from the new package structure for backward compatibility.

Package structure:
    ha_interconnect/
        __init__.py          - Main exports
        directive.py         - Alexa directive processing
        gateway_functions.py - HA-SUGA gateway convenience functions
        ha_api.py           - Direct HA REST API calls
        http_handlers.py    - HTTP method dispatch
        utils.py            - Logging and metrics utilities

Copyright 2025 Joseph Hersey
Licensed under Apache License, Version 2.0
"""

# Import everything from new package for backward compatibility
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
from lee.home_assistant.ha_interconnect.ha_api import devices_call_ha_api
from lee.home_assistant.ha_interconnect.http_handlers import HTTP_METHOD_HANDLERS
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
