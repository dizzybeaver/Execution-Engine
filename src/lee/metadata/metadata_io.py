"""metadata_io.py - Metadata Statistics, Export, and Import
Version: 2026-03-18
Purpose: Statistics tracking and data persistence for metadata
License: Apache 2.0
"""

# pylint: disable=broad-exception-caught
# We catch broad exceptions in import/export operations to provide
# user-friendly error messages instead of crashing the application.

import json
import threading
import time
from pathlib import Path
from typing import Any, Optional

# Statistics tracking
_stats = {
    "events_added": 0,
    "metadata_sets": 0,
    "metadata_gets": 0,
    "metadata_deletes": 0,
    "operations_total": 0,
}
_stats_lock = threading.Lock()


def _get_statistics_implementation(correlation_id: Optional[str] = None, **kwargs) -> dict[str, Any]:
    """Get metadata statistics."""
    _ = correlation_id  # Reserved for future use
    _ = kwargs  # Reserved for future use
    with _stats_lock:
        return dict(_stats)


def _increment_stat(stat_name: str) -> None:
    """Thread-safe stat increment."""
    with _stats_lock:
        _stats[stat_name] = _stats.get(stat_name, 0) + 1
        _stats["operations_total"] = _stats.get("operations_total", 0) + 1


def _export_data_implementation(correlation_id: Optional[str] = None, **kwargs) -> dict[str, Any]:
    """Export all metadata data (events, metadata store, statistics)."""
    _ = correlation_id  # Reserved for future use
    # pylint: disable=import-outside-toplevel
    # Local imports avoid circular dependencies with metadata_store
    from lee.metadata.event_bus import get_event_bus
    from lee.metadata.metadata_store import _metadata_store

    event_bus = get_event_bus()

    export_data = {
        "export_timestamp": time.time(),
        "export_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "events": event_bus.get_all(),
        "metadata": dict(_metadata_store),
        "statistics": dict(_stats),
        "event_count": event_bus.count(),
    }

    return export_data


def _import_data_implementation(
    data: dict[str, Any],
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Import metadata data from export format.

    Returns summary of import operations.
    """
    _ = correlation_id  # Reserved for future use
    _ = kwargs  # Reserved for future use
    # pylint: disable=import-outside-toplevel
    # Local imports avoid circular dependencies with metadata_store
    from lee.metadata.event_bus import get_event_bus
    from lee.metadata.metadata_store import _metadata_store, _store_lock

    if not isinstance(data, dict):
        raise ValueError("Import data must be a dictionary")

    event_bus = get_event_bus()
    summary = {
        "events_imported": 0,
        "metadata_imported": 0,
        "statistics_imported": False,
        "errors": [],
    }

    # Import events
    if "events" in data and isinstance(data["events"], list):
        try:
            for event in data["events"]:
                if isinstance(event, dict):
                    event_bus.add(event)
                    summary["events_imported"] += 1
        except (KeyError, TypeError, AttributeError, ValueError) as e:
            summary["errors"].append(f"Event import data error: {e}")
        except Exception as e:
            summary["errors"].append(f"Event import error: {e}")

    # Import metadata
    if "metadata" in data and isinstance(data["metadata"], dict):
        try:
            with _store_lock:
                _metadata_store.clear()
                _metadata_store.update(data["metadata"])
                summary["metadata_imported"] = len(data["metadata"])
        except (KeyError, TypeError, AttributeError, ValueError) as e:
            summary["errors"].append(f"Metadata import data error: {e}")
        except Exception as e:
            summary["errors"].append(f"Metadata import error: {e}")

    # Import statistics
    if "statistics" in data and isinstance(data["statistics"], dict):
        try:
            with _stats_lock:
                _stats.clear()
                _stats.update(data["statistics"])
                summary["statistics_imported"] = True
        except (KeyError, TypeError, AttributeError, ValueError) as e:
            summary["errors"].append(f"Statistics import data error: {e}")
        except Exception as e:
            summary["errors"].append(f"Statistics import error: {e}")

    return summary


def _export_to_file_implementation(
    file_path: str,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Export metadata to file (JSON format)."""
    _ = kwargs  # Reserved for future use
    data = _export_data_implementation(correlation_id=correlation_id)

    try:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)

        return {
            "success": True,
            "file_path": str(path.absolute()),
            "size_bytes": path.stat().st_size,
            "event_count": data.get("event_count", 0),
            "metadata_count": len(data.get("metadata", {})),
        }
    except OSError as e:
        return {
            "success": False,
            "error": f"File I/O error: {e}",
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


def _import_from_file_implementation(
    file_path: str,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Import metadata from file (JSON format)."""
    _ = kwargs  # Reserved for future use
    try:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Import file not found: {file_path}")

        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        summary = _import_data_implementation(data, correlation_id=correlation_id)
        summary["source_file"] = str(path.absolute())
        return summary

    except (OSError, FileNotFoundError) as e:
        return {
            "success": False,
            "error": f"File not found or I/O error: {e}",
        }
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error": f"Invalid JSON format: {e}",
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


__all__ = [
    "_get_statistics_implementation",
    "_export_data_implementation",
    "_import_data_implementation",
    "_export_to_file_implementation",
    "_import_from_file_implementation",
    "_increment_stat",
]
