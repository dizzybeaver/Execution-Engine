"""Report interface router (UG-ISP Router).

Report generation operations.

UG-ISP Pattern: Gateway -> Interface (Router) -> Implementation
"""

import json
from pathlib import Path
from typing import Any, List


def _generate_report(scan_id: str, output_format: str = 'markdown') -> dict:
    """Generate report from scan results.

    Args:
        scan_id: Scan ID (e.g., 2025-12-25_001)
        output_format: Report format (markdown, json, html)

    Returns:
        Report generation result dict
    """
    from tools.scanner.interface.report_formatters import (
        _generate_markdown_report,
        _generate_html_report
    )

    # Parse scan ID to get date and run number
    parts = scan_id.split('_')
    if len(parts) != 2:
        return {
            'success': False,
            'error': f'Invalid scan ID format: {scan_id}. Expected: YYYY-MM-DD_NNN'
        }

    date_str, run_str = parts
    report_path = Path(f'reports/scanner/{date_str}/{run_str}')

    if not report_path.exists():
        return {
            'success': False,
            'error': f'Scan report not found: {report_path}'
        }

    # Check for existing report files
    violations_file = report_path / 'violations.json'
    summary_file = report_path / 'scan_results.json'

    if not violations_file.exists():
        return {
            'success': False,
            'error': f'Violations file not found: {violations_file}'
        }

    # Load violations
    with open(violations_file, 'r', encoding='utf-8') as f:
        violations = json.load(f)

    # Load summary
    summary = {}
    if summary_file.exists():
        with open(summary_file, 'r', encoding='utf-8') as f:
            summary = json.load(f)

    # Generate report based on format
    if output_format == 'markdown':
        report_file = report_path / 'scan_report.md'
        if not report_file.exists():
            report_content = _generate_markdown_report(violations, summary, scan_id)
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report_content)

        return {
            'success': True,
            'report_path': str(report_file),
            'format': 'markdown',
            'violations_count': len(violations),
            'summary': summary
        }

    elif output_format == 'json':
        report_file = report_path / 'full_report.json'
        full_report = {
            'scan_id': scan_id,
            'summary': summary,
            'violations': violations
        }
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(full_report, f, indent=2)

        return {
            'success': True,
            'report_path': str(report_file),
            'format': 'json',
            'violations_count': len(violations)
        }

    elif output_format == 'html':
        report_file = report_path / 'scan_report.html'
        html_content = _generate_html_report(violations, summary, scan_id)
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return {
            'success': True,
            'report_path': str(report_file),
            'format': 'html',
            'violations_count': len(violations)
        }

    else:
        return {
            'success': False,
            'error': f'Unsupported format: {output_format}. Supported: markdown, json, html'
        }


def _report_last(count: int = 1, output_format: str = 'markdown') -> dict:
    """Generate report for last N scans.

    Args:
        count: Number of recent reports
        output_format: Report format (markdown, json, html)

    Returns:
        Report generation result dict
    """
    reports_dir = Path('reports/scanner')
    if not reports_dir.exists():
        return {
            'success': False,
            'error': 'Reports directory not found'
        }

    # Find all scan directories
    scan_dirs = []
    for date_dir in sorted(reports_dir.iterdir(), reverse=True):
        if date_dir.is_dir():
            for run_dir in sorted(date_dir.iterdir(), reverse=True):
                if run_dir.is_dir():
                    scan_id = f"{date_dir.name}_{run_dir.name}"
                    scan_dirs.append((scan_id, run_dir))

    # Take last N
    recent_scans = scan_dirs[:count]

    reports_generated = []
    for scan_id, run_dir in recent_scans:
        result = _generate_report(scan_id, output_format)
        if result.get('success'):
            reports_generated.append({
                'scan_id': scan_id,
                'report_path': result.get('report_path'),
                'violations_count': result.get('violations_count', 0)
            })

    return {
        'success': True,
        'reports_generated': len(reports_generated),
        'reports': reports_generated
    }


def _list_reports(date: str = None) -> dict:
    """List available reports.

    Args:
        date: Optional date filter (YYYY-MM-DD)

    Returns:
        List of available reports
    """
    reports_dir = Path('reports/scanner')
    if not reports_dir.exists():
        return {
            'success': False,
            'error': 'Reports directory not found',
            'reports': []
        }

    reports = []
    for date_dir in sorted(reports_dir.iterdir(), reverse=True):
        if date and date_dir.name != date:
            continue

        if date_dir.is_dir():
            for run_dir in sorted(date_dir.iterdir(), reverse=True):
                if run_dir.is_dir():
                    scan_id = f"{date_dir.name}_{run_dir.name}"

                    # Check for report files
                    violations_file = run_dir / 'violations.json'
                    summary_file = run_dir / 'scan_results.json'

                    violations_count = 0
                    if violations_file.exists():
                        with open(violations_file, 'r') as f:
                            violations = json.load(f)
                            violations_count = len(violations)

                    report_info = {
                        'scan_id': scan_id,
                        'date': date_dir.name,
                        'run': run_dir.name,
                        'path': str(run_dir),
                        'violations_count': violations_count,
                        'has_violations': violations_file.exists(),
                        'has_summary': summary_file.exists()
                    }

                    reports.append(report_info)

    return {
        'success': True,
        'count': len(reports),
        'reports': reports
    }


# Dispatch dictionary - O(1) operation routing
_REPORT_DISPATCH = {
    'generate': lambda **kw: _generate_report(
        kw.get('scan_id'),
        kw.get('output_format', 'markdown')
    ),
    'last': lambda **kw: _report_last(
        kw.get('count', 1),
        kw.get('output_format', 'markdown')
    ),
    'list': lambda **kw: _list_reports(kw.get('date')),
}


def execute_report_operation(operation: str, **kwargs) -> Any:
    """Route report operation requests.

    Args:
        operation: Operation name (generate, last, list)
        **kwargs: Operation parameters

    Returns:
        Operation result

    Raises:
        ValueError: If operation unknown
    """
    if operation not in _REPORT_DISPATCH:
        raise ValueError(
            f"Unknown report operation: '{operation}'. "
            f"Valid: {', '.join(_REPORT_DISPATCH.keys())}"
        )

    handler = _REPORT_DISPATCH[operation]
    return handler(**kwargs)


__all__ = ['execute_report_operation']
