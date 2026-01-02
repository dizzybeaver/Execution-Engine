"""
Gateway Registry - DI-injectable registry for domain gateways in UG architecture.

This module provides the EEDomainRegistry class that manages all domain
gateways in the EE system. The registry provides centralized registration,
lookup, and lifecycle management.

Architecture:
    UniversalGateway → EEDomainRegistry → DomainGateway instances

Features:
    - Thread-safe domain registration
    - Domain registration and lookup
    - Domain validation
    - Statistics and listing
    - Error handling with descriptive messages

Type Hints:
    - Complete type coverage for all public methods
    - Proper exception types
    - Return type annotations

EE 2.1 Architecture Compliance:
    - Registry is DI-injected (not global singleton)
    - Direct instantiation supported
    - Thread-safe operations using instance locks
"""

from __future__ import annotations
from typing import Dict, List, Optional, Any
from threading import Lock

from EE.universal_gateway.domain_gateway import DomainGateway


# ============================================================================
# Exceptions
# ============================================================================

class RegistryError(Exception):
    """Base exception for registry errors."""
    pass


class DomainNotRegisteredError(RegistryError):
    """Raised when attempting to access an unregistered domain."""
    pass


class DomainAlreadyRegisteredError(RegistryError):
    """Raised when attempting to register a duplicate domain."""
    pass


# ============================================================================
# Domain Registry
# ============================================================================

