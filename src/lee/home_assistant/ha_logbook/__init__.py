"""ha_logbook - Logbook Interface

Version: 2025-12-22_1
Description: Human-readable event logs

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

# Core implementations
from lee.home_assistant.ha_logbook.ha_logbook_core import (
    get_events_impl,
)

__all__ = [
    "get_events_impl",
]
