"""lambda_alexa_minimal.py
Version: 2026-04-08
Purpose: Minimal debug handler - identifies exact hang point
"""

import json
import time
from datetime import datetime


def lambda_handler(event, context):
    """Minimal debug handler."""
    print("=" * 80)
    print("ALEXA DEBUG HANDLER STARTED")
    print(f"Timestamp: {datetime.utcnow().isoformat()}")
    print(f"Request ID: {getattr(context, 'aws_request_id', 'N/A')}")
    print("=" * 80)

    # Step 1: Check event
    step1_start = time.perf_counter()
    print("[STEP 1] Extracting directive...")
    directive = event.get('directive', {})
    header = directive.get('header', {})
    namespace = header.get('namespace', '')
    name = header.get('name', '')
    step1_ms = (time.perf_counter() - step1_start) * 1000
    print(f"[STEP 1] Complete in {step1_ms:.2f}ms")
    print(f"  Namespace: {namespace}")
    print(f"  Name: {name}")

    # Step 2: Validate
    step2_start = time.perf_counter()
    print("[STEP 2] Validating discovery request...")
    if namespace != 'Alexa.Discovery' or name != 'Discover':
        step2_ms = (time.perf_counter() - step2_start) * 1000
        print(f"[STEP 2] FAILED - Not a discovery request ({step2_ms:.2f}ms)")
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'This handler only supports Alexa.Discovery'})
        }
    step2_ms = (time.perf_counter() - step2_start) * 1000
    print(f"[STEP 2] Complete in {step2_ms:.2f}ms")

    # Step 3: Import gateway (this is likely where it hangs)
    step3_start = time.perf_counter()
    print("[STEP 3] About to import gateway...")
    try:
        from lee.gateway import GatewayInterface, execute_operation
        step3_ms = (time.perf_counter() - step3_start) * 1000
        print(f"[STEP 3] Gateway import complete in {step3_ms:.2f}ms")
    except Exception as e:
        step3_ms = (time.perf_counter() - step3_start) * 1000
        print(f"[STEP 3] FAILED after {step3_ms:.2f}ms: {e}")
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Gateway import failed: {e}'})
        }

    # Step 4: Load environment
    step4_start = time.perf_counter()
    print("[STEP 4] About to load environment...")
    try:
        from lee.lee_config import load_from_environment
        load_from_environment()
        step4_ms = (time.perf_counter() - step4_start) * 1000
        print(f"[STEP 4] Environment load complete in {step4_ms:.2f}ms")
    except Exception as e:
        step4_ms = (time.perf_counter() - step4_start) * 1000
        print(f"[STEP 4] FAILED after {step4_ms:.2f}ms: {e}")
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Environment load failed: {e}'})
        }

    # Step 5: Get HA config
    step5_start = time.perf_counter()
    print("[STEP 5] About to get HA config...")
    try:
        ha_url = execute_operation(GatewayInterface.CONFIG, 'get', key='HOME_ASSISTANT_URL')
        ha_token = execute_operation(GatewayInterface.CONFIG, 'get', key='HOME_ASSISTANT_API_KEY')
        step5_ms = (time.perf_counter() - step5_start) * 1000
        print(f"[STEP 5] Config retrieval complete in {step5_ms:.2f}ms")
        print(f"  HA URL: {ha_url}")
        print(f"  Token length: {len(ha_token) if ha_token else 0}")
    except Exception as e:
        step5_ms = (time.perf_counter() - step5_start) * 1000
        print(f"[STEP 5] FAILED after {step5_ms:.2f}ms: {e}")
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Config retrieval failed: {e}'})
        }

    # Step 6: Call HA API via HA gateway
    step6_start = time.perf_counter()
    print("[STEP 6] About to call HA gateway for states...")
    try:
        from lee.home_assistant import ha_gateway
        entities = ha_gateway.ha_devices_get_states()
        step6_ms = (time.perf_counter() - step6_start) * 1000
        print(f"[STEP 6] HA gateway call complete in {step6_ms:.2f}ms")
        print(f"[STEP 6] Retrieved {len(entities)} entities")
    except Exception as e:
        step6_ms = (time.perf_counter() - step6_start) * 1000
        print(f"[STEP 6] FAILED after {step6_ms:.2f}ms: {e}")
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'HA API call failed: {e}'})
        }

    # Step 7: Filter entities
    step7_start = time.perf_counter()
    print("[STEP 7] About to filter discoverable entities...")
    discoverable_entities = [
        entity for entity in entities
        if 'entity_id' in entity and _is_discoverable(entity['entity_id'])
    ]
    step7_ms = (time.perf_counter() - step7_start) * 1000
    print(f"[STEP 7] Entity filtering complete in {step7_ms:.2f}ms")
    print(f"  Discoverable: {len(discoverable_entities)}/{len(entities)}")

    # Step 8: Build response
    step8_start = time.perf_counter()
    print("[STEP 8] About to build discovery response...")
    response = _build_discovery_response(discoverable_entities, directive)
    step8_ms = (time.perf_counter() - step8_start) * 1000
    print(f"[STEP 8] Response building complete in {step8_ms:.2f}ms")

    # Summary
    total_ms = (time.perf_counter() - step1_start) * 1000
    print("=" * 80)
    print("TIMING SUMMARY:")
    print(f"  Step 1 - Extract directive: {step1_ms:.2f}ms")
    print(f"  Step 2 - Validate discovery: {step2_ms:.2f}ms")
    print(f"  Step 3 - Import gateway: {step3_ms:.2f}ms")
    print(f"  Step 4 - Load environment: {step4_ms:.2f}ms")
    print(f"  Step 5 - Get HA config: {step5_ms:.2f}ms")
    print(f"  Step 6 - Call HA API: {step6_ms:.2f}ms")
    print(f"  Step 7 - Filter entities: {step7_ms:.2f}ms")
    print(f"  Step 8 - Build response: {step8_ms:.2f}ms")
    print(f"  TOTAL: {total_ms:.2f}ms")
    print("=" * 80)

    return response


