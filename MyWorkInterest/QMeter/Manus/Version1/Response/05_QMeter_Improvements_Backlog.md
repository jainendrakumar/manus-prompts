# QMeter: Prioritized Improvements Backlog

---

This document outlines a prioritized backlog of actionable engineering recommendations to enhance the accuracy, reproducibility, diagnostic value, and robustness of the QMeter Performance Evaluation Suite.

## P0: Critical Improvements (Measurement Rigor)

---

### P0.1: Implement Warmup and Repetition

- **Current Behavior**: Benchmarks are executed only once, immediately, without a warmup phase. This makes the results susceptible to noise from JIT compilation, cache misses, and other system startup effects.
- **Evidence Pointer**: `QMeter/_Main/BL/Type_BenchmarkDataset/Method_Cat1_SmallTransaction.qbl:10` - The precision counter `start := OS::PrecisionCounter();` is called at the very beginning of the method.
- **Proposed Change**:
    - **Design**: Introduce two new configuration parameters in the `Type_Company` object: `WarmupRuns` (default: 2) and `MeasurementRuns` (default: 5).
    - **Pseudo-Code**:
        ```quill
        // In Job_RunBenchmarkJob
        // ... after resolving reflection method

        // Warmup Phase
        for (i := 1; i <= this.Company().WarmupRuns(); i++)
        {
          reflection.Execute();
        }

        // Measurement Phase
        durations := construct(Reals);
        for (i := 1; i <= this.Company().MeasurementRuns(); i++)
        {
          start := OS::PrecisionCounter();
          reflection.Execute();
          end := OS::PrecisionCounter();
          durations.Add( (end - start) / OS::PrecisionCounterFrequency() );
        }

        // Calculate and record statistics (avg, min, max, stddev)
        avg_duration := durations.Average();
        // ... record avg_duration instead of single run
        ```
- **Expected Impact**:
    - **Reproducibility**: Significantly improved. Reduces variance between runs.
    - **Accuracy**: Increased. Eliminates cold-start penalties, providing a more stable measurement of peak performance.

---

### P0.2: Isolate and Report Garbage Collection (GC) Overhead

- **Current Behavior**: The total measured runtime includes time spent in Garbage Collection pauses, which can be highly variable and obscure the true performance of the benchmarked code.
- **Evidence Pointer**: `QMeter/_Main/BL/Type_BenchmarkDataset/Method_RecordBenchmarkExecutionInfo.qbl:24` - The duration is calculated as a simple difference between end and start counters, with no awareness of GC activity.
- **Proposed Change**:
    - **Design**: Use Quintiq's built-in profiler or monitoring tools to capture GC statistics before and after each measurement run.
    - **Pseudo-Code**:
        ```quill
        // In Job_RunBenchmarkJob, during measurement

        gc_time_before := System::GC_TotalPauseDuration();

        start := OS::PrecisionCounter();
        reflection.Execute();
        end := OS::PrecisionCounter();

        gc_time_after := System::GC_TotalPauseDuration();

        total_duration := (end - start) / OS::PrecisionCounterFrequency();
        gc_duration_during_run := gc_time_after - gc_time_before;
        
        // The actual benchmark runtime, excluding GC pauses
        net_duration := total_duration - gc_duration_during_run;

        // Record both total_duration and net_duration
        ```
- **Expected Impact**:
    - **Diagnostic Value**: High. Allows engineers to distinguish between code performance and memory management pressure.
    - **Accuracy**: High. Provides a much cleaner signal of the benchmark's performance.

---

### P0.3: Introduce CPU Affinity and NUMA Awareness

- **Current Behavior**: Benchmark threads are scheduled by the OS without specific CPU core affinity. On multi-socket (NUMA) systems, this can lead to performance degradation if memory and CPU are on different nodes.
- **Evidence Pointer**: The project contains no calls to `OS::SetThreadAffinity()` or similar process/thread pinning functions.
- **Proposed Change**:
    - **Design**: Add a configuration option `CPUAffinity` (`None`, `SingleCore`, `NUMANode`). When running concurrent datasets, pin threads to specific cores.
    - **Pseudo-Code**:
        ```quill
        // In Company.DelegateBenchmarkJob

        if (this.CPUAffinity() = 'SingleCore')
        {
          // Pin each job to a specific core, e.g., core 'thread'
          job.CPUAffinity( [String]thread ); 
        }
        else if (this.CPUAffinity() = 'NUMANode')
        {
          // Logic to determine NUMA topology and distribute threads
          numa_node := thread % NumberOfNUMANodes;
          job.CPUAffinityForNUMANode( numa_node );
        }
        
        job.Start();
        ```
