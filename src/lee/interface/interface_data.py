# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-11 - Refactor to use graceful_import decorator


"""interface/interface_data.py
Version: 2026-04-11_2
Purpose: Data interface router with Static DDS
License: Apache 2.0
"""

from collections.abc import Callable, Sequence
from typing import Any

from lee.utils.graceful_import import graceful_import


# ===== CONFIGURATION =====

@graceful_import('lee.lee_config.variables')
def _import_config():
    from lee.lee_config.variables import (
        DATA_MAX_BATCH_SIZE,
        DATA_MAX_PARALLEL_OPS,
    )
    return {
        'DATA_MAX_BATCH_SIZE': DATA_MAX_BATCH_SIZE,
        'DATA_MAX_PARALLEL_OPS': DATA_MAX_PARALLEL_OPS,
    }


_config_vars = _import_config()
_CONFIG_AVAILABLE = _import_config.__dict__.get('_VARIABLES_AVAILABLE', False)

if _CONFIG_AVAILABLE:
    DATA_MAX_BATCH_SIZE = _config_vars['DATA_MAX_BATCH_SIZE']
    DATA_MAX_PARALLEL_OPS = _config_vars['DATA_MAX_PARALLEL_OPS']
else:
    # Fallback to hardcoded defaults if config unavailable
    DATA_MAX_BATCH_SIZE = 100
    DATA_MAX_PARALLEL_OPS = 20

# ===== DATABASE INTERFACE IMPORTS =====

@graceful_import(['lee.interface.wrappers.database_cache',
                  'lee.interface.wrappers.database_wrappers'])
def _import_database():
    from lee.interface.wrappers.database_cache import (
        cached_database_execute_query as _cached_execute_query_impl,
        cached_database_get_schema as _cached_get_schema_impl,
        invalidate_database_cache as _invalidate_cache_impl,
    )
    from lee.interface.wrappers.database_wrappers import (
        database_execute_query as _execute_query_impl,
        database_get_schema as _get_schema_impl,
        database_transaction as _transaction_impl,
    )
    return {
        'cached_execute_query': _cached_execute_query_impl,
        'cached_get_schema': _cached_get_schema_impl,
        'invalidate_cache': _invalidate_cache_impl,
        'execute_query': _execute_query_impl,
        'get_schema': _get_schema_impl,
        'transaction': _transaction_impl,
    }


_database_funcs = _import_database()
_DATABASE_AVAILABLE = (
    _import_database.__dict__.get('_DATABASE_CACHE_AVAILABLE', False) or
    _import_database.__dict__.get('_DATABASE_WRAPPERS_AVAILABLE', False)
)
_DATABASE_IMPORT_ERROR = _import_database.__dict__.get('_DATABASE_CACHE_IMPORT_ERROR',
                                        _import_database.__dict__.get('_DATABASE_WRAPPERS_IMPORT_ERROR',
                                                                        None))

if _DATABASE_AVAILABLE:
    _cached_execute_query_impl = _database_funcs['cached_execute_query']
    _cached_get_schema_impl = _database_funcs['cached_get_schema']
    _invalidate_cache_impl = _database_funcs['invalidate_cache']
    _execute_query_impl = _database_funcs['execute_query']
    _get_schema_impl = _database_funcs['get_schema']
    _transaction_impl = _database_funcs['transaction']

# ===== BATCH INTERFACE IMPORTS =====

@graceful_import('lee.batch.batch_generic')
def _import_batch():
    from lee.batch.batch_generic import (
        batch_ha_calls_implementation as _batch_ha_calls_impl,
        batch_process_implementation as _batch_process_impl,
        parallel_execute_implementation as _parallel_execute_impl,
    )
    return {
        'batch_ha_calls': _batch_ha_calls_impl,
        'batch_process': _batch_process_impl,
        'parallel_execute': _parallel_execute_impl,
    }


_batch_funcs = _import_batch()
_BATCH_AVAILABLE = _import_batch.__dict__.get('_BATCH_GENERIC_AVAILABLE', False)
_BATCH_IMPORT_ERROR = _import_batch.__dict__.get('_BATCH_GENERIC_IMPORT_ERROR', None)

