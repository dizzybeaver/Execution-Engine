"""
config/config_validator.py
Version: 2025-12-09_1
Purpose: Configuration validation logic
License: Apache 2.0
"""

from typing import Dict, Any


class ConfigurationValidator:
    """Configuration validation with debug integration."""
    
    def validate_parameter(self, key: str, value: Any) -> Dict[str, Any]:
        """Validate a single parameter."""
        import gateway
        
        gateway.debug_log("CONFIG", "CONFIG", "Validating parameter", key=key)
        
        # Basic validation rules
        if not isinstance(key, str) or not key:
            return {
                'valid': False,
                'error': 'Key must be non-empty string'
            }
        
        if value is None:
            return {
                'valid': False,
                'error': 'Value cannot be None'
            }
        
        return {'valid': True}
    
    def validate_section(self, section: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a configuration section."""
        import gateway
        
        gateway.debug_log("CONFIG", "CONFIG", "Validating section", section=section)
        
        errors = []
        
        # Validate each parameter in section
        for key, value in config.items():
            result = self.validate_parameter(key, value)
            if not result['valid']:
                errors.append({
                    'key': key,
                    'error': result['error']
                })
        
        return {
            'valid': len(errors) == 0,
            'section': section,
            'errors': errors
        }
    
    def validate_all_sections(self, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Validate all configuration sections."""
        import gateway
        
        if config is None:
            from config.config_core import get_config_manager
            manager = get_config_manager()
            config = manager._config
        
        try:
            with gateway.debug_timing("CONFIG", "CONFIG", "validate_all"):
                # Group by sections
                sections = {}
                for key in config.keys():
                    if '.' in key:
                        section = key.split('.')[0]
                    else:
                        section = 'root'
                    
                    if section not in sections:
                        sections[section] = {}
                    sections[section][key] = config[key]
                
                # Validate each section
                results = {}
                all_valid = True
                
                for section, section_config in sections.items():
                    result = self.validate_section(section, section_config)
                    results[section] = result
                    if not result['valid']:
                        all_valid = False
                
                gateway.debug_log("CONFIG", "CONFIG", "Validation complete",
                                valid=all_valid, section_count=len(sections))
                
                return {
                    'valid': all_valid,
                    'sections': results
                }
                
        except Exception as e:
            gateway.log_error(f"Validation failed: {e}")
            return {
                'valid': False,
                'error': str(e)
            }


def validate_all_sections() -> Dict[str, Any]:
    """Convenience function for validation."""
    validator = ConfigurationValidator()
    return validator.validate_all_sections()


__all__ = [
    'ConfigurationValidator',
    'validate_all_sections'
]
