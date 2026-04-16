"""Assist Wrapper Functions Namespace

4 functions for Home Assistant Assist/Conversational AI.

Usage:
    from lee.home_assistant.wrappers import assist

    # Send message
    response = assist.send_message(message="Turn on the lights")

    # Process conversation
    result = assist.process_conversation(text="Turn on the lights")

    # Handle pipeline
    result = assist.handle_pipeline(message="Hello")

    # Get response
    response = assist.get_response(message="Hello")
"""

# Import all Assist wrapper functions
from lee.home_assistant.interface.wrappers.ha_assist_wrappers import (
    get_response,
    handle_pipeline,
    process_conversation,
    send_message,
)

__all__ = [
    'get_response',
    'handle_pipeline',
    'process_conversation',
    'send_message',
]
