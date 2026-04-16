#!/usr/bin/env python3
"""Singleton operation enumeration for singleton system."""

from enum import Enum


class SingletonOperation(Enum):
    """Enumeration of all singleton operations.

    Operations:
        GET: Retrieve a singleton instance
        SET: Set a singleton instance
        HAS: Check if a singleton exists
        DELETE: Delete a singleton instance
        CLEAR: Clear all singletons
        GET_STATS: Get singleton statistics
        RESET: Reset singleton manager
        RESET_ALL: Reset all singleton instances (legacy)
        EXISTS: Check if a singleton exists (legacy)
    """

    GET = "get"
    SET = "set"
    HAS = "has"
    DELETE = "delete"
    CLEAR = "clear"
    GET_STATS = "get_stats"
    RESET = "reset"
    RESET_ALL = "reset_all"
    EXISTS = "exists"
