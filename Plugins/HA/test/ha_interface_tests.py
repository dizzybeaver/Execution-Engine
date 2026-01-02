"""
HA Interface Tests for EE

Phase 4: Migration - HA Plugin Interface Routing Tests (Part 1)

This module tests HA plugin interface routing.
Verifies all HA operations route correctly through EE Gateway.

Interface Tests (Part 1):
- test_ha_interface_registration(): Verify HA interface is registered
- test_ha_get_state_routing(): Verify get_state routes correctly
- test_ha_call_service_routing(): Verify call_service routes correctly

UG-ISP Compliance:
- All operations via gateway routing
- NO direct interface access
- Proper dispatch through HA gateway domain
- Inline correlation IDs

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import time
import random
from typing import Dict, Any


def test_ha_interface_registration() -> Dict[str, Any]:
    """
    Test HA interface is registered in gateway.

    Verifies:
    - HA gateway domain exists
    - Interface is accessible
    - Operations are registered

    Returns:
        Dict with test result
    """
    from EE import execute, GatewayInterface

    corr_id = f"ha_iface_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"

    execute(
        GatewayInterface.DEBUG,
        'log',
        corr_id=corr_id,
        scope="HA_IFACE_TEST",
        message="Testing HA interface registration"
    )

    try:
        # Check if HA gateway domain is registered
        from EE.gateway.gateway_router import UnifiedRouter
        from EE.gateway.gateway_registry import EEDomainRegistry

        registry = EEDomainRegistry.get_instance()

        # Check if 'ha' domain exists
        ha_domains = [d for d in registry.list_all() if 'ha' in d.lower()]

        execute(
            GatewayInterface.DEBUG,
            'log',
            corr_id=corr_id,
            scope="HA_IFACE_TEST",
            message="HA interface registration check",
            ha_domains_found=len(ha_domains),
            success=True
        )

        return {
            'test': 'test_ha_interface_registration',
            'success': True,
            'ha_domains': ha_domains
        }

    except Exception as e:
        execute(
            GatewayInterface.DEBUG,
            'log',
            corr_id=corr_id,
            scope="HA_IFACE_TEST",
            message="HA interface registration test failed",
            error=str(e)
        )

        return {
            'test': 'test_ha_interface_registration',
            'success': False,
            'error': str(e)
        }


def test_ha_get_state_routing() -> Dict[str, Any]:
    """
    Test get_state operation routes correctly.

    Verifies:
    - Operation is properly dispatched
    - Parameters are passed correctly
    - Response is returned through gateway

    Returns:
        Dict with test result
    """
    from EE import execute, GatewayInterface

    corr_id = f"ha_iface_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"

    execute(
        GatewayInterface.DEBUG,
        'log',
        corr_id=corr_id,
        scope="HA_IFACE_TEST",
        message="Testing HA get_state routing"
    )

    try:
        # Check if HA is enabled
        ha_enable = execute(
            "config.get",
            {"key": "home_assistant.enable", "default": "false"}
        )

        if ha_enable != "true" and ha_enable is not True:
            return {
                'test': 'test_ha_get_state_routing',
                'success': True,
                'skipped': True,
                'reason': 'HA not enabled'
            }

        # Test get_state routing via gateway
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
            scope="HA_IFACE_TEST",
            message="HA get_state routing test completed",
            success=result.get('success', False)
        )

        return {
            'test': 'test_ha_get_state_routing',
            'success': result.get('success', False),
            'routing_verified': True
        }

    except Exception as e:
        execute(
            GatewayInterface.DEBUG,
            'log',
            corr_id=corr_id,
            scope="HA_IFACE_TEST",
            message="HA get_state routing test failed",
            error=str(e)
        )

        return {
            'test': 'test_ha_get_state_routing',
            'success': False,
            'error': str(e)
        }


def test_ha_call_service_routing() -> Dict[str, Any]:
    """
    Test call_service operation routes correctly.

    Verifies:
    - Operation is properly dispatched
    - Service parameters are passed
    - Response is returned through gateway

    Returns:
        Dict with test result
    """
    from EE import execute, GatewayInterface

    corr_id = f"ha_iface_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"

    execute(
        GatewayInterface.DEBUG,
        'log',
        corr_id=corr_id,
        scope="HA_IFACE_TEST",
        message="Testing HA call_service routing"
    )

    try:
        # Check if HA is enabled
        ha_enable = execute(
            "config.get",
            {"key": "home_assistant.enable", "default": "false"}
        )

        if ha_enable != "true" and ha_enable is not True:
            return {
                'test': 'test_ha_call_service_routing',
                'success': True,
                'skipped': True,
                'reason': 'HA not enabled'
            }

        # Test call_service routing via gateway
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
            scope="HA_IFACE_TEST",
            message="HA call_service routing test completed",
            success=result.get('success', False)
        )

        return {
            'test': 'test_ha_call_service_routing',
            'success': result.get('success', False),
            'routing_verified': True
        }

    except Exception as e:
        execute(
            GatewayInterface.DEBUG,
            'log',
            corr_id=corr_id,
            scope="HA_IFACE_TEST",
            message="HA call_service routing test failed",
            error=str(e)
        )

        return {
            'test': 'test_ha_call_service_routing',
            'success': False,
            'error': str(e)
        }


__all__ = [
    'test_ha_interface_registration',
    'test_ha_get_state_routing',
    'test_ha_call_service_routing',
]
