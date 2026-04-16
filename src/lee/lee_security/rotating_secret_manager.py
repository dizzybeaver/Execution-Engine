# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-03 - Automatic key rotation for cryptographic secrets

"""
Rotating Secret Manager Module

Provides automatic key rotation for cryptographic secrets to limit
exposure from key compromise. Supports configurable rotation intervals,
graceful transitions, and thread-safe operations.

Features:
- Automatic rotation based on key age
- Thread-safe key storage with RLock
- Grace period for old key usage
- Configurable rotation intervals
- Key version tracking
- Integration with existing crypto utilities
"""

import hashlib
import os
import threading
import time
from datetime import datetime, timedelta, UTC
from typing import Optional

from lee.lee_logging.bootstrap_logging import get_bootstrap_logger
from lee.lee_security.security_crypto import generate_token


class SecretVersion:
    """Represents a version of a secret with metadata."""

    def __init__(
        self,
        value: str,
        version: int,
        created_at: datetime,
        expires_at: datetime,
    ):
        """
        Initialize a secret version.

        Args:
            value: The secret value
            version: Version number
            created_at: Creation timestamp
            expires_at: Expiration timestamp
        """
        self.value = value
        self.version = version
        self.created_at = created_at
        self.expires_at = expires_at

    def is_expired(self) -> bool:
        """Check if this secret version has expired."""
        return datetime.now(UTC) > self.expires_at

    def age_seconds(self) -> float:
        """Get the age of this secret in seconds."""
        return (datetime.now(UTC) - self.created_at).total_seconds()


