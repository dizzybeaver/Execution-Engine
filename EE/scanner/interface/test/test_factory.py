"""Test Factory - EE 2.1 Compliant

Factory contains all business logic for test operations.

Based on: EE/scanner/archive/scanner_test_interface.py.legacy
"""

from __future__ import annotations
import subprocess
from pathlib import Path
from typing import Any, Callable, Dict

from EE.scanner.interface.test.test_ha_helper import run_ha_test


class TestFactory:
    """Factory for test operations (EE 2.1 compliant).

    Responsibilities:
    - Implement all test execution business logic
    - Use DI (logger, metrics, config, call_operation)
    - NO interface logic (that's in the interface router)
    - Support pytest and HA functional tests

    EE 2.1 Pattern:
    - All business logic lives here
    - Interface router is thin (no logic)
    - DI for all dependencies
    - No global state
    """

    def __init__(
        self,
        get_logger: Callable[[str], Any],
        get_metrics: Callable[[str], Any],
        get_config: Callable[[str, Any], Any],
        call_operation: Callable[..., Any],
    ):
        """Initialize test factory with DI.

        Args:
            get_logger: Factory function to create loggers
            get_metrics: Factory function to create metrics collectors
            get_config: Factory function to get configuration values
            call_operation: Callback for cross-domain operations
        """
        self.logger = get_logger("scanner.test.factory")
        self.metrics = get_metrics("scanner.test.factory")
        self._call_operation = call_operation

    def test_all(self, path: str = '.', verbose: bool = False) -> Dict:
        """Run all tests using pytest.

        Args:
            path: Path to test directory
            verbose: Enable verbose output

        Returns:
            Test result dict with:
                - success: True if all tests passed
                - tests_total: Total number of tests
                - tests_passed: Number of passed tests
                - tests_failed: Number of failed tests
                - duration: Test execution time
                - errors: List of error summaries (if any)
                - exit_code: Pytest exit code
        """
        self.logger.debug(f"Running all tests at {path}")

        test_path = Path(path)

        if not test_path.exists():
            return {
                'success': False,
                'error': f'Test path not found: {path}',
                'tests_total': 0,
                'tests_passed': 0,
                'tests_failed': 0,
                'duration': 0
            }

        # Build pytest command with JSON output
        cmd = ['pytest', str(test_path), '-v', '--tb=short']

        if verbose:
            cmd.append('-vv')

        try:
            # Run pytest and capture output
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )

            output = result.stdout + result.stderr

            # Parse pytest output for results
            tests_passed = output.count('PASSED')
            tests_failed = output.count('FAILED')
            tests_total = tests_passed + tests_failed

            # Check for error summary
            error_summary = []
            if tests_failed > 0:
                lines = output.split('\n')
                for i, line in enumerate(lines):
                    if 'FAILED' in line:
                        # Get context around failure
                        context = '\n'.join(lines[max(0, i-2):min(len(lines), i+5)])
                        error_summary.append({
                            'test': line.strip(),
                            'context': context
                        })

            test_result = {
                'success': result.returncode == 0,
                'tests_total': tests_total,
                'tests_passed': tests_passed,
                'tests_failed': tests_failed,
                'duration': getattr(result, 'elapsed', 0),
                'errors': error_summary,
                'exit_code': result.returncode
            }

            self.logger.info(
                f"Tests completed: total={tests_total}, "
                f"passed={tests_passed}, failed={tests_failed}"
            )

            return test_result

        except subprocess.TimeoutExpired:
            self.logger.error("Test execution timeout (>300s)")
            return {
                'success': False,
                'error': 'Test execution timeout (>300s)',
                'tests_total': 0,
                'tests_passed': 0,
                'tests_failed': 0,
                'duration': 300
            }
        except Exception as e:
            self.logger.error(f"Test execution error: {e}")
            return {
                'success': False,
                'error': str(e),
                'tests_total': 0,
                'tests_passed': 0,
                'tests_failed': 0,
                'duration': 0
            }

    def test_suite(self, suite_name: str, base_path: str = '.', verbose: bool = False) -> Dict:
        """Run specific test suite.

        Args:
            suite_name: Test suite name (directory or file pattern)
            base_path: Base path containing test suites
            verbose: Enable verbose output

        Returns:
            Test result dict with:
                - success: True if all tests passed
                - suite: Suite name
                - tests_total: Total number of tests
                - tests_passed: Number of passed tests
                - tests_failed: Number of failed tests
                - errors: List of error summaries (if any)
                - exit_code: Pytest exit code
        """
        self.logger.debug(f"Running test suite '{suite_name}' from {base_path}")

        suite_path = Path(base_path) / suite_name

        if not suite_path.exists():
            return {
                'success': False,
                'error': f'Test suite not found: {suite_path}',
                'suite': suite_name,
                'tests_total': 0,
                'tests_passed': 0,
                'tests_failed': 0
            }

        # Build pytest command for specific suite
        cmd = ['pytest', str(suite_path), '-v', '--tb=short']

        if verbose:
            cmd.append('-vv')

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )

            output = result.stdout + result.stderr

            tests_passed = output.count('PASSED')
            tests_failed = output.count('FAILED')
            tests_total = tests_passed + tests_failed

            error_summary = []
            if tests_failed > 0:
                lines = output.split('\n')
                for i, line in enumerate(lines):
                    if 'FAILED' in line:
                        context = '\n'.join(lines[max(0, i-2):min(len(lines), i+5)])
                        error_summary.append({
                            'test': line.strip(),
                            'context': context
                        })

            test_result = {
                'success': result.returncode == 0,
                'suite': suite_name,
                'tests_total': tests_total,
                'tests_passed': tests_passed,
                'tests_failed': tests_failed,
                'errors': error_summary,
                'exit_code': result.returncode
            }

            self.logger.info(
                f"Suite '{suite_name}' completed: total={tests_total}, "
                f"passed={tests_passed}, failed={tests_failed}"
            )

            return test_result

        except subprocess.TimeoutExpired:
            self.logger.error(f"Suite '{suite_name}' execution timeout (>300s)")
            return {
                'success': False,
                'error': 'Test execution timeout (>300s)',
                'suite': suite_name,
                'tests_total': 0,
                'tests_passed': 0,
                'tests_failed': 0
            }
        except Exception as e:
            self.logger.error(f"Suite '{suite_name}' error: {e}")
            return {
                'success': False,
                'error': str(e),
                'suite': suite_name,
                'tests_total': 0,
                'tests_passed': 0,
                'tests_failed': 0
            }

    def test_file(self, file_path: str, verbose: bool = False) -> Dict:
        """Run tests for single file.

        Args:
            file_path: Path to test file
            verbose: Enable verbose output

        Returns:
            Test result dict with:
                - success: True if all tests passed
                - file: Test file path
                - tests_total: Total number of tests
                - tests_passed: Number of passed tests
                - tests_failed: Number of failed tests
                - errors: List of error summaries (if any)
                - exit_code: Pytest exit code
        """
        self.logger.debug(f"Running tests for file '{file_path}'")

        test_file = Path(file_path)

        if not test_file.exists():
            return {
                'success': False,
                'error': f'Test file not found: {file_path}',
                'file': str(test_file),
                'tests_total': 0,
                'tests_passed': 0,
                'tests_failed': 0
            }

        if test_file.suffix != '.py':
            return {
                'success': False,
                'error': f'Not a Python test file: {file_path}',
                'file': str(test_file),
                'tests_total': 0,
                'tests_passed': 0,
                'tests_failed': 0
            }

        cmd = ['pytest', str(test_file), '-v', '--tb=short']

        if verbose:
            cmd.append('-vv')

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )

            output = result.stdout + result.stderr

            tests_passed = output.count('PASSED')
            tests_failed = output.count('FAILED')
            tests_total = tests_passed + tests_failed

            error_summary = []
            if tests_failed > 0:
                lines = output.split('\n')
                for i, line in enumerate(lines):
                    if 'FAILED' in line:
                        context = '\n'.join(lines[max(0, i-2):min(len(lines), i+5)])
                        error_summary.append({
                            'test': line.strip(),
                            'context': context
                        })

            test_result = {
                'success': result.returncode == 0,
                'file': str(test_file),
                'tests_total': tests_total,
                'tests_passed': tests_passed,
                'tests_failed': tests_failed,
                'errors': error_summary,
                'exit_code': result.returncode
            }

            self.logger.info(
                f"File '{test_file}' completed: total={tests_total}, "
                f"passed={tests_passed}, failed={tests_failed}"
            )

            return test_result

        except subprocess.TimeoutExpired:
            self.logger.error(f"File '{test_file}' execution timeout (>120s)")
            return {
                'success': False,
                'error': 'Test execution timeout (>120s)',
                'file': str(test_file),
                'tests_total': 0,
                'tests_passed': 0,
                'tests_failed': 0
            }
        except Exception as e:
            self.logger.error(f"File '{test_file}' error: {e}")
            return {
                'success': False,
                'error': str(e),
                'file': str(test_file),
                'tests_total': 0,
                'tests_passed': 0,
                'tests_failed': 0
            }

    def test_ha(self, test_type: str, **kwargs) -> Dict:
        """Run HA Gateway functional tests (UG-ISP compliant).

        Delegates to test_ha_helper module to keep factory under 400 lines.

        Args:
            test_type: Type of HA test to run
            **kwargs: Additional parameters (not currently used)

        Returns:
            Test result dict with success, tests_total, tests_passed, tests_failed
        """
        return run_ha_test(
            test_type=test_type,
            call_operation=self._call_operation,
            logger=self.logger
        )


__all__ = ['TestFactory']