- **Expected Impact**:
    - **Reproducibility**: High. Eliminates performance variance caused by thread migration between cores/nodes.
    - **Diagnostic Value**: High. Allows for testing specific NUMA configurations and identifying cross-node latency issues.

## P1: High-Priority Improvements (Scoring & Extensibility)

---

### P1.1: Externalize and Document Scoring Coefficients

- **Current Behavior**: The `Gold_Score` and `Gold_AvgRuntime` values used for normalization are internal attributes of the `Type_Company` object, with no clear documentation on their origin or how they should be calibrated.
- **Evidence Pointer**: `QMeter/_Main/BL/Type_BenchmarkCategory/Method_GetScore.qbl:10-11` - The formula directly references `this.Company().Gold_Score()` and `this.Gold_AvgRuntime()`.
- **Proposed Change**:
    - **Design**: Create a `Scoring.properties` file or a dedicated `Type_ScoringCoefficients` object to store the gold standard values for each benchmark category. This file should be version-controlled and include comments explaining each value.
    - **Pseudo-Code**:
        ```quill
        // In Method_GetScore

        // Load coefficients from an external source
        gold_runtime := ScoringCoefficients::GetGoldRuntime( this.Category() );
        gold_score := ScoringCoefficients::GetGoldScore( this.Category() );

        return guard( gold_score * ( gold_runtime / this.GetAverageRuntime(concurrent_datasets)), 0);
        ```
- **Expected Impact**:
    - **Transparency**: High. Makes the scoring logic clear and auditable.
    - **Maintainability**: High. Allows for easy updates to the baseline as hardware and software evolve, without changing code.

---

### P1.2: Implement a Plugin Architecture for New Benchmarks

- **Current Behavior**: Adding a new benchmark category requires modifying the `Job_RunBenchmarkJob` to recognize a new `CatX_Entry` method, and potentially adding new UI elements.
- **Evidence Pointer**: `QMeter/_Main/BL/Dataset_BenchmarkDataset/Job_RunBenchmarkJob.qbl:19` - The method name is hardcoded as `method_name := 'Cat' + ... + '_Entry'`. 
- **Proposed Change**:
    - **Design**: Define an abstract base type `Type_BenchmarkPlugin` with methods like `GetName()`, `GetDescription()`, and `Execute()`. New benchmarks would be implemented by extending this type. The main orchestrator would discover and run all registered plugins.
    - **Pseudo-Code**:
        ```quill
        // In RunBenchmark orchestrator

        // Discover all subtypes of Type_BenchmarkPlugin
        plugins := select( Model::SubTypes(Type_BenchmarkPlugin), Elements, p, true );

        traverse (plugins, Elements, plugin)
        {
          // For each discovered plugin, create a job to run it
          job := BenchmarkPluginRunner::Run( plugin.Name() );
          // ...
        }
        ```
- **Expected Impact**:
    - **Extensibility**: High. Allows users or other teams to add custom, domain-specific benchmarks without modifying the QMeter core.
    - **Maintainability**: High. Decouples the core orchestration from the specific benchmark implementations.

## P2: Medium-Priority Improvements (Observability & Fidelity)

---

### P2.1: Implement Structured, Actionable Logging

- **Current Behavior**: Logging is done via the `info()` function, producing unstructured text that is difficult to parse automatically.
- **Evidence Pointer**: `QMeter/_Main/BL/Dataset_Company/Daemon_Heartbeat.qbl:136` - `info ('Exporting results to ...');` is used for logging.
- **Proposed Change**:
    - **Design**: Create a dedicated logging module that writes structured logs (e.g., JSON or XML) to a file. Each log entry should include a timestamp, severity, component, thread ID, and a structured message.
    - **Pseudo-Code**:
        ```quill
        // Logger module
        Logger::Log( severity: 'Info',
                     component: 'Daemon_Heartbeat',
                     thread: System::ThreadID(),
                     message: 'Exporting results.',
                     details: 'Path=' + path + ';Mode=Headless' );
        ```
