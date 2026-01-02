"""
debug/debug_config.py
Version: 2025-12-08_1
Purpose: Debug configuration and hierarchical control
License: Apache 2.0
"""

import os
from typing import Dict

class DebugConfig:
    """
    Debug configuration with hierarchical control.
    
    Master switch: DEBUG_MODE (controls all)
    Scope switches: {SCOPE}_DEBUG_MODE, {SCOPE}_DEBUG_TIMING
    """
    
    def __init__(self):
        """Initialize debug configuration from environment."""
        self.master_enabled = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
        
        # 14 debug scopes
        self.scopes = {}
        for scope in ['ALEXA', 'HA', 'DEVICES', 'CACHE', 'HTTP', 'CONFIG', 
                      'SECURITY', 'METRICS', 'CIRCUIT_BREAKER', 'SINGLETON',
                      'GATEWAY', 'INIT', 'WEBSOCKET', 'LOGGING']:
            self.scopes[scope] = {
                'debug': os.getenv(f'{scope}_DEBUG_MODE', 'false').lower() == 'true',
                'timing': os.getenv(f'{scope}_DEBUG_TIMING', 'false').lower() == 'true'
            }
    
    def is_debug_enabled(self, scope: str) -> bool:
        """Check if debug enabled for scope."""
        if not self.master_enabled:
            return False
        return self.scopes.get(scope, {}).get('debug', False)
    
    def is_timing_enabled(self, scope: str) -> bool:
        """Check if timing enabled for scope."""
        if not self.master_enabled:
            return False
        return self.scopes.get(scope, {}).get('timing', False)

# Singleton instance
_DEBUG_CONFIG = None

def get_debug_config() -> DebugConfig:
    """Get debug config singleton."""
    global _DEBUG_CONFIG
    if _DEBUG_CONFIG is None:
        _DEBUG_CONFIG = DebugConfig()
    return _DEBUG_CONFIG

__all__ = ['DebugConfig', 'get_debug_config']
