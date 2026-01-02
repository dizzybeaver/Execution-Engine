"""
HA Plugin for EE Gateway
Version: 1.0.0
Date: 2025-12-28
Description: Home Assistant integration plugin for EE Gateway

Converts HA Gateway to EE Plugin using INT-16 PLUGINS interface.
Removes duplicate functionality by using EE Gateway interfaces:
- HTTP_CLIENT for HTTP operations
- WEBSOCKET for WebSocket connections
- CACHE for state caching
- DEBUG for debug logging
- SECURITY for validation

Architecture:
- Inherits from EEPlugin base class
- Uses EE Gateway for all cross-interface operations
- Keeps only HA-specific logic (Alexa, Assist, device control)
- 100% UG-ISP compliant

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import time
import random
from typing import Any, Dict, Optional, List
from plugins import EEPlugin, plugin
from EE.plugins.gateway.ee_gateway_enums import EEGatewayInterface


@plugin
class HAPlugin(EEPlugin):
    """
    Home Assistant integration plugin for EE Gateway.

    Provides Home Assistant smart home integration while leveraging
    EE Gateway interfaces for common operations.
    """

    # Plugin metadata
    name = "home_assistant"
    version = "1.0.0"
    description = "Home Assistant integration plugin for EE Gateway"

    def __init__(self):
        """Initialize HA plugin state."""
        self._gateway = None
        self._ha_client = None
        self._ha_url = None
        self._ha_token = None
        self._websocket_connected = False
        self._states_cache = {}

    # ===== REQUIRED PLUGIN METHODS =====

    def initialize(self, gateway: Any) -> None:
        """
        Initialize HA plugin with EE Gateway.

        Args:
            gateway: EE Gateway instance for cross-interface operations
        """
        from EE import execute_operation, EEGatewayInterface

        self._gateway = gateway
        corr_id = f"ha_init_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"

        # Debug logging via EE Gateway
        execute_operation(
            EEGatewayInterface.DEBUG,
            'log',
            corr_id=corr_id,
            scope="HA_PLUGIN",
            message="HA Plugin initialize called"
        )

        # Load HA configuration
        self._load_config(corr_id)

        # Initialize HA client
        self._init_ha_client(corr_id)

        # Setup WebSocket connection
        if self._ha_url and self._ha_token:
            self._setup_websocket(corr_id)

        execute_operation(
            EEGatewayInterface.DEBUG,
            'log',
            corr_id=corr_id,
            scope="HA_PLUGIN",
            message="HA Plugin initialized successfully",
            ha_url=self._ha_url,
            websocket_connected=self._websocket_connected
        )

    def shutdown(self) -> None:
        """Cleanup HA plugin resources and shutdown."""
        from EE import execute_operation, EEGatewayInterface

        corr_id = f"ha_shutdown_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"

        execute_operation(
            EEGatewayInterface.DEBUG,
            'log',
            corr_id=corr_id,
            scope="HA_PLUGIN",
            message="HA Plugin shutdown called"
        )

        # Close WebSocket connection
        if self._websocket_connected and self._ha_client:
            self._close_websocket(corr_id)

        # Cleanup HA client
        self._ha_client = None
        self._ha_url = None
        self._ha_token = None
        self._states_cache.clear()

        execute_operation(
            EEGatewayInterface.DEBUG,
            'log',
            corr_id=corr_id,
            scope="HA_PLUGIN",
            message="HA Plugin shutdown completed"
        )

    # ===== HA-SPECIFIC OPERATIONS =====

    def get_states(self, entity_ids: Optional[List[str]] = None,
                   use_cache: bool = True, correlation_id: str = None) -> Dict[str, Any]:
        """
        Get Home Assistant entity states.

        Uses EE Gateway CACHE interface for caching.

        Args:
            entity_ids: Optional list of entity IDs to filter
            use_cache: Whether to use cache (default: True)
            correlation_id: Optional correlation ID for tracking

        Returns:
            Dict with success flag and states data
        """
        from EE import execute_operation, EEGatewayInterface

        if correlation_id is None:
            correlation_id = f"ha_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"

        execute_operation(
            EEGatewayInterface.DEBUG,
            'log',
            corr_id=correlation_id,
            scope="HA_PLUGIN",
            message="get_states called",
            entity_ids=entity_ids,
            use_cache=use_cache
        )

        # Try cache first if enabled and getting all states
        if use_cache and entity_ids is None:
            cached = execute_operation(
                EEGatewayInterface.CACHE,
                'get',
                key='ha_states_all'
            )

            if cached and cached.get('success'):
                execute_operation(
                    EEGatewayInterface.DEBUG,
                    'log',
                    corr_id=correlation_id,
                    scope="HA_PLUGIN",
                    message="get_states cache hit",
                    success=True
                )
                return cached

        # Fetch from HA API using EE Gateway HTTP_CLIENT
        if not self._ha_url or not self._ha_token:
            return {
                'success': False,
                'error': 'HA not configured - missing URL or token'
            }

        try:
            response = execute_operation(
                EEGatewayInterface.HTTP_CLIENT,
                'http_get',
                url=f"{self._ha_url}/api/states",
                headers={
                    'Authorization': f'Bearer {self._ha_token}',
                    'Content-Type': 'application/json'
                },
                correlation_id=correlation_id
            )

            if response and response.get('success'):
                states = response.get('data', [])

                # Filter by entity_ids if specified
                if entity_ids:
                    states = [s for s in states if s.get('entity_id') in entity_ids]

                # Transform to dict keyed by entity_id
                states_dict = {s.get('entity_id'): s for s in states}

                result = {
                    'success': True,
                    'states': states_dict,
                    'count': len(states_dict),
                    'cached': False
                }

                # Cache result if getting all states
                if entity_ids is None:
                    execute_operation(
                        EEGatewayInterface.CACHE,
                        'set',
                        key='ha_states_all',
                        value=result,
                        ttl=60
                    )

                execute_operation(
                    EEGatewayInterface.DEBUG,
                    'log',
                    corr_id=correlation_id,
                    scope="HA_PLUGIN",
                    message="get_states completed",
                    count=len(states_dict),
                    success=True
                )

                return result
            else:
                return {
                    'success': False,
                    'error': response.get('error', 'Unknown error')
                }

        except Exception as e:
            execute_operation(
                EEGatewayInterface.DEBUG,
                'log',
                corr_id=correlation_id,
                scope="HA_PLUGIN",
                message="get_states failed",
                error=str(e)
            )
            return {'success': False, 'error': str(e)}

    def get_by_id(self, entity_id: str,
                  correlation_id: str = None) -> Dict[str, Any]:
        """
        Get device by ID.

        Args:
            entity_id: Entity ID to query
            correlation_id: Optional correlation ID for tracking

        Returns:
            Dict with success flag and entity data
        """
        from EE import execute_operation, EEGatewayInterface

        if correlation_id is None:
            correlation_id = f"ha_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"

        execute_operation(
            EEGatewayInterface.DEBUG,
            'log',
            corr_id=correlation_id,
            scope="HA_PLUGIN",
            message="get_by_id called",
            entity_id=entity_id
        )

        # Try cache first
        cache_key = f'ha_entity_{entity_id}'
        cached = execute_operation(
            EEGatewayInterface.CACHE,
            'get',
            key=cache_key
        )

        if cached and cached.get('success'):
            execute_operation(
                EEGatewayInterface.DEBUG,
                'log',
                corr_id=correlation_id,
                scope="HA_PLUGIN",
                message="get_by_id cache hit",
                entity_id=entity_id,
                success=True
            )
            return cached

        # Fetch from HA API
        if not self._ha_url or not self._ha_token:
            return {
                'success': False,
                'error': 'HA not configured'
            }

        try:
            response = execute_operation(
                EEGatewayInterface.HTTP_CLIENT,
                'http_get',
                url=f"{self._ha_url}/api/states/{entity_id}",
                headers={
                    'Authorization': f'Bearer {self._ha_token}',
                    'Content-Type': 'application/json'
                },
                correlation_id=correlation_id
            )

            if response and response.get('success'):
                result = {
                    'success': True,
                    'entity': response.get('data'),
                    'entity_id': entity_id
                }

                # Cache result
                execute_operation(
                    EEGatewayInterface.CACHE,
                    'set',
                    key=cache_key,
                    value=result,
                    ttl=60
                )

                execute_operation(
                    EEGatewayInterface.DEBUG,
                    'log',
                    corr_id=correlation_id,
                    scope="HA_PLUGIN",
                    message="get_by_id completed",
                    entity_id=entity_id,
                    success=True
                )

                return result
            else:
                return {
                    'success': False,
                    'error': response.get('error', 'Unknown error')
                }

        except Exception as e:
            execute_operation(
                EEGatewayInterface.DEBUG,
                'log',
                corr_id=correlation_id,
                scope="HA_PLUGIN",
                message="get_by_id failed",
                entity_id=entity_id,
                error=str(e)
            )
            return {'success': False, 'error': str(e)}

    def call_service(self, domain: str, service: str,
                     service_data: Optional[Dict[str, Any]] = None,
                     correlation_id: str = None) -> Dict[str, Any]:
        """
        Call Home Assistant service.

        Args:
            domain: Service domain (e.g., 'light', 'switch')
            service: Service name (e.g., 'turn_on', 'turn_off')
            service_data: Optional service data
            correlation_id: Optional correlation ID for tracking

        Returns:
            Dict with success flag
        """
        from EE import execute_operation, EEGatewayInterface

        if correlation_id is None:
            correlation_id = f"ha_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"

        execute_operation(
            EEGatewayInterface.DEBUG,
            'log',
            corr_id=correlation_id,
            scope="HA_PLUGIN",
            message="call_service called",
            domain=domain,
            service=service,
            service_data=service_data
        )

        if not self._ha_url or not self._ha_token:
            return {
                'success': False,
                'error': 'HA not configured'
            }

        try:
            response = execute_operation(
                EEGatewayInterface.HTTP_CLIENT,
                'http_post',
                url=f"{self._ha_url}/api/services/{domain}/{service}",
                headers={
                    'Authorization': f'Bearer {self._ha_token}',
                    'Content-Type': 'application/json'
                },
                json_data=service_data or {},
                correlation_id=correlation_id
            )

            execute_operation(
                EEGatewayInterface.DEBUG,
                'log',
                corr_id=correlation_id,
                scope="HA_PLUGIN",
                message="call_service completed",
                domain=domain,
                service=service,
                success=response.get('success', False) if response else False
            )

            return response if response else {'success': False, 'error': 'No response'}

        except Exception as e:
            execute_operation(
                EEGatewayInterface.DEBUG,
                'log',
                corr_id=correlation_id,
                scope="HA_PLUGIN",
                message="call_service failed",
                domain=domain,
                service=service,
                error=str(e)
            )
            return {'success': False, 'error': str(e)}

    def find_fuzzy(self, search_name: str, threshold: float = 0.6,
                   correlation_id: str = None) -> Optional[str]:
        """
        Find device via fuzzy name matching.

        Args:
            search_name: Name to search for
            threshold: Matching threshold (default: 0.6)
            correlation_id: Optional correlation ID for tracking

        Returns:
            Entity ID if found, None otherwise
        """
        from difflib import SequenceMatcher
        from EE import execute_operation, EEGatewayInterface

        if correlation_id is None:
            correlation_id = f"ha_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"

        execute_operation(
            EEGatewayInterface.DEBUG,
            'log',
            corr_id=correlation_id,
            scope="HA_PLUGIN",
            message="find_fuzzy called",
            search_name=search_name,
            threshold=threshold
        )

        # Get all states
        result = self.get_states(correlation_id=correlation_id)

        if not result.get('success'):
            return None

        states = result.get('states', {})

        # Find best match
        best_match = None
        best_ratio = 0.0

        for entity_id, state in states.items():
            entity_name = state.get('attributes', {}).get('friendly_name', entity_id)
            ratio = SequenceMatcher(None, search_name.lower(), entity_name.lower()).ratio()

            if ratio > best_ratio:
                best_ratio = ratio
                best_match = entity_id

        if best_ratio >= threshold:
            execute_operation(
                EEGatewayInterface.DEBUG,
                'log',
                corr_id=correlation_id,
                scope="HA_PLUGIN",
                message="find_fuzzy found match",
                search_name=search_name,
                matched_entity=best_match,
                ratio=best_ratio,
                success=True
            )
            return best_match

        execute_operation(
            EEGatewayInterface.DEBUG,
            'log',
            corr_id=correlation_id,
            scope="HA_PLUGIN",
            message="find_fuzzy no match found",
            search_name=search_name
        )
        return None

    def warm_cache(self, correlation_id: str = None) -> Dict[str, Any]:
        """
        Pre-warm device state cache.

        Args:
            correlation_id: Optional correlation ID for tracking

        Returns:
            Dict with success flag and count of cached states
        """
        from EE import execute_operation, EEGatewayInterface

        if correlation_id is None:
            correlation_id = f"ha_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"

        execute_operation(
            EEGatewayInterface.DEBUG,
            'log',
            corr_id=correlation_id,
            scope="HA_PLUGIN",
            message="warm_cache called"
        )

        result = self.get_states(use_cache=True, correlation_id=correlation_id)

        execute_operation(
            EEGatewayInterface.DEBUG,
            'log',
            corr_id=correlation_id,
            scope="HA_PLUGIN",
            message="warm_cache completed",
            count=result.get('count', 0),
            success=result.get('success', False)
        )

        return result

    # ===== WEBSOCKET METHODS =====

    def _setup_websocket(self, correlation_id: str) -> None:
        """
        Setup WebSocket connection to Home Assistant.

        Args:
            correlation_id: Correlation ID for tracking
        """
        from EE import execute_operation, EEGatewayInterface

        execute_operation(
            EEGatewayInterface.DEBUG,
            'log',
            corr_id=correlation_id,
            scope="HA_PLUGIN",
            message="Setting up WebSocket connection",
            ha_url=self._ha_url
        )

        # Use EE Gateway WEBSOCKET interface
        ws_url = self._ha_url.replace('http://', 'ws://').replace('https://', 'wss://')
        ws_url = f"{ws_url}/api/websocket"

        try:
            result = execute_operation(
                EEGatewayInterface.WEBSOCKET,
                'connect',
                url=ws_url,
                headers={
                    'Authorization': f'Bearer {self._ha_token}'
                },
                correlation_id=correlation_id
            )

            if result and result.get('success'):
                self._websocket_connected = True
                execute_operation(
                    EEGatewayInterface.DEBUG,
                    'log',
                    corr_id=correlation_id,
                    scope="HA_PLUGIN",
                    message="WebSocket connected successfully",
                    success=True
                )
            else:
                execute_operation(
                    EEGatewayInterface.DEBUG,
                    'log',
                    corr_id=correlation_id,
                    scope="HA_PLUGIN",
                    message="WebSocket connection failed",
                    error=result.get('error') if result else 'Unknown error'
                )

        except Exception as e:
            execute_operation(
                EEGatewayInterface.DEBUG,
                'log',
                corr_id=correlation_id,
                scope="HA_PLUGIN",
                message="WebSocket setup exception",
                error=str(e)
            )

    def _close_websocket(self, correlation_id: str) -> None:
        """
        Close WebSocket connection.

        Args:
            correlation_id: Correlation ID for tracking
        """
        from EE import execute_operation, EEGatewayInterface

        execute_operation(
            EEGatewayInterface.DEBUG,
            'log',
            corr_id=correlation_id,
            scope="HA_PLUGIN",
            message="Closing WebSocket connection"
        )

        # Note: WEBSOCKET interface would need a disconnect operation
        self._websocket_connected = False

    # ===== CONFIGURATION METHODS =====

    def _load_config(self, correlation_id: str) -> None:
        """
        Load HA configuration from environment variables.

        Args:
            correlation_id: Correlation ID for tracking
        """
        import os
        from EE import execute_operation, EEGatewayInterface

        self._ha_url = execute_operation(
            EEGatewayInterface.CONFIG,
            'get',
            key='home_assistant.url',
            default='http://localhost:8123'
        )

        self._ha_token = execute_operation(
            EEGatewayInterface.CONFIG,
            'get',
            key='home_assistant.token',
            default=''
        )

        execute_operation(
            EEGatewayInterface.DEBUG,
            'log',
            corr_id=correlation_id,
            scope="HA_PLUGIN",
            message="HA config loaded",
            ha_url_present=bool(self._ha_url),
            ha_token_present=bool(self._ha_token)
        )

    def _init_ha_client(self, correlation_id: str) -> None:
        """
        Initialize HA client (placeholder for future client logic).

        Args:
            correlation_id: Correlation ID for tracking
        """
        from EE import execute_operation, EEGatewayInterface

        execute_operation(
            EEGatewayInterface.DEBUG,
            'log',
            corr_id=correlation_id,
            scope="HA_PLUGIN",
            message="HA client initialized"
        )

        # HA client initialization would go here
        # For now, using EE Gateway interfaces directly

    # ===== STATUS METHODS =====

    def get_status(self) -> Dict[str, Any]:
        """Get plugin status information."""
        from EE import execute_operation, EEGatewayInterface

        status = super().get_status()
        status.update({
            'ha_url': self._ha_url,
            'ha_configured': bool(self._ha_url and self._ha_token),
            'websocket_connected': self._websocket_connected,
            'cached_states': len(self._states_cache),
        })

        return status


__all__ = ['HAPlugin']
