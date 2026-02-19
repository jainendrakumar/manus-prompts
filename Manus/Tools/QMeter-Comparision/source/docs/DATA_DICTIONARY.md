# QMeter Analyzer Data Dictionary

## Scores

| Metric | Description | Unit | Directionality |
|--------|-------------|------|----------------|
| Score1 | Overall QMeter benchmark score with 1 dataset (single-threaded) | milliseconds | Lower is better |
| Score4 | Overall QMeter benchmark score with 4 datasets | milliseconds | Lower is better |
| Score16 | Overall QMeter benchmark score with 16 datasets | milliseconds | Lower is better |

## Category Metrics

| Metric | Description | Unit | Directionality |
|--------|-------------|------|----------------|
| avg_runtime | Average runtime across all tasks in a category or group | milliseconds | Lower is better |
| group_score | AvgRuntime + StdDevRuntime; penalizes variance in task execution | milliseconds | Lower is better |
| std_dev_runtime | Standard deviation of task runtimes within a group | milliseconds | Lower is better |

## Test Categories

| Number | Name | Description |
|--------|------|-------------|
| 1 | Memory test | Tests memory performance using Workforce Planner Benchmarking Library (WPBL). Creates data volumes and propagates to measure memory bandwidth and latency. |
| 2 | Algorithm test | Tests three optimization algorithms: Path Optimization Algorithm (POA), Constraint Programming (CP), and Mathematical Programming (MP). |
| 3 | Quill speed test | Tests Quill logic execution speed using the Hanoi Tower problem. Measures CPU IPC (instructions per cycle) performance. |
| 4 | Propagator test | Similar to memory test but specifically measures propagator behavior in medium-sized transactions. |
| 5 | Database test | Tests data storage performance across storage options: full storage, partial storage, and memory-only storage. |

## Thread Groups

| NrOfThreads | Corresponding Score | Description |
|-------------|-------------------|-------------|
| 1 | Score1 | Single-threaded baseline performance |
| 4 | Score4 | Moderate parallelism |
| 16 | Score16 | High parallelism, stress test |

## Stability Metrics

| Metric | Description | Unit | Interpretation |
|--------|-------------|------|----------------|
| count | Number of runs analyzed | count | More runs = more reliable statistics |
| mean | Arithmetic mean of values | same as source | Central tendency |
| median | Middle value when sorted | same as source | Robust to outliers |
| stdev | Standard deviation | same as source | Spread of values |
| min | Minimum observed value | same as source | Best case |
| max | Maximum observed value | same as source | Worst case |
| p90 | 90th percentile | same as source | 90% of runs are at or below this |
| p95 | 95th percentile | same as source | 95% of runs are at or below this |
| cv | Coefficient of Variation (stdev/mean * 100) | percent | < 5% excellent, 5-10% acceptable, > 10% investigate |
| ci_95_lower | Lower bound of 95% confidence interval | same as source | True mean likely above this |
| ci_95_upper | Upper bound of 95% confidence interval | same as source | True mean likely below this |

## Comparison Metrics

| Metric | Description | Unit | Interpretation |
|--------|-------------|------|----------------|
| diff | Absolute difference (current - baseline) | same as source | Positive = increase |
| pct_change | Percentage change vs baseline | percent | For durations: positive = worse |
| assessment | Qualitative assessment | text | regression / improvement / unchanged |

## Machine/Infrastructure Fields

| Field | Description |
|-------|-------------|
| machine_name | Hostname of the test machine |
| cpu_name | CPU model name |
| cpu_clock_mhz | Maximum CPU clock speed in MHz |
| cpu_logical_cores | Number of logical CPU cores |
| cpu_physical_cores | Number of physical CPU cores |
| cpu_processors | Number of CPU sockets/processors |
| cpu_hyperthreaded | Whether hyper-threading is enabled |
| cpu_l2_cache | L2 cache size in KB |
| cpu_l3_cache | L3 cache size in KB |
| total_memory_mb | Total system memory in MB |
| available_memory_mb | Available memory at test time in MB |
| computer_model | Computer/VM model identifier |
| os | Operating system name and edition |
| hw_type | Hardware type (Physical, Cloud, Unknown) |
| qmeter_version | QMeter tool version |
| quintiq_version | Quintiq platform version |

## Provenance Fields

| Field | Description |
|-------|-------------|
| source_zip | Name of the ZIP archive containing this file |
| internal_path | Path within the ZIP archive |
| file_hash | SHA-256 hash of the source XML file (first 12 chars shown) |
| adapter | Name of the adapter used to parse this file |
| source_label | Human-readable label derived from filename |
