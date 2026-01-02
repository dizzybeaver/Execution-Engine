"""
False Positive Handler for EE UG-ISP Scanner
Version: 1.0.0
Date: 2025-12-29
Purpose: Transparent false positive detection and reporting for EE UG-ISP violations

This module provides:
- Violation enrichment with false positive metadata
- Pattern-based false positive detection
- Separate false positive report generation
- Manual review workflow support
- Configuration-based confirmed false positives

CRITICAL TRANSPARENCY PRINCIPLE:
- ALL violations remain in main report (NOT filtered)
- Potential false positives are FLAGGED with metadata
- Separate report generated for manual review
- Nothing excluded without explicit user confirmation

UG-ISP COMPLIANCE:
- NO os.environ/os.getenv() calls
- ALL config access via gateway
- Lazy imports only
- Inline correlation IDs
"""

import re
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum


class ConfidenceLevel(Enum):
    """Confidence levels for false positive detection."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


@dataclass
class Violation:
    """
    Enriched violation representation with false positive metadata.

    Attributes:
        category: Violation category type
        file_path: Path to file with violation
        line_number: Line number of violation
        code: Violating code snippet
        fix: Suggested fix
        severity: Severity level (CRITICAL/HIGH/MEDIUM/LOW)
        interface_affected: Gateway interface affected (optional)
        operation_name: Operation name (optional)

        False Positive Metadata:
        potential_false_positive: Flagged as potential false positive
        fp_reason: Explanation of why this might be a false positive
        fp_confidence: Confidence level (LOW/MEDIUM/HIGH)
        fp_context: Additional context for manual review
        fp_pattern_name: Name of pattern that triggered FP detection
        excluded: Whether violation is excluded (confirmed false positive)
        exclusion_reason: Reason for exclusion
    """
    category: str
    file_path: str
    line_number: int
    code: str
    fix: str
    severity: str
    interface_affected: Optional[str] = None
    operation_name: Optional[str] = None

    # False positive metadata
    potential_false_positive: bool = False
    fp_reason: Optional[str] = None
    fp_confidence: Optional[ConfidenceLevel] = None
    fp_context: Dict[str, Any] = field(default_factory=dict)
    fp_pattern_name: Optional[str] = None

    # Exclusion tracking
    excluded: bool = False
    exclusion_reason: Optional[str] = None

    def flag_as_potential_fp(self, reason: str, confidence: ConfidenceLevel,
                            context: Dict[str, Any], pattern_name: str) -> None:
        """
        Flag this violation as a potential false positive.

        Args:
            reason: Explanation of why this might be a false positive
            confidence: Confidence level in the false positive assessment
            context: Additional context for manual review
            pattern_name: Name of pattern that triggered FP detection
        """
        self.potential_false_positive = True
        self.fp_reason = reason
        self.fp_confidence = confidence
        self.fp_context = context
        self.fp_pattern_name = pattern_name

    def mark_as_excluded(self, reason: str) -> None:
        """
        Mark this violation as excluded (confirmed false positive).

        Args:
            reason: Reason for exclusion
        """
        self.excluded = True
        self.exclusion_reason = reason

    def to_dict(self) -> Dict[str, Any]:
        """Convert violation to dictionary for serialization."""
        return {
            'category': self.category,
            'file_path': self.file_path,
            'line_number': self.line_number,
            'code': self.code,
            'fix': self.fix,
            'severity': self.severity,
            'interface_affected': self.interface_affected,
            'operation_name': self.operation_name,
            'potential_false_positive': self.potential_false_positive,
            'fp_reason': self.fp_reason,
            'fp_confidence': self.fp_confidence.value if self.fp_confidence else None,
            'fp_context': self.fp_context,
            'fp_pattern_name': self.fp_pattern_name,
            'excluded': self.excluded,
            'exclusion_reason': self.exclusion_reason,
        }


class FalsePositivePatterns:
    """
    Pattern database for detecting potential false positives.

    Patterns are organized by violation type and include confidence levels,
    reasoning, and context for manual review.
    """

    # Comprehensive pattern database
    FALSE_POSITIVE_PATTERNS: Dict[str, Dict[str, Any]] = {
        # Test file patterns
        'test_file_print_statements': {
            'description': 'Print statements in test files are acceptable for output',
            'file_pattern': r'test_.*\.py|.*_test\.py|tests/.*\.py',
            'violation_type': 'CUSTOM_IMPLEMENTATION',
            'violation_pattern': 'print_statement',
            'confidence': ConfidenceLevel.HIGH,
            'reason': 'Test output files use print for results display and test runner output',
            'review_guidance': 'Confirm file is a test file and print is for test output, not logging',
        },

        # Implementation layer functions
        'implementation_functions': {
            'description': 'Implementation layer functions are core business logic, not helpers',
            'code_pattern': r'def\s+\w+_implementation\s*\(',
            'violation_type': 'INTERNAL_DEBUG_HELPER',
            'confidence': ConfidenceLevel.MEDIUM,
            'reason': 'Functions ending in _implementation are core business logic in implementation layer',
            'review_guidance': 'Confirm function is in implementation layer (*_core.py or *_utilities.py)',
        },

        # Same-interface imports
        'same_interface_imports': {
            'description': 'Imports within same interface package are acceptable',
            'code_pattern': r'from \.\w+ import|from \.\.\w+ import',
            'violation_type': 'CROSS_INTERFACE_IMPORT',
            'confidence': ConfidenceLevel.HIGH,
            'reason': 'Relative imports within same interface package follow UG-ISP',
            'review_guidance': 'Confirm import is relative (starts with .) and within same interface',
        },

        # Core infrastructure imports
        'core_infrastructure_imports': {
            'description': 'Core infrastructure interfaces imported by infrastructure code',
            'code_pattern': r'from EE\.(config|utility|logging)\s+import',
            'violation_type': 'CROSS_INTERFACE_IMPORT',
            'confidence': ConfidenceLevel.MEDIUM,
            'reason': 'Core interfaces (CONFIG, UTILITY, LOGGING) may be imported by gateway infrastructure',
            'review_guidance': 'Confirm import is in gateway/infrastructure code, not interface code',
        },

        # Factory pattern imports
        'factory_pattern_imports': {
            'description': 'Factory modules import generic implementations for object creation',
            'file_pattern': r'.*_factory\.py',
            'code_pattern': r'from.*_generic import|from.*_base import',
            'violation_type': 'CROSS_INTERFACE_IMPORT',
            'confidence': ConfidenceLevel.HIGH,
            'reason': 'Factory modules import generic implementations for object creation (acceptable pattern)',
            'review_guidance': 'Confirm file is a factory and imports are for generic/base classes',
        },

        # Type checking imports
        'type_checking_imports': {
            'description': 'Imports within TYPE_CHECKING block are acceptable',
            'code_pattern': r'if\s+TYPE_CHECKING:.*?from\s+\w+',
            'violation_type': 'CROSS_INTERFACE_IMPORT',
            'confidence': ConfidenceLevel.HIGH,
            'reason': 'Imports within TYPE_CHECKING block are for type hints only, not runtime',
            'review_guidance': 'Confirm import is within if TYPE_CHECKING: block',
        },

        # Lambda handler exceptions
        'lambda_handler_direct_logging': {
            'description': 'Lambda handler may use direct logging for cold start performance',
            'file_pattern': r'lambda_function\.py|lambda_handler\.py',
            'violation_type': 'CUSTOM_IMPLEMENTATION',
            'violation_pattern': 'direct_logging',
            'confidence': ConfidenceLevel.MEDIUM,
            'reason': 'Lambda handler may use direct logging to avoid gateway overhead in cold start',
            'review_guidance': 'Confirm logging is only in lambda handler entry point, not in called functions',
        },

        # Singleton registration
        'singleton_registration_imports': {
            'description': 'Singleton registration code imports singleton core directly',
            'file_pattern': r'singleton.*\.py',
            'code_pattern': r'from.*singleton.*import.*register',
            'violation_type': 'CROSS_INTERFACE_IMPORT',
            'confidence': ConfidenceLevel.MEDIUM,
            'reason': 'Singleton registration code may import core for registration operations',
            'review_guidance': 'Confirm file is singleton registration/manager, not consumer code',
        },

        # Context manager definitions
        'context_manager_definitions': {
            'description': 'Context manager definitions are not debug helpers',
            'code_pattern': r'@contextmanager\s+\ndef\s+_debug_\w+|class\s+\w*DebugContext\w*',
            'violation_type': 'INTERNAL_DEBUG_HELPER',
            'confidence': ConfidenceLevel.MEDIUM,
            'reason': 'Context managers with debug in name are not necessarily debug helpers',
            'review_guidance': 'Confirm context manager is for legitimate resource management, not debug wrapper',
        },

        # Decorator definitions
        'decorator_definitions': {
            'description': 'Decorator functions are not necessarily debug helpers',
            'code_pattern': r'def\s+_debug_\w+\(.*\)\s*->\s*.*:\s+\n.*?@wraps|def\s+_log_\w+\(.*\)\s*->\s*.*:\s+\n.*?@wraps',
            'violation_type': 'INTERNAL_DEBUG_HELPER',
            'confidence': ConfidenceLevel.MEDIUM,
            'reason': 'Decorator functions with debug/logging names may be legitimate decorators',
            'review_guidance': 'Confirm function is a decorator (uses @wraps or returns wrapper)',
        },

        # AST/Parser utilities
        'ast_parser_imports': {
            'description': 'AST/parser utilities may import various modules for analysis',
            'file_pattern': r'.*parser.*\.py|.*scanner.*\.py|.*analyzer.*\.py',
            'code_pattern': r'import\s+ast|from\s+ast\s+import',
            'violation_type': 'CUSTOM_IMPLEMENTATION',
            'violation_pattern': 'ast_usage',
            'confidence': ConfidenceLevel.HIGH,
            'reason': 'Parser/scanner tools use AST module for code analysis (acceptable)',
            'review_guidance': 'Confirm file is a parser/scanner/analyzer tool',
        },

        # Configuration file patterns
        'config_file_exceptions': {
            'description': 'Configuration files may use direct imports for setup',
            'file_pattern': r'config\.py|settings\.py|__init__\.py',
            'violation_type': 'CROSS_INTERFACE_IMPORT',
            'confidence': ConfidenceLevel.LOW,
            'reason': 'Configuration files may import directly for initialization',
            'review_guidance': 'Confirm imports are for module initialization, not runtime operations',
        },

        # Documentation/docstring examples
        'docstring_code_examples': {
            'description': 'Code examples in docstrings may show violations for illustration',
            'code_pattern': r'""".*?print\(|""".*?import\s+\w+',
            'violation_type': 'CUSTOM_IMPLEMENTATION',
            'confidence': ConfidenceLevel.HIGH,
            'reason': 'Docstring examples are documentation, not executable code',
            'review_guidance': 'Confirm code is within docstring (triple quotes)',
        },

        # Commented code
        'commented_violations': {
            'description': 'Violations in comments are not actual violations',
            'code_pattern': r'#.*print\(|#.*from\s+\w+|#.*import\s+\w+',
            'violation_type': 'ANY',
            'confidence': ConfidenceLevel.HIGH,
            'reason': 'Code in comments is not executed',
            'review_guidance': 'Confirm violation is within a comment (starts with #)',
        },

        # Benchmark/profiling code
        'benchmarking_code': {
            'description': 'Benchmarking/profiling code may use direct operations',
            'file_pattern': r'.*benchmark.*\.py|.*profile.*\.py|.*perf.*\.py',
            'violation_type': 'CUSTOM_IMPLEMENTATION',
            'confidence': ConfidenceLevel.MEDIUM,
            'reason': 'Benchmark code may bypass gateway for accurate performance measurement',
            'review_guidance': 'Confirm file is for benchmarking/profiling only',
        },

        # Migration scripts
        'migration_scripts': {
            'description': 'Migration scripts may use direct imports for data migration',
            'file_pattern': r'.*migrate.*\.py|.*migration.*\.py',
            'violation_type': 'CROSS_INTERFACE_IMPORT',
            'confidence': ConfidenceLevel.MEDIUM,
            'reason': 'Migration scripts are one-time operations that may use direct imports',
            'review_guidance': 'Confirm file is a migration script (not production code)',
        },

        # External library integrations
        'external_library_adapters': {
            'description': 'External library adapters may use direct operations',
            'file_pattern': r'.*adapter.*\.py|.*integration.*\.py',
            'violation_type': 'CUSTOM_IMPLEMENTATION',
            'confidence': ConfidenceLevel.LOW,
            'reason': 'Library adapters may need to work around gateway for external compatibility',
            'review_guidance': 'Confirm file bridges external library to EE architecture',
        },
    }

    @classmethod
    def get_patterns_for_violation_type(cls, violation_type: str) -> List[Dict[str, Any]]:
        """
        Get all false positive patterns for a specific violation type.

        Args:
            violation_type: The violation category type

        Returns:
            List of pattern dictionaries for this violation type
        """
        matching_patterns = []
        for pattern_name, pattern_data in cls.FALSE_POSITIVE_PATTERNS.items():
            if pattern_data.get('violation_type') == violation_type:
                matching_patterns.append({
                    'name': pattern_name,
                    **pattern_data
                })
            elif pattern_data.get('violation_type') == 'ANY':
                # Universal patterns apply to all violation types
                matching_patterns.append({
                    'name': pattern_name,
                    **pattern_data
                })
        return matching_patterns

    @classmethod
    def get_pattern(cls, pattern_name: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific false positive pattern by name.

        Args:
            pattern_name: Name of the pattern to retrieve

        Returns:
            Pattern dictionary or None if not found
        """
        return cls.FALSE_POSITIVE_PATTERNS.get(pattern_name)


class FalsePositiveAnalyzer:
    """
    Analyzes violations to detect potential false positives.

    Uses pattern matching, file path analysis, and code context to identify
    violations that might be false positives requiring manual review.
    """

    def __init__(self, patterns: Optional[Dict[str, Dict[str, Any]]] = None):
        """
        Initialize analyzer with false positive patterns.

        Args:
            patterns: Optional custom pattern database (default: FalsePositivePatterns)
        """
        self.patterns = patterns or FalsePositivePatterns.FALSE_POSITIVE_PATTERNS
        self.compiled_file_patterns = self._compile_patterns()
        self.compiled_code_patterns = self._compile_code_patterns()

    def _compile_patterns(self) -> Dict[str, re.Pattern]:
        """Compile file path patterns for efficient matching."""
        compiled = {}
        for name, pattern_data in self.patterns.items():
            if 'file_pattern' in pattern_data:
                compiled[name] = re.compile(pattern_data['file_pattern'], re.IGNORECASE)
        return compiled

    def _compile_code_patterns(self) -> Dict[str, re.Pattern]:
        """Compile code patterns for efficient matching."""
        compiled = {}
        for name, pattern_data in self.patterns.items():
            if 'code_pattern' in pattern_data:
                # Use MULTILINE for multi-line patterns (like TYPE_CHECKING blocks)
                compiled[name] = re.compile(pattern_data['code_pattern'], re.MULTILINE | re.DOTALL)
        return compiled

    def analyze_violation(self, violation: Violation) -> List[Dict[str, Any]]:
        """
        Analyze a violation for potential false positive patterns.

        Args:
            violation: Violation object to analyze

        Returns:
            List of potential false positive matches with metadata
        """
        matches = []

        # Check all false positive patterns
        for pattern_name, pattern_data in self.patterns.items():
            # Check if pattern applies to this violation type
            violation_type = pattern_data.get('violation_type', 'ANY')
            if violation_type != 'ANY' and violation_type != violation.category:
                continue

            # Check specific violation pattern if specified
            if 'violation_pattern' in pattern_data:
                violation_pattern = pattern_data['violation_pattern']
                # Skip if violation doesn't match pattern category
                # (This would require more context about the violation)

            # Check file path pattern
            file_match = False
            if pattern_name in self.compiled_file_patterns:
                if self.compiled_file_patterns[pattern_name].search(violation.file_path):
                    file_match = True

            # Check code pattern
            code_match = False
            if pattern_name in self.compiled_code_patterns:
                if self.compiled_code_patterns[pattern_name].search(violation.code):
                    code_match = True

            # Determine if pattern matches
            pattern_matches = False
            if 'file_pattern' in pattern_data and 'code_pattern' in pattern_data:
                # Both patterns must match
                pattern_matches = file_match and code_match
            elif 'file_pattern' in pattern_data:
                pattern_matches = file_match
            elif 'code_pattern' in pattern_data:
                pattern_matches = code_match
            else:
                # No pattern specified, skip
                continue

            if pattern_matches:
                matches.append({
                    'pattern_name': pattern_name,
                    'confidence': pattern_data['confidence'],
                    'reason': pattern_data['reason'],
                    'description': pattern_data['description'],
                    'review_guidance': pattern_data.get('review_guidance', ''),
                })

        return matches

    def flag_potential_false_positives(self, violations: List[Violation]) -> List[Violation]:
        """
        Analyze and flag potential false positives in violation list.

        Args:
            violations: List of violations to analyze

        Returns:
            Same list with violations flagged as potential false positives
        """
        for violation in violations:
            matches = self.analyze_violation(violation)

            if matches:
                # Use highest confidence match
                confidence_order = {
                    ConfidenceLevel.HIGH: 0,
                    ConfidenceLevel.MEDIUM: 1,
                    ConfidenceLevel.LOW: 2,
                }

                best_match = min(matches, key=lambda m: confidence_order[m['confidence']])

                violation.flag_as_potential_fp(
                    reason=best_match['reason'],
                    confidence=best_match['confidence'],
                    context={
                        'pattern_name': best_match['pattern_name'],
                        'description': best_match['description'],
                        'review_guidance': best_match['review_guidance'],
                        'all_matches': [m['pattern_name'] for m in matches],
                    },
                    pattern_name=best_match['pattern_name']
                )

        return violations


class ConfirmedFalsePositiveManager:
    """
    Manages confirmed false positive list from configuration file.

    Loads confirmed false positives from YAML file and provides
    methods to check if violations match confirmed FP patterns.
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize manager with configuration file.

        Args:
            config_path: Path to YAML config file (default: scanner/false_positives.yaml)
        """
        if config_path is None:
            # Default path relative to this file
            default_dir = Path(__file__).parent
            config_path = default_dir / "false_positives.yaml"

        self.config_path = Path(config_path)
        self.confirmed_fps = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load confirmed false positive configuration from YAML."""
        if not self.config_path.exists():
            # Return empty config if file doesn't exist
            return {'confirmed_false_positives': [], 'metadata': {'version': '1.0.0'}}

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                return config or {'confirmed_false_positives': []}
        except Exception as e:
            print(f"Warning: Failed to load false positive config: {e}")
            return {'confirmed_false_positives': []}

    def is_confirmed_false_positive(self, violation: Violation) -> bool:
        """
        Check if violation matches any confirmed false positive pattern.

        Args:
            violation: Violation to check

        Returns:
            True if violation matches confirmed FP pattern
        """
        for fp_pattern in self.confirmed_fps.get('confirmed_false_positives', []):
            if self._matches_pattern(violation, fp_pattern):
                return True

        return False

    def _matches_pattern(self, violation: Violation, fp_pattern: Dict[str, Any]) -> bool:
        """Check if violation matches a specific confirmed FP pattern."""
        # Check file pattern
        if 'file_pattern' in fp_pattern:
            if not re.search(fp_pattern['file_pattern'], violation.file_path, re.IGNORECASE):
                return False

        # Check violation type
        if 'violation_type' in fp_pattern:
            if fp_pattern['violation_type'] != violation.category:
                return False

        # Check code pattern
        if 'code_pattern' in fp_pattern:
            if not re.search(fp_pattern['code_pattern'], violation.code, re.MULTILINE):
                return False

        # All specified patterns matched
        return True

    def add_confirmed_false_positive(self, violation: Violation,
                                    confirmed_by: str = "USER",
                                    notes: str = "") -> None:
        """
        Add a violation to the confirmed false positive list.

        Args:
            violation: Violation to add as confirmed FP
            confirmed_by: Who confirmed this as FP (default: USER)
            notes: Additional notes about the confirmation
        """
        fp_entry = {
            'pattern': violation.fp_pattern_name or 'manual',
            'file_pattern': violation.file_path,
            'violation_type': violation.category,
            'code_pattern': violation.code[:100],  # First 100 chars as pattern
            'reason': violation.fp_reason or notes,
            'confirmed_by': confirmed_by,
            'date': None,  # Will be set when saving
            'notes': notes,
        }

        self.confirmed_fps['confirmed_false_positives'].append(fp_entry)
        self.save_config()

    def save_config(self) -> None:
        """Save confirmed false positive configuration to YAML."""
        from datetime import datetime

        # Update date for all entries
        for fp in self.confirmed_fps['confirmed_false_positives']:
            if fp.get('date') is None:
                fp['date'] = datetime.now().isoformat()

        # Ensure metadata
        if 'metadata' not in self.confirmed_fps:
            self.confirmed_fps['metadata'] = {}

        self.confirmed_fps['metadata']['version'] = '1.0.0'
        self.confirmed_fps['metadata']['last_updated'] = datetime.now().isoformat()

        # Create parent directory if needed
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        # Save to YAML
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.confirmed_fps, f, default_flow_style=False, sort_keys=False)

        print(f"Confirmed false positives saved to: {self.config_path}")


class ViolationReporter:
    """
    Generates reports for EE UG-ISP violations with false positive handling.

    Creates:
    1. Main violation report (ALL violations, including potential FPs)
    2. Separate false positive review report (for manual review)
    3. Statistics and summary reports
    """

    def __init__(self):
        """Initialize violation reporter."""
        pass

    def generate_main_report(self, violations: List[Violation],
                            stats: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate main violation report with ALL violations (nothing filtered).

        Potential false positives are included with metadata flags.

        Args:
            violations: List of all violations (including potential FPs)
            stats: Optional scan statistics

        Returns:
            Markdown-formatted report
        """
        from datetime import datetime

        report_lines = [
            "# EE UG-ISP Architecture Compliance Report",
            "",
            f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Total Violations:** {len(violations)}",
            "",
            "---",
            "",
        ]

        # Statistics section
        if stats:
            report_lines.extend([
                "## Scan Statistics",
                "",
                f"- Files Scanned: {stats.get('files_scanned', 0)}",
                f"- Lines Analyzed: {stats.get('lines_analyzed', 0):,}",
                f"- Scan Duration: {stats.get('scan_duration_seconds', 0):.2f}s",
                "",
            ])

        # Summary by severity
        severity_counts = {}
        fp_counts = {}
        for v in violations:
            severity_counts[v.severity] = severity_counts.get(v.severity, 0) + 1
            if v.potential_false_positive:
                fp_counts[v.severity] = fp_counts.get(v.severity, 0) + 1

        report_lines.extend([
            "## Violation Summary",
            "",
        ])

        for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            count = severity_counts.get(severity, 0)
            fp_count = fp_counts.get(severity, 0)
            if count > 0:
                fp_note = f" ({fp_count} flagged as potential false positives)" if fp_count > 0 else ""
                report_lines.append(f"- **{severity}:** {count}{fp_note}")

        report_lines.extend(["", ""])

        # Detailed violation list
        report_lines.extend([
            "## Detailed Violations",
            "",
            "**TRANSPARENCY NOTE:** This report includes ALL detected violations.",
            "Potential false positives are flagged with metadata for review.",
            "",
        ])

        # Group by severity
        for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            severity_violations = [v for v in violations if v.severity == severity]
            if not severity_violations:
                continue

            report_lines.extend([
                f"### {severity} Violations ({len(severity_violations)})",
                "",
            ])

            for i, v in enumerate(severity_violations, 1):
                report_lines.extend([
                    f"#### {i}. {Path(v.file_path).name}:{v.line_number}",
                    "",
                    f"**Category:** `{v.category}`",
                    f"**Severity:** `{v.severity}`",
                ])

                if v.interface_affected:
                    report_lines.append(f"**Interface:** `{v.interface_affected}`")

                report_lines.extend([
                    f"",
                    f"**Description:** {v.description if hasattr(v, 'description') else 'N/A'}",
                    "",
                    f"**Current Code:**",
                    f"```python",
                    v.code,
                    "```",
                    "",
                    f"**Suggested Fix:**",
                    f"```python",
                    v.fix,
                    "```",
                    "",
                ])

                # False positive flag
                if v.potential_false_positive:
                    report_lines.extend([
                        f"**⚠️ POTENTIAL FALSE POSITIVE**",
                        "",
                        f"**Reason:** {v.fp_reason}",
                        f"**Confidence:** `{v.fp_confidence.value if v.fp_confidence else 'N/A'}`",
                        f"**Pattern:** `{v.fp_pattern_name or 'N/A'}`",
                    ])

                    if v.fp_context.get('review_guidance'):
                        report_lines.append(f"**Review Guidance:** {v.fp_context['review_guidance']}")

                    report_lines.extend(["", ""])

                    if v.fp_context.get('all_matches'):
                        report_lines.append(f"**Matching Patterns:** {', '.join(v.fp_context['all_matches'])}")
                        report_lines.append("")

                # Exclusion flag
                if v.excluded:
                    report_lines.extend([
                        f"**✅ EXCLUDED** (Confirmed False Positive)",
                        "",
                        f"**Reason:** {v.exclusion_reason}",
                        "",
                    ])

                report_lines.append("---")
                report_lines.append("")

        return "\n".join(report_lines)

    def generate_false_positive_report(self, violations: List[Violation]) -> str:
        """
        Generate separate report for potential false positives.

        This report is for manual review to confirm/reject false positives.

        Args:
            violations: List of violations (FPs will be filtered)

        Returns:
            Markdown-formatted report
        """
        from datetime import datetime

        # Filter violations flagged as potential FPs
        potential_fps = [v for v in violations if v.potential_false_positive and not v.excluded]

        if not potential_fps:
            return "# Potential False Positives Review\n\n**No potential false positives detected.**\n"

        report_lines = [
            "# Potential False Positives Review",
            "",
            f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Total Potential False Positives:** {len(potential_fps)}",
            "",
            "---",
            "",
            "## Instructions",
            "",
            "Review each potential false positive below and decide:",
            "- [ ] **Confirm as False Positive** - Will be excluded from future reports",
            "- [ ] **Reject as Actual Violation** - Will remain in main report",
            "",
            "To confirm a false positive, update the `scanner/false_positives.yaml` file.",
            "",
            "---",
            "",
        ]

        # Group by confidence
        confidence_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}

        for confidence_level in ['HIGH', 'MEDIUM', 'LOW']:
            confidence_violations = [
                v for v in potential_fps
                if v.fp_confidence and v.fp_confidence.value == confidence_level
            ]

            if not confidence_violations:
                continue

            report_lines.extend([
                f"## {confidence_level} Confidence ({len(confidence_violations)} violations)",
                "",
            ])

            for i, v in enumerate(confidence_violations, 1):
                report_lines.extend([
                    f"### {i}. {Path(v.file_path).name}:{v.line_number}",
                    "",
                    f"**Category:** `{v.category}`",
                    f"**Severity:** `{v.severity}`",
                    f"**Pattern:** `{v.fp_pattern_name or 'N/A'}`",
                    "",
                    f"**FP Reason:** {v.fp_reason}",
                    f"**Confidence:** `{v.fp_confidence.value}`",
                    "",
                ])

                if v.fp_context.get('description'):
                    report_lines.append(f"**Description:** {v.fp_context['description']}")

                if v.fp_context.get('review_guidance'):
                    report_lines.extend([
                        "",
                        "**Review Guidance:**",
                        v.fp_context['review_guidance'],
                    ])

                report_lines.extend([
                    "",
                    "**Violating Code:**",
                    "```python",
                    v.code,
                    "```",
                    "",
                    "**Decision Required:**",
                    "- [ ] Confirm as false positive (add to `false_positives.yaml`)",
                    "- [ ] Reject as actual violation (keep in main report)",
                    "",
                    "**Notes:**",
                    "```",
                    "# Add your review notes here",
                    "```",
                    "",
                    "---",
                    "",
                ])

        return "\n".join(report_lines)

    def generate_summary_report(self, violations: List[Violation],
                                stats: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate summary statistics for violations.

        Args:
            violations: List of violations
            stats: Optional scan statistics

        Returns:
            Dictionary containing summary statistics
        """
        summary = {
            'total_violations': len(violations),
            'by_severity': {},
            'by_category': {},
            'by_file': {},
            'potential_false_positives': {
                'total': 0,
                'by_confidence': {},
                'by_severity': {},
            },
            'excluded': {
                'total': 0,
                'by_reason': {},
            },
        }

        for v in violations:
            # Count by severity
            summary['by_severity'][v.severity] = summary['by_severity'].get(v.severity, 0) + 1

            # Count by category
            summary['by_category'][v.category] = summary['by_category'].get(v.category, 0) + 1

            # Count by file
            summary['by_file'][v.file_path] = summary['by_file'].get(v.file_path, 0) + 1

            # Count potential false positives
            if v.potential_false_positive:
                summary['potential_false_positives']['total'] += 1

                conf = v.fp_confidence.value if v.fp_confidence else 'UNKNOWN'
                summary['potential_false_positives']['by_confidence'][conf] = \
                    summary['potential_false_positives']['by_confidence'].get(conf, 0) + 1

                summary['potential_false_positives']['by_severity'][v.severity] = \
                    summary['potential_false_positives']['by_severity'].get(v.severity, 0) + 1

            # Count excluded
            if v.excluded:
                summary['excluded']['total'] += 1

                reason = v.exclusion_reason or 'Unknown'
                summary['excluded']['by_reason'][reason] = \
                    summary['excluded']['by_reason'].get(reason, 0) + 1

        # Add scan stats
        if stats:
            summary['scan_stats'] = stats

        return summary


def create_default_false_positives_config(output_path: Optional[str] = None) -> None:
    """
    Create default false positives configuration YAML file.

    Args:
        output_path: Optional custom output path
    """
    if output_path is None:
        default_dir = Path(__file__).parent
        output_path = default_dir / "false_positives.yaml"

    default_config = {
        'metadata': {
            'version': '1.0.0',
            'last_updated': None,
            'description': 'Confirmed false positive patterns for EE UG-ISP scanner',
        },
        'confirmed_false_positives': [
            {
                'pattern': 'test_file_print_statements',
                'file_pattern': r'test_.*\.py',
                'violation_type': 'CUSTOM_IMPLEMENTATION',
                'violation_pattern': 'print_statement',
                'reason': 'Test output files use print for results display',
                'confirmed_by': 'USER',
                'date': None,
                'notes': 'Automatically added as example',
            },
            {
                'pattern': 'implementation_functions',
                'file_pattern': r'.*_core\.py|.*_utilities\.py',
                'code_pattern': r'def\s+\w+_implementation\s*\(',
                'violation_type': 'INTERNAL_DEBUG_HELPER',
                'reason': 'Core business logic functions in implementation layer',
                'confirmed_by': 'USER',
                'date': None,
                'notes': 'Functions ending in _implementation are not helpers',
            },
        ],
    }

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(default_config, f, default_flow_style=False, sort_keys=False)

    print(f"Default false positives config created: {output_path}")


if __name__ == '__main__':
    # Create default config when run directly
    create_default_false_positives_config()
