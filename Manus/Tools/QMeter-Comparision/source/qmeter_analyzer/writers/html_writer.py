"""HTML report writer with embedded Chart.js charts."""
from __future__ import annotations

import html
import json
import logging
import os
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def write_html_report(
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
    warnings: List[str],
) -> str:
    """Write a self-contained HTML report.

    Returns the path to the written file.
    """
    os.makedirs(outdir, exist_ok=True)
    filepath = os.path.join(outdir, filename)

    # Build chart data
    score_chart_data = _build_score_chart_data(score_summary)
    category_chart_data = _build_category_chart_data(category_comparison)
    stability_chart_data = _build_stability_chart_data(stability_table)

    html_content = _render_html(
        run_inventory=run_inventory,
        infra_table=infra_table,
        score_summary=score_summary,
        score_comparison=score_comparison,
        category_comparison=category_comparison,
        stability_table=stability_table,
        outlier_table=outlier_table,
        findings=findings,
        warnings=warnings,
        score_chart_data=score_chart_data,
        category_chart_data=category_chart_data,
        stability_chart_data=stability_chart_data,
    )

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html_content)

    logger.info("HTML report written to %s", filepath)
    return filepath


def _build_score_chart_data(score_summary: List[Dict]) -> Dict:
    """Build Chart.js data for score comparison chart."""
    labels = [r.get("source_label", "") for r in score_summary]
    datasets = []

    colors = ["#2F5496", "#C00000", "#548235", "#BF8F00", "#7030A0"]

    for i, score_type in enumerate(["score1_mean", "score4_mean", "score16_mean"]):
        values = [r.get(score_type) for r in score_summary]
        datasets.append({
            "label": score_type.replace("_mean", "").upper(),
            "data": [v if v is not None else 0 for v in values],
            "backgroundColor": colors[i % len(colors)],
        })

    return {"labels": labels, "datasets": datasets}


def _build_category_chart_data(category_comparison: List[Dict]) -> Dict:
    """Build Chart.js data for category comparison."""
    # Group by metric, show baseline vs others
    from collections import defaultdict
    by_metric = defaultdict(list)
    for row in category_comparison:
        if "avg_runtime" in row.get("metric", "") and "t1_" not in row.get("metric", ""):
            by_metric[row["metric"]].append(row)

    labels = []
    baseline_data = []
    compare_data = defaultdict(list)

    for metric, rows in sorted(by_metric.items()):
        labels.append(metric.replace("_avg_runtime", "").replace("_", " ").title())
        for row in rows:
            if row.get("is_baseline"):
                baseline_data.append(row.get("baseline_value", 0))
            else:
                compare_data[row["source_label"]].append(row.get("current_value", 0))

    datasets = [{"label": "Baseline", "data": baseline_data, "backgroundColor": "#2F5496"}]
    colors = ["#C00000", "#548235", "#BF8F00", "#7030A0", "#00B0F0"]
    for i, (label, data) in enumerate(compare_data.items()):
        datasets.append({
            "label": label,
            "data": data,
            "backgroundColor": colors[i % len(colors)],
        })

    return {"labels": labels, "datasets": datasets}


def _build_stability_chart_data(stability_table: List[Dict]) -> Dict:
    """Build Chart.js data for stability (CV) chart."""
    from collections import defaultdict
    by_source = defaultdict(list)
    for row in stability_table:
        if "score" in row.get("metric", ""):
            by_source[row["source_label"]].append(row)

    labels = []
    datasets = []
    colors = ["#2F5496", "#C00000", "#548235"]

    for i, (source, rows) in enumerate(by_source.items()):
        metric_labels = [r["metric"] for r in rows]
        cv_values = [r.get("cv", 0) or 0 for r in rows]
        if not labels:
            labels = metric_labels
        datasets.append({
            "label": source,
            "data": cv_values,
            "backgroundColor": colors[i % len(colors)],
        })

    return {"labels": labels, "datasets": datasets}


