"""System Collector

Collects and provides system information with caching.

Ported from UGA observability foundation (2026-03-08)
Ref: ee-obs-metadata-system-core

Security Considerations:
- System information collection is read-only
- IP address detection uses external connectivity (8.8.8.8:80)
- Cached to avoid repeated system calls
- No sensitive data exposure

Lambda Impact:
    Memory: ~5KB for cached system info
    Cold start: +20ms (first call only)
    Runtime: <1ms (cached), ~10ms (cache miss)
"""

import platform
import socket
import threading
from datetime import datetime, timezone


class SystemCollector:
    """System information collector with caching.

    Collects platform, Python version, hostname, machine architecture,
    processor info, and IP address. Results are cached to avoid
    repeated system calls.

    Attributes:
        _cached_info: Cached system information dictionary
        _cache_timestamp: Cache timestamp
        _cache_ttl: Cache time-to-live in seconds (default 60)
        _data_lock: Thread safety lock for cache operations

    Caching:
        - Cache TTL: 60 seconds (configurable)
        - Thread-safe cache updates
        - Force refresh available via get_system_info(force_refresh=True)

    Lambda Impact:
        - Cold start: ~20ms (first call)
        - Cached calls: <1ms
        - Memory: ~5KB

    """

    _default_cache_ttl = 60

    def __init__(self, cache_ttl: int = 60):
        """Initialize SystemCollector with caching.

        Args:
            cache_ttl: Cache time-to-live in seconds (default 60)

        Note:
            cache_ttl determines how long system info remains valid
            before automatic refresh.

        """
        self._cached_info = None
        self._cache_timestamp = None
        self._cache_ttl = cache_ttl
        self._data_lock = threading.Lock()

    def get_system_info(self, force_refresh: bool = False) -> dict:
        """Get system information.

        Args:
            force_refresh: Force refresh of cached information

        Returns:
            System information dictionary with keys:
            - platform: Platform description
            - python_version: Python version
            - hostname: System hostname
            - machine: Machine architecture
            - processor: Processor info
            - ip_address: Local IP address (may be None)
            - timestamp: Collection timestamp

        Example:
            >>> collector = SystemCollector()
            >>> info = collector.get_system_info()
            >>> print(info['python_version'])
            '3.9.16'

        """
        if force_refresh or self._is_cache_expired():
            self._refresh_cache()

        return dict(self._cached_info) if self._cached_info else {}

    def get_platform(self) -> str:
        """Get platform string.

        Returns:
            Platform description (e.g., 'Linux-5.15.0-x86_64')

        Example:
            >>> collector = SystemCollector()
            >>> collector.get_platform()
            'Windows-10-10.0.19041'

        """
        return platform.platform()

    def get_python_version(self) -> str:
        """Get Python version.

        Returns:
            Python version string (e.g., '3.9.16')

        Example:
            >>> collector = SystemCollector()
            >>> collector.get_python_version()
            '3.9.16'

        """
        return platform.python_version()

    def get_hostname(self) -> str:
        """Get system hostname.

        Returns:
            Hostname string

        Example:
            >>> collector = SystemCollector()
            >>> collector.get_hostname()
            'lee-lambda-container'

        """
        return platform.node()

    def get_machine(self) -> str:
        """Get machine architecture.

        Returns:
            Machine architecture string (e.g., 'x86_64', 'AMD64')

        Example:
            >>> collector = SystemCollector()
            >>> collector.get_machine()
            'x86_64'

        """
        return platform.machine()

    def get_processor(self) -> str:
        """Get processor information.

        Returns:
            Processor string (may be empty on some systems)

        Example:
            >>> collector = SystemCollector()
            >>> collector.get_processor()
            'Intel(R) Xeon(R) CPU @ 2.50GHz'

        """
        return platform.processor()

    def get_ip_address(self) -> str | None:
        """Get local IP address.

        Returns:
            IP address string or None if unavailable

        Note:
            This method attempts to connect to 8.8.8.8:80 (Google DNS)
            to determine the local IP address. No data is sent.

        Example:
            >>> collector = SystemCollector()
            >>> collector.get_ip_address()
            '192.168.1.100'

        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                ip = s.getsockname()[0]
                return ip
        except (ConnectionError, OSError, socket.error):
            return None

    def _is_cache_expired(self) -> bool:
        """Check if cache is expired.

        Returns:
            True if cache is expired or not set

        """
        if self._cache_timestamp is None:
            return True

        age = (datetime.now() - self._cache_timestamp).total_seconds()
        return age > self._cache_ttl

    def _refresh_cache(self) -> None:
        """Refresh cached system information.

        Thread-safe cache update with current system information.
        """
        with self._data_lock:
            self._cached_info = {
                "platform": self.get_platform(),
                "python_version": self.get_python_version(),
                "hostname": self.get_hostname(),
                "machine": self.get_machine(),
                "processor": self.get_processor(),
                "ip_address": self.get_ip_address(),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            self._cache_timestamp = datetime.now()


# Module-level singleton instance
_system_collector_instance = None
_system_collector_lock = threading.Lock()


def get_system_collector(cache_ttl: int = 60) -> SystemCollector:
    """Get singleton SystemCollector instance.

    Thread-safe singleton accessor with lazy initialization.

    Args:
        cache_ttl: Cache TTL in seconds (only used on first call)

    Returns:
        Singleton SystemCollector instance

    Thread Safety:
        Thread-safe initialization using double-checked locking

    Example:
        >>> from lee.metadata import get_system_collector
        >>> collector = get_system_collector()
        >>> info = collector.get_system_info()

    """
    global _system_collector_instance

    if _system_collector_instance is None:
        with _system_collector_lock:
            # Double-check lock pattern
            if _system_collector_instance is None:
                _system_collector_instance = SystemCollector(cache_ttl=cache_ttl)

    return _system_collector_instance


# ===== GATEWAY INTERFACE IMPLEMENTATIONS =====

def _get_system_info_implementation(force_refresh: bool = False, **kwargs) -> dict:
    """Get system information (gateway interface implementation)."""
    collector = get_system_collector()
    info = collector.get_system_info(force_refresh=force_refresh)
    return {"status": "ok", "system_info": info}


__all__ = [
    "SystemCollector",
    "_get_system_info_implementation",
    "get_system_collector",
]
