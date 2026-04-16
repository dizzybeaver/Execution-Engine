"""cache_operations_split/stampede_protection.py

Stampede protection and stale-while-revalidate implementations.
"""

from __future__ import annotations

from typing import Any

from lee.lee_cache.cache_operations_split.models import _get_gateway
from lee.lee_cache.cache_enums import DEFAULT_CACHE_TTL
from lee.lee_cache.lee_stampede_protection import get_stampede_protection
from lee.lee_cache.stale_while_revalidate import get_stale_while_revalidate
from lee.gateway.gateway_core import generate_correlation_id

def _execute_get_with_grace_period_implementation(
    key: str,
    factory,
    ttl: int = DEFAULT_CACHE_TTL,
    grace_period: int = 30,
    correlation_id: str = None,
    **_kwargs,
) -> tuple:
    """Get value with stale-while-revalidate grace period.

    Returns tuple of (value, status) where status is 'fresh', 'stale', or 'computed'
    """
    _GatewayInterface, _execute_operation = _get_gateway()

    if correlation_id is None:
        # time and random imported at module level
        correlation_id = generate_correlation_id("cache")

    # Safe debug log
    if _execute_operation and _GatewayInterface:
        try:
            _execute_operation(_GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="CACHE",
                             message="get_with_grace_period called",
                             key=key, ttl=ttl, grace_period=grace_period)
        except (AttributeError, TypeError, ValueError):
            # Optional dependency - continue if unavailable
            ...

    swr = get_stale_while_revalidate(correlation_id=correlation_id)
    return swr.get_with_grace_period(
        key=key,
        factory=factory,
        ttl=ttl,
        grace_period=grace_period,
        correlation_id=correlation_id,
    )

def _execute_get_or_compute_implementation(
    key: str,
    factory,
    ttl: int = DEFAULT_CACHE_TTL,
    correlation_id: str = None,
    **_kwargs,
) -> Any:
    """Get value with stampede protection (request coalescing).

    Multiple concurrent requests for the same key will wait for
    a single computation instead of all executing factory().
    """
    _GatewayInterface, _execute_operation = _get_gateway()

    if correlation_id is None:
        # time and random imported at module level
        correlation_id = generate_correlation_id("cache")

    # Safe debug log
    if _execute_operation and _GatewayInterface:
        try:
            _execute_operation(_GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="CACHE",
                             message="get_or_compute called",
                             key=key, ttl=ttl)
        except (AttributeError, TypeError, ValueError):
            # Optional dependency - continue if unavailable
            ...

    protection = get_stampede_protection(correlation_id=correlation_id)
    return protection.get_or_compute(
        key=key,
        factory=factory,
        ttl=ttl,
        correlation_id=correlation_id,
    )


def _execute_process_pending_refreshes_implementation(
    correlation_id: str = None,
    **_kwargs,
) -> int:
    """Process pending async refreshes from stale-while-revalidate.

    Returns number of refreshes processed
    """
    if correlation_id is None:
        # time and random imported at module level
        correlation_id = generate_correlation_id("cache")

    swr = get_stale_while_revalidate(correlation_id=correlation_id)
    return swr.process_pending_refreshes(correlation_id=correlation_id)

