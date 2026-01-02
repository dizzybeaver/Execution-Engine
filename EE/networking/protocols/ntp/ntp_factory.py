"""
NTP Factory - Networking Domain

NTP protocol implementation (RFC 5905).

UG-ISP Compliant:
- Factory contains actual implementation
- Receives get_logger, get_metrics, call_operation via DI
- NO imports outside networking domain (except stdlib)
- Implements NTP protocol
"""

import socket
import struct
import time
import logging
from typing import Any, Dict, Optional, Callable


class NTPFactory:
    """NTP factory.

    Provides NTP protocol operations:
    - get_time: Get time from NTP server
    - sync: Get time offset for synchronization

    UG-ISP Compliance:
    - Uses only standard library
    - Implements NTP protocol (RFC 5905)
    - Cross-domain calls via call_operation callback
    """

    # NTP constants
    NTP_DELTA = 2208988800  # Seconds between 1900 and 1970
    NTP_PACKET_SIZE = 48
    NTP_VERSION = 4

    def __init__(
        self,
        get_logger: Optional[Callable] = None,
        get_metrics: Optional[Callable] = None,
        call_operation: Optional[Callable] = None
    ):
        """Initialize NTP factory.

        Args:
            get_logger: Logger factory function
            get_metrics: Metrics factory function
            call_operation: Callback for cross-domain operations
        """
        if get_logger:
            self.logger = get_logger("networking.protocols.ntp")
        else:
            self.logger = logging.getLogger(__name__)

        self.metrics = get_metrics
        self.call_operation = call_operation

    def get_time(
        self,
        host: str = 'pool.ntp.org',
        port: int = 123,
        timeout: int = 10,
        **kwargs
    ) -> Dict[str, Any]:
        """Get time from NTP server.

        Args:
            host: NTP server host (default: pool.ntp.org)
            port: NTP server port (default: 123)
            timeout: Request timeout in seconds

        Returns:
            Dictionary with:
                - server_time: NTP server time (Unix timestamp)
                - local_time: Local time when response received
                - offset: Estimated time offset (seconds)
                - delay: Round-trip delay (seconds)
                - stratum: NTP server stratum level
                - precision: NTP server precision

        Example:
            factory = NTPFactory()
            result = factory.get_time(host="pool.ntp.org")
            print(f"Server time: {result['server_time']}")
        """
        self.logger.debug(f"NTP get_time: {host}:{port}")

        # Create UDP socket
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client.settimeout(timeout)

        try:
            # Build NTP request packet
            packet = bytearray(self.NTP_PACKET_SIZE)
            # LI=0, VN=4, Mode=3 (client)
            packet[0] = (0 << 6) | (self.NTP_VERSION << 3) | 3

            # Record local time before sending
            t1 = time.time()

            # Send request
            client.sendto(packet, (host, port))

            # Receive response
            data, _ = client.recvfrom(1024)
            if not data or len(data) < self.NTP_PACKET_SIZE:
                raise ConnectionError('Invalid NTP response')

            # Record local time after receiving
            t4 = time.time()

            # Parse NTP response
            unpacked = struct.unpack('!12I', data)

            # Extract timestamps
            t2_ntp = unpacked[10]  # Transmit timestamp
            t3_ntp = unpacked[11]  # Reference timestamp

            # Convert NTP time to Unix time
            if t2_ntp > 0:
                server_time = t2_ntp - self.NTP_DELTA
            else:
                server_time = t4  # Fallback to local time

            # Calculate offset and delay
            offset = ((server_time - t1) + (server_time - t4)) / 2
            delay = t4 - t1

            # Extract stratum and precision
            stratum = unpacked[1] >> 24
            precision = unpacked[3]

            return {
                'server_time': server_time,
                'local_time': t4,
                'offset': offset,
                'delay': delay,
                'stratum': stratum,
                'precision': precision,
                'host': host
            }

        except socket.timeout:
            raise TimeoutError(f'NTP request to {host} timed out')
        except Exception as e:
            raise ConnectionError(f'NTP request failed: {e}')
        finally:
            client.close()

    def sync(
        self,
        host: str = 'pool.ntp.org',
        port: int = 123,
        timeout: int = 10,
        **kwargs
    ) -> float:
        """Get time offset for synchronization.

        Args:
            host: NTP server host
            port: NTP server port
            timeout: Request timeout in seconds

        Returns:
            Time offset in seconds (positive = server ahead, negative = server behind)

        Example:
            factory = NTPFactory()
            offset = factory.sync(host="pool.ntp.org")
            if offset > 0:
                print(f"Server is {offset:.3f} seconds ahead")
            else:
                print(f"Server is {-offset:.3f} seconds behind")
        """
        result = self.get_time(host=host, port=port, timeout=timeout)
        return result['offset']


__all__ = [
    "NTPFactory",
]
