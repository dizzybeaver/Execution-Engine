# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-03-25 - Added LEE file header for compliance


"""ha_google_mail_core.py - Gmail Integration Core Implementation

Version: 2025-12-22_1
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from lee.home_assistant.ha_gateway import HAGatewayInterface, ha_execute_operation
from lee.home_assistant.utils import missing_parameter


def set_vacation_impl(entity_id=None, enabled=None, title=None, message=None, plain_text=None, restrict_contacts=None, restrict_domain=None, start=None, end=None, ha_config=None, correlation_id=None, **kwargs):  # pylint: disable=too-many-arguments,too-many-positional-arguments
    """Set Gmail vacation responder.

    Args:
        entity_id: Gmail sensor entity ID
        enabled: Enable vacation responder (default: true)
        title: Vacation responder title
        message: Vacation responder message (required)
        plain_text: Use plain text format (default: true)
        restrict_contacts: Restrict to contacts only
        restrict_domain: Restrict to domain only
        start: Vacation start date
        end: Vacation end date
        ha_config: HA configuration (optional, auto-loaded)
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Operation result dictionary
    """
    if not entity_id:
        return missing_parameter("entity_id")

    service_data = {"entity_id": entity_id}
    if enabled is not None:
        service_data["enabled"] = enabled
    if title:
        service_data["title"] = title
    if message:
        service_data["message"] = message
    if plain_text is not None:
        service_data["plain_text"] = plain_text
    if restrict_contacts is not None:
        service_data["restrict_contacts"] = restrict_contacts
    if restrict_domain is not None:
        service_data["restrict_domain"] = restrict_domain
    if start:
        service_data["start"] = start
    if end:
        service_data["end"] = end

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="google_mail",
        service="set_vacation",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id,
        **kwargs,
    )
    return result
