"""ha_statistics - Statistics Interface

Version: 2025-12-22_1
Description: Long-term statistics analytics operations

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

# Core implementations
from lee.home_assistant.ha_statistics.ha_statistics_core import (
    adjust_sum_statistics_impl,
    change_statistics_unit_impl,
    clear_statistics_impl,
    get_statistic_during_period_impl,
    get_statistics_during_period_impl,
    get_statistics_metadata_impl,
    import_statistics_impl,
    list_statistic_ids_impl,
    update_statistics_issues_impl,
    update_statistics_metadata_impl,
    validate_statistics_impl,
)

__all__ = [
    "adjust_sum_statistics_impl",
    "change_statistics_unit_impl",
    "clear_statistics_impl",
    "get_statistic_during_period_impl",
    "get_statistics_during_period_impl",
    "get_statistics_metadata_impl",
    "import_statistics_impl",
    "list_statistic_ids_impl",
    "update_statistics_issues_impl",
    "update_statistics_metadata_impl",
    "validate_statistics_impl",
]