class EEDomainRegistry:
    """DI-injectable registry for EE domain gateways.

    This registry manages all domain gateways in the EE system, providing
    centralized registration, lookup, and lifecycle management.

    Thread Safety:
        The registry is thread-safe. All methods that modify internal state
        use locking to prevent race conditions.

    EE 2.1 Architecture:
        This registry is designed for dependency injection. It should be
        instantiated once and injected into components that need it.
        Do NOT use singleton patterns - create instances directly and
        inject them where needed.

    Usage:
        # Create registry instance (typically in application setup)
        registry = EEDomainRegistry()

        # Register a domain gateway
        registry.register("config", config_gateway)

        # Get a domain gateway
        gateway = registry.get("config")

        # Check if domain exists
        if registry.has_domain("config"):
            print("Config domain is registered")

        # List all domains
        domains = registry.list_domains()

        # Get registry statistics
        stats = registry.get_stats()

    Error Handling:
        - DomainNotRegisteredError: When accessing unregistered domain
        - DomainAlreadyRegisteredError: When registering duplicate domain
        - RegistryError: Base class for registry errors
    """

    # FIXED: Removed singleton pattern - no more _instance or _lock class variables
    _domains: Dict[str, DomainGateway]
    _domain_lock: Lock

    def __init__(self) -> None:
        """Initialize the registry.

        Creates a new registry instance. This should be called once during
        application setup and the instance should be injected into components
        that need domain registry access.

        Example:
            # In application setup
            registry = EEDomainRegistry()
            registry.register("config", ConfigGateway(...))

            # Inject into components that need it
            gateway = UniversalGateway(registry=registry)
        """
        # FIXED: Removed _initialized check - simple direct initialization
        self._domains: Dict[str, DomainGateway] = {}
        self._domain_lock: Lock = Lock()

    # REMOVED: get_instance() classmethod - singleton pattern eliminated
    # REMOVED: reset_instance() classmethod - singleton pattern eliminated

    def register(
        self,
        domain_name: str,
        gateway: DomainGateway,
    ) -> None:
        """Register a domain gateway.

        Args:
            domain_name: Unique identifier for the domain (e.g., "config", "security")
            gateway: Domain gateway instance to register

        Raises:
            DomainAlreadyRegisteredError: If domain already registered
            ValueError: If domain_name is empty or gateway is None

        Example:
            registry = EEDomainRegistry()
            registry.register("config", ConfigGateway(...))
        """
        if not domain_name:
            raise ValueError("Domain name cannot be empty")

        if gateway is None:
            raise ValueError("Gateway cannot be None")

        with self._domain_lock:
            if domain_name in self._domains:
                raise DomainAlreadyRegisteredError(
                    f"Domain '{domain_name}' is already registered. "
                    f"Use update() to replace an existing domain."
                )

            self._domains[domain_name] = gateway

    def update(
        self,
        domain_name: str,
        gateway: DomainGateway,
    ) -> None:
        """Update or register a domain gateway.

        Unlike register(), this method allows replacing an existing domain.

        Args:
            domain_name: Unique identifier for the domain
            gateway: Domain gateway instance to register

        Example:
            registry.update("config", new_config_gateway)
        """
        if not domain_name:
            raise ValueError("Domain name cannot be empty")

        if gateway is None:
            raise ValueError("Gateway cannot be None")

        with self._domain_lock:
            self._domains[domain_name] = gateway

    def get(self, domain_name: str) -> DomainGateway:
        """Get a domain gateway by name.

        Args:
            domain_name: Domain identifier

        Returns:
            Domain gateway instance

        Raises:
            DomainNotRegisteredError: If domain not registered

        Example:
            gateway = registry.get("config")
            result = gateway.execute_domain_operation(...)
        """
        if domain_name not in self._domains:
            available = list(self._domains.keys())
            raise DomainNotRegisteredError(
                f"Domain '{domain_name}' is not registered. "
                f"Available domains: {available}"
            )

        return self._domains[domain_name]

    def get_optional(
        self,
        domain_name: str,
    ) -> Optional[DomainGateway]:
        """Get a domain gateway by name, returning None if not found.

        This is a convenience method that doesn't raise an exception.

        Args:
            domain_name: Domain identifier

        Returns:
            Domain gateway instance or None

        Example:
            gateway = registry.get_optional("config")
            if gateway:
                result = gateway.execute_domain_operation(...)
        """
        return self._domains.get(domain_name)

    def has_domain(self, domain_name: str) -> bool:
        """Check if a domain is registered.

        Args:
            domain_name: Domain identifier

        Returns:
            True if domain is registered, False otherwise

        Example:
            if registry.has_domain("config"):
                gateway = registry.get("config")
        """
        return domain_name in self._domains

    def list_domains(self) -> List[str]:
        """List all registered domain names.

        Returns:
            List of domain identifiers

        Example:
            domains = registry.list_domains()
            print(f"Registered domains: {domains}")
        """
        with self._domain_lock:
            return list(self._domains.keys())

    def unregister(self, domain_name: str) -> None:
        """Unregister a domain gateway.

        Args:
            domain_name: Domain identifier

        Raises:
            DomainNotRegisteredError: If domain not registered

        Example:
            registry.unregister("config")
        """
        with self._domain_lock:
            if domain_name not in self._domains:
                raise DomainNotRegisteredError(
                    f"Domain '{domain_name}' is not registered"
                )

            del self._domains[domain_name]

    def clear(self) -> None:
        """Clear all registered domains.

        Warning:
            This removes all domain registrations. Use with caution,
            mainly intended for testing.

        Example:
            registry.clear()
        """
        with self._domain_lock:
            self._domains.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics.

        Returns:
            Dictionary with registry statistics:
            {
                "total_domains": 5,
                "domains": ["config", "security", "logging", "metrics", "debug"]
            }

        Example:
            stats = registry.get_stats()
            print(f"Total domains: {stats['total_domains']}")
        """
        with self._domain_lock:
            return {
                "total_domains": len(self._domains),
                "domains": list(self._domains.keys()),
            }

    def list_all_operations(self) -> Dict[str, Any]:
        """List all operations from all registered domains.

        This method aggregates operation information from all domain gateways.

        Returns:
            Dictionary mapping domain names to their operations:
            {
                "config": {"domain": "config", "interfaces": [...]},
                "security": {"domain": "security", "interfaces": [...]},
                ...
            }

        Example:
            all_ops = registry.list_all_operations()
            for domain, ops in all_ops.items():
                print(f"{domain}: {ops}")
        """
        result: Dict[str, Any] = {}

        with self._domain_lock:
            domain_items = list(self._domains.items())

        for domain_name, gateway in domain_items:
            try:
                result[domain_name] = gateway.list_all()
            except Exception as e:
                result[domain_name] = {
                    "error": f"Failed to list operations: {e}"
                }

        return result

    def get_domain_count(self) -> int:
        """Get the number of registered domains.

        Returns:
            Number of registered domains

        Example:
            count = registry.get_domain_count()
            print(f"Registered {count} domains")
        """
        with self._domain_lock:
            return len(self._domains)


__all__ = [
    'EEDomainRegistry',

    # Exceptions
    'RegistryError',
    'DomainNotRegisteredError',
    'DomainAlreadyRegisteredError',
]