def _is_discoverable(entity_id: str) -> bool:
    """Check if entity is discoverable by Alexa."""
    discoverable_domains = {
        'light', 'switch', 'fan', 'cover', 'climate',
        'lock', 'sensor', 'binary_sensor', 'input_boolean',
        'scene', 'script', 'automation'
    }

    if '.' not in entity_id:
        return False

    domain = entity_id.split('.')[0]
    return domain in discoverable_domains


def _build_discovery_response(entities, directive):
    """Build discovery response with per-device timing."""
    print(f"[BUILD] Starting discovery response for {len(entities)} entities...")

    header = directive.get('header', {})
    correlation_token = header.get('correlationToken', '')
    message_id = header.get('messageId', '')

    endpoints = []
    device_timings = []

    build_start = time.perf_counter()

    for i, entity in enumerate(entities):
        entity_start = time.perf_counter()

        entity_id = entity.get('entity_id', 'unknown')
        friendly_name = entity.get('attributes', {}).get('friendly_name', entity_id)

        # Log every 10 devices
        if (i + 1) % 10 == 0:
            elapsed_so_far = (time.perf_counter() - build_start) * 1000
            print(f"[PROGRESS] Processed {i+1}/{len(entities)} devices ({elapsed_so_far:.2f}ms elapsed)")

        try:
            endpoint = _build_endpoint(entity)
            entity_build_ms = (time.perf_counter() - entity_start) * 1000

            if endpoint:
                endpoints.append(endpoint)
                device_timings.append({
                    'entity_id': entity_id,
                    'friendly_name': friendly_name,
                    'build_ms': entity_build_ms
                })

                print(f"[DEVICE] #{len(endpoints)}: {entity_id} ({friendly_name}) - {entity_build_ms:.2f}ms")

                if entity_build_ms > 10:
                    print(f"[SLOW DEVICE] {entity_id} took {entity_build_ms:.2f}ms")

        except Exception as e:
            entity_build_ms = (time.perf_counter() - entity_start) * 1000
            print(f"[ERROR] Failed to build {entity_id}: {e} ({entity_build_ms:.2f}ms)")

    total_build_ms = (time.perf_counter() - build_start) * 1000
    print(f"[BUILD] Built {len(endpoints)} endpoints in {total_build_ms:.2f}ms")

    if device_timings:
        avg_ms = sum(t['build_ms'] for t in device_timings) / len(device_timings)
        max_ms = max(t['build_ms'] for t in device_timings)
        min_ms = min(t['build_ms'] for t in device_timings)

        print("[STATS] Per-device build times:")
        print(f"  Average: {avg_ms:.2f}ms")
        print(f"  Min: {min_ms:.2f}ms")
        print(f"  Max: {max_ms:.2f}ms")

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


def _build_endpoint(entity):
    """Build Alexa endpoint from entity."""
    entity_id = entity.get('entity_id', '')
    if not entity_id:
        return None

    domain = entity_id.split('.')[0]
    friendly_name = entity.get('attributes', {}).get('friendly_name', entity_id)

    endpoint = {
        'endpointId': entity_id,
        'manufacturerName': 'Home Assistant',
        'friendlyName': friendly_name,
        'description': f'{entity_id} via Home Assistant',
        'displayCategories': _get_display_category(domain),
        'capabilities': _get_capabilities(domain)
    }

    return endpoint


def _get_display_category(domain):
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


def _get_capabilities(domain):
    """Get Alexa capabilities for domain."""
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
