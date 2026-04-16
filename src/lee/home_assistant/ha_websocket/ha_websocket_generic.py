# ha_websocket_core.py
"""ha_websocket_core.py - Core WebSocket Operations (Compatibility Layer)
Version: 3.0.0
Description: Core WebSocket communication with debug tracing and timing metrics

REFACTORED: Further split to meet AWS Lambda 350-line limit.
This file now serves as a compatibility layer importing from connection and messaging modules.

Split modules:
- ha_websocket_connection.py: Connection management (connect, close, auth)
- ha_websocket_messaging.py: Message operations (send, receive, request)

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

# ===== SUGA-ISP COMPLIANT DEBUG FUNCTIONS =====



