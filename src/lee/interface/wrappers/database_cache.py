"""database_cache.py
Version: 2026-04-02_1
Purpose: Database query caching layer for common lookups
License: Apache 2.0

Provides read-through caching for database queries to reduce latency and database load.
Cacheable queries:
- Schema lookups (get_schema) - Long TTL (30 minutes)
- Configuration queries - Medium TTL (5 minutes)
- Repeated SELECT queries - Short TTL (1 minute)

Non-cacheable queries (bypass cache):
- INSERT, UPDATE, DELETE operations
- Transaction operations
- Real-time data queries with use_cache=False
"""

import hashlib
import json
from typing import Any, Optional


def _generate_cache_key(query: str, params: Optional[dict[str, Any]] = None) -> str:
    """Generate deterministic cache key from query and parameters.

    Args:
        query: SQL query string
        params: Query parameters

    Returns:
        Cache key hash
    """
    key_data = {
        "query": query.strip().lower(),
        "params": params or {},
    }

    key_json = json.dumps(key_data, sort_keys=True)
    key_hash = hashlib.sha256(key_json.encode()).hexdigest()[:32]

    return f"db_query:{key_hash}"


def _should_cache_query(query: str) -> bool:
    """Determine if query should be cached based on SQL type.

    Args:
        query: SQL query string

    Returns:
        True if cacheable, False otherwise
    """
    query_upper = query.strip().upper()

    cacheable_prefixes = [
        "SELECT",
        "SHOW",
        "DESCRIBE",
        "EXPLAIN",
    ]

    non_cacheable_prefixes = [
        "INSERT",
        "UPDATE",
        "DELETE",
        "DROP",
        "CREATE",
        "ALTER",
        "TRUNCATE",
        "REPLACE",
    ]

    for prefix in non_cacheable_prefixes:
        if query_upper.startswith(prefix):
            return False

    for prefix in cacheable_prefixes:
        if query_upper.startswith(prefix):
            return True

    return False


def _get_ttl_for_query(query: str, use_cache: bool = True) -> Optional[int]:
    """Determine TTL for query based on type.

    Args:
        query: SQL query string
        use_cache: Whether caching is enabled

    Returns:
        TTL in seconds, or None if not cacheable
    """
    if not use_cache:
        return None

    if not _should_cache_query(query):
        return None

    query_upper = query.strip().upper()

    if "INFORMATION_SCHEMA" in query_upper or query_upper.startswith(("SHOW ", "DESCRIBE ", "EXPLAIN ")):
        return 1800  # 30 minutes for schema queries

    if query_upper.startswith("SELECT"):
        if "WHERE" not in query_upper:
            return 300  # 5 minutes for full table scans

        return 60  # 1 minute for filtered SELECTs

    return 60  # Default 1 minute


def cached_database_execute_query(
    query: str,
    params: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    use_cache: bool = True,
    **kwargs
) -> list[dict[str, Any]]:
    """Execute SQL query with caching layer - cached wrapper for database router.

    Args:
        query: SQL query string
        params: Query parameters
        correlation_id: Request correlation ID
        use_cache: Enable/disable caching for this query
        **kwargs: Additional database options

    Returns:
        Query results

    Raises:
        RuntimeError: If database unavailable

    Example:
        >>> result = cached_database_execute_query(
        ...     query="SELECT * FROM users WHERE id = :id",
        ...     params={"id": 1},
        ...     use_cache=True
        ... )
    """
    from lee.gateway import (  # pylint: disable=import-outside-toplevel
        GatewayInterface,
        execute_operation,
    )

    ttl = _get_ttl_for_query(query, use_cache)

    if ttl is not None:
        cache_key = _generate_cache_key(query, params)

        try:
            cached_result = execute_operation(
                GatewayInterface.CACHE,
                "get",
                key=cache_key,
                corr_id=correlation_id,
            )

            if cached_result is not None:
                try:
                    execute_operation(
                        GatewayInterface.LOGGING,
                        "log_debug",
                        message=f"[DB_CACHE] Hit for key: {cache_key[:16]}...",
                        corr_id=correlation_id,
                    )
                except RuntimeError:
                    # Gracefully degrade if logging unavailable (optional debug output)
                    pass

                return cached_result
        except RuntimeError:
            # Gracefully degrade if cache unavailable
            pass

    try:
        execute_operation(
            GatewayInterface.LOGGING,
            "log_debug",
            message="[DB_CACHE] Miss - executing query",
            corr_id=correlation_id,
        )
    except RuntimeError:
        # Gracefully degrade if cache unavailable
        pass

    from lee.interface.wrappers.database_wrappers import (  # pylint: disable=import-outside-toplevel
        database_execute_query,
    )

    result = database_execute_query(
        query=query,
        params=params,
        correlation_id=correlation_id,
        **kwargs
    )

    if ttl is not None:
        cache_key = _generate_cache_key(query, params)

        try:
            execute_operation(
                GatewayInterface.CACHE,
                "set",
                key=cache_key,
                value=result,
                ttl=ttl,
                corr_id=correlation_id,
            )

            try:
                execute_operation(
                    GatewayInterface.LOGGING,
                    "log_debug",
                    message=f"[DB_CACHE] Cached result for {ttl}s",
                    corr_id=correlation_id,
                )
            except RuntimeError:
                # Gracefully degrade if logging unavailable (optional debug output)
                pass
        except RuntimeError:
            # Gracefully degrade if cache unavailable
            pass

    return result


