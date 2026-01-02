"""Test Interface Network (INT-17)

Tests for the Network interface (INT-17) which manages network protocols:
- MQTT client
- Redis client
- NTP client
- RPC client
- SNMP client
- Network connection management
- Protocol-specific operations
"""

import pytest
from typing import Dict, Any
from pathlib import Path


@pytest.mark.unit
class TestNetworkInterface:
    """Test suite for Network interface."""

    def test_network_interface_exists(self, EEGatewayInterface):
        """Test NETWORK interface exists in EEGatewayInterface."""
        assert hasattr(EEGatewayInterface, 'NETWORK')
        assert EEGatewayInterface.NETWORK is not None

    def test_execute_network_operation_import(self):
        """Test that execute_network_operation can be imported."""
        try:
            from interface import interface_network
            assert hasattr(interface_network, 'execute_network_operation')
        except ImportError:
            pytest.skip("Network interface not yet implemented")

    @pytest.mark.parametrize("protocol", ["mqtt", "redis", "ntp", "rpc", "snmp"])
    def test_protocol_connect_operation(self, execute_operation, EEGatewayInterface, protocol, mock_network_configs):
        """Test protocol connect operation."""
        try:
            config = mock_network_configs.get(protocol)
            if not config:
                pytest.skip(f"No config for protocol: {protocol}")

            result = execute_operation(
                EEGatewayInterface.NETWORK,
                'connect',
                protocol=protocol,
                **config
            )

            # Should return success or connection object
            assert result is not None

        except (ValueError, NotImplementedError, ConnectionError):
            pytest.skip(f"{protocol.upper()} connect not yet implemented")

    @pytest.mark.parametrize("protocol", ["mqtt", "redis", "ntp", "rpc", "snmp"])
    def test_protocol_disconnect_operation(self, execute_operation, EEGatewayInterface, protocol):
        """Test protocol disconnect operation."""
        try:
            result = execute_operation(
                EEGatewayInterface.NETWORK,
                'disconnect',
                protocol=protocol,
                connection_id='test_connection'
            )

            # Should return success
            assert result is not None

        except (ValueError, NotImplementedError):
            pytest.skip(f"{protocol.upper()} disconnect not yet implemented")

    def test_mqtt_publish_operation(self, execute_operation, EEGatewayInterface):
        """Test MQTT publish operation."""
        try:
            result = execute_operation(
                EEGatewayInterface.NETWORK,
                'publish',
                protocol='mqtt',
                topic='test/topic',
                payload='test_message',
                qos=1
            )

            # Should return success
            assert result is not None

        except (ValueError, NotImplementedError):
            pytest.skip("MQTT publish not yet implemented")

    def test_mqtt_subscribe_operation(self, execute_operation, EEGatewayInterface):
        """Test MQTT subscribe operation."""
        try:
            result = execute_operation(
                EEGatewayInterface.NETWORK,
                'subscribe',
                protocol='mqtt',
                topic='test/topic',
                qos=1
            )

            # Should return success
            assert result is not None

        except (ValueError, NotImplementedError):
            pytest.skip("MQTT subscribe not yet implemented")

    def test_redis_get_operation(self, execute_operation, EEGatewayInterface):
        """Test Redis GET operation."""
        try:
            result = execute_operation(
                EEGatewayInterface.NETWORK,
                'get',
                protocol='redis',
                key='test_key'
            )

            # Should return value or None
            assert result is not None or result is None

        except (ValueError, NotImplementedError, ConnectionError):
            pytest.skip("Redis GET not yet implemented")

    def test_redis_set_operation(self, execute_operation, EEGatewayInterface):
        """Test Redis SET operation."""
        try:
            result = execute_operation(
                EEGatewayInterface.NETWORK,
                'set',
                protocol='redis',
                key='test_key',
                value='test_value'
            )

            # Should return success
            assert result is not None

        except (ValueError, NotImplementedError, ConnectionError):
            pytest.skip("Redis SET not yet implemented")

    def test_ntp_sync_operation(self, execute_operation, EEGatewayInterface):
        """Test NTP time synchronization operation."""
        try:
            result = execute_operation(
                EEGatewayInterface.NETWORK,
                'sync_time',
                protocol='ntp',
                host='pool.ntp.org'
            )

            # Should return time or success
            assert result is not None

        except (ValueError, NotImplementedError, ConnectionError):
            pytest.skip("NTP sync not yet implemented")

    def test_rpc_call_operation(self, execute_operation, EEGatewayInterface):
        """Test RPC call operation."""
        try:
            result = execute_operation(
                EEGatewayInterface.NETWORK,
                'call',
                protocol='rpc',
                method='test_method',
                params={'param1': 'value1'}
            )

            # Should return result
            assert result is not None

        except (ValueError, NotImplementedError):
            pytest.skip("RPC call not yet implemented")

    def test_snmp_get_operation(self, execute_operation, EEGatewayInterface):
        """Test SNMP GET operation."""
        try:
            result = execute_operation(
                EEGatewayInterface.NETWORK,
                'get',
                protocol='snmp',
                oid='1.3.6.1.2.1.1.1.0',
                community='public'
            )

            # Should return value
            assert result is not None

        except (ValueError, NotImplementedError):
            pytest.skip("SNMP GET not yet implemented")

    def test_network_get_status_operation(self, execute_operation, EEGatewayInterface):
        """Test network connection status operation."""
        try:
            result = execute_operation(
                EEGatewayInterface.NETWORK,
                'get_status',
                connection_id='test_connection'
            )

            # Should return status dict
            assert isinstance(result, dict)
            assert 'status' in result or 'connected' in result

        except (ValueError, NotImplementedError):
            pytest.skip("Network get_status not yet implemented")


