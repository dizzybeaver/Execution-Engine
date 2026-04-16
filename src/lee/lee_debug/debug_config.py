"""debug/debug_config.py
Version: 2025-12-08_1
Purpose: Debug configuration and hierarchical control
License: Apache 2.0
"""

import os

# Cache environment variables at module load time
# For AWS Lambda: Read from environment variables set by Lambda configuration
# For local testing: .env file should set these via environment variables
_LEE_DEBUG_ENABLED = os.getenv("LEE_DEBUG", "false").lower() == "true"

# Pre-compute scope debug flags (14 scopes)
_DEBUG_SCOPES = {}
for scope in ["ALEXA", "HA", "DEVICES", "CACHE", "HTTP", "CONFIG",
              "SECURITY", "METRICS", "CIRCUIT_BREAKER", "SINGLETON",
              "GATEWAY", "INIT", "WEBSOCKET", "LOGGING"]:
    _DEBUG_SCOPES[scope] = {
        "debug": os.getenv(f"{scope}_DEBUG_MODE", "false").lower() == "true",
        "timing": os.getenv(f"{scope}_DEBUG_TIMING", "false").lower() == "true",
    }


class DebugConfig:
    """Debug configuration with hierarchical control.

    Master switch: LEE_DEBUG (controls all)
    Scope switches: {SCOPE}_DEBUG_MODE, {SCOPE}_DEBUG_TIMING
    """

    def __init__(self) -> None:
        """Initialize debug configuration from cached module-level values."""
        self.master_enabled = _LEE_DEBUG_ENABLED
        self.scopes = _DEBUG_SCOPES

    def is_debug_enabled(self, debug_scope: str) -> bool:
        """Check if debug enabled for scope."""
        if not self.master_enabled:
            return False
        return self.scopes.get(debug_scope, {}).get("debug", False)

    def is_timing_enabled(self, timing_scope: str) -> bool:
        """Check if timing enabled for scope."""
        if not self.master_enabled:
            return False
        return self.scopes.get(timing_scope, {}).get("timing", False)

# Singleton instance
_DEBUG_CONFIG = None

def get_debug_config() -> DebugConfig:
    """Get debug config singleton."""
    global _DEBUG_CONFIG  # pylint: disable=global-statement
    if _DEBUG_CONFIG is None:
        _DEBUG_CONFIG = DebugConfig()
    return _DEBUG_CONFIG

__all__ = ["DebugConfig", "get_debug_config"]