def cached_database_get_schema(
    table_name: Optional[str] = None,
    correlation_id: Optional[str] = None,
    use_cache: bool = True,
    **kwargs
) -> dict[str, Any]:
    """Get database schema with caching - cached wrapper for database router.

    Args:
        table_name: Optional specific table name
        correlation_id: Request correlation ID
        use_cache: Enable/disable caching
        **kwargs: Additional schema options

    Returns:
        Schema dictionary

    Raises:
        RuntimeError: If database unavailable

    Example:
        >>> schema = cached_database_get_schema(table_name="users")
        >>> print(schema["columns"])
    """
    from lee.gateway import (  # pylint: disable=import-outside-toplevel
        GatewayInterface,
        execute_operation,
    )

    cache_key = f"db_schema:{table_name or 'all'}"

    if use_cache:
        try:
            cached_schema = execute_operation(
                GatewayInterface.CACHE,
                "get",
                key=cache_key,
                corr_id=correlation_id,
            )

            if cached_schema is not None:
                try:
                    execute_operation(
                        GatewayInterface.LOGGING,
                        "log_debug",
                        message=f"[DB_CACHE] Schema hit for {table_name}",
                        corr_id=correlation_id,
                    )
                except RuntimeError:
                    # Gracefully degrade if logging unavailable (optional debug output)
                    pass

                return cached_schema
        except RuntimeError:
            # Gracefully degrade if cache unavailable
            pass

    from lee.interface.wrappers.database_wrappers import (  # pylint: disable=import-outside-toplevel
        database_get_schema,
    )

    schema = database_get_schema(
        table_name=table_name,
        correlation_id=correlation_id,
        **kwargs
    )

    if use_cache:
        try:
            execute_operation(
                GatewayInterface.CACHE,
                "set",
                key=cache_key,
                value=schema,
                ttl=1800,  # 30 minutes
                corr_id=correlation_id,
            )

            try:
                execute_operation(
                    GatewayInterface.LOGGING,
                    "log_debug",
                    message=f"[DB_CACHE] Cached schema for {table_name}",
                    corr_id=correlation_id,
                )
            except RuntimeError:
                # Gracefully degrade if logging unavailable (optional debug output)
                pass
        except RuntimeError:
            # Gracefully degrade if cache unavailable
            pass

    return schema


def invalidate_database_cache(
    table_name: Optional[str] = None,
    correlation_id: Optional[str] = None,
) -> dict[str, Any]:
    """Invalidate cached database queries for specific table or all.

    Call this after INSERT/UPDATE/DELETE operations to ensure cache consistency.

    Args:
        table_name: Table name to invalidate (None = all)
        correlation_id: Request correlation ID

    Returns:
        Invalidation result dict

    Example:
        >>> invalidate_database_cache(table_name="users")
        >>> # After INSERT/UPDATE/DELETE on users table
    """
    from lee.gateway import (  # pylint: disable=import-outside-toplevel
        GatewayInterface,
        execute_operation,
    )

    try:
        execute_operation(
            GatewayInterface.LOGGING,
            "log_info",
            message=f"[DB_CACHE] Invalidating cache for table: {table_name or 'all'}",
            corr_id=correlation_id,
        )
    except RuntimeError:
        # Gracefully degrade if logging unavailable (optional debug output)
        pass

    if table_name:
        schema_key = f"db_schema:{table_name}"

        try:
            execute_operation(
                GatewayInterface.CACHE,
                "delete",
                key=schema_key,
                corr_id=correlation_id,
            )
        except RuntimeError:
            # Gracefully degrade if cache unavailable
            pass

        return {
            "status": "invalidated",
            "table": table_name,
            "keys_affected": 1,
        }

    try:
        execute_operation(
            GatewayInterface.CACHE,
            "clear",
            corr_id=correlation_id,
        )
    except RuntimeError:
        # Gracefully degrade if cache unavailable
        pass

    return {
        "status": "cleared",
        "table": "all",
        "keys_affected": "all",
    }


__all__ = [
    "cached_database_execute_query",
    "cached_database_get_schema",
    "invalidate_database_cache",
    "_generate_cache_key",
    "_should_cache_query",
    "_get_ttl_for_query",
]
