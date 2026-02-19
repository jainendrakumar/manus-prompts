"""CLI entry point for QMeter Analyzer."""
from __future__ import annotations

import argparse
import logging
import os
import sys
from typing import Dict, List, Optional

import yaml

from .ingest import ingest_inputs
from .normalize import (
    build_infrastructure_table,
    build_run_inventory,
    build_score_summary,
    normalize_results,
)
from .analytics.compare import compare_category_scores, compare_scores_summary
from .analytics.stability import (
    analyze_stability,
    build_outlier_table,
    build_stability_table,
)
from .analytics.findings import generate_findings, format_findings_text
from .writers.excel_writer import write_excel_report
from .writers.html_writer import write_html_report
from .writers.json_writer import write_json_report

logger = logging.getLogger("qmeter_analyzer")

__version__ = "1.0.0"


def main(argv: Optional[List[str]] = None) -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="qmeter-analyze",
        description="QMeter Performance Analyzer - Analyze DELMIA Quintiq QMeter benchmark results",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  qmeter-analyze --inputs data/*.zip data/*.xml --formats excel html
  qmeter-analyze --inputs run1.zip run2.zip --baseline first --formats excel html json
  qmeter-analyze --inputs results/ --label-map labels.yaml --metric-rules rules.yaml
        """,
    )

    parser.add_argument(
        "--inputs", "-i",
        nargs="+",
        required=True,
        help="Input ZIP/XML files or glob patterns",
    )
    parser.add_argument(
        "--guide",
        nargs="*",
        help="DOCX guide file(s) for category semantics (optional)",
    )
    parser.add_argument(
        "--baseline",
        default="first",
        help="Baseline selection: 'first', index number, or source label (default: first)",
    )
    parser.add_argument(
        "--label-map",
        help="YAML file mapping source filenames to labels/tags",
    )
    parser.add_argument(
        "--metric-rules",
        help="YAML file with metric directionality/category overrides",
    )
    parser.add_argument(
        "--include-category",
        nargs="*",
        help="Include only these categories (by name or number)",
    )
    parser.add_argument(
        "--exclude-category",
        nargs="*",
        help="Exclude these categories (by name or number)",
    )
    parser.add_argument(
        "--formats", "-f",
        nargs="+",
        default=["excel", "html"],
        choices=["excel", "html", "json"],
        help="Output formats (default: excel html)",
    )
    parser.add_argument(
        "--outdir", "-o",
        default="output",
        help="Output directory (default: output)",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: INFO)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output (same as --log-level DEBUG)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    args = parser.parse_args(argv)

    # Configure logging
    log_level = "DEBUG" if args.verbose else args.log_level
    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logger.info("QMeter Analyzer v%s starting", __version__)

    # Load label map
    label_map = {}
    if args.label_map:
        try:
            with open(args.label_map) as f:
                label_map = yaml.safe_load(f) or {}
            logger.info("Loaded label map with %d entries", len(label_map))
        except Exception as e:
            logger.error("Failed to load label map: %s", e)

    # Load metric rules
    metric_rules = {}
    if args.metric_rules:
        try:
            with open(args.metric_rules) as f:
                metric_rules = yaml.safe_load(f) or {}
            logger.info("Loaded metric rules with %d entries", len(metric_rules))
        except Exception as e:
            logger.error("Failed to load metric rules: %s", e)

    # Determine baseline index
    baseline_idx = 0
    if args.baseline != "first":
        try:
            baseline_idx = int(args.baseline)
        except ValueError:
            # Will try to match by label later
            baseline_idx = 0

    # Ingest
    logger.info("Ingesting %d input path(s)...", len(args.inputs))
    context = ingest_inputs(args.inputs, label_map=label_map)
    context.metric_rules = metric_rules

    if not context.results:
        logger.error("No valid QMeter results found in inputs!")
        return 1

    logger.info("Parsed %d result files", len(context.results))

    # Resolve baseline by label if needed
    if args.baseline != "first" and not args.baseline.isdigit():
        for i, r in enumerate(context.results):
            if args.baseline.lower() in r.source_label.lower():
                baseline_idx = i
                break

    context.baseline_index = baseline_idx

    # Normalize
    logger.info("Normalizing results...")
    normalized_rows = normalize_results(context)
    run_inventory = build_run_inventory(context)
    infra_table = build_infrastructure_table(context)
    score_summary = build_score_summary(context)

    # Analytics
    logger.info("Running analytics...")
    category_comparison = compare_category_scores(
        context, baseline_idx=baseline_idx, metric_rules=metric_rules
    )
    score_comparison = compare_scores_summary(
        context, baseline_idx=baseline_idx, metric_rules=metric_rules
    )
    stability_report = analyze_stability(context)
    stability_table = build_stability_table(stability_report)
    outlier_table = build_outlier_table(stability_report)

    # Findings
    logger.info("Generating findings...")
    findings = generate_findings(
        context, category_comparison, stability_report, score_comparison
    )

    all_warnings = context.warnings[:]
    for r in context.results:
        all_warnings.extend(r.warnings)

    # Write outputs
    os.makedirs(args.outdir, exist_ok=True)
    output_files = []

    if "excel" in args.formats:
        logger.info("Writing Excel report...")
        path = write_excel_report(
            args.outdir, "qmeter_report.xlsx",
            run_inventory=run_inventory,
            infra_table=infra_table,
            score_summary=score_summary,
            category_comparison=category_comparison,
            stability_table=stability_table,
            outlier_table=outlier_table,
            findings=findings,
            normalized_rows=normalized_rows,
        )
        output_files.append(path)

    if "html" in args.formats:
        logger.info("Writing HTML report...")
        path = write_html_report(
            args.outdir, "qmeter_report.html",
            run_inventory=run_inventory,
            infra_table=infra_table,
            score_summary=score_summary,
            score_comparison=score_comparison,
            category_comparison=category_comparison,
            stability_table=stability_table,
            outlier_table=outlier_table,
            findings=findings,
            warnings=all_warnings,
        )
        output_files.append(path)

    if "json" in args.formats:
        logger.info("Writing JSON report...")
        path = write_json_report(
            args.outdir, "qmeter_report.json",
            run_inventory=run_inventory,
            infra_table=infra_table,
            score_summary=score_summary,
            score_comparison=score_comparison,
            category_comparison=category_comparison,
            stability_table=stability_table,
            outlier_table=outlier_table,
            findings=findings,
            normalized_rows=normalized_rows,
            warnings=all_warnings,
        )
        output_files.append(path)

    # Summary
    logger.info("=" * 60)
    logger.info("Analysis complete!")
    logger.info("Results: %d runs from %d sources",
                len(context.results),
                len(set(r.source_label for r in context.results)))
    logger.info("Findings: %d total (%d critical/high)",
                len(findings),
                len([f for f in findings if f["severity"] in ("critical", "high")]))
    logger.info("Output files:")
    for f in output_files:
        logger.info("  %s", f)
    if all_warnings:
        logger.info("Warnings: %d (see report appendix)", len(all_warnings))
    logger.info("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
