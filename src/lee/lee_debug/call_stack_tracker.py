"""lee_debug/call_stack_tracker.py
Version: 2025-03-03_1
Purpose: Call stack tracking for gateway operations
License: Apache 2.0

Tracks gateway operation call chains across interfaces.
Provides visibility into WHO calls WHAT throughout the LEE system.

Memory-efficient design using bounded deques.
Thread-safe singleton implementation.
"""

from __future__ import annotations

import threading
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class CallFrame:
    """Single frame in call stack.

    Memory-efficient representation using only essential data.
    Approximately 120-200 bytes per frame depending on string lengths.

    Attributes:
        interface: GatewayInterface value (e.g., 'cache', 'logging')
        operation: Operation name (e.g., 'get', 'set')
        timestamp: time.time() when called
        filename: Caller's filename (basename only)
        lineno: Caller's line number
        function: Caller's function name

    """

    interface: str
    operation: str
    timestamp: float
    filename: str
    lineno: int
    function: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization.

        Returns:
            Dict[str, Any]: Dict representation of frame

        """
        return {
            "interface": self.interface,
            "operation": self.operation,
            "timestamp": self.timestamp,
            "filename": self.filename,
            "lineno": self.lineno,
            "function": self.function,
        }


@dataclass
class CallStack:
    """Complete call stack for a correlation_id.

    Memory Management:
    - Average 5-10 calls per request
    - ~150 bytes per frame
    - ~1-1.5KB per request
    - Deque with maxlen=50 prevents runaway growth

    Attributes:
        correlation_id: Request correlation ID
        frames: Deque of CallFrame objects (maxlen=50)
        created_at: When this stack was created

    """

    correlation_id: str
    frames: deque[CallFrame] = field(default_factory=lambda: deque(maxlen=50))
    created_at: float = field(default_factory=time.time)

    def add_frame(self, frame: CallFrame) -> None:
        """Add frame to call stack.

        Args:
            frame: CallFrame to add

        """
        self.frames.append(frame)

    def get_frame_count(self) -> int:
        """Get number of frames in stack.

        Returns:
            int: Number of frames

        """
        return len(self.frames)

    def get_total_size_bytes(self) -> int:
        """Estimate memory size in bytes.

        Returns:
            int: Estimated size in bytes

        """
        # Base overhead + frames
        return 200 + (len(self.frames) * 150)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization.

        Returns:
            Dict[str, Any]: Dict representation of call stack

        """
        return {
            "correlation_id": self.correlation_id,
            "created_at": self.created_at,
            "frame_count": len(self.frames),
            "estimated_size_bytes": self.get_total_size_bytes(),
            "frames": [frame.to_dict() for frame in self.frames],
        }


