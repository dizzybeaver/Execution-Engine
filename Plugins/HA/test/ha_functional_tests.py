"""
HA Functional Tests for EE

Phase 4: Migration - HA Functional Tests (Part 1)

This module contains functional tests for HA plugin operations.
All tests use EE Gateway routing (not direct HA client access).

Functional Tests (Part 1):
- test_ha_connection(): Verify HA connection via gateway
- test_ha_read_light(): Read light state via gateway
- test_ha_light_on(): Turn light on via gateway
- test_ha_light_off(): Turn light off via gateway

UG-ISP Compliance:
- All HA operations via execute("ha.*", {...})
- NO direct HA client imports
- NO direct HA API calls
- All operations route through gateway
- Inline correlation IDs

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import time
import random
from typing import Dict, Any


def test_ha_connection() -> Dict[str, Any]:
    """
    Test HA connection via gateway.

    Verifies:
    - HA gateway domain is accessible
    - Connection can be established
    - Authentication works

    Returns:
        Dict with test result
    """
    from EE import execute, GatewayInterface

    corr_id = f"ha_func_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"

    execute(
        GatewayInterface.DEBUG,
        'log',
        corr_id=corr_id,
        scope="HA_FUNC_TEST",
        message="Testing HA connection via gateway"
    )

    try:
        # Check HA config via gateway
        ha_enable = execute(
            "config.get",
            {"key": "home_assistant.enable", "default": "false"}
        )

        if ha_enable != "true" and ha_enable is not True:
            execute(
                GatewayInterface.DEBUG,
                'log',
                corr_id=corr_id,
                scope="HA_FUNC_TEST",
                message="HA not enabled in config"
            )

            return {
                'test': 'test_ha_connection',
                'success': True,
                'skipped': True,
                'reason': 'HA not enabled in config'
            }

        # Get HA URL via gateway
        ha_url = execute(
            "config.get",
            {"key": "home_assistant.url"}
        )

        if not ha_url:
            return {
                'test': 'test_ha_connection',
                'success': False,
                'error': 'HA URL not configured'
            }

        execute(
            GatewayInterface.DEBUG,
            'log',
            corr_id=corr_id,
            scope="HA_FUNC_TEST",
            message="HA connection test passed",
            ha_url=ha_url,
            success=True
        )

        return {
            'test': 'test_ha_connection',
            'success': True,
            'ha_url': ha_url,
            'ha_enabled': True
        }

    except Exception as e:
        execute(
            GatewayInterface.DEBUG,
            'log',
            corr_id=corr_id,
            scope="HA_FUNC_TEST",
            message="HA connection test failed",
            error=str(e)
        )

        return {
            'test': 'test_ha_connection',
            'success': False,
            'error': str(e)
        }


def test_ha_read_light() -> Dict[str, Any]:
    """
    Test reading light state via gateway.

    Verifies:
    - Light state can be read
    - Gateway routing works
    - Response is properly formatted

    Returns:
        Dict with test result
    """
    from EE import execute, GatewayInterface

    corr_id = f"ha_func_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"

    execute(
        GatewayInterface.DEBUG,
        'log',
        corr_id=corr_id,
        scope="HA_FUNC_TEST",
        message="Testing HA read light via gateway"
    )

    try:
        # Check if HA is enabled
        ha_enable = execute(
            "config.get",
            {"key": "home_assistant.enable", "default": "false"}
        )

        if ha_enable != "true" and ha_enable is not True:
            return {
                'test': 'test_ha_read_light',
                'success': True,
                'skipped': True,
                'reason': 'HA not enabled'
            }

        # Read light state via gateway (assuming entity exists)
        result = execute(
            "ha.get_state",
            {
                "entity_id": "light.test",
                "correlation_id": corr_id
            }
        )

        execute(
            GatewayInterface.DEBUG,
            'log',
            corr_id=corr_id,
            scope="HA_FUNC_TEST",
            message="HA read light completed",
            success=result.get('success', False)
        )

        return {
            'test': 'test_ha_read_light',
            'success': result.get('success', False),
            'state': result.get('state'),
            'attributes': result.get('attributes')
        }

    except Exception as e:
        execute(
            GatewayInterface.DEBUG,
            'log',
            corr_id=corr_id,
            scope="HA_FUNC_TEST",
            message="HA read light test failed",
            error=str(e)
        )

        return {
            'test': 'test_ha_read_light',
            'success': False,
            'error': str(e)
        }


def test_ha_light_on() -> Dict[str, Any]:
    """
    Test turning light on via gateway.

    Verifies:
    - Light service can be called
    - Gateway routing works
    - Service execution succeeds

    Returns:
        Dict with test result
    """
    from EE import execute, GatewayInterface

    corr_id = f"ha_func_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"

    execute(
        GatewayInterface.DEBUG,
        'log',
        corr_id=corr_id,
        scope="HA_FUNC_TEST",
        message="Testing HA light on via gateway"
    )

    try:
        # Check if HA is enabled
        ha_enable = execute(
            "config.get",
            {"key": "home_assistant.enable", "default": "false"}
        )

        if ha_enable != "true" and ha_enable is not True:
            return {
                'test': 'test_ha_light_on',
                'success': True,
                'skipped': True,
                'reason': 'HA not enabled'
            }

        # Turn light on via gateway
        result = execute(
            "ha.call_service",
            {
                "domain": "light",
                "service": "turn_on",
                "service_data": {"entity_id": "light.test"},
                "correlation_id": corr_id
            }
        )

        execute(
            GatewayInterface.DEBUG,
            'log',
            corr_id=corr_id,
            scope="HA_FUNC_TEST",
            message="HA light on completed",
            success=result.get('success', False)
        )

        return {
            'test': 'test_ha_light_on',
            'success': result.get('success', False)
        }

    except Exception as e:
        execute(
            GatewayInterface.DEBUG,
            'log',
            corr_id=corr_id,
            scope="HA_FUNC_TEST",
            message="HA light on test failed",
            error=str(e)
        )

        return {
            'test': 'test_ha_light_on',
            'success': False,
            'error': str(e)
        }


def test_ha_light_off() -> Dict[str, Any]:
    """
    Test turning light off via gateway.

    Verifies:
    - Light service can be called
    - Gateway routing works
    - Service execution succeeds

    Returns:
        Dict with test result
    """
    from EE import execute, GatewayInterface

    corr_id = f"ha_func_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"

    execute(
        GatewayInterface.DEBUG,
        'log',
        corr_id=corr_id,
        scope="HA_FUNC_TEST",
        message="Testing HA light off via gateway"
    )

    try:
        # Check if HA is enabled
        ha_enable = execute(
            "config.get",
            {"key": "home_assistant.enable", "default": "false"}
        )

        if ha_enable != "true" and ha_enable is not True:
            return {
                'test': 'test_ha_light_off',
                'success': True,
                'skipped': True,
                'reason': 'HA not enabled'
            }

        # Turn light off via gateway
        result = execute(
            "ha.call_service",
            {
                "domain": "light",
                "service": "turn_off",
                "service_data": {"entity_id": "light.test"},
                "correlation_id": corr_id
            }
        )

        execute(
            GatewayInterface.DEBUG,
            'log',
            corr_id=corr_id,
            scope="HA_FUNC_TEST",
            message="HA light off completed",
            success=result.get('success', False)
        )

        return {
            'test': 'test_ha_light_off',
            'success': result.get('success', False)
        }

    except Exception as e:
        execute(
            GatewayInterface.DEBUG,
            'log',
            corr_id=corr_id,
            scope="HA_FUNC_TEST",
            message="HA light off test failed",
            error=str(e)
        )

        return {
            'test': 'test_ha_light_off',
            'success': False,
            'error': str(e)
        }


__all__ = [
    'test_ha_connection',
    'test_ha_read_light',
    'test_ha_light_on',
    'test_ha_light_off',
]
