"""
Pytest Factory - Test Domain

Contains implementation of pytest operations.

UG-ISP Architecture:
- Factory contains implementation
- Interface routes to factory methods
- Cross-domain via call_operation() only
"""

from __future__ import annotations
from typing import Any, Dict, Optional, List, Protocol
import subprocess
import sys
import json
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


class PytestFactory:
    """Pytest Factory - Implementation Layer.

    Contains actual pytest operations implementation.
    """

    def __init__(
        self,
        logger: Optional[Logger] = None,
        metrics: Optional[Metrics] = None,
        call_operation: Optional[OperationCaller] = None,
    ):
        """Initialize pytest factory with injected dependencies."""
        self._logger = logger
        self._metrics = metrics
        self._call_operation = call_operation

    def run_all(
        self,
        path: str = "tests/",
        verbose: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """Run all tests using pytest.

        Args:
            path: Path to test directory
            verbose: Enable verbose output
            **kwargs: Additional pytest arguments

        Returns:
            Dictionary with test results:
            {
                "status": "success" | "failed",
                "tests_run": int,
                "failures": int,
                "errors": int,
                "skipped": int,
                "duration": float,
            }
        """
        if self._logger:
            self._logger.debug(
                f"Running all tests",
                path=path,
                verbose=verbose
            )

        # Build pytest command
        cmd = [sys.executable, "-m", "pytest", path]
        if verbose:
            cmd.append("-v")

        # Add additional kwargs as pytest options
        for key, value in kwargs.items():
            if key.startswith("pytest_"):
                opt = key.replace("pytest_", "").replace("_", "-")
                cmd.append(f"--{opt}")
                if value is not True:
                    cmd.append(str(value))

        try:
            # Run pytest
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=Path.cwd()
            )

            # Parse output
            output = result.stdout + result.stderr

            # Extract basic statistics
            tests_run = 0
            failures = 0
            errors = 0
            skipped = 0

            # Simple parsing (could be enhanced with pytest JSON output)
            for line in output.split("\n"):
                if "passed" in line:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part.isdigit():
                            tests_run = int(part)
                            if i + 1 < len(parts) and "passed" in parts[i+1]:
                                pass

            response = {
                "status": "success" if result.returncode == 0 else "failed",
                "tests_run": tests_run,
                "failures": failures,
                "errors": errors,
                "skipped": skipped,
                "duration": 0.0,
                "output": output,
                "returncode": result.returncode,
            }

            if self._metrics:
                self._metrics.increment("test.pytest.run_all.count", tests_run)
                self._metrics.increment("test.pytest.run_all.failures", failures)

            return response

        except Exception as e:
            if self._logger:
                self._logger.error(f"Failed to run tests: {e}")

            return {
                "status": "error",
                "error": str(e),
                "tests_run": 0,
                "failures": 0,
                "errors": 1,
            }

    def run_suite(
        self,
        suite: str,
        path: str = "tests/",
        **kwargs
    ) -> Dict[str, Any]:
        """Run specific test suite.

        Args:
            suite: Suite name or pattern
            path: Path to test directory
            **kwargs: Additional arguments

        Returns:
            Dictionary with test results
        """
        if self._logger:
            self._logger.debug(
                f"Running test suite",
                suite=suite,
                path=path
            )

        # Build suite path
        suite_path = str(Path(path) / suite)

        # Run as a subset of run_all
        return self.run_all(path=suite_path, **kwargs)

    def run_file(
        self,
        file: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Run tests for specific file.

        Args:
            file: File path to test
            **kwargs: Additional arguments

        Returns:
            Dictionary with test results
        """
        if self._logger:
            self._logger.debug(f"Running file tests", file=file)

        # Run specific file
        return self.run_all(path=file, **kwargs)

    def get_results(
        self,
        run_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Get test results.

        Args:
            run_id: Optional run ID to retrieve
            **kwargs: Additional arguments

        Returns:
            Dictionary with test results
        """
        if self._logger:
            self._logger.debug(f"Getting test results", run_id=run_id)

        # TODO: Implement results retrieval from storage
        return {
            "status": "not_implemented",
            "run_id": run_id,
            "message": "Results retrieval not yet implemented",
        }


__all__ = [
    'PytestFactory',
]
