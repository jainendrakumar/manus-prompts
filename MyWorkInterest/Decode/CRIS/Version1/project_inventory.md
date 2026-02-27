# QUINTIQ PROJECT INVENTORY - release-model_1_341_0_0_skipftf.qproject

## EXTRACTION SUMMARY
- Archive Type: 7-zip (version 0.3)
- Archive Size: 12 MB
- Extraction Status: SUCCESS
- Total Directories: 4,376
- Total Files: 72,615

## FILE TYPE DISTRIBUTION
- Quill Source Files (.qbl): 53,220 files
- Definition Files (.def): 14,351 files
- Resource Files (.res): 3,973 files
- Query Definitions (.qcd): 684 files
- Translations (.qtr): 425 files
- XML Files (.xml): 190 files
- Properties Files (.properties): 183 files
- Reports (.qrp): 119 files
- Data Model Extensions (.dme): 99 files
- C# Code (.cs): 56 files
- Query Patterns (.qp): 39 files
- Image Metadata (.imd): 30 files
- Element Definitions (.elm): 30 files
- Views (.vw): 28 files
- Knowledge Base Configs (.kbc): 21 files
- Robot Test Files (.robot): 16 files

## PROJECT STRUCTURE

### Root Level
- Default.properties: Installation configuration
- Indianrailways/: Main project directory (40 subdirectories)

### Main Modules (39 directories)
1. _Main: Core model definitions
2. LibServicePlanner: Service planning library
3. LibIndianRailways: Indian Railways domain library
4. LibOpt: Optimization framework
5. LibOpt_BT: Optimization backtracking
6. ChannelSP: Channel Service Planner
7. DataExchangeFramework: Data exchange handling
8. LibServicePlannerIntegration: Integration layer
9. LibServicePlannerIO: Input/Output handling
10. LibServicePlannerFTF: Functional test framework
11. LibServicePlannerPTF: Performance test framework
12. LibServicePlannerTC: Test configuration
13. LibServicePlannerUTF: UI test framework
14. LibServicePlannerUIConfig: UI configuration
15. LibIndianRailwaysFTF: Railway functional tests
16. LibIndianRailwaysPTF: Railway performance tests
17. LibIndianRailwaysTC: Railway test config
18. LibIndianRailwaysInt: Railway integration
19. LibException: Exception handling
20. LibSvc: Service library
21. LibUISelection: UI selection library
22. LibWorkflow: Workflow engine
23. MessageFramework: Message handling
24. DataSnapshotManager: Data snapshot management
25. ScenarioManager: Scenario management
26. SettingsEngine: Configuration engine
27. Periodicity: Periodic scheduling
28. Qapi: API layer
29. WizardLibrary: UI wizard framework
30. TestLibrary: Test utilities
31. TestGenerator: Test generation
32. CodeGenerator: Code generation
33. ModuleUpgradeManager: Module upgrades
34. FunctionalTestFramework: FTF framework
35. PerformanceTestFramework: PTF framework
36. UIEventLogger: UI event logging
37. Lib_QLogViewer: Log viewer
38. _var: Variable/runtime data

## CORE DOMAIN MODEL

### Type Definitions
- Total Type Definitions: 2,872
- Optimization-Related Types: 504
- Constraint-Related Types: 9
- Location: Primarily in /BL/Type_* directories

### Key Entity Types (Sample)
- Board: Logical grouping of network geographical parts
- BoardSector: Board sector definitions
- TrainService: Train service planning
- ClockFacingGroup: Clock-facing group management
- Buffer: Buffer management
- CompanyNode: Company network nodes
- CompanyLink: Company network links
- AxleCounterBlockUsage: Axle counter block tracking
- ActivePlanMonth: Active plan periods
- AuditTrail: Audit trail tracking
- CallbackInstance: Callback management

### Optimization Components
- AMOpt (Adjustable Maintenance Optimizer)
- MDOpt (Micro Deconflicting Optimizer)
- MROptimizer (Macro Routing Optimizer)
- IROpt (Integrated Routing Optimizer)
- LibOpt (Core Optimization Framework)
- Suboptimizers and Scope Converters

### Integration Components
- DataExchangeFramework: Event-based data exchange
- IntegrationEvent: Event definitions
- DataTransformationDefinition: Transformation logic
- MessageHandlerIntegration: Message processing
- GlobalParameterIntegration: Parameter management
- EventDatasetIntegration: Event dataset handling

## ARCHITECTURAL LAYERS

### Business Logic Layer (BL)
- Type definitions for all domain entities
- Methods and algorithms
- Constraints and optimization logic
- Relations and data model
- Integration handlers

### System Layer (Sys)
- System definitions
- UI configurations
- Views and representations
- Translations

### Test Frameworks
- FunctionalTestFramework (FTF)
- PerformanceTestFramework (PTF)
- Unit Test Framework (UTF)
- Test Configuration (TC)

## KEY CONFIGURATION FILES
- Default.properties: Installation and deployment settings
- metadata.properties: Module metadata
- Various .properties files for module-specific configuration

## DATASET DEFINITIONS
- Dataset_Integration: Integration dataset
- Dataset_LibSM_ScenarioManager: Scenario management dataset
- Dataset_ServicePlanner: Service planner dataset
- Dataset_LibSM_Dataset: Generic dataset definitions

## KNOWLEDGE BASES
- KnowledgeBaseDomain_ServicePlanner: Service planner KB
- Multiple .kbc files for domain knowledge

## CONSTRAINT GROUPS
- MPConstraintGroups: Mathematical programming constraint groups
- Constraint violation tracking types (7 types)
- Constraint violation metrics

## AUTHORIZATION & SECURITY
- AuthorizationGroups: Role-based access control
- ApplicationAuthorization: Application-level authorization
- RoleConfigSets: Role configuration sets

## REMOTE JOBS & CALLBACKS
- RemoteJobs: Asynchronous job execution
- CallbackInstance: Callback management
- CallbackTaskBase: Base callback task definitions
- CallbackTaskManagerBase: Callback task management

## SOAP INTERFACES
- SOAPInterfaces: Web service definitions
- Integration with external systems

## PROJECT CLASSIFICATION
This is a **LARGE, COMPLEX enterprise-grade DELMIA Quintiq solution** for:
- Railway service planning and scheduling
- Train scheduling optimization
- Maintenance optimization
- Conflict resolution and deconflicting
- Multi-objective optimization with constraints
- Real-time integration with external systems
- Comprehensive testing and validation frameworks

The project follows a modular architecture with clear separation of concerns:
- Domain models (LibServicePlanner, LibIndianRailways)
- Optimization engines (LibOpt, multiple suboptimizers)
- Integration layer (DataExchangeFramework, LibServicePlannerIntegration)
- Testing frameworks (FTF, PTF, UTF, TC)
- UI and configuration (LibServicePlannerUIConfig, SettingsEngine)
