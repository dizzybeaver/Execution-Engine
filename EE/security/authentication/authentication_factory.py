"""
Authentication Factory - Security Domain

Authentication and authorization implementation.

UG-ISP Compliant:
- Factory contains actual implementation
- Receives get_logger, get_metrics, call_operation factory functions via DI
- NO imports outside security domain (except stdlib)
- All cross-domain calls via call_operation(domain, interface, operation, **kwargs) callback
"""

import hashlib
import secrets
import logging
import time
import json
import base64
from typing import Any, Dict, Optional, Callable, List
from datetime import datetime, timedelta


class AuthenticationFactory:
    """Authentication factory.

    Provides authentication and authorization operations:
    - Password hashing with bcrypt
    - JWT token generation and verification
    - API key management
    - Authorization checks

    UG-ISP Compliance:
    - ONLY standard library (no external bcrypt/JWT libraries)
    - Cross-domain calls via call_operation callback
    - Implements secure hashing and token generation
    """

    # MODIFIED: EE 2.1 compliant constructor - receives factory functions
    def __init__(
        self,
        get_logger: Optional[Callable] = None,
        get_metrics: Optional[Callable] = None,
        call_operation: Optional[Callable] = None
    ):
        """Initialize authentication factory.

        Args:
            get_logger: Factory function to create loggers
            get_metrics: Factory function to create metrics collectors
            call_operation: Callback for cross-domain operations with signature: call_operation(domain, interface, operation, **kwargs)
        """
        # Create logger using factory function
        if get_logger:
            self.logger = get_logger("security.authentication")
        else:
            self.logger = logging.getLogger(__name__)

        self.get_metrics = get_metrics
        self.call_operation = call_operation

        # Default token settings
        self._token_secret = None  # Will load from config
        self._token_expiry = 3600  # 1 hour default

    # MODIFIED: EE 2.1 compliant - use correct call_operation signature
    def _get_token_secret(self) -> str:
        """Get token secret from config."""
        if self._token_secret is None:
            # Try to get from config via cross-domain call
            if self.call_operation:
                try:
                    # EE 2.1: call_operation signature is call_operation(domain, interface, operation, **kwargs)
                    self._token_secret = self.call_operation(
                        "config", "config", "get_value",
                        key="security.token_secret",
                        default="default-secret-change-me"
                    )
                except Exception:
                    self._token_secret = "default-secret-change-me"
            else:
                self._token_secret = "default-secret-change-me"
        return self._token_secret

    def hash_password(self, password: str, salt: Optional[str] = None, **kwargs) -> str:
        """Hash password using secure algorithm.

        Note: Using PBKDF2 as it's in stdlib (bcrypt is not).
        For production, consider using bcrypt or argon2.

        Args:
            password: Password to hash
            salt: Optional salt (generated if not provided)
            **kwargs: Additional parameters
                - rounds: Number of iterations (default: 100000)

        Returns:
            Hashed password with salt encoded

        Format: pbkdf2_sha256$rounds$salt$hash
        """
        if not password:
            raise ValueError("Password cannot be empty")

        rounds = kwargs.get("rounds", 100000)

        # Generate salt if not provided
        if salt is None:
            salt = secrets.token_hex(16)

        # Hash using PBKDF2-SHA256
        hash_obj = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            rounds
        )

        # Encode hash
        hash_hex = hash_obj.hex()

        # Return in format: pbkdf2_sha256$rounds$salt$hash
        return f"pbkdf2_sha256${rounds}${salt}${hash_hex}"

    def verify_password(self, password: str, hash: str, **kwargs) -> bool:
        """Verify password against hash.

        Args:
            password: Password to verify
            hash: Hash to verify against
            **kwargs: Additional parameters

        Returns:
            True if password matches hash
        """
        if not password or not hash:
            return False

        try:
            # Parse hash format
            parts = hash.split('$')
            if len(parts) != 4 or parts[0] != 'pbkdf2_sha256':
                self.logger.warning(f"Invalid hash format: {parts[0] if parts else 'empty'}")
                return False

            algorithm, rounds, salt, original_hash = parts

            # Hash the password with same parameters
            new_hash = self.hash_password(
                password,
                salt=salt,
                rounds=int(rounds)
            )

            # Compare hashes
            return new_hash == hash

        except Exception as e:
            self.logger.error(f"Password verification error: {e}")
            return False

    def generate_token(
        self,
        payload: Dict[str, Any],
        expiry: Optional[int] = None,
        **kwargs
    ) -> str:
        """Generate JWT-like token.

        Note: Simplified JWT implementation using stdlib only.
        For production, use PyJWT library.

        Args:
            payload: Token payload data
            expiry: Expiry time in seconds (default: 3600)
            **kwargs: Additional parameters

        Returns:
            Encoded token string
        """
        if not payload:
            raise ValueError("Token payload cannot be empty")

        # Set expiry
        if expiry is None:
            expiry = self._token_expiry

        # Add standard claims
        token_payload = {
            "sub": payload.get("sub", "user"),
            "iat": int(time.time()),
            "exp": int(time.time()) + expiry,
            "data": payload
        }

        # Encode header and payload
        header = {"alg": "HS256", "typ": "JWT"}
        header_b64 = base64.urlsafe_b64encode(
            json.dumps(header).encode()
        ).rstrip(b'=').decode()

        payload_b64 = base64.urlsafe_b64encode(
            json.dumps(token_payload).encode()
        ).rstrip(b'=').decode()

        # Create signature
        secret = self._get_token_secret()
        message = f"{header_b64}.{payload_b64}"
        signature = hashlib.sha256(
            f"{message}.{secret}".encode()
        ).digest()
        signature_b64 = base64.urlsafe_b64encode(signature).rstrip(b'=').decode()

        return f"{message}.{signature_b64}"

    def verify_token(self, token: str, **kwargs) -> Dict[str, Any]:
        """Verify JWT-like token.

        Args:
            token: Token string to verify
            **kwargs: Additional parameters

        Returns:
            Token payload if valid

        Raises:
            ValueError: If token is invalid or expired
        """
        if not token:
            raise ValueError("Token cannot be empty")

        try:
            # Split token
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError("Invalid token format")

            header_b64, payload_b64, signature_b64 = parts

            # Verify signature
            secret = self._get_token_secret()
            message = f"{header_b64}.{payload_b64}"
            expected_signature = hashlib.sha256(
                f"{message}.{secret}".encode()
            ).digest()
            expected_signature_b64 = base64.urlsafe_b64encode(
                expected_signature
            ).rstrip(b'=').decode()

            if signature_b64 != expected_signature_b64:
                raise ValueError("Invalid token signature")

            # Decode payload
            # Add padding if needed
            payload_b64_padded = payload_b64 + '=' * (4 - len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64_padded)
            payload = json.loads(payload_bytes)

            # Check expiry
            if payload.get("exp", 0) < int(time.time()):
                raise ValueError("Token expired")

            return payload

        except ValueError as e:
            raise
        except Exception as e:
            raise ValueError(f"Token verification failed: {e}")

    def decode_token(self, token: str, **kwargs) -> Dict[str, Any]:
        """Decode JWT-like token without verification.

        WARNING: For debugging only. Always use verify_token for security.

        Args:
            token: Token string to decode
            **kwargs: Additional parameters

        Returns:
            Token payload
        """
        if not token:
            raise ValueError("Token cannot be empty")

        try:
            # Split token
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError("Invalid token format")

            payload_b64 = parts[1]

            # Decode payload
            payload_b64_padded = payload_b64 + '=' * (4 - len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64_padded)
            payload = json.loads(payload_bytes)

            return payload

        except Exception as e:
            raise ValueError(f"Token decoding failed: {e}")

    def authorize(
        self,
        token: str,
        required_permissions: List[str],
        **kwargs
    ) -> bool:
        """Check if token has required permissions.

        Args:
            token: Token string
            required_permissions: List of required permissions
            **kwargs: Additional parameters

        Returns:
            True if authorized
        """
        try:
            # Verify token
            payload = self.verify_token(token)

            # Get user permissions
            token_permissions = payload.get("data", {}).get("permissions", [])

            # Check if all required permissions are present
            for perm in required_permissions:
                if perm not in token_permissions:
                    self.logger.warning(f"Missing permission: {perm}")
                    return False

            return True

        except Exception as e:
            self.logger.error(f"Authorization check failed: {e}")
            return False

    def generate_api_key(self, prefix: str = "ee", **kwargs) -> str:
        """Generate API key.

        Args:
            prefix: Key prefix (default: "ee")
            **kwargs: Additional parameters

        Returns:
            API key string
        """
        # Generate random bytes
        random_bytes = secrets.token_bytes(32)

        # Encode to hex
        key_hex = random_bytes.hex()

        # Format: ee_<hex>
        return f"{prefix}_{key_hex}"

    def verify_api_key(self, api_key: str, **kwargs) -> bool:
        """Verify API key format.

        Note: This only validates format. For real security,
        API keys should be stored in database and verified against stored values.

        Args:
            api_key: API key to verify
            **kwargs: Additional parameters

        Returns:
            True if format is valid
        """
        if not api_key:
            return False

        try:
            # Check format: prefix_hex
            parts = api_key.split('_')
            if len(parts) != 2:
                return False

            prefix, key_hex = parts

            # Check hex is 64 characters (32 bytes)
            if len(key_hex) != 64:
                return False

            # Check if valid hex
            int(key_hex, 16)

            return True

        except ValueError:
            return False


__all__ = [
    "AuthenticationFactory",
]
