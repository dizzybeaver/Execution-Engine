# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-01 - Extracted infrastructure functions from ha_gateway.py

"""ha_gateway_infrastructure.py - Infrastructure Interfaces for HA Gateway
Version: 2026-04-01
Purpose: Registry, automation, blueprint, supervisor, and configuration interfaces

This module contains functions for managing Home Assistant infrastructure:
- Registry (areas, devices, entities)
- Automation (automations, scripts, triggers)
- Blueprint management
- Supervisor (add-ons, host info)
- Configuration
- Health checks

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

# Core imports
from lee.home_assistant.ha_gateway_convenience import ha_generate_correlation_id
from lee.home_assistant import ha_gateway
from lee.home_assistant.ha_gateway_enums import HAGatewayInterface
from lee.gateway import GatewayInterface, execute_operation

# ===== HEALTH AND DIAGNOSTICS =====

def ha_health_check_system(**kwargs) -> dict:
    """Check overall HA system health."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.HEALTH, "check_system_health", **kwargs)


def ha_health_check_lee_connectivity(**kwargs) -> dict:
    """Check connectivity to LEE systems (SUGA-ISP compliant)."""
    try:
        # Try a simple gateway operation to verify it works
        execute_operation(GatewayInterface.LOGGING, "log_info",
                        message="LEE connectivity check",
                        corr_id=ha_generate_correlation_id())

        return {
            "lee_connected": True,
            "timestamp": ha_generate_correlation_id(),
        }
    except (ConnectionError, TimeoutError, OSError) as e:
        return {
            "lee_connected": False,
            "error": f"Network error: {str(e)}",
            "timestamp": ha_generate_correlation_id(),
        }
    except (AttributeError, ImportError) as e:
        return {
            "lee_connected": False,
            "error": f"Gateway error: {str(e)}",
            "timestamp": ha_generate_correlation_id(),
        }
    except Exception as e:  # pylint: disable=W0718
        return {
            "lee_connected": False,
            "error": str(e),
            "timestamp": ha_generate_correlation_id(),
        }


# ===== CONFIGURATION =====

def ha_config_get_ha_config(**kwargs) -> dict:
    """Get Home Assistant configuration."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.CONFIG, "get_ha_config", **kwargs)


def ha_config_get_ha_entities(**kwargs) -> list:
    """Get Home Assistant entity configuration."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.CONFIG, "get_ha_entities", **kwargs)


# ===== REGISTRY INTERFACE =====

# Area Registry
def ha_registry_list_areas(**kwargs) -> list:
    """List all areas through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.REGISTRY, "list_areas", **kwargs)


def ha_registry_get_area(area_id: str, **kwargs) -> dict:
    """Get area by ID through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.REGISTRY, "get_area", area_id=area_id, **kwargs)


def ha_registry_create_area(name: str, **kwargs) -> dict:
    """Create area through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.REGISTRY, "create_area", name=name, **kwargs)


def ha_registry_update_area(area_id: str, **kwargs) -> dict:
    """Update area through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.REGISTRY, "update_area", area_id=area_id, **kwargs)


def ha_registry_delete_area(area_id: str, **kwargs) -> dict:
    """Delete area through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.REGISTRY, "delete_area", area_id=area_id, **kwargs)


# Device Registry
def ha_registry_list_devices(**kwargs) -> list:
    """List all devices through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.REGISTRY, "list_devices", **kwargs)


def ha_registry_get_device(device_id: str, **kwargs) -> dict:
    """Get device by ID through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.REGISTRY, "get_device", device_id=device_id, **kwargs)


def ha_registry_update_device(device_id: str, **kwargs) -> dict:
    """Update device through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.REGISTRY, "update_device", device_id=device_id, **kwargs)


def ha_registry_delete_device(device_id: str, **kwargs) -> dict:
    """Delete device through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.REGISTRY, "delete_device", device_id=device_id, **kwargs)


# Entity Registry
def ha_registry_list_entities(**kwargs) -> list:
    """List all entities through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.REGISTRY, "list_entities", **kwargs)


def ha_registry_get_entity(entity_id: str, **kwargs) -> dict:
    """Get entity by ID through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.REGISTRY, "get_entity", entity_id=entity_id, **kwargs)


def ha_registry_update_entity(entity_id: str, **kwargs) -> dict:
    """Update entity through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.REGISTRY, "update_entity", entity_id=entity_id, **kwargs)


def ha_registry_remove_entity(entity_id: str, **kwargs) -> dict:
    """Remove entity through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.REGISTRY, "remove_entity", entity_id=entity_id, **kwargs)


# Category Registry
def ha_registry_list_categories(**kwargs) -> list:
    """List all categories through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.REGISTRY, "list_categories", **kwargs)


# ===== AUTOMATION INTERFACE =====

# Automation Management
def ha_automation_list_automations(**kwargs) -> list:
    """List all automations through HA gateway."""
    result = ha_gateway.ha_execute_operation(HAGatewayInterface.AUTOMATION, "list_automations", **kwargs)
    return result.get("entities", []) if isinstance(result, dict) else result


