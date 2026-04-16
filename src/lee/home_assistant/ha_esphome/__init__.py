# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-03-25 - Added LEE file header for compliance


"""ha_esphome - ESPHome Interface

Version: 2025-12-22_1
Description: ESPHome integration operations

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

# Core implementations
from lee.home_assistant.ha_esphome.ha_esphome_core import (
    get_encryption_key_impl,
)

__all__ = [
    "get_encryption_key_impl",
]
