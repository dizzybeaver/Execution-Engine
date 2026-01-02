"""
http_client/http_client_transformation.py
Version: 2025-12-10_1
Purpose: HTTP response transformation
License: Apache 2.0
"""

from typing import Dict, Any, Callable, Optional, List


class ResponseTransformer:
    """HTTP response transformation with chainable operations."""
    
    def flatten(self, data: Any, separator: str = '.') -> Dict[str, Any]:
        """Flatten nested dictionary."""
        def _flatten(d, parent_key=''):
            items = []
            for k, v in d.items():
                new_key = f"{parent_key}{separator}{k}" if parent_key else k
                if isinstance(v, dict):
                    items.extend(_flatten(v, new_key).items())
                else:
                    items.append((new_key, v))
            return dict(items)
        
        return _flatten(data) if isinstance(data, dict) else data
    
    def extract(self, data: Any, keys: List[str]) -> Dict[str, Any]:
        """Extract specific keys from data."""
        if not isinstance(data, dict):
            return data
        return {k: data.get(k) for k in keys if k in data}
    
    def map_fields(self, data: Any, field_map: Dict[str, str]) -> Dict[str, Any]:
        """Rename fields according to mapping."""
        if not isinstance(data, dict):
            return data
        return {field_map.get(k, k): v for k, v in data.items()}
    
    def filter_fields(self, data: Any, predicate: Callable) -> Dict[str, Any]:
        """Filter fields using predicate function."""
        if not isinstance(data, dict):
            return data
        return {k: v for k, v in data.items() if predicate(k, v)}
    
    def transform_values(self, data: Any, transformer: Callable) -> Dict[str, Any]:
        """Transform all values using function."""
        if not isinstance(data, dict):
            return data
        return {k: transformer(v) for k, v in data.items()}
    
    def normalize(self, data: Any, schema: Dict[str, type]) -> Dict[str, Any]:
        """Normalize data types according to schema."""
        if not isinstance(data, dict):
            return data
        result = {}
        for key, expected_type in schema.items():
            if key in data:
                try:
                    result[key] = expected_type(data[key])
                except (ValueError, TypeError):
                    result[key] = data[key]
        return result


class TransformationPipeline:
    """Chainable transformation pipeline for HTTP responses."""
    
    def __init__(self):
        self._transformations = []
    
    def add_validation(self, validator: Callable, error_handler: Optional[Callable] = None):
        """Add validation step."""
        metadata = {'error_handler': error_handler} if error_handler else {}
        self._transformations.append(('validation', validator, metadata))
        return self
    
    def add_transformation(self, transformer: Callable, metadata: Optional[Dict[str, Any]] = None):
        """Add transformation step."""
        self._transformations.append(('transformation', transformer, metadata or {}))
        return self
    
    def add_filter(self, filter_func: Callable):
        """Add filter step."""
        self._transformations.append(('filter', filter_func, {}))
        return self
    
    def execute(self, data: Any) -> Dict[str, Any]:
        """Execute pipeline on data."""
        result = data
        for step_type, operation, metadata in self._transformations:
            try:
                if step_type == 'validation':
                    validator = operation
                    error_handler = metadata.get('error_handler')
                    if not validator(result):
                        if error_handler:
                            result = error_handler(result)
                        else:
                            return {'success': False, 'error': 'Validation failed', 'data': result}
                elif step_type == 'transformation':
                    result = operation(result)
                elif step_type == 'filter':
                    result = operation(result)
            except Exception as e:
                return {'success': False, 'error': f'Pipeline step failed: {str(e)}', 'data': result}
        return {'success': True, 'data': result}


def transform_http_response(response: Dict[str, Any], transformer: Callable) -> Dict[str, Any]:
    """Transform HTTP response data."""
    from gateway import create_error_response
    
    if not response.get('success'):
        return response
    
    try:
        data = response.get('data')
        transformed = transformer(data)
        
        response['data'] = transformed
        response['transformed'] = True
        return response
        
    except Exception as e:
        return create_error_response(f"Transformation failed: {str(e)}", 'TRANSFORM_ERROR')


def create_common_transformers() -> Dict[str, Callable]:
    """Create dictionary of common transformation functions."""
    transformer = ResponseTransformer()
    
    return {
        'flatten': transformer.flatten,
        'extract': transformer.extract,
        'map': transformer.map_fields,
        'filter': transformer.filter_fields,
        'transform_values': transformer.transform_values,
        'normalize': transformer.normalize
    }


def create_transformer() -> ResponseTransformer:
    """Create response transformer instance."""
    return ResponseTransformer()


def create_pipeline() -> TransformationPipeline:
    """Create transformation pipeline instance."""
    return TransformationPipeline()


__all__ = [
    'ResponseTransformer',
    'TransformationPipeline',
    'transform_http_response',
    'create_common_transformers',
    'create_transformer',
    'create_pipeline',
]