def _render_html(**kwargs) -> str:
    """Render the complete HTML report."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>QMeter Performance Analysis Report</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
:root {{
    --primary: #2F5496;
    --danger: #C00000;
    --success: #548235;
    --warning: #BF8F00;
    --bg: #f8f9fa;
    --card-bg: #ffffff;
}}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: var(--bg); color: #333; line-height: 1.6; }}
.container {{ max-width: 1400px; margin: 0 auto; padding: 20px; }}
header {{ background: var(--primary); color: white; padding: 30px; margin-bottom: 30px; border-radius: 8px; }}
header h1 {{ font-size: 2em; margin-bottom: 5px; }}
header p {{ opacity: 0.9; }}
.card {{ background: var(--card-bg); border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); padding: 24px; margin-bottom: 24px; }}
.card h2 {{ color: var(--primary); margin-bottom: 16px; padding-bottom: 8px; border-bottom: 2px solid #e0e0e0; }}
.card h3 {{ color: #555; margin: 16px 0 8px; }}
table {{ width: 100%; border-collapse: collapse; margin: 12px 0; font-size: 0.9em; }}
th {{ background: var(--primary); color: white; padding: 10px 12px; text-align: left; position: sticky; top: 0; }}
td {{ padding: 8px 12px; border-bottom: 1px solid #e0e0e0; }}
tr:hover {{ background: #f0f4f8; }}
.regression {{ background: #FFC7CE; color: #9C0006; font-weight: bold; }}
.improvement {{ background: #C6EFCE; color: #006100; font-weight: bold; }}
.unchanged {{ background: #FFEB9C; color: #9C6500; }}
.badge {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.8em; font-weight: bold; }}
.badge-critical {{ background: #C00000; color: white; }}
.badge-high {{ background: #FF6B6B; color: white; }}
.badge-medium {{ background: #FFD93D; color: #333; }}
.badge-low {{ background: #6BCB77; color: white; }}
.badge-info {{ background: #4D96FF; color: white; }}
.chart-container {{ position: relative; height: 400px; margin: 20px 0; }}
.finding {{ border-left: 4px solid var(--primary); padding: 12px 16px; margin: 12px 0; background: #f8f9fa; border-radius: 0 4px 4px 0; }}
.finding.critical {{ border-color: #C00000; }}
.finding.high {{ border-color: #FF6B6B; }}
.finding.medium {{ border-color: #FFD93D; }}
.finding.low {{ border-color: #6BCB77; }}
.nav {{ position: sticky; top: 0; background: white; z-index: 100; padding: 10px 0; border-bottom: 1px solid #ddd; margin-bottom: 20px; }}
.nav a {{ color: var(--primary); text-decoration: none; margin-right: 16px; font-weight: 500; font-size: 0.9em; }}
.nav a:hover {{ text-decoration: underline; }}
.table-wrapper {{ overflow-x: auto; }}
.warning-list {{ background: #FFF3CD; border: 1px solid #FFEEBA; padding: 12px; border-radius: 4px; margin: 12px 0; }}
.exec-summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin: 16px 0; }}
.stat-card {{ background: #f0f4f8; padding: 16px; border-radius: 8px; text-align: center; }}
.stat-card .value {{ font-size: 2em; font-weight: bold; color: var(--primary); }}
.stat-card .label {{ font-size: 0.85em; color: #666; margin-top: 4px; }}
</style>
</head>
<body>
<div class="container">
<header>
<h1>QMeter Performance Analysis Report</h1>
<p>DELMIA Quintiq QMeter Benchmark Comparison &amp; Stability Analysis</p>
</header>

<div class="nav">
<a href="#exec-summary">Executive Summary</a>
<a href="#scores">Scores</a>
<a href="#categories">Categories</a>
<a href="#stability">Stability</a>
<a href="#findings">Findings</a>
<a href="#infrastructure">Infrastructure</a>
<a href="#inventory">Inventory</a>
<a href="#appendix">Appendix</a>
</div>

{_render_exec_summary(kwargs)}
{_render_score_section(kwargs)}
{_render_category_section(kwargs)}
{_render_stability_section(kwargs)}
{_render_findings_section(kwargs)}
{_render_infrastructure_section(kwargs)}
{_render_inventory_section(kwargs)}
{_render_appendix(kwargs)}

</div>

<script>
{_render_chart_scripts(kwargs)}
</script>
</body>
</html>"""


