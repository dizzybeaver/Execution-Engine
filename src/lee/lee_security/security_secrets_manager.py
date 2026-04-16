# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-06 - AWS Secrets Manager integration for secure token storage

"""
AWS Secrets Manager Integration Module

Provides secure token retrieval from AWS Secrets Manager with fallback to
environment variables. Implements caching, error handling, and CloudWatch
metrics integration.
"""

import json
import logging
import os
import time
from typing import Optional, Dict, Any

# Import boto3 for AWS Secrets Manager
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class SecretsManagerError(Exception):
    """Base exception for Secrets Manager operations."""


# Error code handler mapping for O(1) dispatch
_SECRET_ERROR_HANDLERS = {
    'ResourceNotFoundException': (
        lambda msg, logger: logger.warning("Secret not found: %s", msg)
    ),
    'AccessDeniedException': (
        lambda msg, logger: logger.error("Access denied to secret: %s", msg)
    ),
}


class SecretsManagerClient:
    """
    AWS Secrets Manager client with caching and fallback support.

    Features:
    - Token caching with TTL (5 minutes)
    - Automatic fallback to environment variables
    - CloudWatch metrics integration
    - Comprehensive error handling
    - Lazy initialization (only creates client when needed)
    """

    def __init__(self, secret_name: Optional[str] = None, cache_ttl_seconds: int = 300):
        """
        Initialize Secrets Manager client.

        Args:
            secret_name: Name of the secret in Secrets Manager (default: from env var)
            cache_ttl_seconds: Cache TTL in seconds (default: 300)
        """
        self.secret_name = secret_name or os.getenv('SECRETS_MANAGER_SECRET_NAME', 'lee/ha-token')
        self.cache_ttl_seconds = cache_ttl_seconds
        self._cached_secret: Optional[str] = None
        self._cache_timestamp: Optional[float] = None
        self._client: Optional[Any] = None
        self._metrics_enabled = os.getenv('CLOUDWATCH_METRICS_ENABLED', 'true').lower() == 'true'

        # Check if Secrets Manager is enabled
        self._use_secrets_manager = os.getenv('USE_SECRETS_MANAGER', 'false').lower() == 'true'

        logger.info("Secrets Manager initialized: enabled=%s, secret_name=%s",
                    self._use_secrets_manager, self.secret_name)

    def _get_client(self) -> Any:
        """
        Lazy initialization of boto3 Secrets Manager client.

        Returns:
            boto3 Secrets Manager client

        Raises:
            SecretsManagerError: If client creation fails
        """
        if self._client is None:
            try:
                self._client = boto3.client('secretsmanager')
                logger.debug("Secrets Manager client created successfully")
            except Exception as e:
                logger.error("Failed to create Secrets Manager client: %s", e)
                raise SecretsManagerError(f"Failed to create Secrets Manager client: {e}") from e

        return self._client

    def _is_cache_valid(self) -> bool:
        """Check if cached secret is still valid."""
        if self._cached_secret is None or self._cache_timestamp is None:
            return False

        cache_age = time.time() - self._cache_timestamp
        return cache_age < self.cache_ttl_seconds

    def _publish_metric(self, metric_name: str, value: float, unit: str = 'Count') -> None:
        """
        Publish custom metric to CloudWatch.

        Args:
            metric_name: Name of the metric
            value: Metric value
            unit: CloudWatch unit (Count, None, etc.)
        """
        if not self._metrics_enabled:
            return

        try:
            # Note: In Lambda, use CloudWatch Logs Embedded Metric Format (EMF)
            # For simplicity, we log the metric and can use CloudWatch Logs Insights
            logger.info('CloudWatchMetric: {"name": "%s", "value": %s, "unit": "%s"}',
                       metric_name, value, unit)
        except Exception as e:
            logger.warning("Failed to publish metric %s: %s", metric_name, e)

    def get_secret_value(self, secret_key: str = 'ha_token') -> Optional[str]:
        """
        Retrieve secret value from Secrets Manager with caching and fallback.

        Priority order:
        1. Cached secret (if valid)
        2. AWS Secrets Manager (if enabled)
        3. Environment variable fallback

        Args:
            secret_key: Key within the secret JSON (default: 'ha_token')

        Returns:
            Secret value or None if not found

        Raises:
            SecretsManagerError: If retrieval fails and no fallback available
        """
        # Check cache first
        if self._is_cache_valid():
            logger.debug("Using cached secret for key: %s", secret_key)
            return self._cached_secret

        # Try Secrets Manager if enabled
        if self._use_secrets_manager:
            try:
                return self._fetch_from_secrets_manager(secret_key)
            except SecretsManagerError as e:
                logger.warning("Failed to fetch from Secrets Manager: %s", e)
                self._publish_metric('SecretsManagerFetchFailure', 1, 'Count')

        # Fallback to environment variable
        return self._fallback_to_env_var(secret_key)

    def _fetch_from_secrets_manager(self, secret_key: str) -> str:
        """
        Fetch secret from AWS Secrets Manager.

        Args:
            secret_key: Key within the secret JSON

        Returns:
            Secret value

        Raises:
            SecretsManagerError: If retrieval fails
        """
        try:
            client = self._get_client()

            logger.info("Fetching secret from Secrets Manager: %s", self.secret_name)
            start_time = time.time()

            response = client.get_secret_value(SecretId=self.secret_name)

            elapsed_ms = (time.time() - start_time) * 1000
            logger.info("Secrets Manager fetch completed in %.2fms", elapsed_ms)
            self._publish_metric('SecretsManagerFetchLatency', elapsed_ms, 'Milliseconds')

            # Parse secret
            if 'SecretString' in response:
                secret_data = json.loads(response['SecretString'])
            elif 'SecretBinary' in response:
                # pylint: disable=import-outside-toplevel
                import base64
                secret_data = json.loads(base64.b64decode(response['SecretBinary']))
            else:
                raise SecretsManagerError("Secret response contains neither SecretString nor SecretBinary")

            # Extract the requested key
            if secret_key not in secret_data:
                raise SecretsManagerError(f"Key '{secret_key}' not found in secret")

            secret_value = secret_data[secret_key]

            # Validate secret value
            if not secret_value or not isinstance(secret_value, str):
                raise SecretsManagerError(f"Invalid secret value for key '{secret_key}'")

            # Cache the secret
            self._cached_secret = secret_value
            self._cache_timestamp = time.time()

            self._publish_metric('SecretsManagerFetchSuccess', 1, 'Count')
            logger.info("Successfully retrieved and cached secret for key: %s", secret_key)

            return secret_value

        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            error_message = e.response.get('Error', {}).get('Message', str(e))

            # Use dictionary dispatch for O(1) lookup instead of if/elif chain
            error_handler = _SECRET_ERROR_HANDLERS.get(error_code)
            if error_handler:
                error_handler(self.secret_name, logger)
            else:
                logger.error("ClientError fetching secret: %s - %s", error_code, error_message)

            raise SecretsManagerError(f"Failed to fetch secret: {error_message}") from e

        except json.JSONDecodeError as e:
            logger.error("Failed to parse secret JSON: %s", e)
            raise SecretsManagerError(f"Invalid secret JSON format: {e}") from e

        except Exception as e:
            logger.error("Unexpected error fetching secret: %s", e)
            raise SecretsManagerError(f"Unexpected error: {e}") from e

    def _fallback_to_env_var(self, secret_key: str) -> Optional[str]:
        """
        Fallback to environment variable for secret.

        Args:
            secret_key: Key name (used to determine env var name)

        Returns:
            Environment variable value or None
        """
        # Map common secret keys to environment variable names
        env_var_map = {
            'ha_token': 'HOME_ASSISTANT_API_KEY',
            'home_assistant_token': 'HOME_ASSISTANT_API_KEY',
            'token': 'HOME_ASSISTANT_API_KEY'
        }

        env_var_name = env_var_map.get(secret_key)

        if not env_var_name:
            logger.warning("No environment variable mapping for secret key: %s", secret_key)
            return None

        env_value = os.getenv(env_var_name)

        if env_value:
            logger.info("Using environment variable fallback: %s", env_var_name)
            self._publish_metric('SecretsManagerEnvFallback', 1, 'Count')

            # Cache the fallback value
            self._cached_secret = env_value
            self._cache_timestamp = time.time()

            return env_value

        logger.warning("Environment variable not found: %s", env_var_name)
        self._publish_metric('SecretsManagerNoFallback', 1, 'Count')
        return None

    def invalidate_cache(self) -> None:
        """Invalidate the cached secret."""
        self._cached_secret = None
        self._cache_timestamp = None
        logger.debug("Secret cache invalidated")

    def get_ha_token(self) -> Optional[str]:
        """
        Convenience method to get Home Assistant token.

        Returns:
            HA token or None if not found
        """
        return self.get_secret_value('ha_token')

    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on Secrets Manager integration.

        Returns:
            Health check results
        """
        health = {
            'enabled': self._use_secrets_manager,
            'secret_name': self.secret_name,
            'cache_valid': self._is_cache_valid(),
            'cache_ttl_seconds': self.cache_ttl_seconds,
            'has_cached_secret': self._cached_secret is not None,
            'client_initialized': self._client is not None
        }

        if self._use_secrets_manager:
            try:
                # Test connection by attempting to describe secret
                client = self._get_client()
                client.describe_secret(SecretId=self.secret_name)
                health['secret_accessible'] = True
            except Exception as e:
                health['secret_accessible'] = False
                health['error'] = str(e)

        return health


# Singleton instance for reuse across Lambda invocations
_secrets_manager_instance: Optional[SecretsManagerClient] = None


def get_secrets_manager_client() -> SecretsManagerClient:
    """
    Get singleton Secrets Manager client instance.

    Returns:
        SecretsManagerClient instance
    """
    global _secrets_manager_instance  # pylint: disable=global-statement

    if _secrets_manager_instance is None:
        _secrets_manager_instance = SecretsManagerClient()

    return _secrets_manager_instance


def get_ha_token() -> Optional[str]:
    """
    Convenience function to get Home Assistant token.

    Returns:
        HA token or None if not found
    """
    client = get_secrets_manager_client()
    return client.get_ha_token()
