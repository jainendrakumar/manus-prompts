"""Bottleneck inference and narrative findings generator."""
from __future__ import annotations

import logging
from collections import defaultdict
from typing import Any, Dict, List, Optional

from ..models import AnalysisContext

logger = logging.getLogger(__name__)

# Thresholds for assessment
REGRESSION_THRESHOLD_PCT = 5.0   # >5% worse = notable regression
IMPROVEMENT_THRESHOLD_PCT = 5.0  # >5% better = notable improvement
HIGH_CV_THRESHOLD = 10.0         # CV > 10% = high variance


def generate_findings(
    context: AnalysisContext,
    comparison_rows: List[Dict[str, Any]],
    stability_report: Dict[str, Any],
    score_comparison: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Generate narrative findings from analysis data.

    Returns list of finding dicts with: category, severity, title, detail, recommendation
    """
    findings = []

    # 1. Score-level findings
    findings.extend(_score_findings(score_comparison))

    # 2. Category-level regression/improvement findings
    findings.extend(_category_findings(comparison_rows))

    # 3. Stability findings
    findings.extend(_stability_findings(stability_report))

    # 4. Infrastructure findings
    findings.extend(_infrastructure_findings(context))

    # 5. Cross-category correlation findings
    findings.extend(_correlation_findings(comparison_rows))

    # Sort by severity
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
    findings.sort(key=lambda f: severity_order.get(f.get("severity", "info"), 5))

    return findings


def _score_findings(score_comparison: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate findings from score comparisons."""
    findings = []

    for row in score_comparison:
        if row.get("is_baseline"):
            continue

        pct = row.get("pct_change")
        if pct is None:
            continue

        score_type = row.get("score_type", "")
        label = row.get("source_label", "")
        assessment = row.get("assessment", "")

        if assessment == "regression" and abs(pct) > REGRESSION_THRESHOLD_PCT:
            severity = "critical" if abs(pct) > 20 else "high"
            findings.append({
                "category": "Score Regression",
                "severity": severity,
                "title": f"{score_type.upper()} regression on {label}",
                "detail": (
                    f"{score_type.upper()} is {abs(pct):.1f}% worse than baseline. "
                    f"Baseline mean: {row.get('baseline_mean')}, "
                    f"Current mean: {row.get('current_mean')}. "
                    f"This indicates overall performance degradation "
                    f"{'at single-thread level' if score_type == 'score1' else 'under parallel load'}."
                ),
                "recommendation": (
                    f"Investigate {'CPU single-core performance and memory latency' if score_type == 'score1' else 'multi-threaded scaling and NUMA effects'} "
                    f"on {label}."
                ),
            })
        elif assessment == "improvement" and abs(pct) > IMPROVEMENT_THRESHOLD_PCT:
            findings.append({
                "category": "Score Improvement",
                "severity": "info",
                "title": f"{score_type.upper()} improvement on {label}",
                "detail": (
                    f"{score_type.upper()} is {abs(pct):.1f}% better than baseline. "
                    f"Baseline mean: {row.get('baseline_mean')}, "
                    f"Current mean: {row.get('current_mean')}."
                ),
                "recommendation": "No action needed. Document as performance gain.",
            })

    return findings


def _category_findings(comparison_rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate findings from category-level comparisons."""
    findings = []

    # Group by source
    by_source = defaultdict(list)
    for row in comparison_rows:
        if not row.get("is_baseline"):
            by_source[row["source_label"]].append(row)

    for label, rows in by_source.items():
        regressions = [r for r in rows if r.get("assessment") == "regression"
                       and r.get("pct_change") is not None
                       and abs(r["pct_change"]) > REGRESSION_THRESHOLD_PCT]

        if not regressions:
            continue

        # Identify worst category
        worst = max(regressions, key=lambda r: abs(r["pct_change"]))
        metric = worst["metric"]

        if "quill" in metric:
            findings.append({
                "category": "Quill Regression",
                "severity": "high",
                "title": f"Quill speed regression on {label}",
                "detail": (
                    f"Quill test shows {abs(worst['pct_change']):.1f}% regression. "
                    f"This indicates CPU IPC (instructions per cycle) sensitivity. "
                    f"Quill tests are single-threaded logic-heavy workloads."
                ),
                "recommendation": (
                    "Check CPU model differences, clock speed, and IPC characteristics. "
                    "Virtualization overhead may also impact Quill performance."
                ),
            })
        elif "database" in metric:
            findings.append({
                "category": "Database Regression",
                "severity": "high",
                "title": f"Database test regression on {label}",
                "detail": (
                    f"Database test shows {abs(worst['pct_change']):.1f}% regression. "
                    f"This suggests storage latency or I/O stack overhead issues."
                ),
                "recommendation": (
                    "Investigate storage subsystem: disk type (SSD vs HDD), "
                    "I/O scheduler, virtualization storage driver, and network storage latency."
                ),
            })
        elif "memory" in metric:
            findings.append({
                "category": "Memory Regression",
                "severity": "high",
                "title": f"Memory test regression on {label}",
                "detail": (
                    f"Memory test shows {abs(worst['pct_change']):.1f}% regression. "
                    f"This indicates memory bandwidth or latency issues."
                ),
                "recommendation": (
                    "Check memory configuration: speed, channels, NUMA topology, "
                    "and whether memory is shared with other VMs."
                ),
            })
        elif "algorithm" in metric:
            findings.append({
                "category": "Algorithm Regression",
                "severity": "medium",
                "title": f"Algorithm test regression on {label}",
                "detail": (
                    f"Algorithm test shows {abs(worst['pct_change']):.1f}% regression. "
                    f"This affects optimization solver performance."
                ),
                "recommendation": (
                    "Review CPU computational throughput and cache hierarchy. "
                    "Algorithm tests stress both CPU and memory subsystems."
                ),
            })

    return findings


def _stability_findings(stability_report: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate findings from stability analysis."""
    findings = []

    for label, metrics in stability_report.items():
        high_cv_metrics = []
        for metric_name, stats in metrics.items():
            cv = stats.get("cv", 0)
            if cv and cv > HIGH_CV_THRESHOLD:
                high_cv_metrics.append((metric_name, cv))

        if high_cv_metrics:
            worst = max(high_cv_metrics, key=lambda x: x[1])
            findings.append({
                "category": "Stability Warning",
                "severity": "medium",
                "title": f"High variance detected on {label}",
                "detail": (
                    f"{len(high_cv_metrics)} metrics show CV > {HIGH_CV_THRESHOLD}%. "
                    f"Worst: {worst[0]} with CV={worst[1]:.1f}%. "
                    f"This suggests inconsistent performance, possibly due to "
                    f"background processes, thermal throttling, or resource contention."
                ),
                "recommendation": (
                    "Ensure test machine is idle during benchmarking. "
                    "Check for thermal throttling, power management settings, "
                    "and competing workloads."
                ),
            })

        # Check for outliers
        total_outliers = sum(
            stats.get("outlier_count", 0) for stats in metrics.values()
        )
        if total_outliers > 0:
            findings.append({
                "category": "Outlier Detection",
                "severity": "low",
                "title": f"{total_outliers} outlier(s) detected on {label}",
                "detail": (
                    f"Found {total_outliers} statistical outliers across metrics. "
                    f"These may represent warm-up effects, transient interference, "
                    f"or genuine performance anomalies."
                ),
                "recommendation": (
                    "Review outlier runs for external factors. "
                    "Consider excluding warm-up runs from analysis."
                ),
            })

    return findings


def _infrastructure_findings(context: AnalysisContext) -> List[Dict[str, Any]]:
    """Generate findings from infrastructure differences."""
    findings = []

    machines = {}
    for result in context.results:
        m = result.machine
        if m.name not in machines:
            machines[m.name] = m

    if len(machines) < 2:
        return findings

    machine_list = list(machines.values())
    for i in range(1, len(machine_list)):
        m0 = machine_list[0]
        m1 = machine_list[i]

        diffs = []
        if m0.cpu_name != m1.cpu_name:
            diffs.append(f"CPU: {m0.cpu_name} vs {m1.cpu_name}")
        if m0.cpu_nr_of_physical_cores != m1.cpu_nr_of_physical_cores:
            diffs.append(
                f"Physical cores: {m0.cpu_nr_of_physical_cores} vs "
                f"{m1.cpu_nr_of_physical_cores}"
            )
        if m0.total_memory_mb != m1.total_memory_mb:
            diffs.append(
                f"Memory: {m0.total_memory_mb}MB vs {m1.total_memory_mb}MB"
            )
        if m0.hw_type != m1.hw_type:
            diffs.append(f"HW type: {m0.hw_type} vs {m1.hw_type}")

        if diffs:
            findings.append({
                "category": "Infrastructure Difference",
                "severity": "info",
                "title": f"Infrastructure differs: {m0.name} vs {m1.name}",
                "detail": "; ".join(diffs),
                "recommendation": (
                    "Account for hardware differences when interpreting "
                    "performance comparisons."
                ),
            })

    return findings


def _correlation_findings(comparison_rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate cross-category correlation findings."""
    findings = []

    by_source = defaultdict(dict)
    for row in comparison_rows:
        if not row.get("is_baseline") and row.get("pct_change") is not None:
            by_source[row["source_label"]][row["metric"]] = row["pct_change"]

    for label, metrics in by_source.items():
        # Check if algorithm improves but quill/memory regresses
        algo_metrics = {k: v for k, v in metrics.items() if "algorithm" in k}
        quill_metrics = {k: v for k, v in metrics.items() if "quill" in k}
        memory_metrics = {k: v for k, v in metrics.items() if "memory" in k}

        algo_improved = any(v < -IMPROVEMENT_THRESHOLD_PCT for v in algo_metrics.values())
        quill_regressed = any(v > REGRESSION_THRESHOLD_PCT for v in quill_metrics.values())
        memory_regressed = any(v > REGRESSION_THRESHOLD_PCT for v in memory_metrics.values())

        if algo_improved and (quill_regressed or memory_regressed):
            findings.append({
                "category": "Cross-Category Analysis",
                "severity": "medium",
                "title": f"Mixed results on {label}: algorithm gains offset by other regressions",
                "detail": (
                    "Algorithm test shows improvement, but "
                    f"{'Quill' if quill_regressed else ''}"
                    f"{' and ' if quill_regressed and memory_regressed else ''}"
                    f"{'Memory' if memory_regressed else ''} "
                    f"tests show regression. The algorithm improvement may not "
                    f"offset the regressions in real-world workloads."
                ),
                "recommendation": (
                    "Evaluate the relative importance of each test category "
                    "for your specific Quintiq workload profile."
                ),
            })

    return findings


def format_findings_text(findings: List[Dict[str, Any]]) -> str:
    """Format findings as readable text."""
    if not findings:
        return "No significant findings detected."

    lines = ["# QMeter Analysis Findings", ""]

    for i, f in enumerate(findings, 1):
        severity_icon = {
            "critical": "[CRITICAL]",
            "high": "[HIGH]",
            "medium": "[MEDIUM]",
            "low": "[LOW]",
            "info": "[INFO]",
        }.get(f["severity"], "[?]")

        lines.append(f"## {i}. {severity_icon} {f['title']}")
        lines.append(f"**Category:** {f['category']}")
        lines.append(f"**Detail:** {f['detail']}")
        lines.append(f"**Recommendation:** {f['recommendation']}")
        lines.append("")

    return "\n".join(lines)
