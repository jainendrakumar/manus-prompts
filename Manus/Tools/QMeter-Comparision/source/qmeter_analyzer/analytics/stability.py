"""Stability analysis and outlier detection for multi-run packs."""
from __future__ import annotations

import logging
import math
import statistics
from collections import defaultdict
from typing import Any, Dict, List, Optional

from ..models import AnalysisContext, QMeterResult

logger = logging.getLogger(__name__)


def compute_stability_stats(values: List[float]) -> Dict[str, Any]:
    """Compute comprehensive stability statistics for a list of values.

    Returns: mean, median, stdev, min, max, p90, p95, cv, ci_95_lower, ci_95_upper
    """
    if not values:
        return {k: None for k in [
            "count", "mean", "median", "stdev", "min", "max",
            "p90", "p95", "cv", "ci_95_lower", "ci_95_upper",
        ]}

    n = len(values)
    sorted_vals = sorted(values)
    mean = statistics.mean(values)
    median = statistics.median(values)
    stdev = statistics.stdev(values) if n > 1 else 0.0
    p90 = _percentile(sorted_vals, 90)
    p95 = _percentile(sorted_vals, 95)
    cv = (stdev / mean * 100.0) if mean != 0 else 0.0

    # 95% CI using t-distribution approximation
    if n > 1:
        # Use 1.96 for large samples, adjust for small
        t_val = 1.96 if n >= 30 else _t_critical(n - 1)
        margin = t_val * (stdev / math.sqrt(n))
        ci_lower = mean - margin
        ci_upper = mean + margin
    else:
        ci_lower = mean
        ci_upper = mean

    return {
        "count": n,
        "mean": round(mean, 4),
        "median": round(median, 4),
        "stdev": round(stdev, 4),
        "min": round(min(values), 4),
        "max": round(max(values), 4),
        "p90": round(p90, 4),
        "p95": round(p95, 4),
        "cv": round(cv, 4),
        "ci_95_lower": round(ci_lower, 4),
        "ci_95_upper": round(ci_upper, 4),
    }


def _percentile(sorted_vals: List[float], pct: float) -> float:
    """Compute percentile from sorted values."""
    if not sorted_vals:
        return 0.0
    k = (len(sorted_vals) - 1) * (pct / 100.0)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return sorted_vals[int(k)]
    d0 = sorted_vals[int(f)] * (c - k)
    d1 = sorted_vals[int(c)] * (k - f)
    return d0 + d1


def _t_critical(df: int) -> float:
    """Approximate t-critical value for 95% CI."""
    # Common t-values for small samples
    t_table = {
        1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571,
        6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228,
        15: 2.131, 20: 2.086, 25: 2.060, 30: 2.042,
    }
    if df in t_table:
        return t_table[df]
    # Find closest
    for threshold in sorted(t_table.keys()):
        if df <= threshold:
            return t_table[threshold]
    return 1.96


def detect_outliers(
    values: List[float],
    method: str = "iqr",
    threshold: float = 1.5,
) -> List[Dict[str, Any]]:
    """Detect outliers using IQR method.

    Returns list of dicts with index, value, and reason.
    """
    if len(values) < 4:
        return []

    sorted_vals = sorted(values)
    q1 = _percentile(sorted_vals, 25)
    q3 = _percentile(sorted_vals, 75)
    iqr = q3 - q1

    lower_bound = q1 - threshold * iqr
    upper_bound = q3 + threshold * iqr

    outliers = []
    for i, v in enumerate(values):
        if v < lower_bound:
            outliers.append({
                "index": i,
                "value": round(v, 4),
                "reason": f"Below Q1 - {threshold}*IQR ({round(lower_bound, 2)})",
                "severity": "low" if v >= q1 - 3 * iqr else "high",
            })
        elif v > upper_bound:
            outliers.append({
                "index": i,
                "value": round(v, 4),
                "reason": f"Above Q3 + {threshold}*IQR ({round(upper_bound, 2)})",
                "severity": "low" if v <= q3 + 3 * iqr else "high",
            })

    return outliers


def analyze_stability(
    context: AnalysisContext,
) -> Dict[str, Any]:
    """Analyze stability across all sources.

    Returns a dict keyed by source_label with stability stats for each metric.
    """
    # Group results by source
    groups = defaultdict(list)
    for result in context.results:
        groups[result.source_label].append(result)

    stability_report = {}

    for label, results in groups.items():
        if len(results) < 2:
            continue  # Need multiple runs for stability analysis

        metrics = defaultdict(list)

        for result in results:
            for run in result.runs:
                if run.score1 is not None:
                    metrics["score1"].append(run.score1)
                if run.score4 is not None:
                    metrics["score4"].append(run.score4)
                if run.score16 is not None:
                    metrics["score16"].append(run.score16)

                for cat in run.categories:
                    cat_name = cat.name.lower().replace(" ", "_")
                    metrics[f"{cat_name}_avg_runtime"].append(cat.avg_runtime)

                    for grp in cat.groups:
                        prefix = f"{cat_name}_t{grp.nr_of_threads}"
                        metrics[f"{prefix}_group_score"].append(grp.group_score)
                        metrics[f"{prefix}_avg_runtime"].append(grp.avg_runtime)

        source_stats = {}
        for metric_name, values in sorted(metrics.items()):
            stats = compute_stability_stats(values)
            outliers = detect_outliers(values)
            stats["outliers"] = outliers
            stats["outlier_count"] = len(outliers)
            source_stats[metric_name] = stats

        stability_report[label] = source_stats

    return stability_report


def build_stability_table(
    stability_report: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """Flatten stability report into table rows."""
    rows = []
    for label, metrics in stability_report.items():
        for metric_name, stats in metrics.items():
            row = {
                "source_label": label,
                "metric": metric_name,
            }
            row.update({k: v for k, v in stats.items() if k != "outliers"})
            rows.append(row)
    return rows


def build_outlier_table(
    stability_report: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """Extract all outliers into a flat table."""
    rows = []
    for label, metrics in stability_report.items():
        for metric_name, stats in metrics.items():
            for outlier in stats.get("outliers", []):
                rows.append({
                    "source_label": label,
                    "metric": metric_name,
                    "run_index": outlier["index"],
                    "value": outlier["value"],
                    "reason": outlier["reason"],
                    "severity": outlier["severity"],
                })
    return rows
