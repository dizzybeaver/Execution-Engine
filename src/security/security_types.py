"""
security_types.py - Security type definitions and enums
Version: 2025.10.20.01
Description: Security operation types and validation patterns

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

from enum import Enum


class SecurityOperation(Enum):
    """Security operations enumeration."""
    # Existing operations
    VALIDATE_REQUEST = "validate_request"
    VALIDATE_TOKEN = "validate_token"
    VALIDATE_STRING = "validate_string"
    VALIDATE_EMAIL = "validate_email"
    VALIDATE_URL = "validate_url"
    ENCRYPT = "encrypt"
    DECRYPT = "decrypt"
    HASH = "hash"
    VERIFY_HASH = "verify_hash"
    SANITIZE = "sanitize"
    GENERATE_CORRELATION_ID = "generate_correlation_id"
    # NEW: Cache security operations (CVE fixes)
    VALIDATE_CACHE_KEY = "validate_cache_key"
    VALIDATE_TTL = "validate_ttl"
    VALIDATE_MODULE_NAME = "validate_module_name"
    VALIDATE_NUMBER_RANGE = "validate_number_range"


class ValidationPattern(Enum):
    """Validation regex patterns."""
    EMAIL = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    URL = r'^https?://[^\s]+$'
    TOKEN = r'^[A-Za-z0-9-_]{20,}$'
    ALPHANUMERIC = r'^[a-zA-Z0-9]+$'
    NUMERIC = r'^\d+$'


# ===== EXPORTS =====

__all__ = [
    'SecurityOperation',
    'ValidationPattern'
]

# EOF