- **Expected Impact**:
    - **Observability**: High. Enables automated log analysis, monitoring, and alerting.
    - **Diagnostic Value**: High. Makes it much easier to trace execution flow and debug issues, especially in concurrent runs.

---

### P2.2: Enhance Storage Test Fidelity

- **Current Behavior**: The database tests use simple, single-record operations inside a loop. This does not reflect modern application patterns that use batching, transactions, and prepared statements.
- **Evidence Pointer**: `QMeter/_Main/BL/Type_BenchmarkDataset/Method_Cat5_UpdateData_SingleField.qbl:18-22` - A `traverse` loop updates records one by one.
- **Proposed Change**:
    - **Design**: Add new sub-tests to Category 5 that use more realistic database access patterns.
    - **Pseudo-Code**:
        ```quill
        // New method: Cat5_BatchUpdate_1k

        // Collect 1000 orders to be updated
        orders_to_update := selectset( this, Order, o, ... , 1000);

        // Start a transaction
        Transaction::Transaction().Start();

        // Update all orders within the transaction
        traverse(orders_to_update, Elements, o)
        {
          o.Update(...);
        }

        // Commit the transaction and measure the time
        Transaction::Transaction().Commit();
        ```
- **Expected Impact**:
    - **Accuracy**: Medium. Provides a more realistic measure of database performance for applications that use transactions and batching.
    - **Diagnostic Value**: Medium. Helps identify performance differences between row-by-row processing and batch operations.

## P3: Low-Priority Improvements (Robustness & UX)

---

### P3.1: Improve Headless Mode Robustness

- **Current Behavior**: The headless mode has a hardcoded output path and lacks robust error handling and exit codes.
- **Evidence Pointer**: `QMeter/_Main/BL/Dataset_Company/Daemon_Heartbeat.qbl:137` - The export path is hardcoded to `Util::GetHomeDirectory() + "results.xml"`.
- **Proposed Change**:
    - **Design**: Allow the output path to be specified via a command-line argument (e.g., `/exportpath=...`). Implement proper exit codes (`0` for success, non-zero for failure) and propagate detailed error messages to the console.
    - **Pseudo-Code**:
        ```quill
        // In OnCreate or Heartbeat
        export_path := guard(CommandLine::Instance().StringArgument("exportpath"), Util::GetHomeDirectory() + "results.xml");

        // In top-level try/catch block of the application
        onerror
        {
          Logger::Log(severity: 'Fatal', ...);
          System::Exit(1); // Exit with an error code
        }
        
        System::Exit(0); // Exit with success code
        ```
- **Expected Impact**:
    - **Robustness**: High. Makes headless mode suitable for reliable, automated scripting and integration into CI/CD pipelines.

---

### P3.2: Enhance UI/UX Clarity

- **Current Behavior**: The UI allows users to change scoring coefficients and other settings that can invalidate the comparability of results, with only a general warning in the user guide.
- **Evidence Pointer**: The user guide warns against changing settings, but the UI itself does not prevent it or make the implications clear.
- **Proposed Change**:
    - **Design**: In the UI, visually distinguish between "Standard" and "Custom" run configurations. If any setting that affects comparability is changed, automatically flag the run as "Custom" and disable submission to a central database. The `IsGoldScoreAltered` attribute is a good starting point.
    - **Pseudo-Code**:
        ```quill
        // In the UI form's OnChange event for a critical setting

        if ( setting.Value() <> setting.DefaultValue() )
        {
          this.IsComparableRun( false );
          StatusLabel.Text( 'Warning: Custom run, results not comparable.' );
        }
        ```
- **Expected Impact**:
    - **Usability**: High. Prevents users from accidentally generating invalid or misleading benchmark scores.
    - **Data Quality**: High. Ensures that centrally collected benchmark data is consistent and comparable.
