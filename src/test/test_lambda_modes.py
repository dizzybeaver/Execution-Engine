"""
test/test_lambda_modes.py
Version: 2025-12-08_1
Purpose: Lambda mode testing (migrated from lambda_function.py mode logic)
License: Apache 2.0
"""

from typing import Dict, Any

def test_lambda_mode(mode: str, event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Test Lambda mode by routing to appropriate handler."""
    mode_map = {
        'failsafe': test_failsafe_mode,
        'diagnostic': test_diagnostic_mode,
        'emergency': test_emergency_mode,
        'ha_connection_test': test_ha_connection_mode,
        'ha_discovery': test_ha_discovery_mode
    }
    
    handler = mode_map.get(mode)
    if not handler:
        return {
            'statusCode': 400,
            'body': {
                'error': f'Unknown mode: {mode}',
                'available_modes': list(mode_map.keys())
            }
        }
    
    return handler(event, context)


def test_failsafe_mode(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Test failsafe mode handler."""
    try:
        import lambda_failsafe
        return lambda_failsafe.lambda_failsafe_handler(event, context)
    except ImportError:
        return {
            'statusCode': 503,
            'body': {
                'error': 'lambda_failsafe not available',
                'mode': 'failsafe'
            }
        }


def test_diagnostic_mode(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Test diagnostic mode handler."""
    try:
        import lambda_diagnostic
        return lambda_diagnostic.lambda_handler(event, context)
    except ImportError:
        return {
            'statusCode': 503,
            'body': {
                'error': 'lambda_diagnostic not available',
                'mode': 'diagnostic'
            }
        }


def test_emergency_mode(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Test emergency mode handler."""
    try:
        import lambda_emergency
        return lambda_emergency.lambda_handler(event, context)
    except ImportError:
        return {
            'statusCode': 503,
            'body': {
                'error': 'lambda_emergency not available',
                'mode': 'emergency'
            }
        }


def test_ha_connection_mode(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Test HA connection test mode."""
    try:
        import lambda_ha_connection
        return lambda_ha_connection.lambda_handler(event, context)
    except ImportError:
        return {
            'statusCode': 503,
            'body': {
                'error': 'lambda_ha_connection not available',
                'mode': 'ha_connection_test'
            }
        }


def test_ha_discovery_mode(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Test HA discovery mode."""
    try:
        import debug_discovery
        return debug_discovery.lambda_handler(event, context)
    except ImportError:
        return {
            'statusCode': 503,
            'body': {
                'error': 'debug_discovery not available',
                'mode': 'ha_discovery'
            }
        }


__all__ = [
    'test_lambda_mode',
    'test_failsafe_mode',
    'test_diagnostic_mode',
    'test_emergency_mode'
]
