# QMeter: Code Evidence Pack

---

This document provides curated code excerpts from the QMeter v0.34.19.90.33.8 project, demonstrating the implementation of key benchmark areas, orchestration logic, and scoring mechanisms.

## Category 1: Memory Test

---

**File**: `QMeter/_Main/BL/Type_BenchmarkDataset/Method_Cat1_SmallTransaction.qbl` | **Lines**: 1-38 | **Component**: `Method_Cat1_SmallTransaction` | **Explanation**: This method implements the "Small Transaction" memory benchmark. It creates a small workforce dataset (10 working units, 10 employees, 3-day horizon) and then measures the time taken for a full propagation of all constraints.

```quill
Quintiq file version 2.0
#parent: #root
Method Cat1_SmallTransaction
{
  Description: 'Small transaction'
  TextBody:
  [*
    // chee liang Dec-19-2014 (created)
    
    start := OS::PrecisionCounter();
    
    workingunits := 10;
    employees    := 10;
    startdate    := Date::Today();
    enddate      := Date::Today() + 3;
    
    // Lite mode reduces the dataset size for faster runs
    if( this.LiteMode() )
    {
      workingunits := 5;
      employees    := 5;
      enddate      := Date::Today() + 2
    }
    
    this.Workforce().CreateData( workingunits, employees, startdate, enddate );
    
    // The core of the memory test: trigger a full propagation
    Transaction::Transaction().Propagate();
    
    end := OS::PrecisionCounter();
    
    this.RecordBenchmarkExecutionInfo( false
                                     , this.RunNr()
                                     , this.ThreadNr()
                                     , start
                                     , end
                                     , 'Category 1: Execute method SmallTransaction' );
  *]
}
```

---

**File**: `QMeter/_Main/BL/Type_BenchmarkDataset/Method_Cat1_BigTransaction.qbl` | **Lines**: 1-36 | **Component**: `Method_Cat1_BigTransaction` | **Explanation**: This method implements the "Big Transaction" memory benchmark. It creates a larger dataset (100 working units, 100 employees, 7-day horizon) but, unlike the small transaction, it **does not** perform a propagation. This test focuses purely on the data creation aspect.

```quill
Quintiq file version 2.0
#parent: #root
Method Cat1_BigTransaction
{
  Description: 'Big transaction'
  TextBody:
  [*
    // chee liang Dec-19-2014 (created)
    
    start := OS::PrecisionCounter();
    
    workingunits := 100;
    employees    := 100;
    startdate    := Date::Today();
    enddate      := Date::Today() + 7;
    
    if( this.LiteMode() )
    {
      workingunits := 50;
      employees    := 50;
      enddate      := Date::Today() + 3;
    }
    
    this.Workforce().CreateData( workingunits, employees, startdate, enddate );
    
    end := OS::PrecisionCounter();
    
    this.RecordBenchmarkExecutionInfo( false
                                     , this.RunNr()
                                     , this.ThreadNr()
                                     , start
                                     , end
                                     , 'Category 1: Execute method BigTransaction' );
  *]
}
```

## Category 2: Algorithm Test

---

**File**: `QMeter/_Main/BL/Type_BenchmarkDataset/POAAlgorithm_POA_Test.qbl` | **Lines**: 1-39 | **Component**: `POAAlgorithm_POA_Test` | **Explanation**: This defines the Path Optimization Algorithm (POA) benchmark. It creates 100 nodes and then applies a simple strategy of random destruction and random construction for a specified number of iterations or until a timeout is reached. This tests the raw performance of the POA engine.

```quill
Quintiq file version 2.0
#parent: #root
POAAlgorithm POA_Test (...) 
{
  CurrentStrategy: trivial
  Description: "N doesn't really matter; 100 is fine"
  NodeInitializationText:
  [*
    poa.Async( async );
    for (i := 0; i < 100; i++)
    {
      poa.AddNode('node-' + [String]i, null( Order ) );
    }
  *]
  POAStrategy.Strategies trivial
  {
    TextBody:
    [*
      Number::Randomize( 1 );
      
      actions := strategy.NewActions( 'useless' );
      
      // Define the optimization strategy
      actions.NewRandomDestruction()
      actions.NewRandomConstruction();
      
      // Execute the strategy with iteration and time limits
      actions.Execute( maxiterations, maxduration.TotalInSeconds() );
    *]
  }
}
```

---

