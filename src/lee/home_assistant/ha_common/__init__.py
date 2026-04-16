# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-03-25 - Added LEE file header for compliance


"""Home Assistant Common Utilities

Provides shared utilities for Home Assistant integration.
"""

from lee.home_assistant.ha_common.alexa_response_utils import (
    create_error_response,
    create_success_response,
)

__all__ = [
    'create_success_response',
    'create_error_response',
]
