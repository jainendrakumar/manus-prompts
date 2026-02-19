# QMeter Analyzer

**Enterprise-grade DELMIA Quintiq QMeter performance analysis tool.**

QMeter Analyzer ingests QMeter benchmark XML reports (from ZIP archives or standalone files), performs multi-run statistical analysis, and produces comprehensive Excel, HTML, and JSON reports with directionality-aware comparisons, stability analytics, and bottleneck inference.

## Features

- **Multi-format ingestion**: ZIP archives with nested XML, standalone XML files, glob patterns
- **Adapter registry**: Automatically detects XML schema variants (Machine/Run, log entries, transactions)
- **Locale-safe parsing**: Handles comma/dot ambiguity in numeric values
- **Directionality-aware comparison**: Correctly interprets "lower is better" for durations and scores
- **Multi-run stability analysis**: Mean, median, stdev, CV, p90, p95, 95% CI, outlier detection
- **Bottleneck inference**: Generates narrative findings from data and infrastructure differences
- **Rich reporting**: Excel workbook (12 sheets), self-contained HTML with Chart.js, JSON

## Quick Start

### Installation

```bash
pip install -e .
```

### Basic Usage

```bash
# Analyze ZIP files and standalone XMLs
qmeter-analyze --inputs data/*.zip data/*.xml --formats excel html

# With all options
qmeter-analyze \
  --inputs run1.zip run2.zip report.xml \
  --baseline first \
  --label-map labels.yaml \
  --metric-rules rules.yaml \
  --formats excel html json \
  --outdir output \
  --verbose
```

### CLI Options

| Option | Description |
|--------|-------------|
| `--inputs`, `-i` | Input ZIP/XML files or glob patterns (required) |
| `--guide` | DOCX guide file(s) for category semantics |
| `--baseline` | Baseline selection: `first`, index, or label (default: `first`) |
| `--label-map` | YAML file mapping source filenames to labels |
| `--metric-rules` | YAML file with directionality/category overrides |
| `--include-category` | Include only specified categories |
| `--exclude-category` | Exclude specified categories |
| `--formats`, `-f` | Output formats: `excel`, `html`, `json` (default: `excel html`) |
| `--outdir`, `-o` | Output directory (default: `output`) |
| `--log-level` | Logging level: `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `--verbose`, `-v` | Enable verbose/debug output |

## Output Reports

### Excel Workbook (`qmeter_report.xlsx`)

| Sheet | Content |
|-------|---------|
| 00_Run_Inventory | All parsed runs with provenance |
| 01_Infrastructure | Machine hardware comparison |
| 02_Score_Summary | Score statistics by source |
| 03_Category_Summary | All category comparisons |
| 04_Memory_Test | Memory test details |
| 05_Algorithm_Test | Algorithm test details |
| 06_Quill_Speed_Test | Quill speed test details |
| 07_Propagator_Test | Propagator test details |
| 08_Database_Test | Database test details |
| 09_Stability_Variance | Multi-run stability stats |
| 10_Outliers | Detected outliers |
| 11_Findings_Text | Narrative findings |
| 12_Data_Dictionary | Metric definitions |

### HTML Report (`qmeter_report.html`)

Self-contained HTML with:
- Executive summary with key metrics
- Interactive Chart.js charts
- Score and category comparison tables
- Stability analysis with CV charts
- Findings and recommendations
- Data dictionary appendix

## QMeter Categories

| # | Category | What it measures |
|---|----------|-----------------|
| 1 | Memory test | Memory performance via WPBL data creation and propagation |
| 2 | Algorithm test | POA, CP, and MP optimization algorithms |
| 3 | Quill speed test | Quill logic speed (Hanoi Tower test) |
| 4 | Propagator test | Propagator behavior in medium transactions |
| 5 | Database test | Data storage performance (full/partial/memory) |

## Scoring Convention

- **Score1**: Performance with 1 dataset (single-threaded baseline)
- **Score4**: Performance with 4 datasets (moderate parallelism)
- **Score16**: Performance with 16 datasets (high parallelism)
- **All scores**: Lower is better (duration-based)
- **GroupScore**: AvgRuntime + StdDevRuntime (penalizes variance)

## Configuration

### Label Map (`labels.yaml`)

```yaml
QMeter-20Runs_20260217.zip: "On-Prem VMware (20 runs)"
Report_AzureHBv2_20260215.zip: "Azure HBv2 (20 runs)"
```

### Metric Rules (`metric_rules.yaml`)

```yaml
# Override directionality for custom metrics
custom_throughput: higher_is_better
custom_latency: lower_is_better
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=qmeter_analyzer --cov-report=html
```

## Project Structure

```
qmeter_analyzer/
├── __init__.py          # Package init
├── __main__.py          # python -m support
├── cli.py               # CLI entry point
├── models.py            # Data models
├── ingest.py            # ZIP/XML ingestion
├── normalize.py         # Data normalization
├── adapters/
│   ├── base.py          # Base adapter interface
│   ├── registry.py      # Adapter registry
│   ├── adapter_v1.py    # Machine/Run/Category schema
│   ├── adapter_v2.py    # Log entry schema
│   └── adapter_fallback.py
├── analytics/
│   ├── compare.py       # Comparison engine
│   ├── stability.py     # Stability analysis
│   └── findings.py      # Bottleneck inference
├── writers/
│   ├── excel_writer.py  # Excel workbook
│   ├── html_writer.py   # HTML report
│   └── json_writer.py   # JSON output
└── utils/
    └── numeric.py       # Locale-safe parsing
```

## License

MIT License - see [LICENSE](LICENSE) for details.
