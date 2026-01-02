"""
Report Factory - Test Domain

Contains implementation of report generation and export operations.

UG-ISP Architecture:
- Factory contains implementation
- Interface routes to factory methods
- Cross-domain via call_operation() only
"""

from __future__ import annotations
from typing import Any, Dict, Optional, List, Protocol
from pathlib import Path
import json
from datetime import datetime


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


class ReportFactory:
    """Report Factory - Implementation Layer.

    Contains actual report generation and export implementation.
    """

    def __init__(
        self,
        logger: Optional[Logger] = None,
        metrics: Optional[Metrics] = None,
        call_operation: Optional[OperationCaller] = None,
    ):
        """Initialize report factory with injected dependencies."""
        self._logger = logger
        self._metrics = metrics
        self._call_operation = call_operation

    def generate(
        self,
        test_results: Optional[Dict[str, Any]] = None,
        title: str = "Test Report",
        **kwargs
    ) -> Dict[str, Any]:
        """Generate test report.

        Args:
            test_results: Test results to include in report
            title: Report title
            **kwargs: Additional arguments

        Returns:
            Dictionary with report data
        """
        if self._logger:
            self._logger.debug(
                f"Generating test report",
                title=title
            )

        # Default test results if none provided
        if test_results is None:
            test_results = {
                "status": "no_results",
                "message": "No test results provided",
            }

        report = {
            "title": title,
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total": test_results.get("tests_run", 0),
                "passed": test_results.get("tests_run", 0) - test_results.get("failures", 0),
                "failed": test_results.get("failures", 0),
                "errors": test_results.get("errors", 0),
                "skipped": test_results.get("skipped", 0),
            },
            "details": test_results,
        }

        if self._metrics:
            self._metrics.increment("test.report.generated")

        return report

    def export_html(
        self,
        report: Dict[str, Any],
        output_path: str = "reports/test_report.html",
        **kwargs
    ) -> Dict[str, Any]:
        """Export report as HTML.

        Args:
            report: Report data dictionary
            output_path: Path to save HTML file
            **kwargs: Additional arguments

        Returns:
            Dictionary with export results
        """
        if self._logger:
            self._logger.debug(
                f"Exporting report as HTML",
                output_path=output_path
            )

        # Create output directory if needed
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Generate HTML content
        html_content = self._generate_html(report)

        # Write to file
        try:
            output_file.write_text(html_content, encoding='utf-8')

            if self._metrics:
                self._metrics.increment("test.report.export_html")

            return {
                "status": "success",
                "format": "html",
                "path": str(output_file.absolute()),
            }
        except Exception as e:
            if self._logger:
                self._logger.error(f"Failed to export HTML report: {e}")

            return {
                "status": "error",
                "error": str(e),
            }

    def export_json(
        self,
        report: Dict[str, Any],
        output_path: str = "reports/test_report.json",
        **kwargs
    ) -> Dict[str, Any]:
        """Export report as JSON.

        Args:
            report: Report data dictionary
            output_path: Path to save JSON file
            **kwargs: Additional arguments

        Returns:
            Dictionary with export results
        """
        if self._logger:
            self._logger.debug(
                f"Exporting report as JSON",
                output_path=output_path
            )

        # Create output directory if needed
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Write to file
        try:
            output_file.write_text(
                json.dumps(report, indent=2),
                encoding='utf-8'
            )

            if self._metrics:
                self._metrics.increment("test.report.export_json")

            return {
                "status": "success",
                "format": "json",
                "path": str(output_file.absolute()),
            }
        except Exception as e:
            if self._logger:
                self._logger.error(f"Failed to export JSON report: {e}")

            return {
                "status": "error",
                "error": str(e),
            }

    def _generate_html(self, report: Dict[str, Any]) -> str:
        """Generate HTML content from report data.

        Args:
            report: Report data dictionary

        Returns:
            HTML content as string
        """
        summary = report.get("summary", {})

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{report.get('title', 'Test Report')}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background-color: #333;
            color: white;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        .stat-card {{
            background: white;
            padding: 15px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .stat-card h3 {{
            margin: 0 0 10px 0;
            color: #666;
            font-size: 14px;
        }}
        .stat-card .value {{
            font-size: 32px;
            font-weight: bold;
            margin: 0;
        }}
        .passed {{ color: #28a745; }}
        .failed {{ color: #dc3545; }}
        .errors {{ color: #fd7e14; }}
        .skipped {{ color: #6c757d; }}
        .details {{
            background: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .timestamp {{
            color: #666;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{report.get('title', 'Test Report')}</h1>
        <p class="timestamp">Generated: {report.get('generated_at', 'Unknown')}</p>
    </div>

    <div class="summary">
        <div class="stat-card">
            <h3>Total Tests</h3>
            <p class="value">{summary.get('total', 0)}</p>
        </div>
        <div class="stat-card">
            <h3>Passed</h3>
            <p class="value passed">{summary.get('passed', 0)}</p>
        </div>
        <div class="stat-card">
            <h3>Failed</h3>
            <p class="value failed">{summary.get('failed', 0)}</p>
        </div>
        <div class="stat-card">
            <h3>Errors</h3>
            <p class="value errors">{summary.get('errors', 0)}</p>
        </div>
        <div class="stat-card">
            <h3>Skipped</h3>
            <p class="value skipped">{summary.get('skipped', 0)}</p>
        </div>
    </div>

    <div class="details">
        <h2>Test Details</h2>
        <pre>{json.dumps(report.get('details', {}), indent=2)}</pre>
    </div>
</body>
</html>"""

        return html


__all__ = [
    'ReportFactory',
]