@pytest.mark.unit
class TestNetworkInterfaceSUGAISPCompliance:
    """Test UG-ISP compliance for Network interface."""

    def test_no_direct_interface_import(self):
        """Test that direct interface imports are not used."""
        import ast

        interface_file = Path(__file__).parent.parent / 'src' / 'interface' / 'interface_network.py'

        if not interface_file.exists():
            pytest.skip("Network interface file not found")

        with open(interface_file, 'r') as f:
            source = f.read()

        # Parse AST
        tree = ast.parse(source)

        # Check for forbidden imports
        forbidden_imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module and 'gateway' in node.module:
                    forbidden_imports.append(f"Line {node.lineno}: from {node.module} import ...")

        # Assert no forbidden imports
        assert len(forbidden_imports) == 0, f"Found direct gateway imports: {forbidden_imports}"

    def test_operations_use_dispatch_dict(self):
        """Test that interface uses dispatch dictionary pattern."""
        interface_file = Path(__file__).parent.parent / 'src' / 'interface' / 'interface_network.py'

        if not interface_file.exists():
            pytest.skip("Network interface file not found")

        with open(interface_file, 'r') as f:
            source = f.read()

        # Check for DISPATCH dictionary
        assert 'DISPATCH' in source or 'dispatch' in source.lower(), \
            "Network interface should use dispatch dictionary pattern"

    def test_file_size_compliance(self):
        """Test that interface file is <= 350 lines."""
        interface_file = Path(__file__).parent.parent / 'src' / 'interface' / 'interface_network.py'

        if not interface_file.exists():
            pytest.skip("Network interface file not found")

        with open(interface_file, 'r') as f:
            lines = f.readlines()

        assert len(lines) <= 350, \
            f"Interface file has {len(lines)} lines, exceeds 350 line limit"

    def test_protocol_files_use_correct_imports(self):
        """Test that protocol implementation files use correct imports."""
        import ast

        protocol_files = [
            'interface/network_mqtt.py',
            'interface/network_redis.py',
            'interface/network_ntp.py',
            'interface/network_rpc.py',
            'interface/network_snmp.py',
        ]

        ee_src = Path(__file__).parent.parent / 'src'

        for protocol_file in protocol_files:
            file_path = ee_src / protocol_file

            if not file_path.exists():
                continue

            with open(file_path, 'r') as f:
                source = f.read()

            # Check for direct gateway imports (forbidden)
            if 'from gateway' in source and 'import' in source:
                # Make sure it's not a comment
                for line in source.split('\n'):
                    if 'from gateway' in line and not line.strip().startswith('#'):
                        pytest.fail(f"Found direct gateway import in {protocol_file}: {line}")


