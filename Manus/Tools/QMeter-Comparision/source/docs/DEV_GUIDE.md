# QMeter Analyzer Developer Guide

## Architecture Overview

QMeter Analyzer follows a pipeline architecture:

```
Input (ZIP/XML) → Ingestion → Adapters → Normalization → Analytics → Writers → Output
```

### Core Modules

| Module | Responsibility |
|--------|---------------|
| `ingest.py` | ZIP extraction, file discovery, label derivation |
| `adapters/` | XML schema detection and parsing |
| `models.py` | Data classes for all entities |
| `normalize.py` | Flatten parsed data into tabular form |
| `analytics/` | Comparison, stability, findings |
| `writers/` | Excel, HTML, JSON output |
| `cli.py` | Command-line interface |
| `utils/numeric.py` | Locale-safe number parsing |

## Extending Adapters

### Creating a New Adapter

1. Create a new file in `qmeter_analyzer/adapters/`:

```python
# adapter_v3.py
from .base import BaseAdapter
from ..models import QMeterResult

class AdapterV3(BaseAdapter):
    def can_parse(self, filepath: str) -> bool:
        # Check if this adapter can handle the file
        # Return True/False based on XML structure
        ...

    def parse(self, filepath, source_zip=None, internal_path=""):
        # Parse the file and return QMeterResult
        ...
```

2. Register in `adapters/__init__.py`:

```python
from .adapter_v3 import AdapterV3
register_adapter("adapter_v3", AdapterV3)
```

3. The registry tries adapters in priority order: v1, v2, ..., fallback.

### Adapter Contract

- `can_parse()`: Must be fast (read only first few elements)
- `parse()`: Must return `QMeterResult`, `List[LogEntry]`, or `None`
- Must set `Provenance` with source_zip, internal_path, file_hash, adapter_used
- Must log warnings for ambiguous data

## Adding New Analytics

### Custom Comparison Metrics

1. Add metric to `analytics/compare.py`:

```python
DEFAULT_DIRECTIONALITY["new_metric"] = "lower_is_better"
```

2. Update `_compute_category_means()` to extract the new metric.

### Custom Findings

1. Add a new finding generator in `analytics/findings.py`:

```python
def _custom_findings(context, comparison_rows):
    findings = []
    # Your logic here
    findings.append({
        "category": "Custom",
        "severity": "medium",
        "title": "...",
        "detail": "...",
        "recommendation": "...",
    })
    return findings
```

2. Call it from `generate_findings()`.

## Adding New Report Formats

### Writer Contract

All writers follow this pattern:

```python
def write_FORMAT_report(outdir, filename, **data_kwargs) -> str:
    # Write the report
    # Return the file path
    ...
```

### Adding a New Writer

1. Create `writers/new_writer.py`
2. Register in `writers/__init__.py`
3. Add format choice to `cli.py` argparse
4. Call writer in `cli.py` main function

## Adding Charts

### HTML Charts (Chart.js)

Charts are embedded in the HTML report using Chart.js. To add a new chart:

1. Build chart data in `html_writer.py`:

```python
def _build_new_chart_data(data):
    return {
        "labels": [...],
        "datasets": [{"label": "...", "data": [...]}]
    }
```

2. Add a `<canvas>` element in the HTML template
3. Add Chart.js initialization in `_render_chart_scripts()`

## Testing

### Running Tests

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=qmeter_analyzer --cov-report=html

# Specific test file
pytest tests/test_numeric.py -v
```

### Writing Tests

- Place tests in `tests/` directory
- Use `pytest` fixtures for shared setup
- Test edge cases: empty data, None values, malformed XML
- Use temporary files for XML adapter tests

### Test Data

- Use `SAMPLE_V1_XML` and `SAMPLE_V2_XML` constants in tests
- For integration tests, use the sample data in `examples/`

## Code Style

- Type hints on all function signatures
- Docstrings on all public functions
- Logging instead of print statements
- `from __future__ import annotations` in all modules

## Release Process

1. Update version in `qmeter_analyzer/__init__.py` and `pyproject.toml`
2. Run full test suite
3. Create release artifacts:
   ```bash
   cd release/
   zip -r qmeter-analyzer-vX.Y.Z.zip ../qmeter_analyzer ../tests ../README.md ../pyproject.toml
   sha256sum *.zip > checksums.txt
   ```
4. Tag and push:
   ```bash
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```
5. Create GitHub Release with artifacts