if _BATCH_AVAILABLE:
    _batch_ha_calls_impl = _batch_funcs['batch_ha_calls']
    _batch_process_impl = _batch_funcs['batch_process']
    _parallel_execute_impl = _batch_funcs['parallel_execute']

# ===== SECURITY VALIDATION =====

# SQL query allowlist (safe operations only) - from DATABASE
_SQL_QUERY_ALLOWLIST = {
    'SELECT',
    'PRAGMA',
    'EXPLAIN',
    'BEGIN',
    'COMMIT',
    'ROLLBACK',
}

# Dangerous SQL patterns to block - from DATABASE
_SQL_DANGEROUS_PATTERNS = [
    ';--',
    'DROP',
    'DELETE',
    'TRUNCATE',
    'ALTER',
    'CREATE',
    'INSERT',
    'UPDATE',
    'GRANT',
    'REVOKE',
    'EXEC',
    'EXECUTE',
    'SCRIPT',
    'EVAL',
    'xp_',
    'sp_',
]

# Maximum batch sizes to prevent DoS - from BATCH (now from config)
_MAX_BATCH_SIZE = DATA_MAX_BATCH_SIZE
_MAX_PARALLEL_OPS = DATA_MAX_PARALLEL_OPS


def _validate_sql_query(query: str) -> None:
    """Validate SQL query to prevent injection attacks.

    Args:
        query: SQL query string to validate

    Raises:
        ValueError: If query contains dangerous patterns or violates allowlist
        TypeError: If query is not a string
    """
    if not isinstance(query, str):
        raise TypeError(f"SQL query must be string, got {type(query).__name__}")

    query_upper = query.strip().upper()

    is_allowed = False
    for allowed_op in _SQL_QUERY_ALLOWLIST:
        if query_upper.startswith(allowed_op):
            is_allowed = True
            break

    if not is_allowed:
        allowed = ', '.join(sorted(_SQL_QUERY_ALLOWLIST))
        first_word = (
            query_upper.split()[0] if query_upper.split() else 'empty'
        )
        raise ValueError(
            f"SQL query must start with allowed operation. "
            f"Query starts with: {first_word}. "
            f"Allowed: {allowed}"
        )

    query_upper_for_check = query.upper()
    for pattern in _SQL_DANGEROUS_PATTERNS:
        if pattern in query_upper_for_check:
            raise ValueError(
                f"SQL query contains dangerous pattern: '{pattern}'. "
                f"This operation is not allowed through the generic query interface."
            )

    if ';' in query and not query.strip().endswith(';'):
        raise ValueError(
            "SQL query contains multiple statements (semicolon in middle). "
            "Only single statements are allowed."
        )


def _validate_query_params(kwargs: dict[str, Any]) -> None:
    """Validate query parameter for execute_query operation."""
    if "query" not in kwargs:
        raise ValueError("data.execute_query requires 'query' parameter")

    query = kwargs["query"]
    if not isinstance(query, str):
        raise TypeError(f"Query must be string, got {type(query).__name__}")

    _validate_sql_query(query)


def _validate_batch_size(batch_size: int, max_size: int = _MAX_BATCH_SIZE) -> None:
    """Validate batch size parameter.

    Args:
        batch_size: Batch size to validate
        max_size: Maximum allowed batch size

    Raises:
        ValueError: If batch_size exceeds maximum or is negative
        TypeError: If batch_size is not an integer
    """
    if not isinstance(batch_size, int):
        raise TypeError(f"Batch size must be integer, got {type(batch_size).__name__}")

    if batch_size < 1:
        raise ValueError(f"Batch size must be at least 1, got {batch_size}")

    if batch_size > max_size:
        raise ValueError(
            f"Batch size {batch_size} exceeds maximum {max_size}. "
            f"Large batches can cause performance issues or DoS."
        )


