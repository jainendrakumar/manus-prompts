"""Normalization module: flatten QMeter results into tabular form."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from .models import AnalysisContext, QMeterResult

logger = logging.getLogger(__name__)

# Standard category names and their numbers
CATEGORY_MAP = {
    1: "Memory test",
    2: "Algorithm test",
    3: "Quill speed test",
    4: "Propagator test",
    5: "Database test",
}

# Thread count to score label mapping
THREAD_SCORE_MAP = {
    1: "Score1",
    4: "Score4",
    16: "Score16",
}


def normalize_results(context: AnalysisContext) -> List[Dict[str, Any]]:
    """Flatten all results into a list of normalized row dicts.

    Each row represents one run with all metrics flattened.
    """
    rows = []
    for result in context.results:
        for run in result.runs:
            row = _build_row(result, run)
            rows.append(row)
    return rows


def _build_row(result: QMeterResult, run) -> Dict[str, Any]:
    """Build a flat dictionary from a QMeterResult and RunRecord."""
    m = result.machine
    row: Dict[str, Any] = {
        # Provenance
        "source_label": result.source_label,
        "label": result.label,
        "source_zip": result.provenance.source_zip or "",
        "internal_path": result.provenance.internal_path,
        "file_hash": result.provenance.file_hash,
        "adapter": result.provenance.adapter_used,
        # Machine info
        "machine_name": m.name,
        "cpu_name": m.cpu_name,
        "cpu_clock_mhz": m.cpu_max_clock_speed,
        "cpu_logical_cores": m.cpu_nr_of_logical_cores,
        "cpu_physical_cores": m.cpu_nr_of_physical_cores,
        "cpu_processors": m.cpu_number_of_processors,
        "cpu_hyperthreaded": m.cpu_is_hyper_threaded,
        "cpu_l2_cache": m.cpu_l2_cache,
        "cpu_l3_cache": m.cpu_l3_cache,
        "total_memory_mb": m.total_memory_mb,
        "available_memory_mb": m.available_memory_mb,
        "computer_model": m.computer_model,
        "os": m.computer_os,
        "hw_type": m.hw_type,
        "qmeter_version": m.qmeter_version,
        "quintiq_version": m.quintiq_version,
        "test_date": m.current_date,
        # Run info
        "run_number": run.run_number,
        "score1": run.score1,
        "score4": run.score4,
        "score16": run.score16,
        "config_categories": run.config_categories,
        "config_lite_mode": run.config_lite_mode,
        "config_timeout": run.config_timeout,
    }

    # Flatten categories and groups
    for cat in run.categories:
        cat_prefix = _cat_prefix(cat.number, cat.name)
        row[f"{cat_prefix}_avg_runtime"] = cat.avg_runtime

        for grp in cat.groups:
            grp_prefix = f"{cat_prefix}_t{grp.nr_of_threads}"
            row[f"{grp_prefix}_group_score"] = grp.group_score
            row[f"{grp_prefix}_avg_runtime"] = grp.avg_runtime
            row[f"{grp_prefix}_std_dev"] = grp.std_dev_runtime
            row[f"{grp_prefix}_task_count"] = len(grp.tasks)

    return row


def _cat_prefix(number: int, name: str) -> str:
    """Create a column prefix from category number and name."""
    short = {
        "Memory test": "memory",
        "Algorithm test": "algorithm",
        "Quill speed test": "quill",
        "Propagator test": "propagator",
        "Database test": "database",
    }
    return f"cat{number}_{short.get(name, name.lower().replace(' ', '_'))}"


def build_infrastructure_table(context: AnalysisContext) -> List[Dict[str, Any]]:
    """Build infrastructure comparison table from unique machines."""
    seen = {}
    for result in context.results:
        m = result.machine
        key = m.name
        if key not in seen:
            seen[key] = {
                "machine_name": m.name,
                "cpu_name": m.cpu_name,
                "cpu_clock_mhz": m.cpu_max_clock_speed,
                "cpu_logical_cores": m.cpu_nr_of_logical_cores,
                "cpu_physical_cores": m.cpu_nr_of_physical_cores,
                "cpu_processors": m.cpu_number_of_processors,
                "cpu_hyperthreaded": m.cpu_is_hyper_threaded,
                "cpu_l2_cache_kb": m.cpu_l2_cache,
                "cpu_l3_cache_kb": m.cpu_l3_cache,
                "total_memory_mb": m.total_memory_mb,
                "available_memory_mb": m.available_memory_mb,
                "computer_model": m.computer_model,
                "os": m.computer_os,
                "hw_type": m.hw_type,
                "qmeter_version": m.qmeter_version,
                "quintiq_version": m.quintiq_version,
                "source_label": result.source_label,
            }
    return list(seen.values())


def build_run_inventory(context: AnalysisContext) -> List[Dict[str, Any]]:
    """Build run inventory table."""
    rows = []
    for i, result in enumerate(context.results):
        for run in result.runs:
            cat_names = []
            for cat in run.categories:
                cat_names.append(cat.name)
            rows.append({
                "index": i,
                "source_label": result.source_label,
                "label": result.label,
                "machine_name": result.machine.name,
                "run_number": run.run_number,
                "score1": run.score1,
                "score4": run.score4,
                "score16": run.score16,
                "categories_tested": ", ".join(cat_names),
                "source_zip": result.provenance.source_zip or "standalone",
                "internal_path": result.provenance.internal_path,
                "file_hash": result.provenance.file_hash[:12],
                "adapter": result.provenance.adapter_used,
                "test_date": result.machine.current_date,
            })
    return rows


def build_score_summary(context: AnalysisContext) -> List[Dict[str, Any]]:
    """Build score summary grouped by source."""
    from collections import defaultdict
    import statistics

    groups = defaultdict(list)
    for result in context.results:
        key = result.source_label
        for run in result.runs:
            groups[key].append({
                "score1": run.score1,
                "score4": run.score4,
                "score16": run.score16,
                "machine": result.machine.name,
            })

    rows = []
    for label, runs in groups.items():
        s1 = [r["score1"] for r in runs if r["score1"] is not None]
        s4 = [r["score4"] for r in runs if r["score4"] is not None]
        s16 = [r["score16"] for r in runs if r["score16"] is not None]

        row = {
            "source_label": label,
            "machine": runs[0]["machine"] if runs else "",
            "run_count": len(runs),
        }

        for name, vals in [("score1", s1), ("score4", s4), ("score16", s16)]:
            if vals:
                row[f"{name}_mean"] = statistics.mean(vals)
                row[f"{name}_median"] = statistics.median(vals)
                row[f"{name}_min"] = min(vals)
                row[f"{name}_max"] = max(vals)
                if len(vals) > 1:
                    row[f"{name}_stdev"] = statistics.stdev(vals)
                else:
                    row[f"{name}_stdev"] = 0.0
            else:
                for suffix in ("mean", "median", "min", "max", "stdev"):
                    row[f"{name}_{suffix}"] = None

        rows.append(row)
    return rows
