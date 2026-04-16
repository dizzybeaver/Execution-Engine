"""network/http_constants.py

Shared constants for HTTP modules.
"""

import os

# Environment variable caching at module load time
# Eliminates repeated os.environ.get() calls in hot path (1.5-3ms per request)
_DEBUG_MODE = os.environ.get("LEE_DEBUG", "false").lower() == "true"
_PRODUCTION_MODE = os.environ.get("PRODUCTION", "false").lower() == "true"


__all__ = [
    "_DEBUG_MODE",
    "_PRODUCTION_MODE",
]
