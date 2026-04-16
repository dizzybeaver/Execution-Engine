"""ha_notify - Notify Interface

Version: 2025-12-22_1
Description: Notification sending operations

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

# Core implementations
from lee.home_assistant.ha_notify.ha_notify_core import (
    send_message_impl,
)

__all__ = [
    "send_message_impl",
]
