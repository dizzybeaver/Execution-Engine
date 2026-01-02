"""
config/config_presets.py
Version: 2025-12-09_1
Purpose: Configuration preset management
License: Apache 2.0
"""

from typing import Dict, Any, List
from config.config_core import get_config_manager

# Configuration presets
_PRESETS = {
    'minimal': {
        'description': 'Minimal resource usage',
        'config': {
            'cache.enabled': 'false',
            'metrics.enabled': 'false',
            'logging.level': 'ERROR'
        }
    },
    'standard': {
        'description': 'Standard production configuration',
        'config': {
            'cache.enabled': 'true',
            'cache.ttl': '300',
            'metrics.enabled': 'true',
            'logging.level': 'INFO'
        }
    },
    'debug': {
        'description': 'Debug mode with verbose logging',
        'config': {
            'cache.enabled': 'true',
            'metrics.enabled': 'true',
            'logging.level': 'DEBUG',
            'debug.enabled': 'true'
        }
    },
    'performance': {
        'description': 'Performance optimized',
        'config': {
            'cache.enabled': 'true',
            'cache.ttl': '600',
            'metrics.enabled': 'true',
            'logging.level': 'WARNING'
        }
    }
}


def switch_preset(preset_name: str) -> Dict[str, Any]:
    """Switch to a configuration preset."""
    import gateway
    
    manager = get_config_manager()
    
    try:
        with gateway.debug_timing("CONFIG", "CONFIG", "switch_preset"):
            gateway.debug_log("CONFIG", "CONFIG", "Switching preset", preset=preset_name)
            
            if preset_name not in _PRESETS:
                return {
                    'success': False,
                    'error': f'Unknown preset: {preset_name}',
                    'available': list(_PRESETS.keys())
                }
            
            preset = _PRESETS[preset_name]
            
            # Apply preset configuration
            for key, value in preset['config'].items():
                manager._config[key] = value
            
            gateway.debug_log("CONFIG", "CONFIG", "Preset applied",
                            preset=preset_name,
                            param_count=len(preset['config']))
            
            return {
                'success': True,
                'preset': preset_name,
                'description': preset['description'],
                'applied_count': len(preset['config'])
            }
            
    except Exception as e:
        gateway.log_error(f"Switch preset failed ({preset_name}): {e}")
        return {'success': False, 'error': str(e)}


def get_preset_list() -> List[Dict[str, str]]:
    """Get list of available presets."""
    return [
        {
            'name': name,
            'description': preset['description']
        }
        for name, preset in _PRESETS.items()
    ]


def get_preset_config(preset_name: str) -> Dict[str, Any]:
    """Get configuration for a specific preset."""
    if preset_name not in _PRESETS:
        return {}
    
    return _PRESETS[preset_name]['config'].copy()


__all__ = [
    'switch_preset',
    'get_preset_list',
    'get_preset_config'
]
