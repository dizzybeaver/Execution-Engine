"""
FaaS Plugin - Function as a Service plugin for EE.

This plugin provides serverless function execution capabilities
by integrating the FaaS (LocalLambda) gateway with EE architecture.

UG-ISP Architecture:
- Inherits from EEPlugin base class
- Uses EE Gateway for all operations (cache, logging, config)
- No duplicate functionality - delegates to EE interfaces
- FaaS-specific logic only

Plugin Features:
- Entity management (discover, save, load, get, list)
- Server management (start, stop, restart, status, health)
- Test scenario operations
- Mock context operations
- Test result operations

Configuration:
- Port: 5001 (configurable via ee_config.yaml)
- Home Assistant URL/Token from EE config
"""

import time
import random
from typing import Any, Dict
from pathlib import Path

from plugins import EEPlugin, plugin


@plugin
class FaaSPlugin(EEPlugin):
    """FaaS Gateway plugin for EE.

    Provides serverless function execution with Home Assistant integration.
    """

    name = "faas"
    version = "1.0.0"
    description = "Function as a Service plugin for serverless execution"

    def __init__(self):
        """Initialize FaaS plugin."""
        self.gateway = None
        self.config = {}
        self.server_running = False
        self.server_port = 5001
        self.entity_manager = None

    def initialize(self, gateway: Any) -> None:
        """Initialize FaaS plugin with EE Gateway.

        Args:
            gateway: EE Gateway instance for cross-interface operations
        """
        from EE import execute_operation, GatewayInterface

        self.gateway = gateway

        # Generate correlation ID
        corr_id = f"faas_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"

        # Log initialization via EE Gateway (UG-ISP compliant)
        execute_operation(
            GatewayInterface.LOGGING,
            'log_info',
            message="FaaS plugin initialization started"
        )

        # Get FaaS configuration from EE config
        self.config = execute_operation(
            GatewayInterface.CONFIG,
            'get',
            key='faas'
        ) or {}

        # Set server port from config
        self.server_port = self.config.get('port', 5001)

        # Initialize entity manager
        self._initialize_entity_manager()

        # Log success via EE Gateway
        execute_operation(
            GatewayInterface.LOGGING,
            'log_info',
            message=f"FaaS plugin initialized on port {self.server_port}"
        )

    def _initialize_entity_manager(self):
        """Initialize FaaS entity manager."""
        from EE import execute_operation, GatewayInterface

        # Lazy import FaaS entity manager
        import sys
        faas_path = Path(__file__).parent.parent.parent.parent / 'src' / 'faas'
        if str(faas_path) not in sys.path:
            sys.path.insert(0, str(faas_path))

        try:
            from core.entity_manager import get_entity_manager
            self.entity_manager = get_entity_manager()

            execute_operation(
                GatewayInterface.LOGGING,
                'log_info',
                message="FaaS entity manager initialized"
            )
        except ImportError as e:
            execute_operation(
                GatewayInterface.LOGGING,
                'log_error',
                message=f"Failed to initialize FaaS entity manager: {e}"
            )

    def shutdown(self) -> None:
        """Shutdown FaaS plugin and cleanup resources."""
        from EE import execute_operation, GatewayInterface

        # Stop server if running
        if self.server_running:
            self._stop_server()

        # Cleanup entity manager
        self.entity_manager = None

        # Log shutdown via EE Gateway
        execute_operation(
            GatewayInterface.LOGGING,
            'log_info',
            message="FaaS plugin shutdown complete"
        )

    # ========================================================================
    # FaaS Entity Operations
    # ========================================================================

    def discover_entities(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Discover entities from Home Assistant.

        Args:
            force_refresh: Force refresh from HA

        Returns:
            Dict with discovered entities and count
        """
        from EE import execute_operation, GatewayInterface

        if not self.entity_manager:
            return {'entities': [], 'count': 0, 'error': 'Entity manager not initialized'}

        entities = self.entity_manager.discover_entities(force_refresh=force_refresh)

        execute_operation(
            GatewayInterface.LOGGING,
            'log_info',
            message=f"Discovered {len(entities)} entities"
        )

        return {'entities': entities, 'count': len(entities)}

    def get_entity(self, entity_id: str) -> Dict[str, Any]:
        """Get specific entity by ID.

        Args:
            entity_id: Entity ID to retrieve

        Returns:
            Dict with entity data and found flag
        """
        if not self.entity_manager:
            return {'entity': None, 'found': False, 'error': 'Entity manager not initialized'}

        entity = self.entity_manager.get_entity(entity_id)

        return {'entity': entity, 'found': entity is not None}

    def list_entities(self, domain: str = None) -> Dict[str, Any]:
        """List entities, optionally filtered by domain.

        Args:
            domain: Optional domain filter

        Returns:
            Dict with entities list and count
        """
        if not self.entity_manager:
            return {'entities': [], 'count': 0, 'error': 'Entity manager not initialized'}

        entities = self.entity_manager.list_entities(domain=domain)

        return {'entities': entities, 'count': len(entities), 'domain': domain}

    # ========================================================================
    # FaaS Server Operations
    # ========================================================================

    def start_server(self) -> Dict[str, Any]:
        """Start FaaS server.

        Returns:
            Dict with start status and server info
        """
        from EE import execute_operation, GatewayInterface

        if self.server_running:
            return {'started': False, 'message': 'Server already running'}

        # Start server (placeholder for actual implementation)
        self.server_running = True

        execute_operation(
            GatewayInterface.LOGGING,
            'log_info',
            message=f"FaaS server started on port {self.server_port}"
        )

        return {
            'started': True,
            'port': self.server_port,
            'message': f'FaaS server started on port {self.server_port}'
        }

    def stop_server(self) -> Dict[str, Any]:
        """Stop FaaS server.

        Returns:
            Dict with stop status
        """
        from EE import execute_operation, GatewayInterface

        if not self.server_running:
            return {'stopped': False, 'message': 'Server not running'}

        # Stop server (placeholder for actual implementation)
        self.server_running = False

        execute_operation(
            GatewayInterface.LOGGING,
            'log_info',
            message="FaaS server stopped"
        )

        return {'stopped': True, 'message': 'FaaS server stopped'}

    def restart_server(self) -> Dict[str, Any]:
        """Restart FaaS server.

        Returns:
            Dict with restart status and server info
        """
        # Stop if running
        if self.server_running:
            self.stop_server()

        # Start server
        return self.start_server()

    def get_server_status(self) -> Dict[str, Any]:
        """Get FaaS server status.

        Returns:
            Dict with server status information
        """
        return {
            'running': self.server_running,
            'port': self.server_port if self.server_running else None,
            'entity_manager_initialized': self.entity_manager is not None
        }

    def get_server_health(self) -> Dict[str, Any]:
        """Get FaaS server health.

        Returns:
            Dict with health check results
        """
        entity_count = 0
        if self.entity_manager:
            summary = self.entity_manager.get_entity_summary()
            entity_count = summary.get('total', 0)

        return {
            'healthy': True,
            'checks': {
                'server': 'healthy' if self.server_running else 'stopped',
                'entity_manager': 'healthy' if self.entity_manager else 'not_initialized',
                'entities': entity_count
            }
        }

    # ========================================================================
    # Plugin Lifecycle Hooks
    # ========================================================================

    def on_enable(self) -> None:
        """Called when plugin is enabled."""
        from EE import execute_operation, GatewayInterface

        execute_operation(
            GatewayInterface.LOGGING,
            'log_info',
            message="FaaS plugin enabled"
        )

    def on_disable(self) -> None:
        """Called when plugin is disabled."""
        from EE import execute_operation, GatewayInterface

        # Stop server if running
        if self.server_running:
            self.stop_server()

        execute_operation(
            GatewayInterface.LOGGING,
            'log_info',
            message="FaaS plugin disabled"
        )

    def get_status(self) -> Dict[str, Any]:
        """Get plugin status information.

        Returns:
            Dict with plugin status details
        """
        status = super().get_status()

        # Add FaaS-specific status
        status['server_running'] = self.server_running
        status['server_port'] = self.server_port
        status['entity_manager_initialized'] = self.entity_manager is not None

        if self.entity_manager:
            summary = self.entity_manager.get_entity_summary()
            status['entity_count'] = summary.get('total', 0)

        return status

    # ========================================================================
    # Private Helper Methods
    # ========================================================================

    def _stop_server(self) -> None:
        """Internal method to stop server."""
        self.server_running = False
