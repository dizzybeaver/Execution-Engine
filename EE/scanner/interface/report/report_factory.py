"""Report Factory - EE 2.1 Compliant

Version: 2.1.0
Date: 2025-12-31
Purpose: Factory contains all business logic for report operations
Type: EE 2.1 Factory Implementation
"""

from __future__ import annotations
from typing import Any, Callable, Dict, List
from pathlib import Path
import json


class ReportFactory:
    """Factory for report operations (EE 2.1 compliant).

    Responsibilities:
    - Implement all business logic for report generation
    - Use DI (logger, metrics, config, call_operation)
    - NO interface logic
    """

    def __init__(
        self,
        get_logger: Callable[[str], Any],
        get_metrics: Callable[[str], Any],
        get_config: Callable[[str, Any], Any],
        call_operation: Callable[..., Any],
    ):
        """Initialize Report Factory with DI.

        Args:
            get_logger: Logger getter function
            get_metrics: Metrics getter function
            get_config: Config getter function
            call_operation: Operation caller function
        """
        self.logger = get_logger("scanner.report.factory")
        self.metrics = get_metrics("scanner.report.factory")
        self._call_operation = call_operation
        self._get_config = get_config

    def _generate_markdown_report(
        self,
        violations: List[Dict],
        summary: Dict,
        scan_id: str
    ) -> str:
        """Generate markdown report content.

        Args:
            violations: List of violation dictionaries
            summary: Scan summary dictionary
            scan_id: Scan ID

        Returns:
            Markdown report content
        """
        lines = [
            f"# Scan Report: {scan_id}",
            "",
            "## Summary",
            f"- Total Violations: {len(violations)}",
            "",
            "## Violations",
            ""
        ]

        for violation in violations:
            lines.append(f"### {violation.get('rule_id', 'Unknown')}")
            lines.append(f"- **File**: {violation.get('file_path', 'N/A')}")
            lines.append(f"- **Line**: {violation.get('line_number', 'N/A')}")
            lines.append(f"- **Severity**: {violation.get('severity', 'N/A')}")
            lines.append(f"- **Message**: {violation.get('message', 'N/A')}")
            lines.append("")

        return '\n'.join(lines)

    def _generate_html_report(
        self,
        violations: List[Dict],
        summary: Dict,
        scan_id: str
    ) -> str:
        """Generate HTML report content.

        Args:
            violations: List of violation dictionaries
            summary: Scan summary dictionary
            scan_id: Scan ID

        Returns:
            HTML report content
        """
        lines = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            f"<title>Scan Report: {scan_id}</title>",
            "<style>",
            "body { font-family: Arial, sans-serif; margin: 20px; }",
            ".violation { border: 1px solid #ddd; padding: 10px; margin: 10px 0; }",
            ".error { border-left: 4px solid #f44336; }",
            ".warning { border-left: 4px solid #ff9800; }",
            ".info { border-left: 4px solid #2196f3; }",
            "</style>",
            "</head>",
            "<body>",
            f"<h1>Scan Report: {scan_id}</h1>",
            f"<p>Total Violations: {len(violations)}</p>",
            ""
        ]

        for violation in violations:
            severity = violation.get('severity', 'info')
            css_class = {
                'error': 'error',
                'warning': 'warning',
                'info': 'info'
            }.get(severity, 'info')

            lines.append(f'<div class="violation {css_class}">')
            lines.append(f'<h3>{violation.get("rule_id", "Unknown")}</h3>')
            lines.append(f'<p><strong>File:</strong> {violation.get("file_path", "N/A")}</p>')
            lines.append(f'<p><strong>Line:</strong> {violation.get("line_number", "N/A")}</p>')
            lines.append(f'<p><strong>Severity:</strong> {severity}</p>')
            lines.append(f'<p><strong>Message:</strong> {violation.get("message", "N/A")}</p>')
            lines.append('</div>')

        lines.extend(["</body>", "</html>"])

        return '\n'.join(lines)

    def generate_report(self, scan_id: str, output_format: str = 'markdown') -> dict:
        """Generate report from scan results.

        Args:
            scan_id: Scan ID (e.g., 2025-12-25_001)
            output_format: Report format (markdown, json, html)

        Returns:
            Report generation result dict
        """
        self.logger.info(f"Generating {output_format} report for scan: {scan_id}")

        # Parse scan ID to get date and run number
        parts = scan_id.split('_')
        if len(parts) != 2:
            self.logger.error(f"Invalid scan ID format: {scan_id}")
            return {
                'success': False,
                'error': f'Invalid scan ID format: {scan_id}. Expected: YYYY-MM-DD_NNN'
            }

        date_str, run_str = parts
        report_path = Path(f'reports/scanner/{date_str}/{run_str}')

        if not report_path.exists():
            self.logger.error(f"Scan report not found: {report_path}")
            return {
                'success': False,
                'error': f'Scan report not found: {report_path}'
            }

        # Check for existing report files
        violations_file = report_path / 'violations.json'
        summary_file = report_path / 'scan_results.json'

        if not violations_file.exists():
            self.logger.error(f"Violations file not found: {violations_file}")
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
                report_content = self._generate_markdown_report(
                    violations, summary, scan_id
                )
                with open(report_file, 'w', encoding='utf-8') as f:
                    f.write(report_content)

            self.logger.info(f"Markdown report generated: {report_file}")
            self.metrics.increment('report.generate.markdown', value=1)

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

            self.logger.info(f"JSON report generated: {report_file}")
            self.metrics.increment('report.generate.json', value=1)

            return {
                'success': True,
                'report_path': str(report_file),
                'format': 'json',
                'violations_count': len(violations)
            }

        elif output_format == 'html':
            report_file = report_path / 'scan_report.html'
            html_content = self._generate_html_report(violations, summary, scan_id)
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(html_content)

            self.logger.info(f"HTML report generated: {report_file}")
            self.metrics.increment('report.generate.html', value=1)

            return {
                'success': True,
                'report_path': str(report_file),
                'format': 'html',
                'violations_count': len(violations)
            }

        else:
            self.logger.error(f"Unsupported format: {output_format}")
            return {
                'success': False,
                'error': f'Unsupported format: {output_format}. Supported: markdown, json, html'
            }

    def report_last(self, count: int = 1, output_format: str = 'markdown') -> dict:
        """Generate report for last N scans.

        Args:
            count: Number of recent reports
            output_format: Report format (markdown, json, html)

        Returns:
            Report generation result dict
        """
        self.logger.info(f"Generating {output_format} reports for last {count} scans")

        reports_dir = Path('reports/scanner')
        if not reports_dir.exists():
            self.logger.error("Reports directory not found")
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
            result = self.generate_report(scan_id, output_format)
            if result.get('success'):
                reports_generated.append({
                    'scan_id': scan_id,
                    'report_path': result.get('report_path'),
                    'violations_count': result.get('violations_count', 0)
                })

        self.logger.info(f"Generated {len(reports_generated)} reports")
        self.metrics.increment('report.last.calls', value=1)

        return {
            'success': True,
            'reports_generated': len(reports_generated),
            'reports': reports_generated
        }

    def list_reports(self, date: str = None) -> dict:
        """List available reports.

        Args:
            date: Optional date filter (YYYY-MM-DD)

        Returns:
            List of available reports
        """
        self.logger.info(f"Listing reports{' for date: ' + date if date else ''}")

        reports_dir = Path('reports/scanner')
        if not reports_dir.exists():
            self.logger.error("Reports directory not found")
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

        self.logger.info(f"Found {len(reports)} reports")
        self.metrics.increment('report.list.calls', value=1)

        return {
            'success': True,
            'count': len(reports),
            'reports': reports
        }


__all__ = ['ReportFactory']
