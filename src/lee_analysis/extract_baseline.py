#!/usr/bin/env python3
"""Baseline extraction tool for controller consolidation Phase 0.

Extracts current response patterns from all 20+ controllers and saves
them as JSON baselines for equivalence testing.

Usage:
    python scripts/extract_baseline.py
    python scripts/extract_baseline.py --controller power_controller
    python scripts/extract_baseline.py --output /path/to/baselines
"""

import argparse
import importlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# List of all controllers to extract baselines from
ALL_CONTROLLERS = [
    "power_controller",
    "brightness_controller",
    "color_controller",
    "color_temperature_controller",
    "thermostat_controller",
    "lock_controller",
    "channel_controller",
    "input_controller",
    "speaker_controller",
    "mode_controller",
    "toggle_controller",
    "range_controller",
    "scene_controller",
    "playback_controller",
    "seek_controller",
    "equalizer_controller",
    "camera_stream_controller",
    "vacuum_controller",
    "security_panel_controller",
    "time_hold_controller",
]


def import_controller(controller_name: str):
    """Import a controller module.

    Args:
        controller_name: Name of the controller module

    Returns:
        Module object or None if import fails
    """
    try:
        module_path = f"home_assistant.ha_alexa.controllers.{controller_name}"
        module = importlib.import_module(module_path)
        return module
    except ImportError as e:
        print(f"Warning: Could not import {controller_name}: {e}")
        return None
    except (AttributeError, ValueError, TypeError) as e:
        print(f"Error importing {controller_name}: {e}")
        return None


def extract_controller_baseline(controller_name: str, test_token: str = "test_token") -> Optional[Dict[str, Any]]:
    """Extract baseline responses from a controller.

    Args:
        controller_name: Name of the controller
        test_token: Correlation token to use for testing

    Returns:
        Dictionary with baseline responses or None if extraction fails
    """
    module = import_controller(controller_name)
    if module is None:
        return None

    baseline = {
        "controller": controller_name,
        "test_correlation_token": test_token
    }

    # Extract success response
    create_success = getattr(module, "_create_success_response", None)
    if create_success:
        try:
            success_response = create_success(test_token)
            baseline["success_response"] = success_response
            baseline["has_success_response"] = True
        except (AttributeError, TypeError, ValueError) as e:
            print(f"Error creating success response for {controller_name}: {e}")
            baseline["has_success_response"] = False
            baseline["success_error"] = str(e)
    else:
        baseline["has_success_response"] = False

    # Extract error response
    create_error = getattr(module, "_create_error_response", None)
    if create_error:
        try:
            test_error = "Test error message for baseline"
            error_response = create_error(test_token, test_error)
            baseline["error_response"] = error_response
            baseline["has_error_response"] = True
        except (AttributeError, TypeError, ValueError) as e:
            print(f"Error creating error response for {controller_name}: {e}")
            baseline["has_error_response"] = False
            baseline["error_error"] = str(e)
    else:
        baseline["has_error_response"] = False

    # Extract handle functions if available
    handle_functions = []
    for attr_name in dir(module):
        if attr_name.startswith("handle_") and callable(getattr(module, attr_name)):
            handle_functions.append(attr_name)

    if handle_functions:
        baseline["handle_functions"] = sorted(handle_functions)

    return baseline


def save_baseline(baseline: Dict[str, Any], output_dir: Path) -> Optional[Path]:
    """Save baseline to JSON file.

    Args:
        baseline: Baseline dictionary
        output_dir: Output directory path

    Returns:
        Path to saved file or None if save fails
    """
    controller_name = baseline.get("controller", "unknown")
    filename = f"{controller_name}_baseline.json"
    output_path = output_dir / filename

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(baseline, f, indent=2, sort_keys=True, ensure_ascii=False)
        return output_path
    except (OSError, IOError, TypeError) as e:
        print(f"Error saving baseline for {controller_name}: {e}")
        return None


def generate_summary_report(baselines: List[Dict[str, Any]], output_dir: Path) -> Path:
    """Generate summary report of all extracted baselines.

    Args:
        baselines: List of baseline dictionaries
        output_dir: Output directory path

    Returns:
        Path to summary report
    """
    summary = {
        "total_controllers": len(ALL_CONTROLLERS),
        "successfully_extracted": len([b for b in baselines if b is not None]),
        "failed_extractions": len([b for b in baselines if b is None]),
        "controllers_with_success": len([b for b in baselines if b and b.get("has_success_response")]),
        "controllers_with_error": len([b for b in baselines if b and b.get("has_error_response")]),
        "controllers": []
    }

    for baseline in baselines:
        if baseline is None:
            continue

        controller_info = {
            "name": baseline.get("controller"),
            "has_success": baseline.get("has_success_response", False),
            "has_error": baseline.get("has_error_response", False),
            "handle_functions": baseline.get("handle_functions", [])
        }
        summary["controllers"].append(controller_info)

    summary_path = output_dir / "baseline_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, sort_keys=True, ensure_ascii=False)

    return summary_path


