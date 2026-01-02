"""EE Test Runner - Comprehensive Testing Framework

Main test runner for EE (Execution Environment) testing framework.
Supports unit tests, integration tests, performance benchmarks, and compliance tests.

Usage:
    python test_runner.py --all              # Run all tests
    python test_runner.py --unit             # Run unit tests only
    python test_runner.py --integration      # Run integration tests
    python test_runner.py --benchmark        # Run performance benchmarks
    python test_runner.py --compliance       # Run UG-ISP compliance tests
    python test_runner.py --test test_name   # Run specific test
    python test_runner.py --coverage         # Generate coverage report
    python test_runner.py --parallel         # Run tests in parallel
"""

import sys
import os
import argparse
import subprocess
import time
from pathlib import Path
from typing import List, Dict, Any
import json


class TestRunner:
    """Main test runner for EE testing framework."""

    def __init__(self, tests_dir: Path):
        self.tests_dir = tests_dir
        self.results = {
            'unit': {'passed': 0, 'failed': 0, 'skipped': 0, 'time': 0},
            'integration': {'passed': 0, 'failed': 0, 'skipped': 0, 'time': 0},
            'performance': {'passed': 0, 'failed': 0, 'skipped': 0, 'time': 0},
            'compliance': {'passed': 0, 'failed': 0, 'skipped': 0, 'time': 0},
        }
        self.total_start_time = time.time()

    def run_command(self, command: List[str]) -> subprocess.CompletedProcess:
        """Run a command and return result."""
        print(f"\n{'=' * 70}")
        print(f"Running: {' '.join(command)}")
        print(f"{'=' * 70}\n")
        result = subprocess.run(command, capture_output=True, text=True)
        return result

    def run_unit_tests(self) -> bool:
        """Run unit tests."""
        print("\n" + "=" * 70)
        print("UNIT TESTS")
        print("=" * 70)

        start_time = time.time()
        test_files = [
            'test_interface_plugins.py',
            'test_interface_object_pool.py',
            'test_interface_network.py',
            'test_gateway_factory.py',
            'test_gateway_routing.py',
            'test_di_gateway.py',
        ]

        command = ['python', '-m', 'pytest', '-v'] + test_files
        result = self.run_command(command)

        elapsed = time.time() - start_time
        self.results['unit']['time'] = elapsed

        # Parse results
        if result.returncode == 0:
            print(f"\n✅ Unit tests PASSED in {elapsed:.2f}s")
            return True
        else:
            print(f"\n❌ Unit tests FAILED in {elapsed:.2f}s")
            print(result.stdout)
            print(result.stderr)
            return False

    def run_integration_tests(self) -> bool:
        """Run integration tests."""
        print("\n" + "=" * 70)
        print("INTEGRATION TESTS")
        print("=" * 70)

        start_time = time.time()
        test_files = [
            'test_integration_e2e.py',
            'test_integration_plugins.py',
        ]

        command = ['python', '-m', 'pytest', '-v'] + test_files
        result = self.run_command(command)

        elapsed = time.time() - start_time
        self.results['integration']['time'] = elapsed

        if result.returncode == 0:
            print(f"\n✅ Integration tests PASSED in {elapsed:.2f}s")
            return True
        else:
            print(f"\n❌ Integration tests FAILED in {elapsed:.2f}s")
            print(result.stdout)
            print(result.stderr)
            return False

    def run_performance_tests(self) -> bool:
        """Run performance benchmarks."""
        print("\n" + "=" * 70)
        print("PERFORMANCE BENCHMARKS")
        print("=" * 70)

        start_time = time.time()
        test_files = [
            'test_performance_cold_start.py',
            'test_performance_hot_path.py',
            'test_performance_memory.py',
        ]

        command = ['python', '-m', 'pytest', '-v', '-s'] + test_files
        result = self.run_command(command)

        elapsed = time.time() - start_time
        self.results['performance']['time'] = elapsed

        if result.returncode == 0:
            print(f"\n✅ Performance benchmarks PASSED in {elapsed:.2f}s")
            return True
        else:
            print(f"\n❌ Performance benchmarks FAILED in {elapsed:.2f}s")
            print(result.stdout)
            print(result.stderr)
            return False

    def run_compliance_tests(self) -> bool:
        """Run UG-ISP compliance tests."""
        print("\n" + "=" * 70)
        print("UG-ISP COMPLIANCE TESTS")
        print("=" * 70)

        start_time = time.time()
        test_files = [
            'test_ug_isp_compliance.py',
            'test_import_rules.py',
        ]

        command = ['python', '-m', 'pytest', '-v'] + test_files
        result = self.run_command(command)

        elapsed = time.time() - start_time
        self.results['compliance']['time'] = elapsed

        if result.returncode == 0:
            print(f"\n✅ UG-ISP compliance tests PASSED in {elapsed:.2f}s")
            return True
        else:
            print(f"\n❌ UG-ISP compliance tests FAILED in {elapsed:.2f}s")
            print(result.stdout)
            print(result.stderr)
            return False

    def run_specific_test(self, test_name: str) -> bool:
        """Run a specific test file."""
        print(f"\n{'=' * 70}")
        print(f"RUNNING SPECIFIC TEST: {test_name}")
        print(f"{'=' * 70}")

        command = ['python', '-m', 'pytest', '-v', test_name]
        result = self.run_command(command)

        if result.returncode == 0:
            print(f"\n✅ {test_name} PASSED")
            return True
        else:
            print(f"\n❌ {test_name} FAILED")
            print(result.stdout)
            print(result.stderr)
            return False

    def run_coverage_report(self) -> bool:
        """Generate coverage report."""
        print("\n" + "=" * 70)
        print("COVERAGE REPORT")
        print("=" * 70)

        # Add EE src to Python path
        ee_src = Path(__file__).parent.parent / 'src'
        command = [
            'python', '-m', 'pytest',
            '--cov=' + str(ee_src),
            '--cov-report=html',
            '--cov-report=term-missing',
            'test_*.py'
        ]
        result = self.run_command(command)

        if result.returncode == 0:
            print(f"\n✅ Coverage report generated")
            print(f"HTML report: {self.tests_dir / 'htmlcov' / 'index.html'}")
            return True
        else:
            print(f"\n❌ Coverage report generation FAILED")
            return False

    def print_summary(self):
        """Print test summary."""
        total_time = time.time() - self.total_start_time

        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        print(f"\nTotal Time: {total_time:.2f}s\n")

        for category, results in self.results.items():
            if results['time'] > 0:
                status = "✅ PASSED" if results['failed'] == 0 else "❌ FAILED"
                print(f"{category.upper()}: {status}")
                print(f"  Time: {results['time']:.2f}s")

        print("\n" + "=" * 70)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='EE Test Runner - Comprehensive Testing Framework'
    )

    parser.add_argument(
        '--all',
        action='store_true',
        help='Run all tests (unit, integration, performance, compliance)'
    )

    parser.add_argument(
        '--unit',
        action='store_true',
        help='Run unit tests only'
    )

    parser.add_argument(
        '--integration',
        action='store_true',
        help='Run integration tests only'
    )

    parser.add_argument(
        '--benchmark',
        action='store_true',
        help='Run performance benchmarks only'
    )

    parser.add_argument(
        '--compliance',
        action='store_true',
        help='Run UG-ISP compliance tests only'
    )

    parser.add_argument(
        '--test',
        type=str,
        help='Run specific test file'
    )

    parser.add_argument(
        '--coverage',
        action='store_true',
        help='Generate coverage report'
    )

    parser.add_argument(
        '--parallel',
        action='store_true',
        help='Run tests in parallel (requires pytest-xdist)'
    )

    args = parser.parse_args()

    # Get tests directory
    tests_dir = Path(__file__).parent
    os.chdir(tests_dir)

    # Add EE src to path
    ee_src = tests_dir.parent / 'src'
    sys.path.insert(0, str(ee_src))

    # Create test runner
    runner = TestRunner(tests_dir)

    # Run tests based on arguments
    success = True

    if args.all:
        success = (
            runner.run_unit_tests() and
            runner.run_integration_tests() and
            runner.run_performance_tests() and
            runner.run_compliance_tests()
        )
    elif args.unit:
        success = runner.run_unit_tests()
    elif args.integration:
        success = runner.run_integration_tests()
    elif args.benchmark:
        success = runner.run_performance_tests()
    elif args.compliance:
        success = runner.run_compliance_tests()
    elif args.test:
        success = runner.run_specific_test(args.test)
    elif args.coverage:
        success = runner.run_coverage_report()
    else:
        parser.print_help()
        return 1

    runner.print_summary()

    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
