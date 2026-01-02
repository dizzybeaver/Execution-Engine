"""
Encryption Factory - Security Domain

Data encryption and hashing implementation.

UG-ISP Compliant:
- Factory contains actual implementation
- Receives logger, metrics, call_operation via DI
- NO imports outside security domain (except stdlib)
- All cross-domain calls via call_operation callback
"""

import hashlib
import secrets
import logging
import base64
import os
from typing import Any, Dict, Optional, Callable


class EncryptionFactory:
    """Encryption factory.

    Provides encryption and hashing operations:
    - XOR encryption with hash-based key derivation
    - Secure hashing (SHA256, SHA512, MD5)
    - Key and salt generation
    - Base64 encoding/decoding

    UG-ISP Compliance:
    - Uses ONLY standard library
    - Cross-domain calls via call_operation callback
    - Implements secure encryption practices
    """

    def __init__(
        self,
        logger: Optional[Any] = None,
        metrics: Optional[Any] = None,
        call_operation: Optional[Callable] = None
    ):
        """Initialize encryption factory.

        Args:
            logger: Logger instance
            metrics: Metrics instance
            call_operation: Callback for cross-domain operations
        """
        self.logger = logger or logging.getLogger(__name__)
        self.metrics = metrics
        self.call_operation = call_operation

    def encrypt(self, data: str, key: Optional[str] = None, **kwargs) -> Dict[str, str]:
        """Encrypt data using XOR encryption with hash-based key derivation.

        Note: Using XOR encryption as it's in stdlib. For production,
        consider using cryptography library's AES-GCM.

        Args:
            data: Data to encrypt
            key: Encryption key. If None, generates new key.
            **kwargs: Additional parameters

        Returns:
            Dictionary with:
                - encrypted: Base64 encoded encrypted data
                - key: Base64 encoded key (if new key was generated)
        """
        if not data:
            raise ValueError("Data cannot be empty")

        # Generate or use provided key
        if key is None:
            key_bytes = secrets.token_bytes(32)  # 256-bit key
            key_provided = False
        else:
            # Derive 32-byte key from provided key
            key_bytes = hashlib.sha256(key.encode()).digest()
            key_provided = True

        # Convert data to bytes
        data_bytes = data.encode('utf-8')

        # Simple XOR encryption with key cycling
        encrypted_bytes = bytearray()
        for i, byte in enumerate(data_bytes):
            key_byte = key_bytes[i % len(key_bytes)]
            encrypted_bytes.append(byte ^ key_byte)

        # Encode to base64
        result = {
            "encrypted": base64.b64encode(bytes(encrypted_bytes)).decode('utf-8'),
        }

        # Include key if it was generated
        if not key_provided:
            result["key"] = base64.b64encode(key_bytes).decode('utf-8')

        return result

    def decrypt(
        self,
        encrypted: str,
        key: str,
        **kwargs
    ) -> str:
        """Decrypt XOR encrypted data.

        Args:
            encrypted: Base64 encoded encrypted data
            key: Base64 encoded encryption key (or raw key string)
            **kwargs: Additional parameters

        Returns:
            Decrypted data string
        """
        if not encrypted or not key:
            raise ValueError("Both encrypted and key are required")

        try:
            # Decode from base64
            ciphertext = base64.b64decode(encrypted)

            # Derive key from provided key
            # Try to decode as base64 first
            try:
                key_bytes = base64.b64decode(key)
            except Exception:
                # If not base64, hash the string key
                key_bytes = hashlib.sha256(key.encode()).digest()

            # XOR decrypt (same as encrypt for XOR)
            decrypted_bytes = bytearray()
            for i, byte in enumerate(ciphertext):
                key_byte = key_bytes[i % len(key_bytes)]
                decrypted_bytes.append(byte ^ key_byte)

            return decrypted_bytes.decode('utf-8')

        except Exception as e:
            raise ValueError(f"Decryption failed: {e}")

    def hash(self, data: str, salt: Optional[str] = None, **kwargs) -> str:
        """Generate SHA256 hash of data.

        Args:
            data: Data to hash
            salt: Optional salt string
            **kwargs: Additional parameters

        Returns:
            Hex encoded hash
        """
        if not data:
            raise ValueError("Data cannot be empty")

        # Create hash
        hash_obj = hashlib.sha256()

        # Add salt if provided
        if salt:
            hash_obj.update(salt.encode('utf-8'))

        # Hash data
        hash_obj.update(data.encode('utf-8'))

        return hash_obj.hexdigest()

    def hash_sha512(self, data: str, salt: Optional[str] = None, **kwargs) -> str:
        """Generate SHA512 hash of data.

        Args:
            data: Data to hash
            salt: Optional salt string
            **kwargs: Additional parameters

        Returns:
            Hex encoded hash
        """
        if not data:
            raise ValueError("Data cannot be empty")

        # Create hash
        hash_obj = hashlib.sha512()

        # Add salt if provided
        if salt:
            hash_obj.update(salt.encode('utf-8'))

        # Hash data
        hash_obj.update(data.encode('utf-8'))

        return hash_obj.hexdigest()

    def hash_md5(self, data: str, **kwargs) -> str:
        """Generate MD5 hash of data.

        WARNING: MD5 is not secure for cryptographic purposes.
        Only use for legacy compatibility or non-security purposes.

        Args:
            data: Data to hash
            **kwargs: Additional parameters

        Returns:
            Hex encoded hash
        """
        if not data:
            raise ValueError("Data cannot be empty")

        return hashlib.md5(data.encode('utf-8')).hexdigest()

    def verify_hash(
        self,
        data: str,
        expected_hash: str,
        salt: Optional[str] = None,
        algorithm: str = "sha256",
        **kwargs
    ) -> bool:
        """Verify data against expected hash.

        Args:
            data: Data to verify
            expected_hash: Expected hash value
            salt: Optional salt (must match salt used for hashing)
            algorithm: Hash algorithm (sha256, sha512, md5)
            **kwargs: Additional parameters

        Returns:
            True if hash matches
        """
        if not data or not expected_hash:
            return False

        try:
            if algorithm == "sha256":
                computed_hash = self.hash(data, salt=salt)
            elif algorithm == "sha512":
                computed_hash = self.hash_sha512(data, salt=salt)
            elif algorithm == "md5":
                computed_hash = self.hash_md5(data)
            else:
                raise ValueError(f"Unsupported algorithm: {algorithm}")

            # Constant-time comparison to prevent timing attacks
            return secrets.compare_digest(computed_hash, expected_hash)

        except Exception:
            return False

    def generate_key(self, length: int = 32, **kwargs) -> str:
        """Generate cryptographic key.

        Args:
            length: Key length in bytes (default: 32)
            **kwargs: Additional parameters

        Returns:
            Base64 encoded key
        """
        key_bytes = secrets.token_bytes(length)
        return base64.b64encode(key_bytes).decode('utf-8')

    def generate_salt(self, length: int = 16, **kwargs) -> str:
        """Generate cryptographic salt.

        Args:
            length: Salt length in bytes (default: 16)
            **kwargs: Additional parameters

        Returns:
            Hex encoded salt
        """
        salt_bytes = secrets.token_bytes(length)
        return salt_bytes.hex()

    def encode_base64(self, data: str, **kwargs) -> str:
        """Encode data to base64.

        Args:
            data: Data to encode
            **kwargs: Additional parameters

        Returns:
            Base64 encoded string
        """
        if not data:
            raise ValueError("Data cannot be empty")

        data_bytes = data.encode('utf-8')
        encoded = base64.b64encode(data_bytes)
        return encoded.decode('utf-8')

    def decode_base64(self, encoded: str, **kwargs) -> str:
        """Decode data from base64.

        Args:
            encoded: Base64 encoded string
            **kwargs: Additional parameters

        Returns:
            Decoded string
        """
        if not encoded:
            raise ValueError("Encoded data cannot be empty")

        try:
            encoded_bytes = encoded.encode('utf-8')
            decoded = base64.b64decode(encoded_bytes)
            return decoded.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Base64 decoding failed: {e}")


__all__ = [
    "EncryptionFactory",
]