def _render_exec_summary(ctx: Dict) -> str:
    """Render executive summary section."""
    inventory = ctx.get("run_inventory", [])
    findings = ctx.get("findings", [])
    score_summary = ctx.get("score_summary", [])

    total_runs = len(inventory)
    total_sources = len(set(r.get("source_label", "") for r in inventory))
    total_machines = len(set(r.get("machine_name", "") for r in inventory))
    critical_findings = len([f for f in findings if f.get("severity") in ("critical", "high")])

    return f"""
<div class="card" id="exec-summary">
<h2>Executive Summary</h2>
<div class="exec-summary">
<div class="stat-card"><div class="value">{total_runs}</div><div class="label">Total Runs Analyzed</div></div>
<div class="stat-card"><div class="value">{total_sources}</div><div class="label">Data Sources</div></div>
<div class="stat-card"><div class="value">{total_machines}</div><div class="label">Unique Machines</div></div>
<div class="stat-card"><div class="value" style="color: {'#C00000' if critical_findings > 0 else '#548235'}">{critical_findings}</div><div class="label">Critical/High Findings</div></div>
</div>
</div>"""


def _render_score_section(ctx: Dict) -> str:
    """Render score comparison section."""
    score_summary = ctx.get("score_summary", [])
    score_comparison = ctx.get("score_comparison", [])

    table_html = _dict_list_to_table(score_summary)
    comp_table = _dict_list_to_table(score_comparison, highlight_col="assessment")

    return f"""
<div class="card" id="scores">
<h2>Score Summary</h2>
<div class="table-wrapper">{table_html}</div>
<h3>Score Comparison vs Baseline</h3>
<div class="table-wrapper">{comp_table}</div>
<h3>Score Distribution by Source</h3>
<div class="chart-container"><canvas id="scoreChart"></canvas></div>
</div>"""


def _render_category_section(ctx: Dict) -> str:
    """Render category comparison section."""
    category_comparison = ctx.get("category_comparison", [])
    table_html = _dict_list_to_table(category_comparison, highlight_col="assessment")

    return f"""
<div class="card" id="categories">
<h2>Category Comparison</h2>
<div class="table-wrapper">{table_html}</div>
<h3>Category Average Runtime Comparison</h3>
<div class="chart-container"><canvas id="categoryChart"></canvas></div>
</div>"""


def _render_stability_section(ctx: Dict) -> str:
    """Render stability analysis section."""
    stability_table = ctx.get("stability_table", [])
    outlier_table = ctx.get("outlier_table", [])

    stab_html = _dict_list_to_table(stability_table)
    outlier_html = _dict_list_to_table(outlier_table)

    return f"""
<div class="card" id="stability">
<h2>Stability &amp; Variance Analysis</h2>
<div class="table-wrapper">{stab_html}</div>
<h3>Coefficient of Variation by Metric</h3>
<div class="chart-container"><canvas id="stabilityChart"></canvas></div>
<h3>Outliers</h3>
<div class="table-wrapper">{outlier_html if outlier_table else '<p>No outliers detected.</p>'}</div>
</div>"""


def _render_findings_section(ctx: Dict) -> str:
    """Render findings section."""
    findings = ctx.get("findings", [])
    if not findings:
        return '<div class="card" id="findings"><h2>Findings &amp; Recommendations</h2><p>No significant findings.</p></div>'

    items = []
    for f in findings:
        sev = f.get("severity", "info")
        items.append(f"""
<div class="finding {sev}">
<span class="badge badge-{sev}">{sev.upper()}</span>
<strong>{html.escape(f.get('title', ''))}</strong>
<p>{html.escape(f.get('detail', ''))}</p>
<p><em>Recommendation: {html.escape(f.get('recommendation', ''))}</em></p>
</div>""")

    return f"""
<div class="card" id="findings">
<h2>Findings &amp; Recommendations</h2>
{''.join(items)}
</div>"""


def _render_infrastructure_section(ctx: Dict) -> str:
    """Render infrastructure comparison."""
    infra_table = ctx.get("infra_table", [])
    table_html = _dict_list_to_table(infra_table)

    return f"""
<div class="card" id="infrastructure">
<h2>Infrastructure Comparison</h2>
<div class="table-wrapper">{table_html}</div>
</div>"""


def _render_inventory_section(ctx: Dict) -> str:
    """Render run inventory."""
    inventory = ctx.get("run_inventory", [])
    table_html = _dict_list_to_table(inventory)

    return f"""
<div class="card" id="inventory">
<h2>Run Inventory</h2>
<div class="table-wrapper">{table_html}</div>
</div>"""