def _validate_operations_list(
    operations: list,
    max_size: int = _MAX_BATCH_SIZE
) -> None:
    """Validate operations list for batch processing.

    Args:
        operations: List of operations to validate
        max_size: Maximum allowed operations

    Raises:
        ValueError: If operations list exceeds maximum
        TypeError: If operations is not a list
    """
    if not isinstance(operations, Sequence):
        raise TypeError(f"Operations must be sequence, got {type(operations).__name__}")

    if len(operations) > max_size:
        raise ValueError(
            f"Operations list size {len(operations)} exceeds maximum {max_size}. "
            f"Large batches can cause performance issues or DoS."
        )

    if len(operations) == 0:
        raise ValueError("Operations list cannot be empty")


def _validate_execute_query_params(kwargs: dict[str, Any]) -> None:
    """Validate parameters for execute_query operation."""
    _validate_query_params(kwargs)


def _validate_transaction_params(kwargs: dict[str, Any]) -> None:
    """Validate parameters for transaction operation."""
    if "queries" in kwargs:
        queries = kwargs["queries"]
        if not isinstance(queries, Sequence):
            raise TypeError("Transaction 'queries' must be a sequence")
        for i, query_item in enumerate(queries):
            if not isinstance(query_item, dict):
                raise TypeError(f"Transaction query {i} must be a dict")
            if "query" not in query_item:
                raise ValueError(f"Transaction query {i} missing 'query' field")
            _validate_sql_query(query_item["query"])


def _validate_batch_ha_calls_params(kwargs: dict[str, Any]) -> None:
    """Validate parameters for batch_ha_calls operation."""
    if "operations" in kwargs:
        _validate_operations_list(kwargs["operations"])


def _validate_parallel_execute_params(kwargs: dict[str, Any]) -> None:
    """Validate parameters for parallel_execute operation."""
    if "operations" in kwargs:
        _validate_operations_list(kwargs["operations"], max_size=_MAX_PARALLEL_OPS)


def _validate_batch_process_params(kwargs: dict[str, Any]) -> None:
    """Validate parameters for batch_process operation."""
    if "batch_size" in kwargs:
        _validate_batch_size(kwargs["batch_size"])
    if "items" in kwargs:
        items = kwargs["items"]
        if isinstance(items, (list, tuple)):
            _validate_operations_list(list(items), max_size=_MAX_BATCH_SIZE * 2)


# ===== VALIDATION DISPATCH =====

_VALIDATION_DISPATCH: dict[str, dict[str, Any]] = {
    "execute_query": {
        "func": _validate_execute_query_params,
        "category": "database",
        "description": "Validate SQL query parameters",
    },
    "execute_query_nocache": {
        "func": _validate_execute_query_params,
        "category": "database",
        "description": "Validate SQL query parameters (no cache)",
    },
    "get_schema": {
        "func": _validate_query_params,
        "category": "database",
        "description": "Validate get_schema parameters",
    },
    "get_schema_nocache": {
        "func": _validate_query_params,
        "category": "database",
        "description": "Validate get_schema parameters (no cache)",
    },
    "transaction": {
        "func": _validate_transaction_params,
        "category": "database",
        "description": "Validate transaction parameters",
    },
    "invalidate_cache": {
        "func": lambda _kwargs: None,
        "category": "database",
        "description": "No validation needed for cache invalidation",
    },
    "batch_ha_calls": {
        "func": _validate_batch_ha_calls_params,
        "category": "batch",
        "description": "Validate batch HA calls parameters",
    },
    "parallel_execute": {
        "func": _validate_parallel_execute_params,
        "category": "batch",
        "description": "Validate parallel execute parameters",
    },
    "batch_process": {
        "func": _validate_batch_process_params,
        "category": "batch",
        "description": "Validate batch process parameters",
    },
}


# ===== DATABASE IMPLEMENTATION IMPORTS =====

try:
    from lee.interface.wrappers.database_cache import (
        cached_database_execute_query as _cached_execute_query_impl,
    )
    from lee.interface.wrappers.database_cache import (
        cached_database_get_schema as _cached_get_schema_impl,
    )
    from lee.interface.wrappers.database_cache import (
        invalidate_database_cache as _invalidate_cache_impl,
    )
    from lee.interface.wrappers.database_wrappers import (
        database_execute_query as _execute_query_impl,
    )
    from lee.interface.wrappers.database_wrappers import (
        database_get_schema as _get_schema_impl,
    )
    from lee.interface.wrappers.database_wrappers import (
        database_transaction as _transaction_impl,
    )
