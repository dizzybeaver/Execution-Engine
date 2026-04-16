"""ha_siren.py - Home Assistant Siren Interface

Version: 2025-12-22_1
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from lee.home_assistant.ha_siren.ha_siren_core import (
    list_sirens_impl,
    toggle_siren_impl,
    turn_on_siren_impl,
)

__all__ = [
    "list_sirens_impl",
    "turn_on_siren_impl",
    "toggle_siren_impl",
]
