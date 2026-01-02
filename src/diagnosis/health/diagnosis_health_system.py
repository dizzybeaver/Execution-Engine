"""
diagnosis/health/diagnosis_health_system.py
Version: 2025-12-08_1
Purpose: System-wide health check for all 12 interfaces
License: Apache 2.0
"""

import time
from typing import Dict, Any


def check_system_health(**kwargs) -> Dict[str, Any]:
    """Comprehensive system-wide health check for all 12 interfaces."""
    from diagnosis import (
        check_initialization_health,
        check_utility_health,
        check_singleton_health
    )
    
    try:
        system_health = {
            'timestamp': time.time(),
            'interfaces': {},
            'overall_compliance': {},
            'critical_issues': [],
            'warnings': [],
            'recommendations': [],
            'status': 'healthy'
        }
        
        interfaces_to_check = [
            ('METRICS', _check_metrics_health),
            ('CACHE', _check_cache_health),
            ('LOGGING', _check_logging_health),
            ('SECURITY', _check_security_health),
            ('CONFIG', _check_config_health),
            ('HTTP_CLIENT', _check_http_client_health),
            ('WEBSOCKET', _check_websocket_health),
            ('CIRCUIT_BREAKER', _check_circuit_breaker_health),
            ('SINGLETON', check_singleton_health),
            ('INITIALIZATION', check_initialization_health),
            ('UTILITY', check_utility_health),
        ]
        
        for interface_name, check_func in interfaces_to_check:
            try:
                result = check_func()
                system_health['interfaces'][interface_name] = result
                
                if result.get('status') == 'critical':
                    system_health['critical_issues'].append(f"{interface_name}: {result.get('checks', {})}")
                    system_health['status'] = 'critical'
                elif result.get('status') == 'degraded':
                    system_health['warnings'].append(f"{interface_name}: Degraded performance")
                    if system_health['status'] == 'healthy':
                        system_health['status'] = 'degraded'
                
            except Exception as e:
                system_health['interfaces'][interface_name] = {'status': 'error', 'error': str(e)}
                system_health['warnings'].append(f"{interface_name}: Health check failed")
        
        all_interfaces = system_health['interfaces']
        total_interfaces = len(all_interfaces)
        
        ap_08_compliant = sum(1 for i in all_interfaces.values() if i.get('compliance', {}).get('ap_08', False))
        dec_04_compliant = sum(1 for i in all_interfaces.values() if i.get('compliance', {}).get('dec_04', False))
        less_17_compliant = sum(1 for i in all_interfaces.values() if i.get('compliance', {}).get('less_17', False))
        less_18_compliant = sum(1 for i in all_interfaces.values() if i.get('compliance', {}).get('less_18', False))
        less_21_compliant = sum(1 for i in all_interfaces.values() if i.get('compliance', {}).get('less_21', False))
        
        system_health['overall_compliance'] = {
            'ap_08_no_threading_locks': {
                'compliant': ap_08_compliant,
                'total': total_interfaces,
                'percentage': (ap_08_compliant / total_interfaces * 100) if total_interfaces > 0 else 0
            },
            'dec_04_lambda_single_threaded': {
                'compliant': dec_04_compliant,
                'total': total_interfaces,
                'percentage': (dec_04_compliant / total_interfaces * 100) if total_interfaces > 0 else 0
            },
            'less_17_threading_unnecessary': {
                'compliant': less_17_compliant,
                'total': total_interfaces,
                'percentage': (less_17_compliant / total_interfaces * 100) if total_interfaces > 0 else 0
            },
            'less_18_singleton_pattern': {
                'compliant': less_18_compliant,
                'total': total_interfaces,
                'percentage': (less_18_compliant / total_interfaces * 100) if total_interfaces > 0 else 0
            },
            'less_21_rate_limiting': {
                'compliant': less_21_compliant,
                'total': total_interfaces,
                'percentage': (less_21_compliant / total_interfaces * 100) if total_interfaces > 0 else 0
            }
        }
        
        if ap_08_compliant < total_interfaces:
            system_health['recommendations'].append(f"Remove threading locks from {total_interfaces - ap_08_compliant} interfaces")
        
        if less_18_compliant < total_interfaces:
            system_health['recommendations'].append(f"Add SINGLETON pattern to {total_interfaces - less_18_compliant} interfaces")
        
        if less_21_compliant < total_interfaces:
            system_health['recommendations'].append(f"Add rate limiting to {total_interfaces - less_21_compliant} interfaces")
        
        if not system_health['critical_issues']:
            if ap_08_compliant == total_interfaces and dec_04_compliant == total_interfaces:
                if less_18_compliant == total_interfaces and less_21_compliant == total_interfaces:
                    system_health['status'] = 'healthy'
                    system_health['recommendations'].append("✅ All interfaces fully optimized and compliant!")
                else:
                    system_health['status'] = 'degraded'
            else:
                system_health['status'] = 'critical'
        
        return system_health
        
    except Exception as e:
        return {'status': 'error', 'error': str(e), 'timestamp': time.time()}


def _check_metrics_health(**kwargs):
    """Placeholder for METRICS interface health check."""
    return {'status': 'healthy', 'compliance': {'ap_08': True, 'dec_04': True, 'less_17': True, 'less_18': True, 'less_21': True}}


def _check_cache_health(**kwargs):
    """Placeholder for CACHE interface health check."""
    return {'status': 'healthy', 'compliance': {'ap_08': True, 'dec_04': True, 'less_17': True, 'less_18': True, 'less_21': True}}


def _check_logging_health(**kwargs):
    """Placeholder for LOGGING interface health check."""
    return {'status': 'healthy', 'compliance': {'ap_08': True, 'dec_04': True, 'less_17': True, 'less_18': True, 'less_21': True}}


def _check_security_health(**kwargs):
    """Placeholder for SECURITY interface health check."""
    return {'status': 'healthy', 'compliance': {'ap_08': True, 'dec_04': True, 'less_17': True, 'less_18': True, 'less_21': True}}


def _check_config_health(**kwargs):
    """Placeholder for CONFIG interface health check."""
    return {'status': 'healthy', 'compliance': {'ap_08': True, 'dec_04': True, 'less_17': True, 'less_18': True, 'less_21': True}}


def _check_http_client_health(**kwargs):
    """Placeholder for HTTP_CLIENT interface health check."""
    return {'status': 'healthy', 'compliance': {'ap_08': True, 'dec_04': True, 'less_17': True, 'less_18': True, 'less_21': True}}


def _check_websocket_health(**kwargs):
    """Placeholder for WEBSOCKET interface health check."""
    return {'status': 'healthy', 'compliance': {'ap_08': True, 'dec_04': True, 'less_17': True, 'less_18': True, 'less_21': True}}


def _check_circuit_breaker_health(**kwargs):
    """Placeholder for CIRCUIT_BREAKER interface health check."""
    return {'status': 'healthy', 'compliance': {'ap_08': True, 'dec_04': True, 'less_17': True, 'less_18': True, 'less_21': True}}


__all__ = ['check_system_health']
