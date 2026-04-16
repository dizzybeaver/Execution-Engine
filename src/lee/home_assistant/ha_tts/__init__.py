"""ha_tts.py - Home Assistant TTS Interface

Version: 2025-12-22_1
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from lee.home_assistant.ha_tts.ha_tts_core import say_impl, speak_impl

__all__ = [
    "say_impl",
    "speak_impl",
]