def ha_automation_get_automation(automation_id: str, **kwargs) -> dict:
    """Get automation by ID through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.AUTOMATION, "get_automation", automation_id=automation_id, **kwargs)


def ha_automation_trigger_automation(automation_id: str, **kwargs) -> dict:
    """Trigger automation through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.AUTOMATION, "trigger_automation", automation_id=automation_id, **kwargs)


def ha_automation_enable_automation(automation_id: str, **kwargs) -> dict:
    """Enable automation through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.AUTOMATION, "enable_automation", automation_id=automation_id, **kwargs)


def ha_automation_disable_automation(automation_id: str, **kwargs) -> dict:
    """Disable automation through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.AUTOMATION, "disable_automation", automation_id=automation_id, **kwargs)


def ha_automation_reload_automations(**kwargs) -> dict:
    """Reload all automations through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.AUTOMATION, "reload_automations", **kwargs)


# Script Management
def ha_automation_list_scripts(**kwargs) -> list:
    """List all scripts through HA gateway."""
    result = ha_gateway.ha_execute_operation(HAGatewayInterface.AUTOMATION, "list_scripts", **kwargs)
    return result.get("entities", []) if isinstance(result, dict) else result


def ha_automation_get_script(script_id: str, **kwargs) -> dict:
    """Get script by ID through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.AUTOMATION, "get_script", script_id=script_id, **kwargs)


def ha_automation_run_script(script_id: str, variables: dict = None, **kwargs) -> dict:
    """Run script through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.AUTOMATION, "run_script", script_id=script_id, variables=variables, **kwargs)


def ha_automation_reload_scripts(**kwargs) -> dict:
    """Reload all scripts through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.AUTOMATION, "reload_scripts", **kwargs)


# Trigger Management
def ha_automation_list_triggers(**kwargs) -> list:
    """List all triggers through HA gateway."""
    result = ha_gateway.ha_execute_operation(HAGatewayInterface.AUTOMATION, "list_triggers", **kwargs)
    return result.get("entities", []) if isinstance(result, dict) else result


# ===== BLUEPRINT INTERFACE =====

def ha_blueprint_list_blueprints(domain: str, **kwargs) -> dict:
    """List all blueprints for a domain through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.BLUEPRINT, "list_blueprints", domain=domain, **kwargs)


def ha_blueprint_import_blueprint(url: str, **kwargs) -> dict:
    """Import blueprint from URL through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.BLUEPRINT, "import_blueprint", url=url, **kwargs)


def ha_blueprint_save_blueprint(domain: str, path: str, yaml: str, **kwargs) -> dict:
    """Save blueprint through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.BLUEPRINT, "save_blueprint", domain=domain, path=path, yaml=yaml, **kwargs)


def ha_blueprint_delete_blueprint(domain: str, path: str, **kwargs) -> dict:
    """Delete blueprint through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.BLUEPRINT, "delete_blueprint", domain=domain, path=path, **kwargs)


def ha_blueprint_substitute_blueprint(domain: str, path: str, input_data: dict, **kwargs) -> dict:
    """Substitute blueprint inputs through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.BLUEPRINT, "substitute_blueprint", domain=domain, path=path, input_data=input_data, **kwargs)


# ===== SUPERVISOR INTERFACE =====

def ha_supervisor_get_info(**kwargs) -> dict:
    """Get supervisor information through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.SUPERVISOR, "get_supervisor_info", **kwargs)


def ha_supervisor_get_host_info(**kwargs) -> dict:
    """Get host information through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.SUPERVISOR, "get_host_info", **kwargs)


def ha_supervisor_get_core_info(**kwargs) -> dict:
    """Get Home Assistant Core information through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.SUPERVISOR, "get_core_info", **kwargs)


def ha_supervisor_get_os_info(**kwargs) -> dict:
    """Get Operating System information through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.SUPERVISOR, "get_os_info", **kwargs)


def ha_supervisor_list_addons(**kwargs) -> dict:
    """List all add-ons through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.SUPERVISOR, "list_addons", **kwargs)


def ha_supervisor_get_addon_info(addon_slug: str, **kwargs) -> dict:
    """Get add-on information through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.SUPERVISOR, "get_addon_info", addon_slug=addon_slug, **kwargs)


def ha_supervisor_start_addon(addon_slug: str, **kwargs) -> dict:
    """Start add-on through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.SUPERVISOR, "start_addon", addon_slug=addon_slug, **kwargs)


def ha_supervisor_stop_addon(addon_slug: str, **kwargs) -> dict:
    """Stop add-on through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.SUPERVISOR, "stop_addon", addon_slug=addon_slug, **kwargs)


def ha_supervisor_restart_addon(addon_slug: str, **kwargs) -> dict:
    """Restart add-on through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.SUPERVISOR, "restart_addon", addon_slug=addon_slug, **kwargs)