except ImportError as e:
    _DATABASE_AVAILABLE = False
    _DATABASE_IMPORT_ERROR = str(e)


# ===== BATCH IMPLEMENTATION IMPORTS =====

try:
    from lee.batch.batch_generic import (
        batch_ha_calls_implementation as _batch_ha_calls_impl,
    )
    from lee.batch.batch_generic import (
        batch_process_implementation as _batch_process_impl,
    )
    from lee.batch.batch_generic import (
        parallel_execute_implementation as _parallel_execute_impl,
    )
except ImportError as e:
    _BATCH_AVAILABLE = False
    _BATCH_IMPORT_ERROR = str(e)


# ===== CONSOLIDATED DISPATCH =====

_DATA_DISPATCH: dict[str, dict[str, Any]] = {}

# Add DATABASE operations if available
if _DATABASE_AVAILABLE:
    _DATA_DISPATCH.update({
        "execute_query": {
            "func": _cached_execute_query_impl,
            "category": "database",
            "description": "Execute SQL query with parameters (cached)",
        },
        "execute_query_nocache": {
            "func": _execute_query_impl,
            "category": "database",
            "description": "Execute SQL query without caching",
        },
        "get_schema": {
            "func": _cached_get_schema_impl,
            "category": "database",
            "description": "Get database schema information (cached)",
        },
        "get_schema_nocache": {
            "func": _get_schema_impl,
            "category": "database",
            "description": "Get database schema without caching",
        },
        "transaction": {
            "func": _transaction_impl,
            "category": "database",
            "description": "Execute multiple queries in a transaction",
        },
        "invalidate_cache": {
            "func": _invalidate_cache_impl,
            "category": "database",
            "description": "Invalidate database query cache",
        },
    })

# Add BATCH operations if available
if _BATCH_AVAILABLE:
    _DATA_DISPATCH.update({
        "batch_ha_calls": {
            "func": _batch_ha_calls_impl,
            "category": "batch",
            "description": "Execute multiple HA operations in batch",
        },
        "parallel_execute": {
            "func": _parallel_execute_impl,
            "category": "batch",
            "description": "Execute operations in parallel",
        },
        "batch_process": {
            "func": _batch_process_impl,
            "category": "batch",
            "description": "Process multiple items in batch",
        },
    })


def execute_data_operation(operation: str, **kwargs) -> Any:
    """Route data operations using static dispatch dictionary.

    Consolidates DATABASE and BATCH operations into single interface.

    Args:
        operation: Data operation to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result

    Raises:
        RuntimeError: If data interface unavailable
        ValueError: If operation unknown or validation fails
        TypeError: If parameters are wrong type
    """
    # Check if required subsystems are available
    operation_entry = _DATA_DISPATCH.get(operation)
    if not operation_entry:
        category = "unknown"
        # Try to determine category from operation name
        if operation in ["execute_query", "get_schema", "transaction"]:
            category = "database"
            if not _DATABASE_AVAILABLE:
                error_msg = (
                    f"Database operations unavailable: "
                    f"{_DATABASE_IMPORT_ERROR}"
                )
                raise RuntimeError(error_msg)
        elif operation in ["batch_ha_calls", "parallel_execute", "batch_process"]:
            category = "batch"
            if not _BATCH_AVAILABLE:
                error_msg = (
                    f"Batch operations unavailable: "
                    f"{_BATCH_IMPORT_ERROR}"
                )
                raise RuntimeError(error_msg)

        valid_ops = ", ".join(_DATA_DISPATCH.keys())
        raise ValueError(
            f"Unknown data operation: '{operation}' (category: {category}). "
            f"Valid: {valid_ops}",
        )

    # SECURITY: Validate based on operation type using dispatch dictionary
    validation_entry = _VALIDATION_DISPATCH.get(operation)
    if validation_entry:
        validator = validation_entry["func"]
        validator(kwargs)

    handler: Callable = operation_entry["func"]
    return handler(**kwargs)


__all__ = ["execute_data_operation"]
