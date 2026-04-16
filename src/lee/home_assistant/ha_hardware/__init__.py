# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-03-25 - Added LEE file header for compliance


"""ha_hardware - Hardware Interface

Version: 2025-12-22_1
Description: Hardware integration operations

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

# Core implementations
from lee.home_assistant.ha_hardware.ha_hardware_core import (
    get_hardware_info_impl,
)

__all__ = [
    "get_hardware_info_impl",
]