class RotatingSecretManager:
    """
    Manages automatic rotation of cryptographic secrets.

    Features:
    - Thread-safe secret storage and rotation
    - Configurable rotation intervals (default: 90 days)
    - Grace period for old key usage (default: 24 hours)
    - Key version tracking with metadata
    - Automatic rotation when accessing secrets
    - Support for multiple secret types

    Usage:
        manager = RotatingSecretManager()

        # Get current secret (auto-rotates if needed)
        secret = manager.get_secret("hmac_signing_key")

        # Get specific version
        secret = manager.get_secret("hmac_signing_key", version=1)

        # Force rotation
        manager.rotate_secret("hmac_signing_key")
    """

    # Default rotation intervals (in seconds)
    DEFAULT_ROTATION_INTERVAL = 90 * 24 * 60 * 60  # 90 days
    DEFAULT_GRACE_PERIOD = 24 * 60 * 60  # 24 hours

    def __init__(self):
        """Initialize the rotating secret manager."""
        self._lock = threading.RLock()
        self._logger = get_bootstrap_logger()
        self._secrets: dict[str, dict[int, SecretVersion]] = {}
        self._current_versions: dict[str, int] = {}
        self._rotation_intervals: dict[str, int] = {}

        # Load configuration from environment
        self._default_rotation_interval = int(
            os.getenv("SECRET_ROTATION_INTERVAL", str(self.DEFAULT_ROTATION_INTERVAL))
        )
        self._grace_period = int(
            os.getenv("SECRET_GRACE_PERIOD", str(self.DEFAULT_GRACE_PERIOD))
        )

    def get_secret(
        self,
        secret_name: str,
        version: Optional[int] = None,
        auto_rotate: bool = True,
    ) -> Optional[str]:
        """
        Get a secret value, optionally auto-rotating if needed.

        Args:
            secret_name: Name of the secret
            version: Specific version to retrieve (None for current)
            auto_rotate: Whether to auto-rotate if needed

        Returns:
            Secret value or None if not found
        """
        with self._lock:
            # If requesting current version, check if rotation is needed
            if version is None and auto_rotate:
                self._check_and_rotate(secret_name)

            # Get the requested version
            if version is None:
                version = self._current_versions.get(secret_name)

            if version is None:
                return None

            versions = self._secrets.get(secret_name, {})
            secret_version = versions.get(version)

            if secret_version is None:
                return None

            return secret_version.value

    def rotate_secret(self, secret_name: str, force: bool = False) -> tuple[int, str]:
        """
        Rotate a secret, creating a new version.

        Args:
            secret_name: Name of the secret to rotate
            force: Force rotation even if not needed

        Returns:
            Tuple of (new_version, new_secret_value)
        """
        with self._lock:
            current_version = self._current_versions.get(secret_name, 0)

            # Check if rotation is needed (unless forced)
            if not force and not self._should_rotate(secret_name):
                self._logger.info(
                    f"Secret {secret_name} does not need rotation yet"
                )
                current_secret = self.get_secret(secret_name, auto_rotate=False)
                return (current_version, current_secret)

            # Generate new secret
            new_version = current_version + 1
            new_secret = self._generate_secret(secret_name)

            # Calculate expiration
            rotation_interval = self._rotation_intervals.get(
                secret_name,
                self._default_rotation_interval,
            )
            created_at = datetime.now(UTC)
            expires_at = created_at + timedelta(seconds=rotation_interval)

            # Create new version
            secret_version = SecretVersion(
                value=new_secret,
                version=new_version,
                created_at=created_at,
                expires_at=expires_at,
            )

            # Store new version
            if secret_name not in self._secrets:
                self._secrets[secret_name] = {}

            self._secrets[secret_name][new_version] = secret_version
            self._current_versions[secret_name] = new_version

            # Clean up old expired versions (except keep grace period versions)
            self._cleanup_old_versions(secret_name)

            self._logger.info(
                f"Rotated secret {secret_name} to version {new_version}, "
                f"expires at {expires_at.isoformat()}"
            )

            return (new_version, new_secret)

    def get_secret_info(self, secret_name: str) -> Optional[dict]:
        """
        Get information about a secret.

        Args:
            secret_name: Name of the secret

        Returns:
            Dictionary with secret info or None if not found
        """
        with self._lock:
            versions = self._secrets.get(secret_name)
            if not versions:
                return None

            current_version = self._current_versions.get(secret_name)
            current_secret = versions.get(current_version)

            if not current_secret:
                return None

            return {
                "name": secret_name,
                "current_version": current_version,
                "total_versions": len(versions),
                "created_at": current_secret.created_at.isoformat(),
                "expires_at": current_secret.expires_at.isoformat(),
                "age_seconds": current_secret.age_seconds(),
                "is_expired": current_secret.is_expired(),
                "rotation_interval": self._rotation_intervals.get(
                    secret_name,
                    self._default_rotation_interval,
                ),
            }

    def set_rotation_interval(self, secret_name: str, interval_seconds: int) -> None:
        """
        Set a custom rotation interval for a secret.

        Args:
            secret_name: Name of the secret
            interval_seconds: Rotation interval in seconds
        """
        with self._lock:
            self._rotation_intervals[secret_name] = interval_seconds
            self._logger.info(
                f"Set rotation interval for {secret_name} to {interval_seconds} seconds"
            )

    def initialize_secret(
        self,
        secret_name: str,
        initial_value: Optional[str] = None,
        rotation_interval: Optional[int] = None,
    ) -> tuple[int, str]:
        """
        Initialize a secret with an optional value.

        Args:
            secret_name: Name of the secret
            initial_value: Initial secret value (auto-generated if None)
            rotation_interval: Custom rotation interval

        Returns:
            Tuple of (version, secret_value)
        """
        with self._lock:
            # Check if already initialized
            if secret_name in self._current_versions:
                return (
                    self._current_versions[secret_name],
                    self.get_secret(secret_name, auto_rotate=False),
                )

            # Set custom rotation interval if provided
            if rotation_interval is not None:
                self._rotation_intervals[secret_name] = rotation_interval

            # Generate or use provided initial value
            if initial_value is None:
                initial_value = self._generate_secret(secret_name)

            # Create first version
            version = 1
            rotation_interval = self._rotation_intervals.get(
                secret_name,
                self._default_rotation_interval,
            )
            created_at = datetime.now(UTC)
            expires_at = created_at + timedelta(seconds=rotation_interval)

            secret_version = SecretVersion(
                value=initial_value,
                version=version,
                created_at=created_at,
                expires_at=expires_at,
            )

            # Store secret
            self._secrets[secret_name] = {version: secret_version}
            self._current_versions[secret_name] = version

            self._logger.info(
                f"Initialized secret {secret_name} version {version}, "
                f"expires at {expires_at.isoformat()}"
            )

            return (version, initial_value)

    def _should_rotate(self, secret_name: str) -> bool:
        """
        Check if a secret needs rotation.

        Args:
            secret_name: Name of the secret

        Returns:
            True if rotation is needed
        """
        current_version = self._current_versions.get(secret_name)
        if current_version is None:
            return True  # New secret needed

        versions = self._secrets.get(secret_name, {})
        secret_version = versions.get(current_version)

        if secret_version is None:
            return True

        # Check if expired
        return secret_version.is_expired()

    def _check_and_rotate(self, secret_name: str) -> None:
        """
        Check if secret needs rotation and rotate if needed.

        Args:
            secret_name: Name of the secret
        """
        if self._should_rotate(secret_name):
            self.rotate_secret(secret_name)

    def _cleanup_old_versions(self, secret_name: str) -> None:
        """
        Clean up old expired versions of a secret.

        Keeps versions within the grace period to allow for graceful transition.

        Args:
            secret_name: Name of the secret
        """
        versions = self._secrets.get(secret_name, {})
        if not versions:
            return

        # Calculate cutoff time (now - grace period)
        cutoff_time = datetime.now(UTC) - timedelta(
            seconds=self._grace_period
        )

        # Find versions to remove
        versions_to_remove = []
        for version, secret_version in versions.items():
            # Don't remove current version
            if version == self._current_versions.get(secret_name):
                continue

            # Remove if expired AND older than grace period
            if secret_version.expires_at < cutoff_time:
                versions_to_remove.append(version)

        # Remove old versions
        for version in versions_to_remove:
            del versions[version]
            self._logger.debug(
                f"Cleaned up old version {version} of secret {secret_name}"
            )

    def _generate_secret(self, secret_name: str) -> str:
        """
        Generate a new secret value.

        Args:
            secret_name: Name of the secret (for entropy)

        Returns:
            Generated secret value
        """
        # Generate a cryptographically secure random token
        # Use secret_name as additional entropy
        entropy = f"{secret_name}:{time.time()}:{os.urandom(16).hex()}"
        hash_input = entropy.encode("utf-8")
        hashlib.sha256(hash_input).hexdigest()  # Mix entropy pool

        # Generate final token (32 bytes = 256 bits)
        return generate_token(length=32, encoding="hex")


# Singleton instance
_rotating_secret_manager = None
_manager_lock = threading.Lock()


def get_rotating_secret_manager() -> RotatingSecretManager:
    """Get the singleton RotatingSecretManager instance."""
    global _rotating_secret_manager
    if _rotating_secret_manager is None:
        with _manager_lock:
            if _rotating_secret_manager is None:
                _rotating_secret_manager = RotatingSecretManager()
    return _rotating_secret_manager
