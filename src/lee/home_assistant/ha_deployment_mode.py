# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-03-26 - Deployment mode detection system

"""
Deployment Mode Detection System for HA Gateway.

Detects the runtime environment (Lambda, WSGI, Local) and provides
configuration constraints and priorities for each mode.
"""

import os
from enum import Enum


class DeploymentMode(Enum):
    """Deployment environment modes."""
    LAMBDA = "lambda"
    WSGI = "wsgi"
    LOCAL = "local"


def get_deployment_mode() -> DeploymentMode:
    """
    Detect the current deployment mode.

    Priority:
    1. AWS_LAMBDA_FUNCTION_NAME env var => LAMBDA
    2. LEE_MODE=wsgi => WSGI
    3. Default => LOCAL

    Returns:
        DeploymentMode: The detected deployment mode
    """
    # Check for Lambda environment first (highest priority)
    lambda_function_name = os.environ.get('AWS_LAMBDA_FUNCTION_NAME', '').strip()
    if lambda_function_name:
        return DeploymentMode.LAMBDA

    # Check for WSGI mode
    lee_mode = os.environ.get('LEE_MODE', '').strip().lower()
    if lee_mode == 'wsgi':
        return DeploymentMode.WSGI

    # Default to LOCAL mode
    return DeploymentMode.LOCAL


def is_lambda_mode() -> bool:
    """
    Check if running in Lambda mode.

    Returns:
        bool: True if in Lambda mode, False otherwise
    """
    return get_deployment_mode() == DeploymentMode.LAMBDA


def is_local_mode() -> bool:
    """
    Check if running in local mode.

    Returns:
        bool: True if in local mode, False otherwise
    """
    return get_deployment_mode() == DeploymentMode.LOCAL


_MODE_CONSTRAINTS_DISPATCH: dict[DeploymentMode, dict[str, bool]] = {
    DeploymentMode.LAMBDA: {
        'memory_limited': True,
        'cold_start_sensitive': True,
        'filesystem_limited': True,
        'network_limited': True,
        'debug_enabled': False
    },
    DeploymentMode.WSGI: {
        'memory_limited': False,
        'cold_start_sensitive': False,
        'filesystem_limited': False,
        'network_limited': False,
        'debug_enabled': True
    },
    DeploymentMode.LOCAL: {
        'memory_limited': False,
        'cold_start_sensitive': False,
        'filesystem_limited': False,
        'network_limited': False,
        'debug_enabled': True
    }
}


_MODE_CONFIG_PRIORITY_DISPATCH: dict[DeploymentMode, list[str]] = {
    DeploymentMode.LAMBDA: [
        'environment',
        'parameter_store',
        'defaults'
    ],
    DeploymentMode.WSGI: [
        'config_file',
        'environment',
        'defaults'
    ],
    DeploymentMode.LOCAL: [
        'config_file',
        'environment',
        'defaults'
    ]
}


def get_mode_constraints() -> dict[str, bool]:
    """
    Get constraints for the current deployment mode.

    Returns:
        Dict[str, bool]: Dictionary with constraint keys:
            - memory_limited: Memory is constrained
            - cold_start_sensitive: Performance impacted by cold starts
            - filesystem_limited: Filesystem is read-only or limited
            - network_limited: Network has restrictions
            - debug_enabled: Debug features are available
    """
    mode = get_deployment_mode()

    constraints = _MODE_CONSTRAINTS_DISPATCH.get(mode)
    if constraints is None:
        raise ValueError(f"Unknown deployment mode: {mode}")

    return constraints


def get_config_source_priority() -> list[str]:
    """
    Get configuration source priority for the current mode.

    Returns:
        List[str]: Ordered list of config sources by priority
    """
    mode = get_deployment_mode()

    priority = _MODE_CONFIG_PRIORITY_DISPATCH.get(mode)
    if priority is None:
        raise ValueError(f"Unknown deployment mode: {mode}")

    return priority