def print_report(baselines: List[Dict[str, Any]], output_dir: Path):
    """Print extraction report to console.

    Args:
        baselines: List of baseline dictionaries
        output_dir: Output directory path
    """
    print("\n" + "=" * 70)
    print("BASELINE EXTRACTION REPORT")
    print("=" * 70)

    successful = [b for b in baselines if b is not None]
    failed = len(baselines) - len(successful)

    print(f"\nTotal Controllers: {len(ALL_CONTROLLERS)}")
    print(f"Successfully Extracted: {len(successful)}")
    print(f"Failed Extractions: {failed}")

    if successful:
        with_success = [b for b in successful if b.get("has_success_response")]
        with_error = [b for b in successful if b.get("has_error_response")]

        print(f"\nControllers with Success Response: {len(with_success)}")
        print(f"Controllers with Error Response: {len(with_error)}")

    print(f"\nBaselines saved to: {output_dir}")
    print("=" * 70 + "\n")

    # List each controller
    for baseline in successful:
        controller_name = baseline.get("controller", "unknown")
        has_success = baseline.get("has_success_response", False)
        has_error = baseline.get("has_error_response", False)
        handle_funcs = baseline.get("handle_functions", [])

        status = []
        if has_success:
            status.append("SUCCESS")
        if has_error:
            status.append("ERROR")

        print(f"  {controller_name:40} {', '.join(status):15} ({len(handle_funcs)} handlers)")

    if failed > 0:
        print(f"\n  {failed} controllers failed to extract")


def generate_test_cases(baselines: List[Dict[str, Any]], output_dir: Path) -> Path:
    """Generate pytest test cases from extracted baselines.

    Args:
        baselines: List of baseline dictionaries
        output_dir: Output directory path

    Returns:
        Path to generated test file
    """
    test_lines = [
        '"""Generated test cases from extracted baselines.',
        '',
        'This file is auto-generated by scripts/extract_baseline.py',
        'Do not edit manually.',
        '"""',
        '',
        'import pytest',
        'from test_equivalence_data import (',
        '    compare_response_fields,',
        '    get_expected_response,',
        ')',
        '',
        '',
    ]

    for baseline in baselines:
        if baseline is None:
            continue

        controller_name = baseline.get("controller")
        if not controller_name:
            continue

        # Success response test
        if baseline.get("has_success_response"):
            test_lines.extend([
                f'def test_{controller_name}_success_response():',
                f'    """Test {controller_name} success response matches baseline."""',
                f'    from lee.home_assistant.ha_alexa.controllers.{controller_name} import (',
                '        _create_success_response',
                '    )',
                '',
                '    response = _create_success_response("test_token")',
                f'    expected = get_expected_response("{controller_name}", "success")',
                '',
                '    if expected:',
                '        comparison = compare_response_fields(response, expected)',
                '        assert comparison["matches"], f"Differences: {comparison[\'differences\']}"',
                '    else:',
                '        # Verify structure if no baseline',
                '        assert "event" in response',
                '        assert response["event"]["header"]["name"] == "Response"',
                '',
                '',
            ])

        # Error response test
        if baseline.get("has_error_response"):
            test_lines.extend([
                f'def test_{controller_name}_error_response():',
                f'    """Test {controller_name} error response matches baseline."""',
                f'    from lee.home_assistant.ha_alexa.controllers.{controller_name} import (',
                '        _create_error_response',
                '    )',
                '',
                '    response = _create_error_response("test_token", "Test error")',
                f'    expected = get_expected_response("{controller_name}", "error")',
                '',
                '    if expected:',
                '        comparison = compare_response_fields(response, expected)',
                '        assert comparison["matches"], f"Differences: {comparison[\'differences\']}"',
                '    else:',
                '        # Verify structure if no baseline',
                '        assert "event" in response',
                '        assert response["event"]["header"]["name"] == "ErrorResponse"',
                '',
                '',
            ])

    # Add main guard
    test_lines.extend([
        'if __name__ == "__main__":',
        '    pytest.main([__file__, "-v"])',
    ])

    test_path = output_dir / "test_generated_cases.py"
    with open(test_path, "w", encoding="utf-8") as f:
        f.write("\n".join(test_lines))

    return test_path


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Extract baseline responses from Alexa controllers"
    )
    parser.add_argument(
        "--controller",
        choices=ALL_CONTROLLERS,
        help="Specific controller to extract (default: all)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="tests/home_assistant/baseline",
        help="Output directory for baselines (default: tests/home_assistant/baseline)"
    )
    parser.add_argument(
        "--test-token",
        type=str,
        default="test_token",
        help="Correlation token to use for testing (default: test_token)"
    )
    parser.add_argument(
        "--generate-tests",
        action="store_true",
        help="Generate pytest test cases from baselines"
    )

    args = parser.parse_args()

    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Determine which controllers to process
    if args.controller:
        controllers = [args.controller]
    else:
        controllers = ALL_CONTROLLERS

    print(f"Extracting baselines for {len(controllers)} controller(s)...")
    print(f"Output directory: {output_dir}")

    # Extract baselines
    baselines = []
    for controller_name in controllers:
        print(f"\nExtracting {controller_name}...")
        baseline = extract_controller_baseline(controller_name, args.test_token)

        if baseline:
            save_baseline(baseline, output_dir)
            print(f"  Saved: {controller_name}_baseline.json")
        else:
            print(f"  Failed: {controller_name}")

        baselines.append(baseline)

    # Generate summary
    generate_summary_report(baselines, output_dir)

    # Generate test cases if requested
    if args.generate_tests:
        print("\nGenerating test cases...")
        test_path = generate_test_cases(baselines, output_dir)
        print(f"Generated: {test_path}")

    # Print report
    print_report(baselines, output_dir)

    # Return exit code
    failed_count = len([b for b in baselines if b is None])
    if failed_count > 0:
        print(f"\nWarning: {failed_count} controller(s) failed to extract")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
