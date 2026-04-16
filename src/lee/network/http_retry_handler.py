"""network/http_retry_handler.py

HTTP retry mechanisms with exponential backoff and error recovery.
"""

import random
import time

from lee.gateway import execute_operation, GatewayInterface
from lee.lee_config.constants import (
    HTTP_BACKOFF_FACTOR,
    HTTP_MAX_BACKOFF_CAP,
    HTTP_MAX_RETRIES,
)
from lee.network.http_constants import _DEBUG_MODE


# Exceptions
class Timeout(Exception):
    """Request timeout exception."""


class RetryHandler:
    """Handles HTTP retry logic with exponential backoff."""

    def __init__(self, max_retries=None, backoff_factor=None):
        """Initialize retry handler.

        Args:
            max_retries: Maximum number of retry attempts
            backoff_factor: Backoff multiplier for exponential delay
        """
        self.max_retries = max_retries if max_retries is not None else HTTP_MAX_RETRIES
        self.backoff_factor = backoff_factor if backoff_factor is not None else HTTP_BACKOFF_FACTOR

    def configure_retry(self, max_retries=None, backoff_factor=None):
        """Configure retry policy.

        Args:
            max_retries: Maximum number of retry attempts (None to keep current)
            backoff_factor: Backoff multiplier for retries (None to keep current)
        """
        debug_enabled = _DEBUG_MODE
        if debug_enabled:
            execute_operation(
                GatewayInterface.DEBUG, 'log',
                message=(
                    f"RetryHandler.configure_retry ENTRY - max_retries={max_retries}, "
                    f"backoff_factor={backoff_factor}"
                ),
                scope='HTTP_CORE'
            )
        if max_retries is not None:
            if not isinstance(max_retries, int) or max_retries < 0:
                raise ValueError(
                    f"max_retries must be non-negative int, got {max_retries}"
                )
            self.max_retries = max_retries

        if backoff_factor is not None:
            if not isinstance(backoff_factor, (int, float)) or backoff_factor < 0:
                raise ValueError(
                    f"backoff_factor must be non-negative number, got {backoff_factor}"
                )
            self.backoff_factor = float(backoff_factor)
        if debug_enabled:
            execute_operation(
                GatewayInterface.DEBUG, 'log',
                message=(
                    f"RetryHandler.configure_retry EXIT - "
                    f"max_retries={self.max_retries}, backoff_factor={self.backoff_factor}"
                ),
                scope='HTTP_CORE'
            )

    def should_retry(self, attempt, exception_type):
        """Determine if request should be retried.

        Args:
            attempt: Current attempt number
            exception_type: Type of exception that occurred

        Returns:
            bool: True if should retry, False otherwise
        """
        debug_enabled = _DEBUG_MODE
        should_retry = attempt <= self.max_retries
        if debug_enabled:
            execute_operation(
                GatewayInterface.DEBUG, 'log',
                message=(
                    f"RetryHandler.should_retry - attempt={attempt}, "
                    f"max_retries={self.max_retries}, should_retry={should_retry}"
                ),
                scope='HTTP_CORE'
            )
        return should_retry

    def calculate_backoff(self, attempt):
        """Calculate exponential backoff delay with jitter.

        Args:
            attempt: Current attempt number

        Returns:
            float: Backoff delay in seconds
        """
        # Optimized jitter: narrower range (95-105%) for more predictable delays
        # Cap maximum backoff at configured maximum to prevent excessive delays
        exponential_backoff = self.backoff_factor * (2 ** (attempt - 1))
        capped_backoff = min(exponential_backoff, HTTP_MAX_BACKOFF_CAP)
        backoff = capped_backoff * random.uniform(0.95, 1.05)

        debug_enabled = _DEBUG_MODE
        if debug_enabled:
            execute_operation(
                GatewayInterface.DEBUG, 'log',
                message=(
                    f"RetryHandler.calculate_backoff - attempt={attempt}, "
                    f"backoff={backoff:.2f}s (exponential={exponential_backoff:.2f}s, "
                    f"capped={capped_backoff:.2f}s)"
                ),
                scope='HTTP_CORE'
            )
        return backoff

    def wait_with_backoff(self, attempt):
        """Wait for calculated backoff period.

        Args:
            attempt: Current attempt number
        """
        backoff = self.calculate_backoff(attempt)
        debug_enabled = _DEBUG_MODE
        if debug_enabled:
            execute_operation(
                GatewayInterface.DEBUG, 'log',
                message=f"RetryHandler.wait_with_backoff - sleeping {backoff:.2f}s",
                scope='HTTP_CORE'
            )
        time.sleep(backoff)


__all__ = [
    "RetryHandler",
    "Timeout",
]