**File**: `QMeter/_Main/BL/Type_BenchmarkDataset/MathematicalProgram_MP_Test.qbl` | **Lines**: 51-87 | **Component**: `MathematicalProgram_MP_Test` | **Explanation**: This defines the Mathematical Programming (MP) benchmark, which appears to be a variation of the knapsack problem. It creates N binary variables, each with a random weight, and a constraint to select a subset of items whose weights sum to a target value, while minimizing the count of items.

```quill
  VariableInitializationText:
  [*
    program.Async( async );
    program.TimeLimit( maxduration.TotalInSeconds() );
    
    Number::Randomize( seed );
    
    TARGET := 1000.0;
    
    // Define sum and count variables and constraints
    varsum := program.NewVariable( 'sum' );
    varsum.LowerBound( TARGET );
    cnstrsum := program.NewConstraint( 'sum' );
    cnstrsum.NewTerm( -1.0, varsum );
    
    varcount := program.NewIntegerVariable( 'count' );
    cnstrcount := program.NewConstraint( 'count' );
    cnstrcount.NewTerm( -1.0, varcount );

    // Create N binary variables with random weights
    for ( i := 0; i < N; i++ )
    {
      x := program.NewBinaryVariable( 'number-' + [String]i );
    
      weight := Real::Random( 1.0, 5.0 );
      cnstrsum.NewTerm( 1.0*weight, x ); // Add to sum constraint
    
      cnstrcount.NewTerm( 1.0, x ); // Add to count constraint
    }
  *]
```

## Category 3: Quill Speed Test

---

**File**: `QMeter/NQueens/BL/Type_LibNQ_NQueens/Method_SolveWithoutPropagation.qbl` | **Lines**: 1-42 | **Component**: `Method_SolveWithoutPropagation` | **Explanation**: This method implements the "Hanoi Tower" benchmark, which is actually an N-Queens solver. It creates a board of size N, and then iteratively calls `StepWithoutPropagation()` to solve the puzzle. The benchmark measures the total time to find a solution without using the Quintiq propagation engine, testing pure Quill execution speed.

```quill
Quintiq file version 2.0
#parent: #root
Method SolveWithoutPropagation (Number n)
{
  TextBody:
  [*
    start := OS::PrecisionCounter();
    
    this.CreateData(n); // Initialize the N-Queens board
    
    end := OS::PrecisionCounter();
    info( 'Created board in', ((end-start)/OS::PrecisionCounterFrequency()).Round(5), 'seconds');
    
    Transaction::Transaction().Propagate(); // Initial propagation after setup
    
    maxiterations := 1000000;
    iterations    := 0;
    start         := OS::PrecisionCounter();
    
    // Main solver loop
    while ( not this.ProceduralSolved() and iterations < maxiterations )
    {
      this.StepWithoutPropagation(); // Perform one move
      this.PrintBoard();
    
      iterations++;
    }
    
    end := OS::PrecisionCounter();
    
    if ( this.ProceduralSolved() )
    {
      info( 'Solved in', ((end-start)/OS::PrecisionCounterFrequency()).Round(5), 'seconds and', iterations, 'moves');
    }
  *]
}
```

## Category 4: Propagation Test

---

**File**: `QMeter/_Main/BL/Type_BenchmarkDataset/Method_Cat4_MediumTransaction.qbl` | **Lines**: 1-38 | **Component**: `Method_Cat4_MediumTransaction` | **Explanation**: This method implements the "Medium Transaction" propagation benchmark. It is similar to the memory test but uses a different dataset size (50 working units, 50 employees, 5-day horizon) to measure propagation performance under a medium load.

```quill
Quintiq file version 2.0
#parent: #root
Method Cat4_MediumTransaction
{
  Description: 'Medium transaction'
  TextBody:
  [*
    start := OS::PrecisionCounter();
    
    workingunits := 50;
    employees    := 50;
    startdate    := Date::Today();
    enddate      := Date::Today() + 5;
    
    if( this.LiteMode() )
    {
      workingunits := 25;
      employees    := 25;
      enddate      := Date::Today() + 3;
    }
    
    this.Workforce().CreateData( workingunits, employees, startdate, enddate );
    
    // Trigger a full propagation to measure performance
    Transaction::Transaction().Propagate();
    
    end := OS::PrecisionCounter();
    
    this.RecordBenchmarkExecutionInfo( false
                                     , this.RunNr()
                                     , this.ThreadNr()
                                     , start
                                     , end
                                     , 'Category 4: Execute method MediumTransaction' );
  *]
}
```

## Category 5: Dataset-Store / Database Test

---

