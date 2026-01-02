"""
HA Plugin Test Suite for EE

Phase 4: Migration - HA Testing Framework

This package contains comprehensive tests for the HA plugin integration
with EE Gateway. All tests are 100% UG-ISP compliant and use gateway
routing for all operations.

Test Modules:
- ha_test_handler.py: Test suite runner and core tests
- ha_functional_tests.py: HA functional tests (light control)
- ha_sensor_tests.py: HA sensor tests (temperature, contact)
- ha_interface_tests.py: HA plugin interface routing tests (Part 1)
- ha_interface_error_tests.py: HA interface error tests (Part 2)
- ha_integration_tests.py: EE Gateway integration tests (Part 1)
- ha_integration_compliance_tests.py: UG-ISP compliance tests (Part 2)

UG-ISP Compliance:
- All HA config access via execute("config.get", {...})
- NO direct os.environ access
- NO direct HA client imports
- All tests use gateway routing
- Inline correlation IDs (no helpers)
- Debug via GatewayInterface.DEBUG

Test Categories:
1. Core Tests (ha_test_handler.py):
   - Plugin import verification
   - Gateway routing verification
   - Config access verification
   - EE Gateway integration

2. Functional Tests (ha_functional_tests.py, ha_sensor_tests.py):
   - Light control (on/off)
   - Sensor reading (temperature, contact)
   - Service listing
   - State retrieval

3. Interface Tests (ha_interface_tests.py, ha_interface_error_tests.py):
   - Interface registration
   - Operation routing
   - Error handling
   - Response format validation

4. Integration Tests (ha_integration_tests.py, ha_integration_compliance_tests.py):
   - Plugin gateway integration
   - UG-ISP compliance verification
   - NO os.environ access verification
   - Debug routing verification
   - Correlation ID format verification

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

__all__ = [
    'EEHATestSuite',
    'run_ha_tests',
]
