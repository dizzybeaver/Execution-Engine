# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-03-25 - Added LEE file header for compliance


"""ha_file_core.py - Core Implementation for FILE Interface

Version: 2025-12-22_1
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Optional

from lee.home_assistant.ha_gateway import HAGatewayInterface, ha_execute_operation
from lee.home_assistant.utils import missing_parameter


def read_file_impl(
    file_name: Optional[str] = None,
    file_encoding: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Read file via file.read_file service.

    Args:
        file_name: Path to file (e.g., "www/my_file.json")
        file_encoding: File encoding ("JSON" or "YAML")
        ha_config: HA configuration
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status and file content
    """
    if not file_name:
        return missing_parameter("file_name")

    service_data = {"file_name": file_name}

    if file_encoding:
        service_data["file_encoding"] = file_encoding

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="file",
        service="read_file",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "File read successfully"

    return result