def _render_appendix(ctx: Dict) -> str:
    """Render appendix with warnings and data dictionary."""
    warnings = ctx.get("warnings", [])

    warning_html = ""
    if warnings:
        items = "".join(f"<li>{html.escape(w)}</li>" for w in warnings)
        warning_html = f'<div class="warning-list"><h3>Parsing Warnings</h3><ul>{items}</ul></div>'

    return f"""
<div class="card" id="appendix">
<h2>Appendix</h2>
{warning_html}
<h3>Data Dictionary</h3>
<table>
<tr><th>Metric</th><th>Description</th><th>Directionality</th></tr>
<tr><td>Score1/4/16</td><td>Overall QMeter benchmark scores (1/4/16 datasets)</td><td>Lower is better</td></tr>
<tr><td>avg_runtime</td><td>Average task runtime in milliseconds</td><td>Lower is better</td></tr>
<tr><td>group_score</td><td>AvgRuntime + StdDev (penalizes variance)</td><td>Lower is better</td></tr>
<tr><td>CV</td><td>Coefficient of Variation (std/mean * 100)</td><td>Lower is more stable</td></tr>
<tr><td>pct_change</td><td>Percentage change vs baseline</td><td>Positive = worse for durations</td></tr>
</table>
</div>"""


def _render_chart_scripts(ctx: Dict) -> str:
    """Render Chart.js initialization scripts."""
    score_data = json.dumps(ctx.get("score_chart_data", {}))
    category_data = json.dumps(ctx.get("category_chart_data", {}))
    stability_data = json.dumps(ctx.get("stability_chart_data", {}))

    return f"""
// Score Chart
try {{
const scoreCtx = document.getElementById('scoreChart');
if (scoreCtx) {{
    new Chart(scoreCtx, {{
        type: 'bar',
        data: {score_data},
        options: {{
            responsive: true,
            maintainAspectRatio: false,
            plugins: {{ title: {{ display: true, text: 'Score Comparison by Source' }} }},
            scales: {{ y: {{ beginAtZero: true, title: {{ display: true, text: 'Score (lower is better)' }} }} }}
        }}
    }});
}}
}} catch(e) {{ console.error('Score chart error:', e); }}

// Category Chart
try {{
const catCtx = document.getElementById('categoryChart');
if (catCtx) {{
    new Chart(catCtx, {{
        type: 'bar',
        data: {category_data},
        options: {{
            responsive: true,
            maintainAspectRatio: false,
            plugins: {{ title: {{ display: true, text: 'Category Average Runtime Comparison' }} }},
            scales: {{ y: {{ beginAtZero: true, title: {{ display: true, text: 'Avg Runtime (ms, lower is better)' }} }} }}
        }}
    }});
}}
}} catch(e) {{ console.error('Category chart error:', e); }}

// Stability Chart
try {{
const stabCtx = document.getElementById('stabilityChart');
if (stabCtx) {{
    new Chart(stabCtx, {{
        type: 'bar',
        data: {stability_data},
        options: {{
            responsive: true,
            maintainAspectRatio: false,
            plugins: {{ title: {{ display: true, text: 'Coefficient of Variation (%) by Metric' }} }},
            scales: {{ y: {{ beginAtZero: true, title: {{ display: true, text: 'CV (%, lower is more stable)' }} }} }}
        }}
    }});
}}
}} catch(e) {{ console.error('Stability chart error:', e); }}
"""


def _dict_list_to_table(rows: List[Dict], highlight_col: str = "") -> str:
    """Convert a list of dicts to an HTML table."""
    if not rows:
        return "<p>No data available.</p>"

    headers = list(rows[0].keys())
    header_html = "".join(f"<th>{html.escape(str(h))}</th>" for h in headers)

    body_rows = []
    for row in rows:
        cells = []
        for h in headers:
            val = row.get(h, "")
            cell_class = ""
            if h == highlight_col:
                if val == "regression":
                    cell_class = ' class="regression"'
                elif val == "improvement":
                    cell_class = ' class="improvement"'
                elif val == "unchanged":
                    cell_class = ' class="unchanged"'

            if isinstance(val, float):
                display = f"{val:.2f}"
            elif val is None:
                display = "N/A"
            else:
                display = html.escape(str(val))
            cells.append(f"<td{cell_class}>{display}</td>")
        body_rows.append(f"<tr>{''.join(cells)}</tr>")

    return f"<table><thead><tr>{header_html}</tr></thead><tbody>{''.join(body_rows)}</tbody></table>"