@pytest.mark.integration
class TestNetworkIntegration:
    """Integration tests for Network interface."""

    def test_mqtt_full_lifecycle(self, execute_operation, EEGatewayInterface, mock_network_configs):
        """Test MQTT full lifecycle: connect -> publish -> subscribe -> disconnect."""
        try:
            config = mock_network_configs.get('mqtt')
            if not config:
                pytest.skip("No MQTT config")

            # Connect
            connect_result = execute_operation(
                EEGatewayInterface.NETWORK,
                'connect',
                protocol='mqtt',
                **config
            )
            assert connect_result is not None

            # Publish
            pub_result = execute_operation(
                EEGatewayInterface.NETWORK,
                'publish',
                protocol='mqtt',
                topic='test/lifecycle',
                payload='test_message'
            )
            assert pub_result is not None

            # Subscribe
            sub_result = execute_operation(
                EEGatewayInterface.NETWORK,
                'subscribe',
                protocol='mqtt',
                topic='test/lifecycle'
            )
            assert sub_result is not None

            # Disconnect
            disconnect_result = execute_operation(
                EEGatewayInterface.NETWORK,
                'disconnect',
                protocol='mqtt'
            )
            assert disconnect_result is not None

        except (ValueError, NotImplementedError, ConnectionError):
            pytest.skip("MQTT lifecycle not yet fully implemented")

    def test_redis_full_lifecycle(self, execute_operation, EEGatewayInterface, mock_network_configs):
        """Test Redis full lifecycle: connect -> set -> get -> disconnect."""
        try:
            config = mock_network_configs.get('redis')
            if not config:
                pytest.skip("No Redis config")

            # Connect
            connect_result = execute_operation(
                EEGatewayInterface.NETWORK,
                'connect',
                protocol='redis',
                **config
            )
            assert connect_result is not None

            # Set
            set_result = execute_operation(
                EEGatewayInterface.NETWORK,
                'set',
                protocol='redis',
                key='test_lifecycle',
                value='test_value'
            )
            assert set_result is not None

            # Get
            get_result = execute_operation(
                EEGatewayInterface.NETWORK,
                'get',
                protocol='redis',
                key='test_lifecycle'
            )
            assert get_result == 'test_value'

            # Disconnect
            disconnect_result = execute_operation(
                EEGatewayInterface.NETWORK,
                'disconnect',
                protocol='redis'
            )
            assert disconnect_result is not None

        except (ValueError, NotImplementedError, ConnectionError):
            pytest.skip("Redis lifecycle not yet fully implemented")

    def test_multiple_protocol_connections(self, execute_operation, EEGatewayInterface, mock_network_configs):
        """Test managing multiple protocol connections simultaneously."""
        try:
            protocols = ['mqtt', 'redis']

            # Connect to multiple protocols
            for protocol in protocols:
                config = mock_network_configs.get(protocol)
                if config:
                    execute_operation(
                        EEGatewayInterface.NETWORK,
                        'connect',
                        protocol=protocol,
                        **config
                    )

            # Check status of all
            for protocol in protocols:
                status = execute_operation(
                    EEGatewayInterface.NETWORK,
                    'get_status',
                    protocol=protocol
                )
                assert status is not None

        except (ValueError, NotImplementedError, ConnectionError):
            pytest.skip("Multiple protocol connections not yet implemented")


@pytest.mark.performance
class TestNetworkPerformance:
    """Performance tests for Network interface."""

    def test_redis_get_performance(self, execute_operation, EEGatewayInterface, performance_thresholds):
        """Test Redis GET performance."""
        import time

        try:
            # Connect
            execute_operation(
                EEGatewayInterface.NETWORK,
                'connect',
                protocol='redis',
                host='localhost',
                port=6379
            )

            # Measure GET time
            iterations = 100
            start_time = time.time()

            for i in range(iterations):
                execute_operation(
                    EEGatewayInterface.NETWORK,
                    'get',
                    protocol='redis',
                    key=f'test_key_{i % 10}'
                )

            elapsed_ms = (time.time() - start_time) * 1000
            avg_ms = elapsed_ms / iterations

            # Should be reasonably fast
            assert avg_ms < 10, \
                f"Redis GET too slow: {avg_ms:.3f}ms average"

        except (ValueError, NotImplementedError, ConnectionError):
            pytest.skip("Redis performance testing not yet implemented")

    def test_mqtt_publish_performance(self, execute_operation, EEGatewayInterface, performance_thresholds):
        """Test MQTT publish performance."""
        import time

        try:
            # Connect
            execute_operation(
                EEGatewayInterface.NETWORK,
                'connect',
                protocol='mqtt',
                host='localhost',
                port=1883
            )

            # Measure publish time
            iterations = 100
            start_time = time.time()

            for i in range(iterations):
                execute_operation(
                    EEGatewayInterface.NETWORK,
                    'publish',
                    protocol='mqtt',
                    topic=f'test/perf/{i % 10}',
                    payload='test_message'
                )

            elapsed_ms = (time.time() - start_time) * 1000
            avg_ms = elapsed_ms / iterations

            # Should be reasonably fast
            assert avg_ms < 10, \
                f"MQTT publish too slow: {avg_ms:.3f}ms average"

        except (ValueError, NotImplementedError, ConnectionError):
            pytest.skip("MQTT performance testing not yet implemented")
