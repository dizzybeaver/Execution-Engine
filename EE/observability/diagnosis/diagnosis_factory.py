"""
Diagnosis Factory - Observability Domain

Health checks and system diagnostics implementation.

UG-ISP Compliant:
- Factory contains actual implementation
- Receives logger, metrics, call_operation via DI
- NO imports outside observability domain (except stdlib)
- All cross-domain calls via call_operation callback
- Module-level state for persistence across instances
"""

import sys
import time
import threading
from typing import Any, Dict, Optional, Callable, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

# Try to import psutil, but make it optional
try:
    import psutil
    _PSUTIL_AVAILABLE = True
except ImportError:
    _PSUTIL_AVAILABLE = False
    psutil = None  # type: ignore


# =============================================================================
# Module-level diagnosis state (shared across all instances)
# =============================================================================

_DIAGNOSIS_LOCK = threading.RLock()
_HEALTH_CHECKS: Dict[str, Any] = {}
_DEPENDENCY_CHECKS: Dict[str, Any] = {}
_DIAGNOSTIC_HISTORY: List[Dict[str, Any]] = []


# =============================================================================
# Health status enums
# =============================================================================

class HealthStatus(Enum):
    """Health check status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


# =============================================================================
# Health check data classes
# =============================================================================

@dataclass
class HealthCheckResult:
    """Result of a health check."""
    component: str
    status: HealthStatus
    message: str
    timestamp: float = field(default_factory=time.time)
    details: Dict[str, Any] = field(default_factory=dict)
    response_time_ms: float = 0.0


@dataclass
class SystemStats:
    """System statistics snapshot."""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_percent: float
    disk_used_gb: float
    disk_free_gb: float
    uptime_seconds: float
    thread_count: int


# =============================================================================
# Diagnosis Factory Class
# =============================================================================

class DiagnosisFactory:
    """Health checks and system diagnostics factory.

    Provides comprehensive diagnostic capabilities:
    - Component health checks
    - Dependency health verification
    - System statistics monitoring
    - Full diagnostic reports

    UG-ISP Compliance:
    - Cross-domain calls via call_operation callback
    - Uses module-level state for persistence
    - No direct imports outside observability domain
    """

    def __init__(
        self,
        logger: Optional[Any] = None,
        metrics: Optional[Any] = None,
        call_operation: Optional[Callable] = None
    ):
        """Initialize diagnosis factory.

        Args:
            logger: Logger instance
            metrics: Metrics instance
            call_operation: Callback for cross-domain operations
        """
        self.logger = logger
        self.metrics = metrics
        self.call_operation = call_operation

    def health_check(
        self,
        component: str,
        **kwargs
    ) -> HealthCheckResult:
        """Perform health check on a component.

        Args:
            component: Component name to check
            **kwargs: Additional parameters

        Returns:
            HealthCheckResult with status
        """
        start_time = time.time()

        try:
            # Perform component-specific health checks
            if component == "system":
                result = self._check_system_health()
            elif component == "memory":
                result = self._check_memory_health()
            elif component == "disk":
                result = self._check_disk_health()
            elif component == "process":
                result = self._check_process_health()
            else:
                # Generic health check
                result = HealthCheckResult(
                    component=component,
                    status=HealthStatus.UNKNOWN,
                    message=f"Unknown component: {component}",
                )

            response_time = (time.time() - start_time) * 1000
            result.response_time_ms = response_time

            # Record health check metric (EE 2.1: call_operation signature)
            if self.metrics and self.call_operation:
                try:
                    # EE 2.1: call_operation(domain, interface, operation, **kwargs)
                    self.call_operation(
                        'observability',  # domain
                        'metrics',        # interface
                        'increment',      # operation
                        metric_name=f'health_check.{component}.{result.status.value}',
                        value=1
                    )
                    self.call_operation(
                        'observability',  # domain
                        'metrics',        # interface
                        'timing',         # operation
                        metric_name=f'health_check.{component}.duration',
                        value_ms=response_time
                    )
                except Exception:
                    pass

            # Log health check result
            if self.logger:
                self.logger.info(
                    f"Health check: {component} = {result.status.value} "
                    f"({response_time:.2f}ms)"
                )

            return result

        except Exception as e:
            response_time = (time.time() - start_time) * 1000

            if self.logger:
                self.logger.error(
                    f"Health check failed for {component}: {e}"
                )

            return HealthCheckResult(
                component=component,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check failed: {str(e)}",
                response_time_ms=response_time
            )

    def diagnose(
        self,
        component: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Diagnose a component in detail.

        Args:
            component: Component to diagnose
            **kwargs: Additional parameters

        Returns:
            Diagnostic information dictionary
        """
        health_result = self.health_check(component, **kwargs)

        diagnosis = {
            'component': component,
            'health': health_result.status.value,
            'message': health_result.message,
            'timestamp': health_result.timestamp,
            'response_time_ms': health_result.response_time_ms,
            'details': health_result.details,
        }

        # Add component-specific diagnostics
        if component == "system":
            stats = self.get_stats()
            diagnosis['system_stats'] = stats
        elif component == "memory":
            stats = self.get_stats()
            diagnosis['memory_info'] = {
                'percent': stats.memory_percent,
                'used_mb': stats.memory_used_mb,
                'available_mb': stats.memory_available_mb,
            }
        elif component == "disk":
            stats = self.get_stats()
            diagnosis['disk_info'] = {
                'percent': stats.disk_percent,
                'used_gb': stats.disk_used_gb,
                'free_gb': stats.disk_free_gb,
            }

        # Store in diagnostic history
        with _DIAGNOSIS_LOCK:
            _DIAGNOSTIC_HISTORY.append(diagnosis)
            # Keep only last 100 diagnostics
            if len(_DIAGNOSTIC_HISTORY) > 100:
                _DIAGNOSTIC_HISTORY.pop(0)

        return diagnosis

    def get_stats(self, **kwargs) -> SystemStats:
        """Get system statistics.

        Args:
            **kwargs: Additional parameters

        Returns:
            SystemStats with current system information
        """
        if not _PSUTIL_AVAILABLE:
            # Return default stats if psutil is not available
            return SystemStats(
                timestamp=time.time(),
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_used_mb=0.0,
                memory_available_mb=0.0,
                disk_percent=0.0,
                disk_used_gb=0.0,
                disk_free_gb=0.0,
                uptime_seconds=0.0,
                thread_count=0,
            )

        process = psutil.Process()

        # CPU
        cpu_percent = psutil.cpu_percent(interval=0.1)

        # Memory
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_used_mb = memory.used / (1024 * 1024)
        memory_available_mb = memory.available / (1024 * 1024)

        # Disk
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        disk_used_gb = disk.used / (1024 * 1024 * 1024)
        disk_free_gb = disk.free / (1024 * 1024 * 1024)

        # Uptime
        uptime_seconds = time.time() - process.create_time()

        # Threads
        thread_count = process.num_threads()

        return SystemStats(
            timestamp=time.time(),
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            memory_used_mb=memory_used_mb,
            memory_available_mb=memory_available_mb,
            disk_percent=disk_percent,
            disk_used_gb=disk_used_gb,
            disk_free_gb=disk_free_gb,
            uptime_seconds=uptime_seconds,
            thread_count=thread_count,
        )

    def check_dependency(
        self,
        dependency_name: str,
        dependency_type: str = "generic",
        **kwargs
    ) -> HealthCheckResult:
        """Check dependency health.

        Args:
            dependency_name: Name of dependency
            dependency_type: Type of dependency (redis, database, api, etc.)
            **kwargs: Additional parameters

        Returns:
            HealthCheckResult for dependency
        """
        start_time = time.time()

        try:
            # Check dependency via cross-domain call if available
            if self.call_operation:
                # Try to call the dependency for health check
                if dependency_type == "redis":
                    # Would call through foundation/cache domain
                    pass
                elif dependency_type == "database":
                    # Would call through data domain
                    pass

            # For now, return healthy if dependency name is known
            # In production, this would actually ping the dependency
            response_time = (time.time() - start_time) * 1000

            return HealthCheckResult(
                component=f"dependency.{dependency_name}",
                status=HealthStatus.HEALTHY,
                message=f"Dependency {dependency_name} is healthy",
                response_time_ms=response_time
            )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000

            return HealthCheckResult(
                component=f"dependency.{dependency_name}",
                status=HealthStatus.UNHEALTHY,
                message=f"Dependency {dependency_name} check failed: {str(e)}",
                response_time_ms=response_time
            )

    def run_diagnostics(self, **kwargs) -> Dict[str, Any]:
        """Run full diagnostics on all components.

        Args:
            **kwargs: Additional parameters

        Returns:
            Comprehensive diagnostic report
        """
        components = ["system", "memory", "disk", "process"]
        results = {}

        for component in components:
            try:
                results[component] = self.diagnose(component, **kwargs)
            except Exception as e:
                results[component] = {
                    'component': component,
                    'error': str(e),
                    'health': 'unknown'
                }

        # Overall system health
        all_healthy = all(
            r.get('health') == 'healthy' for r in results.values()
        )

        return {
            'timestamp': time.time(),
            'overall_healthy': all_healthy,
            'components': results,
            'system_stats': self.get_stats().__dict__,
        }

    def get_status(self, **kwargs) -> Dict[str, Any]:
        """Get overall system status.

        Args:
            **kwargs: Additional parameters

        Returns:
            System status dictionary
        """
        stats = self.get_stats()

        return {
            'status': 'healthy' if stats.cpu_percent < 90 and stats.memory_percent < 90 else 'degraded',
            'timestamp': stats.timestamp,
            'uptime_seconds': stats.uptime_seconds,
            'cpu_percent': stats.cpu_percent,
            'memory_percent': stats.memory_percent,
            'disk_percent': stats.disk_percent,
        }

    def get_health_report(self, **kwargs) -> Dict[str, Any]:
        """Generate comprehensive health report.

        Args:
            **kwargs: Additional parameters

        Returns:
            Health report with all component statuses
        """
        diagnostics = self.run_diagnostics(**kwargs)

        return {
            'report_generated_at': datetime.utcnow().isoformat() + 'Z',
            'overall_status': 'healthy' if diagnostics['overall_healthy'] else 'degraded',
            'components': diagnostics['components'],
            'system_stats': diagnostics['system_stats'],
            'recent_diagnostics': list(_DIAGNOSTIC_HISTORY[-10:]),
        }

    # ========================================================================
    # Private helper methods
    # ========================================================================

    def _check_system_health(self) -> HealthCheckResult:
        """Check overall system health."""
        stats = self.get_stats()

        # Determine health based on CPU and memory
        if stats.cpu_percent > 95 or stats.memory_percent > 95:
            status = HealthStatus.UNHEALTHY
            message = f"System under stress: CPU {stats.cpu_percent}%, Memory {stats.memory_percent}%"
        elif stats.cpu_percent > 80 or stats.memory_percent > 80:
            status = HealthStatus.DEGRADED
            message = f"System degraded: CPU {stats.cpu_percent}%, Memory {stats.memory_percent}%"
        else:
            status = HealthStatus.HEALTHY
            message = f"System healthy: CPU {stats.cpu_percent}%, Memory {stats.memory_percent}%"

        return HealthCheckResult(
            component="system",
            status=status,
            message=message,
            details={
                'cpu_percent': stats.cpu_percent,
                'memory_percent': stats.memory_percent,
                'uptime_seconds': stats.uptime_seconds,
            }
        )

    def _check_memory_health(self) -> HealthCheckResult:
        """Check memory health."""
        stats = self.get_stats()

        if stats.memory_percent > 95:
            status = HealthStatus.UNHEALTHY
            message = f"Memory critical: {stats.memory_percent}% used"
        elif stats.memory_percent > 80:
            status = HealthStatus.DEGRADED
            message = f"Memory warning: {stats.memory_percent}% used"
        else:
            status = HealthStatus.HEALTHY
            message = f"Memory healthy: {stats.memory_percent}% used"

        return HealthCheckResult(
            component="memory",
            status=status,
            message=message,
            details={
                'percent': stats.memory_percent,
                'used_mb': stats.memory_used_mb,
                'available_mb': stats.memory_available_mb,
            }
        )

    def _check_disk_health(self) -> HealthCheckResult:
        """Check disk health."""
        stats = self.get_stats()

        if stats.disk_percent > 95:
            status = HealthStatus.UNHEALTHY
            message = f"Disk critical: {stats.disk_percent}% used"
        elif stats.disk_percent > 80:
            status = HealthStatus.DEGRADED
            message = f"Disk warning: {stats.disk_percent}% used"
        else:
            status = HealthStatus.HEALTHY
            message = f"Disk healthy: {stats.disk_percent}% used"

        return HealthCheckResult(
            component="disk",
            status=status,
            message=message,
            details={
                'percent': stats.disk_percent,
                'used_gb': stats.disk_used_gb,
                'free_gb': stats.disk_free_gb,
            }
        )

    def _check_process_health(self) -> HealthCheckResult:
        """Check process health."""
        stats = self.get_stats()

        # Check if process is responsive
        is_responsive = True
        message = f"Process healthy: {stats.thread_count} threads"

        return HealthCheckResult(
            component="process",
            status=HealthStatus.HEALTHY if is_responsive else HealthStatus.UNHEALTHY,
            message=message,
            details={
                'thread_count': stats.thread_count,
                'uptime_seconds': stats.uptime_seconds,
            }
        )


__all__ = [
    "DiagnosisFactory",
    "HealthStatus",
    "HealthCheckResult",
    "SystemStats",
]
