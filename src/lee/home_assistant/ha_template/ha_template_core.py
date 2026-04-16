"""ha_template_core.py - Core Implementation for TEMPLATE Interface

Version: 2025-12-22_1
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Optional

from lee.home_assistant.ha_device_base import reload_domain_impl


def reload_impl(
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Reload template entities via template.reload service.

    Args:
        ha_config: HA configuration
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status
    """
    return reload_domain_impl("template", ha_config, correlation_id)
