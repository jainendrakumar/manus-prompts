"""JSON output writer for QMeter analysis."""
from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def write_json_report(
    outdir: str,
    filename: str,
    run_inventory: List[Dict],
    infra_table: List[Dict],
    score_summary: List[Dict],
    score_comparison: List[Dict],
    category_comparison: List[Dict],
    stability_table: List[Dict],
    outlier_table: List[Dict],
    findings: List[Dict],
    normalized_rows: List[Dict],
    warnings: List[str],
) -> str:
    """Write analysis results as JSON.

    Returns the path to the written file.
    """
    os.makedirs(outdir, exist_ok=True)
    filepath = os.path.join(outdir, filename)

    report = {
        "metadata": {
            "tool": "qmeter-analyzer",
            "version": "1.0.0",
        },
        "run_inventory": run_inventory,
        "infrastructure": infra_table,
        "score_summary": score_summary,
        "score_comparison": score_comparison,
        "category_comparison": category_comparison,
        "stability": stability_table,
        "outliers": outlier_table,
        "findings": findings,
        "normalized_data": normalized_rows,
        "warnings": warnings,
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)

    logger.info("JSON report written to %s", filepath)
    return filepath
