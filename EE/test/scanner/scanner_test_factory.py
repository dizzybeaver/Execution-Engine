"""
Scanner Test Factory - Test Domain

Contains implementation of scanner test operations.

UG-ISP Architecture:
- Factory contains implementation
- Interface routes to factory methods
- Cross-domain via call_operation() only
"""

from __future__ import annotations
from typing import Any, Dict, Optional, List, Protocol
from pathlib import Path


# Type protocols for dependency injection
class Logger(Protocol):
    def debug(self, msg: str, **kwargs): ...
    def info(self, msg: str, **kwargs): ...
    def warning(self, msg: str, **kwargs): ...
    def error(self, msg: str, **kwargs): ...


class Metrics(Protocol):
    def increment(self, metric: str, value: int = 1): ...
    def timing(self, metric: str, value: float): ...


class OperationCaller(Protocol):
    def __call__(
        self,
        domain: str,
        interface: str,
        operation: str,
        **kwargs: Any
    ) -> Any: ...


class ScannerTestFactory:
    """Scanner Test Factory - Implementation Layer.

    Contains actual scanner test operations implementation.
    """

    def __init__(
        self,
        logger: Optional[Logger] = None,
        metrics: Optional[Metrics] = None,
        call_operation: Optional[OperationCaller] = None,
    ):
        """Initialize scanner test factory with injected dependencies."""
        self._logger = logger
        self._metrics = metrics
        self._call_operation = call_operation

    def scan_all(
        self,
        path: str = "src/",
        pattern: str = "*.py",
        **kwargs
    ) -> Dict[str, Any]:
        """Scan all tests in path.

        Args:
            path: Path to scan
            pattern: File pattern to match
            **kwargs: Additional arguments

        Returns:
            Dictionary with scan results
        """
        if self._logger:
            self._logger.debug(
                f"Scanning all tests",
                path=path,
                pattern=pattern
            )

        scan_path = Path(path)

        if not scan_path.exists():
            return {
                "status": "error",
                "error": f"Path does not exist: {path}",
            }

        # Find all matching files
        files = list(scan_path.rglob(pattern))

        # Count test files (files starting with test_ or containing _test)
        test_files = [
            f for f in files
            if f.name.startswith("test_") or "_test." in f.name
        ]

        if self._metrics:
            self._metrics.increment("test.scanner.files_scanned", len(files))
            self._metrics.increment("test.scanner.test_files_found", len(test_files))

        return {
            "status": "success",
            "path": path,
            "pattern": pattern,
            "files_scanned": len(files),
            "test_files": len(test_files),
            "test_file_list": [str(f) for f in test_files],
        }

    def scan_gateway(
        self,
        gateway_path: str = "src/gateway/",
        **kwargs
    ) -> Dict[str, Any]:
        """Scan gateway for tests.

        Args:
            gateway_path: Path to gateway directory
            **kwargs: Additional arguments

        Returns:
            Dictionary with scan results
        """
        if self._logger:
            self._logger.debug(f"Scanning gateway tests", gateway_path=gateway_path)

        return self.scan_all(path=gateway_path, **kwargs)

    def compile_all(
        self,
        path: str = "src/",
        **kwargs
    ) -> Dict[str, Any]:
        """Compile all test files.

        Args:
            path: Path to compile
            **kwargs: Additional arguments

        Returns:
            Dictionary with compilation results
        """
        if self._logger:
            self._logger.debug(f"Compiling all tests", path=path)

        compile_path = Path(path)

        if not compile_path.exists():
            return {
                "status": "error",
                "error": f"Path does not exist: {path}",
            }

        # Find all Python files
        files = list(compile_path.rglob("*.py"))

        compiled = []
        failed = []

        # Try to compile each file
        import py_compile

        for file in files:
            try:
                py_compile.compile(str(file), doraise=True)
                compiled.append(str(file))
            except py_compile.PyCompileError as e:
                failed.append({"file": str(file), "error": str(e)})

        if self._metrics:
            self._metrics.increment("test.scanner.compiled", len(compiled))
            self._metrics.increment("test.scanner.failed", len(failed))

        return {
            "status": "success" if not failed else "partial",
            "path": path,
            "compiled": len(compiled),
            "failed": len(failed),
            "failed_files": failed,
        }

    def generate_report(
        self,
        report_type: str = "full",
        output_path: str = "reports/scanner/",
        **kwargs
    ) -> Dict[str, Any]:
        """Generate scanner test report.

        Args:
            report_type: Type of report (full, summary, detailed)
            output_path: Path to output report
            **kwargs: Additional arguments

        Returns:
            Dictionary with report generation results
        """
        if self._logger:
            self._logger.debug(
                f"Generating scanner report",
                report_type=report_type,
                output_path=output_path
            )

        # TODO: Implement actual report generation
        return {
            "status": "not_implemented",
            "report_type": report_type,
            "output_path": output_path,
            "message": "Report generation not yet implemented",
        }


__all__ = [
    'ScannerTestFactory',
]
