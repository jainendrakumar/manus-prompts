"""Comparison engine with directionality-aware math."""
from __future__ import annotations

import logging
import statistics
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple

from ..models import AnalysisContext, QMeterResult

logger = logging.getLogger(__name__)

# Default directionality rules
# "lower_is_better" for durations/runtimes, "higher_is_better" for throughput
DEFAULT_DIRECTIONALITY = {
    "score1": "lower_is_better",       # Score IS duration-based
    "score4": "lower_is_better",
    "score16": "lower_is_better",
    "avg_runtime": "lower_is_better",
    "group_score": "lower_is_better",   # GroupScore = AvgRuntime + StdDev
    "std_dev": "lower_is_better",
}


def get_directionality(metric_name: str, overrides: Optional[Dict] = None) -> str:
    """Get directionality for a metric, checking overrides first."""
    if overrides:
        for pattern, direction in overrides.items():
            if pattern in metric_name:
                return direction
    # Check defaults
    for pattern, direction in DEFAULT_DIRECTIONALITY.items():
        if pattern in metric_name:
            return direction
    return "lower_is_better"  # Default assumption


def compute_diff(
    baseline_value: Optional[float],
    compare_value: Optional[float],
    directionality: str = "lower_is_better",
) -> Dict[str, Any]:
    """Compute difference and percentage change between baseline and comparison.

    Sign convention:
        - For lower_is_better (durations): positive % = slower/worse
        - For higher_is_better: positive % = worse (decreased)

    Returns dict with: diff, pct_change, assessment
    """
    if baseline_value is None or compare_value is None:
        return {"diff": None, "pct_change": None, "assessment": "N/A"}

    diff = compare_value - baseline_value

    if baseline_value != 0:
        pct_change = (diff / abs(baseline_value)) * 100.0
    else:
        pct_change = 0.0 if diff == 0 else float("inf")

    # Assessment
    if directionality == "lower_is_better":
        # For durations: positive diff means slower (worse)
        if diff > 0:
            assessment = "regression"
        elif diff < 0:
            assessment = "improvement"
        else:
            assessment = "unchanged"
    else:
        # For higher_is_better: positive diff means higher (better)
        if diff > 0:
            assessment = "improvement"
        elif diff < 0:
            assessment = "regression"
        else:
            assessment = "unchanged"

    return {
        "diff": round(diff, 4),
        "pct_change": round(pct_change, 4),
        "assessment": assessment,
    }


def compare_category_scores(
    context: AnalysisContext,
    baseline_idx: int = 0,
    metric_rules: Optional[Dict] = None,
) -> List[Dict[str, Any]]:
    """Compare category-level metrics across all sources vs baseline.

    Groups results by source_label and compares mean values against baseline.
    """
    # Group results by source
    groups = defaultdict(list)
    for result in context.results:
        groups[result.source_label].append(result)

    source_labels = list(groups.keys())
    if not source_labels:
        return []

    # Determine baseline
    baseline_label = source_labels[min(baseline_idx, len(source_labels) - 1)]
    baseline_results = groups[baseline_label]

    rows = []
    for label, results in groups.items():
        # Compute mean scores across runs for this source
        baseline_means = _compute_category_means(baseline_results)
        current_means = _compute_category_means(results)

        for cat_key in sorted(set(list(baseline_means.keys()) + list(current_means.keys()))):
            bval = baseline_means.get(cat_key)
            cval = current_means.get(cat_key)

            direction = get_directionality(cat_key, metric_rules)
            comparison = compute_diff(bval, cval, direction)

            rows.append({
                "source_label": label,
                "is_baseline": label == baseline_label,
                "metric": cat_key,
                "baseline_value": round(bval, 2) if bval is not None else None,
                "current_value": round(cval, 2) if cval is not None else None,
                "diff": comparison["diff"],
                "pct_change": comparison["pct_change"],
                "assessment": comparison["assessment"],
                "directionality": direction,
            })

    return rows


def compare_scores_summary(
    context: AnalysisContext,
    baseline_idx: int = 0,
    metric_rules: Optional[Dict] = None,
) -> List[Dict[str, Any]]:
    """Compare Score1/Score4/Score16 across sources."""
    groups = defaultdict(list)
    for result in context.results:
        for run in result.runs:
            groups[result.source_label].append({
                "score1": run.score1,
                "score4": run.score4,
                "score16": run.score16,
            })

    source_labels = list(groups.keys())
    if not source_labels:
        return []

    baseline_label = source_labels[min(baseline_idx, len(source_labels) - 1)]

    rows = []
    for score_name in ["score1", "score4", "score16"]:
        baseline_vals = [r[score_name] for r in groups[baseline_label]
                         if r[score_name] is not None]
        baseline_mean = statistics.mean(baseline_vals) if baseline_vals else None

        for label in source_labels:
            vals = [r[score_name] for r in groups[label]
                    if r[score_name] is not None]
            current_mean = statistics.mean(vals) if vals else None

            direction = get_directionality(score_name, metric_rules)
            comparison = compute_diff(baseline_mean, current_mean, direction)

            rows.append({
                "source_label": label,
                "is_baseline": label == baseline_label,
                "score_type": score_name,
                "run_count": len(vals),
                "baseline_mean": round(baseline_mean, 2) if baseline_mean is not None else None,
                "current_mean": round(current_mean, 2) if current_mean is not None else None,
                "diff": comparison["diff"],
                "pct_change": comparison["pct_change"],
                "assessment": comparison["assessment"],
            })

    return rows


def _compute_category_means(results: List[QMeterResult]) -> Dict[str, float]:
    """Compute mean values for each category metric across multiple runs."""
    accum = defaultdict(list)

    for result in results:
        for run in result.runs:
            for cat in run.categories:
                cat_name = cat.name.lower().replace(" ", "_")
                accum[f"{cat_name}_avg_runtime"].append(cat.avg_runtime)

                for grp in cat.groups:
                    prefix = f"{cat_name}_t{grp.nr_of_threads}"
                    accum[f"{prefix}_group_score"].append(grp.group_score)
                    accum[f"{prefix}_avg_runtime"].append(grp.avg_runtime)
                    accum[f"{prefix}_std_dev"].append(grp.std_dev_runtime)

    return {k: statistics.mean(v) for k, v in accum.items() if v}
