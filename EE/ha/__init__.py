"""HA Domain - Home Assistant Gateway for EE.

This domain provides Home Assistant integration operations.
"""
from EE.ha.ha_gateway_factory import HAGateway, create_ha_gateway

__all__ = ['HAGateway', 'create_ha_gateway']
