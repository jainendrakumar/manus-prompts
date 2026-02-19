# QMeter Analyzer Runbook

## Operator Playbook

This document provides step-by-step instructions for common operational scenarios.

## Prerequisites

- Python 3.9 or later
- QMeter XML export files (ZIP or standalone)
- Sufficient disk space for report generation

## Installation

```bash
# Clone the repository
git clone <repo-url>
cd qmeter-analyzer

# Install the package
pip install -e .

# Verify installation
qmeter-analyze --version
```

## Scenario 1: Compare Two VM Environments

**Goal**: Compare QMeter scores between on-premises and cloud VMs.

```bash
qmeter-analyze \
  --inputs onprem_results.zip azure_results.zip \
  --baseline first \
  --formats excel html \
  --outdir comparison_output
```

**Expected output**:
- `comparison_output/qmeter_report.xlsx` with 12 sheets
- `comparison_output/qmeter_report.html` with charts

**What to look for**:
1. Open the Excel report, go to `02_Score_Summary`
2. Check `pct_change` columns for regressions
3. Review `11_Findings_Text` for narrative analysis
4. Open HTML report for visual charts

## Scenario 2: Analyze Multi-Run Stability

**Goal**: Assess performance consistency across 20+ runs.

```bash
qmeter-analyze \
  --inputs multi_run_pack.zip \
  --formats excel html json \
  --outdir stability_output \
  --verbose
```

**What to look for**:
1. `09_Stability_Variance` sheet: Check CV (Coefficient of Variation)
   - CV < 5%: Excellent stability
   - CV 5-10%: Acceptable
   - CV > 10%: Investigation needed
2. `10_Outliers` sheet: Review any flagged runs
3. HTML report: Stability chart shows CV by metric

## Scenario 3: Custom Labels and Rules

**Goal**: Apply custom labels and metric rules.

1. Create `labels.yaml`:
```yaml
prod_server.zip: "Production Server"
staging_server.zip: "Staging Server"
```

2. Create `rules.yaml`:
```yaml
custom_throughput: higher_is_better
```

3. Run:
```bash
qmeter-analyze \
  --inputs *.zip \
  --label-map labels.yaml \
  --metric-rules rules.yaml \
  --formats excel html
```

## Scenario 4: Selective Category Analysis

**Goal**: Analyze only specific test categories.

```bash
# Only memory and algorithm tests
qmeter-analyze \
  --inputs results.zip \
  --include-category "Memory test" "Algorithm test" \
  --formats excel html
```

## Troubleshooting

### No results found
- Verify XML files are valid QMeter exports
- Check log output with `--verbose` flag
- Ensure ZIP files contain XML files (not nested ZIPs)

### Parsing warnings
- Check the HTML report appendix for parsing warnings
- Common issue: locale-dependent number formatting
- Use `--verbose` to see detailed parsing logs

### Large datasets
- For 100+ runs, expect ~30 seconds processing time
- JSON output may be large; use Excel/HTML for viewing
- Consider using `--exclude-category` to reduce scope

## Monitoring

### Log Levels
- `INFO`: Normal operation, summary statistics
- `WARNING`: Non-fatal parsing issues, ambiguous data
- `DEBUG`: Detailed parsing steps, adapter selection
- `ERROR`: Fatal parsing failures

### Health Checks
```bash
# Verify tool works with sample data
qmeter-analyze --inputs sample.xml --formats json --outdir /tmp/test
echo $?  # Should be 0
```

## Maintenance

### Adding New Adapters
See [DEV_GUIDE.md](DEV_GUIDE.md) for instructions on extending the adapter registry.

### Updating Metric Rules
Edit `examples/metric_rules.example.yaml` and distribute to operators.

### Version Updates
Check `qmeter-analyze --version` and compare with latest release.
