"""Database Wrapper Functions

Direct access to database operations (3 functions).
All functions execute via gateway internally.

NOTE: Database operations now use GatewayInterface.DATA (consolidated with BATCH)
CHANGES: 2026-03-25 - Updated from GatewayInterface.DATABASE to GatewayInterface.DATA
CHANGES: 2026-04-04 - Added SQL parameter validation for security (Cycle 6)
CHANGES: 2026-04-04 - Added complete type hints (Cycle 6 Phase 2)

Usage:
    from lee.gateway.wrappers import database

    # Execute query
    results = database.execute_query(sql='SELECT * FROM users WHERE id = ?', params=[1])

    # Get schema
    schema = database.get_schema(table_name='users')

    # Transaction
    results = database.transaction(operations=[
        ('INSERT INTO users (name) VALUES (?)', ['Alice']),
        ('INSERT INTO orders (user_id) VALUES (?)', [1]),
    ])
"""

from collections.abc import Sequence
from typing import Any, Optional

from lee.gateway.gateway_core import GatewayInterface, execute_operation

# Security: Dangerous SQL patterns that indicate injection attempts
DANGEROUS_SQL_PATTERNS = [
    '--',          # SQL comment
    ';--',         # Comment with statement terminator
    '/*',          # Multi-line comment start
    '*/',          # Multi-line comment end
    'xp_',         # Extended stored procedures (SQL Server)
    'sp_',         # System stored procedures (SQL Server)
    'DROP ',       # DROP TABLE/INDEX/etc.
    'EXEC(',       # Execute dynamic SQL
    'EXECUTE(',    # Execute dynamic SQL (full word)
]


def _validate_sql_parameter(param: Any, max_length: int = 1000) -> bool:  # pylint: disable=too-many-return-statements
    """Validate SQL parameter to prevent injection attacks.

    SECURITY CHECK: Ensures parameters are safe for SQL query execution.

    Args:
        param: Parameter to validate
        max_length: Maximum string length (default: 1000)

    Returns:
        True if parameter is safe, False otherwise
    """
    if param is None:
        return True

    if isinstance(param, str):
        # Check length
        if len(param) > max_length:
            return False

        # Check for dangerous SQL patterns (case-insensitive)
        param_lower = param.lower()
        for pattern in DANGEROUS_SQL_PATTERNS:
            if pattern.lower() in param_lower:
                return False

        # Check for shell escape sequences
        if '$(' in param or '`' in param:
            return False

        return True

    if isinstance(param, (int, float, bool)):
        return True

    if isinstance(param, Sequence):
        return all(_validate_sql_parameter(p, max_length) for p in param)

    if isinstance(param, dict):
        return all(_validate_sql_parameter(v, max_length) for v in param.values())

    # Reject unsupported types
    return False


def _validate_sql_query(sql: str) -> bool:
    """Validate SQL query string for safety.

    SECURITY CHECK: Basic SQL injection prevention at query level.

    Args:
        sql: SQL query string

    Returns:
        True if query appears safe, False otherwise
    """
    if not sql or not isinstance(sql, str):
        return False

    # Check for dangerous patterns in query
    sql_upper = sql.upper()
    dangerous_keywords = [
        'DROP TABLE',
        'DROP INDEX',
        'DELETE FROM',
        'TRUNCATE',
        'ALTER TABLE',
        'EXEC(',
        'EXECUTE(',
    ]

    for keyword in dangerous_keywords:
        if keyword in sql_upper:
            return False

    return True


def database_execute_query(
    sql: str,
    params: Optional[list[str | int | float | Optional[bool]]] = None,
    **kwargs: Any
) -> list[dict[str, Any]]:
    """Execute database query with security validation.

    Args:
        sql: SQL query string (must pass validation)
        params: Optional list of query parameters (each must pass validation)
        **kwargs: Additional options passed to gateway (e.g., timeout, retry_count)

    Returns:
        List of dictionaries representing query result rows

    Raises:
        ValueError: If SQL query or parameters are invalid or contain dangerous patterns

    Security:
        - Validates SQL query against injection patterns
        - Validates all parameter types and values
        - Blocks DROP, DELETE, TRUNCATE, ALTER, EXEC statements
        - Checks for shell escape sequences and dangerous SQL patterns
    """
    # SECURITY: Validate SQL query
    if not _validate_sql_query(sql):
        raise ValueError("SQL query validation failed: unsafe query detected")

    # SECURITY: Validate all parameters
    if params:
        for i, param in enumerate(params):
            if not _validate_sql_parameter(param):
                raise ValueError(f"SQL parameter validation failed at index {i}: unsafe parameter detected")

    return execute_operation(GatewayInterface.DATA, 'execute_query', query=sql, params=params, **kwargs)


def database_get_schema(table_name: str, **kwargs: Any) -> dict[str, Any]:
    """Get database schema information for a table.

    Args:
        table_name: Name of the table to query
        **kwargs: Additional options passed to gateway

    Returns:
        Dictionary containing schema information (columns, types, constraints)

    Raises:
        ValueError: If table_name is invalid or empty

    Security:
        - Validates table_name is a non-empty string
        - Table name length limited to 100 characters
    """
    if not table_name or not isinstance(table_name, str):
        raise ValueError(f"Table name must be a non-empty string, got: {type(table_name)}")

    if len(table_name) > 100:
        raise ValueError(f"Table name too long: {len(table_name)} characters (max: 100)")

    return execute_operation(GatewayInterface.DATA, 'get_schema', table_name=table_name, **kwargs)


def database_transaction(
    operations: list[tuple[str, Optional[list[str | int | float | Optional[bool]]]]],
    **kwargs: Any
) -> list[Any]:
    """Execute database transaction with ACID guarantees.

    Args:
        operations: List of (sql, params) tuples where:
            - sql: SQL query string (must pass validation)
            - params: Optional list of query parameters (each must pass validation)
        **kwargs: Additional options passed to gateway (e.g., isolation_level, timeout)

    Returns:
        List of results for each operation in the transaction

    Raises:
        ValueError: If any SQL query or parameters are invalid
        RuntimeError: If transaction fails (operations rolled back)

    Security:
        - Validates all SQL queries against injection patterns
        - Validates all parameters across all operations
        - Blocks dangerous SQL statements (DROP, DELETE, TRUNCATE, etc.)
        - Checks for shell escape sequences

    Transaction Behavior:
        - All operations succeed or none are applied (atomicity)
        - Intermediate state not visible to other connections (isolation)
        - Failed transactions are automatically rolled back
    """
    # SECURITY: Validate all operations
    for i, (sql, params) in enumerate(operations):
        if not _validate_sql_query(sql):
            raise ValueError(f"SQL query validation failed at operation {i}: unsafe query detected")

        if params:
            for j, param in enumerate(params):
                if not _validate_sql_parameter(param):
                    raise ValueError(f"SQL parameter validation failed at operation {i}, parameter {j}: unsafe parameter detected")

    return execute_operation(GatewayInterface.DATA, 'transaction', operations=operations, **kwargs)


__all__ = [
    'database_execute_query',
    'database_get_schema',
    'database_transaction',
]