class CallStackTracker:
    """Tracks gateway operation call chains per correlation_id.

    Thread Safety:
        Uses RLock for thread-safe operations (Lambda single-threaded
        but good practice for consistency).

    Memory Management:
        - Deque with maxlen=50 per call stack (prevents runaway growth)
        - Maximum 1000 concurrent stacks
        - Auto-purge old stacks (>5 minutes)
        - Estimated ~1-1.5MB maximum memory footprint

    Integration:
        Singleton registered via gateway.
        Accessed via DEBUG interface operations.
    """

    _instance: Optional[CallStackTracker] = None
    _lock = threading.RLock()

    def __new__(cls) -> CallStackTracker:
        """Get or create singleton instance.

        Returns:
            CallStackTracker: Singleton instance

        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, max_stacks: int = 1000, max_age_seconds: float = 300.0) -> None:
        """Initialize call stack tracker.

        Args:
            max_stacks: Maximum concurrent correlation_ids to track
            max_age_seconds: Auto-purge stacks older than this (default 5 minutes)

        """
        if getattr(self, "_initialized", False):
            return

        self._stacks: dict[str, CallStack] = {}
        self._max_stacks: int = max_stacks
        self._max_age_seconds: float = max_age_seconds
        self._enabled: bool = True
        self._created_at: float = time.time()
        self._initialized = True

    def enable(self) -> None:
        """Enable call stack tracking.

        Returns:
            None

        """
        with self._lock:
            self._enabled = True

    def disable(self) -> None:
        """Disable call stack tracking.

        Returns:
            None

        """
        with self._lock:
            self._enabled = False

    def is_enabled(self) -> bool:
        """Check if tracking is enabled.

        Returns:
            True if enabled, False otherwise

        """
        return self._enabled

    def start_call(  # pylint: disable=too-many-positional-arguments
        self,
        correlation_id: str,
        interface: str,
        operation: str,
        filename: str = "gateway",
        lineno: int = 0,
        function: str = "unknown",
    ) -> Optional[CallFrame]:
        """Record a gateway operation call.

        Args:
            correlation_id: Request correlation ID
            interface: GatewayInterface value being called
            operation: Operation name being called
            filename: Caller's filename (optional, for debugging)
            lineno: Caller's line number (optional, for debugging)
            function: Caller's function name (optional, for debugging)

        Returns:
            CallFrame if tracking enabled, None otherwise

        """
        if not self._enabled:
            return None

        with self._lock:
            # Auto-purge old stacks if at or above limit
            if len(self._stacks) >= self._max_stacks:
                self._purge_old_stacks()

            # Get or create call stack
            if correlation_id not in self._stacks:
                self._stacks[correlation_id] = CallStack(
                    correlation_id=correlation_id,
                )

            call_stack = self._stacks[correlation_id]

            # Create frame
            frame = CallFrame(
                interface=interface,
                operation=operation,
                timestamp=time.time(),
                filename=filename,
                lineno=lineno,
                function=function,
            )

            # Add frame to stack
            call_stack.add_frame(frame)

            return frame

    def get_call_stack(self, correlation_id: str) -> Optional[CallStack]:
        """Retrieve call stack for a correlation_id.

        Args:
            correlation_id: Request correlation ID

        Returns:
            CallStack if found, None otherwise

        """
        with self._lock:
            return self._stacks.get(correlation_id)

    def get_call_stack_dict(self, correlation_id: str) -> Optional[dict[str, Any]]:
        """Retrieve call stack as dictionary.

        Args:
            correlation_id: Request correlation ID

        Returns:
            Dictionary representation or None

        """
        stack = self.get_call_stack(correlation_id)
        return stack.to_dict() if stack else None

    def _purge_old_stacks(self) -> int:
        """Remove call stacks older than max_age_seconds.

        Returns:
            Number of stacks purged

        """
        now = time.time()
        to_remove = []

        for corr_id, stack in self._stacks.items():
            age = now - stack.created_at
            if age > self._max_age_seconds:
                to_remove.append(corr_id)

        for corr_id in to_remove:
            del self._stacks[corr_id]

        return len(to_remove)

    def clear_call_stack(self, correlation_id: str) -> bool:
        """Clear call stack for a specific correlation_id.

        Args:
            correlation_id: Request correlation ID

        Returns:
            True if cleared, False if not found

        """
        with self._lock:
            if correlation_id in self._stacks:
                del self._stacks[correlation_id]
                return True
            return False

    def reset(self) -> None:
        """Reset all tracked call stacks.

        Returns:
            None

        """
        with self._lock:
            self._stacks.clear()

    def get_stats(self) -> dict[str, Any]:
        """Get tracker statistics.

        Returns:
            Dictionary with tracker stats

        """
        with self._lock:
            total_frames = sum(len(stack.frames) for stack in self._stacks.values())
            total_memory = sum(stack.get_total_size_bytes() for stack in self._stacks.values())

            return {
                "enabled": self._enabled,
                "active_stacks": len(self._stacks),
                "total_frames_tracked": total_frames,
                "estimated_memory_bytes": total_memory,
                "estimated_memory_kb": total_memory / 1024,
                "max_stacks": self._max_stacks,
                "max_age_seconds": self._max_age_seconds,
                "tracker_uptime_seconds": time.time() - self._created_at,
            }


def get_call_stack_tracker() -> CallStackTracker:
    """Get singleton call stack tracker instance.

    Returns:
        CallStackTracker: CallStackTracker singleton instance

    """
    return CallStackTracker()


__all__ = [
    "CallFrame",
    "CallStack",
    "CallStackTracker",
    "get_call_stack_tracker",
]