**File**: `QMeter/_Main/BL/Type_BenchmarkDataset/Method_Cat5_Entry.qbl` | **Lines**: 1-75 | **Component**: `Method_Cat5_Entry` | **Explanation**: This method orchestrates all 8 database benchmark tests (DS1-DS8). It carefully prepares the data in three stages (<10k, >10k, >1M records) and uses precision counters to measure only the execution time of the benchmark operations, excluding the data preparation time.

```quill
Quintiq file version 2.0
#parent: #root
Method Cat5_Entry
{
  Description: 'Database speed test'
  TextBody:
  [*
    // Stage 1: <10k records
    Order::CreateData( this, 0, 9000 );
    s_1 := OS::PrecisionCounter();
    this.Cat5_UpdateData_SingleField(...);
    this.Cat5_UpdateData_MultiField(...);
    this.Cat5_InsertData_1k(...);
    e_1 := OS::PrecisionCounter();
    
    // Stage 2: >10k records
    Order::CreateData( this, 10000, 20000 );
    s_2 := OS::PrecisionCounter();
    diff := s_2 - e_1; // Time spent on data prep
    this.Cat5_UpdateData_SingleField(...);
    this.Cat5_UpdateData_MultiField(...);
    this.Cat5_DeleteData_1k(...);
    e_2 := OS::PrecisionCounter();
    
    // Stage 3: >1M records
    this.Order( relflush );
    Order::CreateData( this, 0, 1000000 );
    s_3 := OS::PrecisionCounter();
    diff := diff + ( s_3 - e_2 ); // Accumulate data prep time
    this.Cat5_InsertData_1k(...);
    this.Cat5_DeleteData_1k(...);
    e_3 := OS::PrecisionCounter();
    
    // Record total time, subtracting the data prep time
    this.RecordBenchmarkExecutionInfo( true, ..., s_1, e_3, diff, 'Category 5: Total' );
  *]
}
```

## Orchestration, Scoring, and Headless Mode

---

**File**: `QMeter/_Main/BL/Dataset_BenchmarkDataset/Job_RunBenchmarkJob.qbl` | **Lines**: 1-51 | **Component**: `Job_RunBenchmarkJob` | **Explanation**: This job is the core of the benchmark dispatch system. It receives a category number and uses reflection to dynamically construct the method name (e.g., `Cat1_Entry`) and execute it. This makes the system extensible to new categories without changing the orchestration logic.

```quill
  Text:
  [*
    // Set information on benchmark dataset
    this.Name( name );
    this.Category( category );
    // ... set other attributes
    
    // Dynamically determine the method to run based on the category number
    method_name := 'Cat' + NumberToString::StandardConverter().Convert( category ) + '_Entry';
    reflection  := Reflection::FindMethod( this.DefinitionName(), method_name );
    
    if( not isnull( reflection ) )
    {
      try
      {
        // Execute the resolved method on the current dataset instance
        reflection.SetThis( this );
        reflection.Execute();
      }
      onerror
      {
        // ... error handling
      }
    }
  *]
```

---

**File**: `QMeter/_Main/BL/Type_BenchmarkCategory/Method_GetScore.qbl` | **Lines**: 1-13 | **Component**: `Method_GetScore` | **Explanation**: This method defines the core scoring formula. It normalizes the measured average runtime for a given number of concurrent datasets against a pre-defined "gold standard" runtime and score. A faster runtime results in a higher score.

```quill
Quintiq file version 2.0
#parent: #root
Method GetScore (Number concurrent_datasets) declarative remote as Real
{
  TextBody:
  [*
    // The score is calculated by comparing the measured runtime
    // against a 'gold standard' baseline.
    return guard(
          this.Company().Gold_Score() *
                  ( this.Gold_AvgRuntime() / this.GetAverageRuntime(concurrent_datasets)), 0);
  *]
}
```

---

**File**: `QMeter/_Main/BL/Dataset_Company/Daemon_Heartbeat.qbl` | **Lines**: 133-138 | **Component**: `Daemon_Heartbeat` | **Explanation**: This daemon runs in the background, and upon completion of all benchmark tasks, it checks for the `runandexport` command-line argument. If present, it automatically triggers the export of the results to an XML file in the home directory, enabling headless operation.

```quill
        autorun := guard (CommandLine::Instance().StringArgument("custom").ToLower() = "runandexport", false)
        if (autorun)
        {
          info ('Exporting results to ' + Util::GetHomeDirectory() + "results.xml");
          this.ExportRun(-1, Util::GetHomeDirectory() + "results.xml","N/A","N/A","Automatic export");
        }
```
