"""ha_history - Home Assistant History Interface

Version: 2025-12-22_1
Description: Core implementations for historical data access operations

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from lee.home_assistant.ha_history.ha_history_core import (
    get_history_during_period_impl,
)

__all__ = [
    "get_history_during_period_impl",
]
