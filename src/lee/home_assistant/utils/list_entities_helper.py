# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-03-23 - List entities helper to eliminate duplication

"""List Entities Helper for Home Assistant

Provides standardized entity filtering logic to eliminate code duplication
across HA device implementations (575-805 line savings potential).
"""

from typing import Any


def list_entities_filtered(
    result: dict[str, Any],
    entity_prefix: str
) -> dict[str, Any]:
    """Filter entities by prefix from HA get_states result.

    Args:
        result: Result from ha_execute_operation with
                 HAGatewayInterface.DEVICES
        entity_prefix: Entity prefix to filter (e.g., "light", "switch")

    Returns:
        Filtered entity list with count

    Example:
        >>> result = {"success": True, "result": [...]}
        >>> list_entities_filtered(result, "light")
        {'success': True, 'entity_name': [...], 'count': 5}
    """
    if not result.get("success"):
        return result

    all_states = result.get("result", [])
    filtered = [
        s for s in all_states
        if s.get("entity_id", "").startswith(f"{entity_prefix}.")
    ]

    return {
        "success": True,
        "entity_name": filtered,
        "count": len(filtered)
    }
