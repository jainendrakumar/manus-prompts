"""QMeter analytics package."""
from .compare import (
    compare_category_scores,
    compare_scores_summary,
    compute_diff,
    get_directionality,
)
from .stability import (
    analyze_stability,
    build_stability_table,
    build_outlier_table,
    compute_stability_stats,
    detect_outliers,
)
from .findings import (
    generate_findings,
    format_findings_text,
)

__all__ = [
    "compare_category_scores",
    "compare_scores_summary",
    "compute_diff",
    "get_directionality",
    "analyze_stability",
    "build_stability_table",
    "build_outlier_table",
    "compute_stability_stats",
    "detect_outliers",
    "generate_findings",
    "format_findings_text",
]
