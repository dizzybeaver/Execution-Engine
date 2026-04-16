"""ha_conversation.py - Conversation Interface Router (DD-1 Dispatch Dictionary)

Version: 2026-04-01_2
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseFallbackRouter


class _ConversationRouter(BaseFallbackRouter):
    """Router for Conversation interface operations."""

    def __init__(self):
        super().__init__(
            interface_name="Conversation",
            import_path="lee.home_assistant.ha_conversation.ha_conversation_core",
            function_names=[
                "process_impl",
                "prepare_impl",
                "list_agents_impl",
                "list_sentences_impl",
                "hass_agent_debug_impl",
                "hass_agent_language_scores_impl",
                "subscribe_chat_log_impl",
                "subscribe_chat_log_index_impl",
            ]
        )


_conversation_router = _ConversationRouter()


def execute_conversation_operation(operation: str, **kwargs) -> dict[str, Any]:
    """Dispatch Conversation interface operations using DD-1 pattern.

    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result dictionary
    """
    return _conversation_router.execute(operation, **kwargs)
