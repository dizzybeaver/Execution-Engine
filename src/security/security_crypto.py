"""
security_crypto.py - Cryptographic operations
Version: 2025.10.16.01
Description: Encryption, decryption, hashing, and correlation ID generation

Copyright 2025 Joseph Hersey

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import base64
import hashlib
import hmac
import uuid
from typing import Dict, Any


class SecurityCrypto:
    """Handles all cryptographic operations."""
    
    def __init__(self):
        self._crypto_stats = {
            'encryptions': 0,
            'decryptions': 0,
            'hashes': 0,
            'correlation_ids_generated': 0
        }
        self._default_key = "lambda-execution-engine-default-key-2025"
    
    def get_default_key(self) -> str:
        """Get the default encryption key (public accessor for encapsulation)."""
        return self._default_key
    
    def encrypt_data(self, data: str, key: str) -> str:
        """
        Encrypt data using XOR cipher (demo only - not cryptographically secure!).
        
        Note: This is a demonstration implementation. For production use,
        implement proper encryption using AWS KMS or similar.
        """
        self._crypto_stats['encryptions'] += 1
        
        try:
            # XOR implementation
            encrypted = bytearray()
            for i, char in enumerate(data.encode()):
                encrypted.append(char ^ ord(key[i % len(key)]))
            return base64.b64encode(bytes(encrypted)).decode()
        except (ValueError, TypeError, UnicodeError) as e:
            # Fallback to simple base64 encoding on expected encoding errors
            encryption_key = key or self._default_key
            combined = f"{encryption_key}:{data}"
            return base64.b64encode(combined.encode('utf-8')).decode('utf-8')
    
    def decrypt_data(self, encrypted_data: str, key: str) -> str:
        """
        Decrypt data using XOR cipher (demo only).
        
        Note: This is a demonstration implementation. For production use,
        implement proper decryption using AWS KMS or similar.
        """
        self._crypto_stats['decryptions'] += 1
        
        try:
            # Try XOR decryption
            encrypted = base64.b64decode(encrypted_data.encode())
            decrypted = bytearray()
            for i, byte in enumerate(encrypted):
                decrypted.append(byte ^ ord(key[i % len(key)]))
            return decrypted.decode()
        except (ValueError, TypeError, UnicodeError):
            # Fallback to simple base64 decoding on expected decoding errors
            try:
                decryption_key = key or self._default_key
                decoded = base64.b64decode(encrypted_data.encode('utf-8')).decode('utf-8')
                if decoded.startswith(f"{decryption_key}:"):
                    return decoded[len(decryption_key)+1:]
                return decoded
            except (ValueError, TypeError, UnicodeError):
                # If all decoding fails, return empty string
                return ""
    
    def hash_data(self, data: str) -> str:
        """Hash data using SHA-256."""
        self._crypto_stats['hashes'] += 1
        return hashlib.sha256(data.encode()).hexdigest()
    
    def verify_hash(self, data: str, hash_value: str) -> bool:
        """Verify data against hash using constant-time comparison."""
        computed_hash = self.hash_data(data)
        return hmac.compare_digest(computed_hash, hash_value)
    
    def generate_correlation_id(self) -> str:
        """Generate unique correlation ID using UUID4."""
        self._crypto_stats['correlation_ids_generated'] += 1
        return str(uuid.uuid4())
    
    def get_stats(self) -> Dict[str, Any]:
        """Get crypto statistics."""
        return self._crypto_stats.copy()


# ===== EXPORTS =====

__all__ = [
    'SecurityCrypto'
]

# EOF
