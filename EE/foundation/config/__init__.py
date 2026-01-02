"""
Config Interface - Foundation Domain

Configuration management with profiles and environment variables.

UG-ISP Compliant:
- Interface uses DISPATCH dictionary pattern
- Factory contains actual implementation
- Cross-domain calls via call_operation callback
- NO imports outside foundation domain
"""

from EE.foundation.config.config_interface import ConfigInterface

__all__ = [
    "ConfigInterface",
]
