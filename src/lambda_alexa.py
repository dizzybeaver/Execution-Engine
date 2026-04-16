"""lambda_alexa.py
Version: 2026-04-08
Purpose: Simplified Lambda handler for Alexa Discovery only with full debugging
License: Apache 2.0

This is a DEBUG variant that:
- Only handles Alexa Discovery requests
- Extensive logging at every step
- Helps identify where 30-second timeout occurs
- Strips away all other functionality
"""

import json
import logging
import os
import sys
import time
from datetime import datetime
from typing import Any

# Set up root directory for imports
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Timing tracker
_timings = {}

def log_timing(step: str, duration_ms: float):
    """Log timing information."""
    logger.info(f"[TIMING] {step}: {duration_ms:.2f}ms")
    _timings[step] = duration_ms

def log_step(step: str, **context):
    """Log a step with context."""
    context_str = ", ".join(f"{k}={v}" for k, v in context.items())
    suffix = f" - {context_str}" if context_str else ""
    logger.info(f"[STEP] {step}{suffix}")

def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Lambda handler for Alexa Discovery only with full debugging."""
    request_start = time.perf_counter()
    request_id = getattr(context, 'aws_request_id', 'N/A')

    logger.info("=" * 80)
    logger.info(f"REQUEST START: {request_id}")
    logger.info(f"Timestamp: {datetime.utcnow().isoformat()}")
    logger.info(f"Event: {json.dumps(event, indent=2, default=str)[:1000]}")
    logger.info("=" * 80)

    try:
        # Step 1: Extract directive
        step_start = time.perf_counter()
        directive = event.get('directive', {})
        header = directive.get('header', {})
        namespace = header.get('namespace', '')
        name = header.get('name', '')
        log_timing('extract_directive', (time.perf_counter() - step_start) * 1000)

        log_step('directive_extracted', namespace=namespace, name=name)

        # Step 2: Validate this is Discovery
        step_start = time.perf_counter()
        if namespace != 'Alexa.Discovery' or name != 'Discover':
            log_timing('validate_discovery', (time.perf_counter() - step_start) * 1000)
            logger.warning(f"NOT A DISCOVERY REQUEST: {namespace}.{name}")
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'This handler only supports Alexa.Discovery',
                    'received': f'{namespace}.{name}'
                })
            }
        log_timing('validate_discovery', (time.perf_counter() - step_start) * 1000)
        log_step('discovery_validated')

        # Step 3: Import gateway and HA modules
        step_start = time.perf_counter()
        log_step('importing_gateway_start')
        from lee.gateway import GatewayInterface, execute_operation
        log_timing('import_gateway', (time.perf_counter() - step_start) * 1000)
        log_step('gateway_imported')

        # Step 4: Load environment
        step_start = time.perf_counter()
        log_step('loading_environment_start')
        from lee.lee_config import load_from_environment
        load_from_environment()
        log_timing('load_environment', (time.perf_counter() - step_start) * 1000)
        log_step('environment_loaded')

        # Step 5: Get HA URL and token
        step_start = time.perf_counter()
        log_step('getting_config_start')
        ha_url = execute_operation(GatewayInterface.CONFIG, 'get', key='HOME_ASSISTANT_URL')
        ha_token = execute_operation(GatewayInterface.CONFIG, 'get', key='HOME_ASSISTANT_API_KEY')
        log_timing('get_config', (time.perf_counter() - step_start) * 1000)
        log_step('config_obtained', ha_url=ha_url, token_length=len(ha_token) if ha_token else 0)

        # Step 6: Call HA API for entities via HA gateway
        step_start = time.perf_counter()
        log_step('ha_gateway_call_start', operation='ha_devices_get_states')
        from lee.home_assistant import ha_gateway
        entities = ha_gateway.ha_devices_get_states()
        api_duration = (time.perf_counter() - step_start) * 1000
        log_timing('ha_gateway_call', api_duration)

        log_step('ha_gateway_call_success', entity_count=len(entities), duration_ms=f"{api_duration:.2f}")

        # Step 7: Filter discoverable entities
        step_start = time.perf_counter()
        log_step('filtering_entities_start', total=len(entities))
        discoverable_entities = [
            entity for entity in entities
            if 'entity_id' in entity and _is_discoverable(entity['entity_id'])
        ]
        log_timing('filter_entities', (time.perf_counter() - step_start) * 1000)
        log_step('entities_filtered', discoverable=len(discoverable_entities))

        # Step 8: Build Alexa discovery response
        step_start = time.perf_counter()
        log_step('building_response_start', endpoints=len(discoverable_entities))
        response = _build_discovery_response(discoverable_entities, directive)
        log_timing('build_response', (time.perf_counter() - step_start) * 1000)
        log_step('response_built', endpoint_count=len(response.get('event', {}).get('payload', {}).get('endpoints', [])))

        # Step 9: Response serialization timing (critical for 381 devices)
        step_start = time.perf_counter()
        log_step('serializing_response_start')
        try:
            # Serialize the response to JSON like Lambda does
            response_json = json.dumps(response, indent=2, default=str)
            response_size_bytes = len(response_json.encode('utf-8'))
            serialize_ms = (time.perf_counter() - step_start) * 1000
            log_timing('serialize_response', serialize_ms)
            log_step('response_serialized', size_bytes=response_size_bytes, size_kb=f"{response_size_bytes / 1024:.2f}")

            # Log first 500 chars of response
            logger.info(f"[RESPONSE PREVIEW] {response_json[:500]}...")

        except Exception as e:
            serialize_ms = (time.perf_counter() - step_start) * 1000
            logger.error(f"[ERROR] Failed to serialize response: {e} ({serialize_ms:.2f}ms)")

        # Step 10: Device list summary
        endpoints_list = response.get('event', {}).get('payload', {}).get('endpoints', [])
        log_step('device_list_summary', total_endpoints=len(endpoints_list))

        # Log all device names grouped by domain
        device_groups = {}
        for ep in endpoints_list:
            entity_id = ep.get('endpointId', '')
            if '.' in entity_id:
                domain = entity_id.split('.')[0]
                if domain not in device_groups:
                    device_groups[domain] = []
                device_groups[domain].append(ep.get('friendlyName', entity_id))

        logger.info(f"[DEVICE GROUPS] Found {len(device_groups)} domains:")
        for domain, devices in sorted(device_groups.items()):
            logger.info(f"  {domain}: {len(devices)} devices")
            # Log each device name
            for device_name in devices[:5]:  # First 5
                logger.info(f"    - {device_name}")
            if len(devices) > 5:
                logger.info(f"    ... and {len(devices) - 5} more")

        # Step 11: Final timing summary
        total_duration = (time.perf_counter() - request_start) * 1000
        log_step('request_complete', total_ms=f"{total_duration:.2f}")

        logger.info("=" * 80)
        logger.info("FINAL TIMING SUMMARY:")
        for step, duration in _timings.items():
            logger.info(f"  {step}: {duration:.2f}ms")
        logger.info(f"  TOTAL: {total_duration:.2f}ms ({total_duration / 1000:.2f} seconds)")
        logger.info("=" * 80)

        return response

    except Exception as e:
        total_duration = (time.perf_counter() - request_start) * 1000
        logger.error(f"ERROR after {total_duration:.2f}ms: {e}", exc_info=True)
        return _create_error_response(str(e))

def _is_discoverable(entity_id: str) -> bool:
    """Check if entity is discoverable by Alexa."""
    # Alexa supports these domains
    discoverable_domains = {
        'light', 'switch', 'fan', 'cover', 'climate',
        'lock', 'sensor', 'binary_sensor', 'input_boolean',
        'scene', 'script', 'automation'
    }

    if '.' not in entity_id:
        return False

    domain = entity_id.split('.')[0]
    return domain in discoverable_domains

def _build_discovery_response(entities: list, directive: dict) -> dict:
    """Build Alexa discovery response from entities with per-device timing."""
    log_step('building_alexa_response', entity_count=len(entities))

    # Extract header info from directive
    header = directive.get('header', {})
    correlation_token = header.get('correlationToken', '')
    message_id = header.get('messageId', '')

    # Build endpoints list with individual device timing
    endpoints = []
    device_timings = []
    slow_devices = []

    build_start = time.perf_counter()

    for i, entity in enumerate(entities):
        entity_start = time.perf_counter()

        # Extract device info early for logging
        entity_id = entity.get('entity_id', 'unknown')
        friendly_name = entity.get('attributes', {}).get('friendly_name', entity_id)
        domain = entity_id.split('.')[0] if '.' in entity_id else 'unknown'

        # Log every 10 devices
        if (i + 1) % 10 == 0:
            elapsed_so_far = (time.perf_counter() - build_start) * 1000
            logger.info(f"[PROGRESS] Processed {i+1}/{len(entities)} devices ({elapsed_so_far:.2f}ms elapsed)")

        # Build endpoint and time it
        try:
            endpoint = _build_endpoint(entity)
            entity_build_ms = (time.perf_counter() - entity_start) * 1000

            if endpoint:
                endpoints.append(endpoint)
                device_timings.append({
                    'entity_id': entity_id,
                    'friendly_name': friendly_name,
                    'domain': domain,
                    'build_ms': entity_build_ms
                })

                # Log each device as it's built
                logger.info(f"[DEVICE] #{len(endpoints)}: {entity_id} ({friendly_name}) - {entity_build_ms:.2f}ms")

                # Track slow devices (>10ms to build)
                if entity_build_ms > 10:
                    slow_devices.append({
                        'entity_id': entity_id,
                        'friendly_name': friendly_name,
                        'build_ms': entity_build_ms
                    })
                    logger.warning(f"[SLOW DEVICE] {entity_id} took {entity_build_ms:.2f}ms to build")

        except Exception as e:
            entity_build_ms = (time.perf_counter() - entity_start) * 1000
            logger.error(f"[ERROR] Failed to build endpoint for {entity_id}: {e} ({entity_build_ms:.2f}ms)")

    total_build_ms = (time.perf_counter() - build_start) * 1000
    log_step('endpoints_built', count=len(endpoints), total_ms=f"{total_build_ms:.2f}")

    # Log timing statistics
    if device_timings:
        avg_ms = sum(t['build_ms'] for t in device_timings) / len(device_timings)
        max_ms = max(t['build_ms'] for t in device_timings)
        min_ms = min(t['build_ms'] for t in device_timings)

        logger.info("[TIMING STATS] Per-device build times:")
        logger.info(f"  Average: {avg_ms:.2f}ms")
        logger.info(f"  Min: {min_ms:.2f}ms")
        logger.info(f"  Max: {max_ms:.2f}ms")
        logger.info(f"  Total devices: {len(device_timings)}")
        logger.info(f"  Slow devices (>10ms): {len(slow_devices)}")

        if slow_devices:
            logger.warning(f"[SLOW DEVICES] Found {len(slow_devices)} slow devices:")
            for dev in sorted(slow_devices, key=lambda x: x['build_ms'], reverse=True)[:10]:
                logger.warning(f"  - {dev['entity_id']} ({dev['friendly_name']}): {dev['build_ms']:.2f}ms")

    # Build response
    response = {
        'event': {
            'header': {
                'namespace': 'Alexa.Discovery',
                'name': 'Discover.Response',
                'payloadVersion': '3',
                'correlationToken': correlation_token,
                'messageId': message_id
            },
            'payload': {
                'endpoints': endpoints
            }
        }
    }

    return response

def _build_endpoint(entity: dict) -> dict:
    """Build Alexa endpoint from entity with detailed step timing."""
    entity_id = entity.get('entity_id', '')

    if not entity_id:
        return None

    domain = entity_id.split('.')[0]
    friendly_name = entity.get('attributes', {}).get('friendly_name', entity_id)

    # Time each step of endpoint building
    step_timings = {}

    # Step 1: Create basic structure
    start = time.perf_counter()
    endpoint = {
        'endpointId': entity_id,
        'manufacturerName': 'Home Assistant',
        'friendlyName': friendly_name,
        'description': f'{entity_id} via Home Assistant',
        'displayCategories': [],
        'capabilities': []
    }
    step_timings['basic_structure'] = (time.perf_counter() - start) * 1000

    # Step 2: Get display categories
    start = time.perf_counter()
    endpoint['displayCategories'] = _get_display_category(domain)
    step_timings['display_categories'] = (time.perf_counter() - start) * 1000

    # Step 3: Get capabilities
    start = time.perf_counter()
    endpoint['capabilities'] = _get_capabilities(domain)
    step_timings['capabilities'] = (time.perf_counter() - start) * 1000

    # Log detailed timing if device is slow
    total_ms = sum(step_timings.values())
    if total_ms > 5:
        logger.debug(f"[TIMING DETAIL] {entity_id} breakdown:")
        for step, ms in step_timings.items():
            logger.debug(f"  {step}: {ms:.2f}ms")

    return endpoint

def _get_display_category(domain: str) -> list:
    """Get Alexa display categories for domain."""
    categories = {
        'light': ['LIGHT'],
        'switch': ['SWITCH'],
        'fan': ['FAN'],
        'cover': ['DOOR', 'WINDOW'],
        'climate': ['THERMOSTAT'],
        'lock': ['SMARTLOCK'],
        'sensor': ['SENSOR'],
        'binary_sensor': ['SENSOR'],
        'scene': ['SCENE_TRIGGER'],
        'script': ['SCENE_TRIGGER'],
        'automation': ['SCENE_TRIGGER'],
    }
    return categories.get(domain, ['OTHER'])

def _get_capabilities(domain: str) -> list:
    """Get Alexa capabilities for domain."""
    # Basic capability - all entities have this
    capabilities = [
        {
            'type': 'AlexaInterface',
            'version': '3',
            'properties': {
                'supported': [],
                'proactivelyReported': False,
                'retrievable': False
            }
        }
    ]

    # Add domain-specific capabilities
    if domain in ['light', 'switch']:
        capabilities.append({
            'type': 'Alexa.PowerController',
            'version': '3',
            'properties': {
                'supported': [{'name': 'powerState'}],
                'proactivelyReported': False,
                'retrievable': True
            }
        })

    return capabilities

def _create_error_response(error_message: str) -> dict:
    """Create error response."""
    return {
        'statusCode': 500,
        'body': json.dumps({
            'error': error_message,
            'timings': _timings
        })
    }

if __name__ == '__main__':
    # Local testing
    test_event = {
        'directive': {
            'header': {
                'namespace': 'Alexa.Discovery',
                'name': 'Discover',
                'messageId': 'test-message-001',
                'correlationToken': 'test-token-001'
            },
            'payload': {
                'scope': {
                    'type': 'BearerToken',
                    'token': 'test-token'
                }
            }
        }
    }

    class MockContext:
        aws_request_id = 'local-test-001'
        memory_limit_in_mb = 128

    result = lambda_handler(test_event, MockContext())
    print(json.dumps(result, indent=2, default=str)[:1000])
