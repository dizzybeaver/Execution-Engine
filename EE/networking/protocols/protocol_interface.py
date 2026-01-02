"""
Base Protocol Interface - Networking Domain

This module provides the base class for all protocol implementations.
Each protocol implements a consistent interface pattern.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseProtocol(ABC):
    """Base class for all protocol implementations.

    All network protocols should inherit from this class and implement
    the required methods.
    """

    def __init__(self, host: str, port: int, timeout: int = 10):
        """Initialize protocol client.

        Args:
            host: Server host
            port: Server port
            timeout: Connection timeout in seconds
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self._connected = False

    @abstractmethod
    def connect(self) -> bool:
        """Connect to server.

        Returns:
            True if connection successful
        """
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from server."""
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """Check if connected to server.

        Returns:
            True if connected
        """
        pass


__all__ = [
    "BaseProtocol",
]
