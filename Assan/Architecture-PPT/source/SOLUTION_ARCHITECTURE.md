
# Overall System Architecture - Dijitaliz Program

## 1. Executive Summary

This document outlines the overall system architecture for the Assan Alüminyum Advanced Planning and Scheduling (APS) and Manufacturing Execution System (MES) program, also known as the Dijitaliz Program. The program aims to implement a comprehensive, integrated solution to streamline planning, scheduling, and execution processes across the entire supply chain.

The core of the solution consists of two main platforms: **DELMIA Quintiq** for advanced planning and scheduling and **DELMIA Apriso** for manufacturing execution. These platforms are integrated with the existing **SAP ERP** system, which remains the system of record for master data, sales orders, and inventory.

### Key Objectives

- **Integrated Planning**: Achieve seamless integration between long-term strategic planning (S&OP) and short-term operational scheduling.
- **Enhanced Visibility**: Provide end-to-end visibility of the supply chain, from raw material to finished goods.
- **Improved Efficiency**: Optimize resource utilization, reduce lead times, and minimize scrap through advanced planning algorithms and real-time execution monitoring.
- **Standardized Processes**: Implement standardized work order lifecycles and planning processes across all plants and production lines.

### Solution Components

The architecture is composed of the following key components:

| Component | Vendor | Purpose |
|---|---|---|
| **SAP ERP** | SAP | System of Record (Master Data, Sales, Inventory) |
| **DELMIA Quintiq** | Dassault Systèmes | Advanced Planning & Scheduling (APS) |
| **DELMIA Apriso** | Dassault Systèmes | Manufacturing Execution System (MES) |
| **Quintiq Data Manager (QDM)** | Dassault Systèmes | Integration Middleware |

![Overall Solution Architecture](diagrams/01-overall-architecture.png)

This document provides a detailed overview of the supply chain scope, planning lifecycle, data flows, technical infrastructure, work order lifecycles, and key use cases that define the solution.

## 2. Objectives & How to Use This Document

### 2.1. Document Purpose and Audience

This document serves as the single source of truth for the overall solution architecture of the Assan Alüminyum Dijitaliz Program. It is intended for a broad audience, including:

- **Project Stakeholders**: To provide a high-level understanding of the solution scope and objectives.
- **Business Analysts**: To understand the detailed business processes and use cases.
- **Solution Architects**: To understand the technical architecture, data flows, and system integrations.
- **Development Teams**: To guide the implementation and configuration of the Quintiq and Apriso modules.

### 2.2. How to Navigate the Documentation

The document is structured to provide a logical flow from high-level concepts to detailed implementation specifics. It is recommended to read the document in the following order:

1.  **Executive Summary**: For a quick overview of the program.
2.  **Supply Chain & Solution Scope**: To understand the business context.
3.  **Planning Lifecycle & Data Flow**: To understand the core planning processes.
4.  **Work Order Lifecycle**: To understand how work orders are managed.
5.  **Use Cases**: For detailed step-by-step process flows.
6.  **Technical Infrastructure**: For integration and data architecture details.

### 2.3. Scope of Coverage

This document covers the functional and technical architecture of the integrated APS and MES solution. It details the processes, data flows, and interactions between SAP, Quintiq, and Apriso. Out-of-scope items and dependencies on other projects are explicitly mentioned in the **Scope Variations** and **Open Items** sections.

## 3. Glossary

This section defines the key terminology, acronyms, and abbreviations used throughout this document.

| Term | Definition |
|---|---|
| **APS** | Advanced Planning and Scheduling |
| **MES** | Manufacturing Execution System |
| **ERP** | Enterprise Resource Planning |
| **QDM** | Quintiq Data Manager |
| **S&OP** | Sales & Operations Planning |
| **DP** | Demand Planner (Quintiq Module) |
| **MP** | Macro Planner (Quintiq Module) |
| **CP** | Company Planner (Quintiq Module) |
| **OC** | Order Combiner (Quintiq Module) |
| **MCSCH** | Melting & Casting Scheduler (Quintiq Module) |
| **CRSCH** | Cold Rolling Scheduler (Quintiq Module) |
| **CMP** | Charge Mix Planner (Quintiq Module) |
| **WO** | Work Order |
| **COL** | Customer Order Line |
| **SKU** | Stock Keeping Unit |
| **BOM** | Bill of Materials |
| **KKB** | Kalite Kontrol Beklemede (Awaiting Quality Control) - A status for coils requiring a quality decision. |
| **FF** | Finishing Floor |
| **MF** | Melting Furnace |
| **TO** | Transfer Order |
| **WIP** | Work In Progress |
| **FG** | Finished Good |
| **CC** | Casted Coil |
| **QAD** | Quintiq Architecture Design |

## 4. Supply Chain & Solution Scope

This section provides a detailed overview of the Assan Alüminyum supply chain, the resources in scope for the Dijitaliz Program, and the defined scope variations.

### 4.1. Supply Chain Definition (Generic)

The generic supply chain model defines the flow of materials from raw material (scrap) to finished goods. It includes stocking points, work orders, and the different production paths for various product types.

![Generic Supply Chain](diagrams/02-supply-chain-generic.png)

The key stages in the generic supply chain are:

- **Recycling (RE WO)**: Processing of scrap material.
- **Melting & Casting (MC WO)**: Production of casted coils from primary and recycled materials.
- **Cold Rolling (CR WO)**: Cold rolling of casted coils.
- **Downstream Operations**: Including Coil & Sheet (SH WO), Foil (FC WO), and Paint (PC WO) processing.
- **Finished Goods**: Final products ready for customer delivery (COL).

### 4.2. Supply Chain Definition (with Plants)

The supply chain spans two main production plants: **Tuzla** and **Dilovası**. The model accounts for inter-plant transfers of Work-In-Progress (WIP) materials, which are managed via transport orders.

![Supply Chain with Plants](diagrams/03-supply-chain-plants.png)

Inter-plant transfers are critical for balancing production capacity and meeting demand. The solution is designed to manage these transfers seamlessly within the planning and scheduling processes.

### 4.3. Supply Chain Definition (Coil & Sheet)

The Coil & Sheet production path involves specific routing options, including short and long routes, depending on the product specifications and processing requirements. The planning system is configured to select the optimal routing based on capacity, cost, and delivery constraints.

### 4.4. Resources in Scope

The Dijitaliz Program covers a wide range of resources across both plants. The following table summarizes the key resources and their relevance to the different Quintiq planning modules:

| Plant | Department | Resource | Planning Module |
|---|---|---|---|
| Tuzla | Melting | Melting Furnaces | MC-SCH, CMP |
| Tuzla | Casting | Casting Lines | MC-SCH |
| Tuzla | Cold Rolling | Cold Rolling Mills | CR-SCH |
| Tuzla | Finishing | Slitting Lines, Annealing Furnaces | CR-SCH |
| Dilovası | Cold Rolling | Cold Rolling Mills | CR-SCH |
| Dilovası | Finishing | Slitting Lines, Annealing Furnaces | CR-SCH |
| Dilovası | Painting | Paint Lines | CR-SCH |

### 4.5. Scope Variations

It is important to define the boundaries of the solution. The following items are considered out of scope for the current phase of the Dijitaliz Program:

- **Paint Preparation**: The paint preparation process (non-metal WO) is not within the scope of the Company Planner (CP) module but is included in the Cold Rolling Scheduler (CR-SCH).
- **Recycling Work Orders (RE WO)**: The detailed planning and scheduling of recycling work orders are not within the scope of the APS solution.
- **Primary/Scrap Stocking Points**: The management of these initial stocking points is outside the scope of the APS solution.

Dependencies on external systems and other projects are detailed in the **Solution Dependencies** and **Open Items** sections.

## 5. Planning Lifecycle & Data Flow

This section details the end-to-end planning lifecycle, from long-term strategic planning to real-time execution. It outlines the key planning decisions, the systems responsible for them, and the flow of data between these systems.

### 5.1. Planning Decisions Overview

The planning process is structured as a hierarchy of decisions, each with a specific time horizon and level of detail. This ensures that strategic goals are translated into actionable operational plans.

![Planning Decisions Overview](diagrams/04-planning-decisions-overview.png)

The key planning decisions are:

- **Sales & Operations Planning (S&OP)**: Long-term demand and supply balancing.
- **Casting Campaign Planning**: Mid-term planning of casting operations.
- **Master Production Schedule (MPS)**: Mid-term order confirmation and flexi WO generation.
- **Order Combination**: Short-term optimization of cutting patterns and firm WO generation.
- **Scheduling**: Short-term sequencing and batching of production operations.
- **Manufacturing Execution**: Real-time execution and monitoring of production.

### 5.2. Sales & Operations Planning (S&OP)

The S&OP process is the starting point of the planning lifecycle, with a horizon of 15 months to 3 months. It involves two key roles:

- **Demand Planner (DP)**: Uses the Quintiq DP module to create a statistical forecast based on sales history and other inputs. This results in an unconstrained forecast.
- **Macro Planner (MP)**: Uses the Quintiq MP module to balance the unconstrained forecast against capacity and material constraints. This produces a constrained demand plan, a material plan, and a casting demand plan.

### 5.3. Casting Campaign Planning

Casting campaign planning bridges the gap between the macro plan and the detailed casting schedule, with a horizon of 4 weeks to 3 days. The **Casting Scheduler (MCSCH)** uses the Quintiq MCSCH module to:

- Disaggregate the casting demand from the MP to the SKU level.
- Create casting work orders.
- Assign work orders to reservations.
- Create and update the casting schedule (campaign).

![Casting Campaign Planning Data Flow](diagrams/06-casting-campaign-data-flow.png)

The output of this process is a published casting campaign, which is sent to the MES for execution and to the Company Planner for further planning.

### 5.4. Master Production Schedule (MPS)

The MPS process, managed by the **Company Planner (CP)** using the Quintiq CP module, has a horizon of 12 weeks to 3 days. Its main responsibilities are:

- **Order Acceptance**: Confirming or updating sales order dates based on material availability and capacity.
- **Flexi WO Generation**: Creating flexible work orders based on the material plan from the MP and the casting campaign from the MCSCH.
- **Replenishment & Reservation**: Running a planning process to manage replenishment and reservation of materials.

![Master Production Schedule Data Flow](diagrams/07-mps-data-flow.png)

### 5.5. Order Combination

The order combination process, managed by the **Order Combiner (OC)** using the Quintiq OC module, has a horizon of 4 weeks to 3 days. This process is critical for optimizing material usage:

- **Combine Orders**: Combine multiple sales orders onto larger pieces of material (physical, planned, or virtual).
- **Create Patterns**: Generate optimal cutting patterns to minimize scrap.
- **Adapt Routings**: Adapt the production routing based on the combination structure.
- **Generate Firm WOs**: Create firm work orders and proposals to be sent to the scheduler and MES.

![Order Combination Data Flow](diagrams/08-order-combination-data-flow.png)

### 5.6. Scheduling

Detailed scheduling is the final step in the planning process before execution, with a horizon of 3 days to now. The **Cold Rolling Scheduler (CRSCH)** uses the Quintiq CRSCH module to:

- Sequence operations for cold rolling, annealing, and finishing.
- Apply sequencing rules and constraints (e.g., roll programs).
- Batch operations for resources like furnaces.
- Publish the final schedule to the MES.

![Scheduling Data Flow](diagrams/09-scheduling-data-flow.png)

### 5.7. Manufacturing Execution System (MES)

The Apriso MES is responsible for the real-time execution of the production plan. Its key functions in this architecture are:

- **Order Dressing**: Generating detailed routing information for each SKU.
- **Production Execution**: Managing the execution of work orders on the shop floor.
- **Firm WO Registry**: Registering firm work orders received from the planning systems.
- **Feedback Loops**: Providing continuous feedback on production status, inventory changes, and downtimes to the planning and ERP systems.

![Manufacturing Execution System Data Flow](diagrams/10-mes-data-flow.png)

### 5.8. Planning Horizons

The different planning horizons are crucial for ensuring that decisions are made at the right time and with the right level of detail. The following Gantt chart illustrates the overlapping nature of these horizons:

![Planning Horizons](diagrams/11-planning-horizons-gantt.png)

## 6. Solution Dependencies

This section outlines the dependencies between the various Quintiq and Apriso solution components. The level of dependency is determined by the number and frequency of data objects exchanged between the modules. A clear understanding of these dependencies is crucial for ensuring smooth data flow and process integration.

### 6.1. Module-to-Module Dependencies

The following table summarizes the key dependencies between the solution modules. The data flows from the "Source Module" to the "Target Module".

| Source Module | Target Module | Data Object(s) | Frequency |
|---|---|---|---|
| **Quintiq DP** | Quintiq MP | Unconstrained Demand, FG Forecast | Monthly |
| **Quintiq MP** | Quintiq MCSCH | Casting Demand | Daily/Weekly |
| **Quintiq MP** | Quintiq CP | Material Plan, Constrained Demand | Daily/Weekly |
| **Quintiq MCSCH** | Quintiq CP | Casted Coil Forecast, Campaign WOs | Daily |
| **Quintiq MCSCH** | Quintiq CMP | Casting Campaign Plan | Daily |
| **Quintiq CP** | Quintiq OC | Flexi WOs, Virtual Materials | Daily |
| **Quintiq CP** | Quintiq CRSCH | Planning Window, Reservation Info | Daily |
| **Quintiq OC** | Quintiq CRSCH | Firm WOs, Adapted Routings | Hourly/Daily |
| **Quintiq CRSCH** | Apriso MES | Detailed Schedules, Sequencing Info | Hourly |
| **Apriso MES** | Quintiq Schedulers | Production Feedback, WO Status | Real-time |
| **Apriso MES** | Quintiq Planners | Inventory Updates, Firm WO Registry | Real-time |
| **Apriso MES** | SAP ERP | Production Confirmations, Inventory | Real-time |
| **SAP ERP** | All Quintiq/Apriso | Master Data, Sales Orders, Inventory | As needed |

### 6.2. Data Object Exchanges

The integration between the modules relies on a set of well-defined data objects. The **Quintiq Data Manager (QDM)** acts as the central middleware for many of these exchanges, providing a loosely-coupled, asynchronous communication channel. However, some specific interfaces may justify tightly-coupled, point-to-point connections for request/reply scenarios.

Key data objects exchanged include:

- **Work Orders (WOs)**: The primary unit of planning and execution, which transitions from Flexi to Firm as it moves through the lifecycle.
- **Inventory**: Real-time inventory levels for raw materials, WIP, and finished goods.
- **Sales Orders**: Customer demand that drives the planning process.
- **Schedules**: Detailed production schedules with start and end times for each operation.
- **Routings**: The sequence of operations required to produce a specific SKU.
- **Master Data**: Product definitions, BOMs, resource information, etc.

For a detailed breakdown of the data objects and their attributes, please refer to the Quintiq Interface Design Document (QID) for each module.

## 7. Technical Infrastructure

This section describes the technical architecture that supports the integrated APS and MES solution, focusing on the integration strategy, the role of the Quintiq Data Manager (QDM), and the principles of data ownership.

### 7.1. Integration Architecture

The integration architecture is designed to provide a robust and scalable framework for data exchange between SAP, Quintiq, and Apriso. The primary component of this architecture is the **Quintiq Data Manager (QDM)**, which serves as a middleware facade.

![To-Be Data Flow Architecture](diagrams/05-to-be-data-flow.mmd)

The key principles of the integration architecture are:

- **Centralized Facade**: QDM acts as a single point of contact for many of the integrations, simplifying the overall landscape and reducing point-to-point connections.
- **Asynchronous Communication**: The architecture favors a loosely-coupled, asynchronous messaging pattern, which improves resilience and allows systems to operate independently.
- **Data Transformation**: QDM is responsible for transforming data into the specific formats required by the receiving systems.
- **Multi-casting**: QDM can efficiently distribute the same business object to multiple consumer systems.

While QDM is the preferred integration path, some specific interfaces may be implemented as tightly-coupled, point-to-point connections, particularly for real-time request/reply scenarios.

The integration between the MES and low-level machines/controllers is considered out of scope for QDM and is handled by the Apriso platform directly.

### 7.2. Data Ownership

Clear data ownership is essential for maintaining data consistency and integrity across the integrated landscape. The following table defines the system of record for key data objects:

| Data Object | System of Record | Description |
|---|---|---|
| **Master Data** | SAP ERP | Product definitions, BOMs, resource master data. |
| **Sales Orders** | SAP ERP | All customer orders are created and managed in SAP. |
| **Inventory** | SAP ERP | The definitive record of inventory levels. MES provides real-time updates. |
| **Work Orders** | Quintiq/Apriso | WOs are created and managed within the Quintiq and Apriso ecosystem. Final status is reported to SAP. |
| **Schedules** | Quintiq Schedulers | The Quintiq scheduling modules are the owners of the production schedules. |
| **Routings** | Apriso MES | The MES is responsible for dressing orders and generating the detailed production routings. |

Data is synchronized between the systems based on the defined data flows and integration patterns. The goal is to ensure that each system has access to the timely and accurate information it needs to perform its function.

## 8. Work Order Lifecycle

This section provides a detailed overview of the lifecycle of a Work Order (WO), the main block for planning and execution. The lifecycle varies depending on the type of product and the production path.

### 8.1. CR-Sheet-Foil-Paint Work Order Lifecycle

This lifecycle applies to the majority of products that go through the cold rolling and downstream finishing processes. It involves a transition from a flexible WO to a firm WO as it moves closer to execution.

![CR-Sheet-Foil-Paint Work Order Lifecycle](diagrams/12-wo-lifecycle-cr-sheet-foil-paint.mmd)

The key stages are:

1.  **SKU Generated (SAP)**: The process begins with the creation of the SKU and sales order in SAP.
2.  **Order Dressed (Apriso)**: The MES dresses the order and generates the routing.
3.  **Flexi WO Proposed (CP)**: The Company Planner creates a flexible WO.
4.  **Firm WO Proposed (OC)**: The Order Combiner creates a firm WO after pattern optimization.
5.  **Firm WO Registered (Apriso)**: The MES registers the firm WO.
6.  **Scheduled (CRSCH)**: The Cold Rolling Scheduler sequences and schedules the WO.
7.  **In Execution (Apriso)**: The WO is executed on the shop floor.
8.  **Completed (Apriso)**: The WO is completed, and feedback is sent to SAP.

The lifecycle also includes paths for handling quality decisions (KKB), where a WO can be put on hold and then scrapped, reused, continued, or reworked.

### 8.2. MC (Melting & Casting) Work Order Lifecycle

This lifecycle is specific to the production of casted coils. It is driven by the casting demand from the S&OP process and managed by the Casting Scheduler.

![MC Work Order Lifecycle](diagrams/13-wo-lifecycle-mc.mmd)

The key stages are:

1.  **S&OP Plan (MP/DP)**: The process starts with the S&OP plan, which generates the casting coil requirement.
2.  **Disaggregation**: The casting demand is disaggregated to the SKU level.
3.  **Flexi WO Proposed (MCSCH)**: The Casting Scheduler creates a flexible WO.
4.  **Firm WO Registered (Apriso)**: The MES registers the firm WO as part of the casting campaign.
5.  **In Execution (Apriso)**: The casting campaign is executed.
6.  **Completed (Apriso)**: The campaign is completed, and feedback is sent to SAP and the scheduler.

### 8.3. Recycle Work Order Lifecycle

This lifecycle manages the process of recycling scrap material back into the production flow. It is primarily managed within the Apriso MES and involves close coordination with the Charge Mix Planner (CMP).

![Recycle Work Order Lifecycle](diagrams/14-recycle-lifecycle.mmd)

The process includes steps for scrap collection, guidance proposals for recycling, melting furnace load registration, charge mix optimization, and output classification (liquid or solid).

### 8.4. Maintenance for Rolls (Casting)

This lifecycle manages the planned and unplanned maintenance of rolls used in the casting process. It involves creating maintenance orders (MOs) in SAP and coordinating downtime with the production schedule.

![Maintenance for Rolls (Casting) Lifecycle](diagrams/15-maintenance-rolls-casting.mmd)

A key feature of this process is the dual confirmation of downtime completion by both the production and maintenance teams, ensuring that the resource is ready before resuming the campaign.

### 8.5. Maintenance for Rolls (Cold Rolling)

Similar to the casting maintenance lifecycle, this process manages the maintenance of rolls for the cold rolling mills. It is integrated with the scheduling process to account for pre-processing time and downtime.

![Maintenance for Rolls (Cold Rolling) Lifecycle](diagrams/16-maintenance-rolls-cold-rolling.mmd)

The process includes the mounting of back-up roll pairs to minimize downtime and the ability to trigger a manual replan of the schedule if the maintenance duration exceeds the planned time.

## 9. Use Cases

This section details the critical business processes, or use cases, that the integrated solution is designed to support. Each use case describes the purpose, trigger, system interactions, and key inputs/outputs.

### 9.1. UC1 – SKU Dressing / Work Order Routing Generation

- **Purpose**: To create the detailed production routing for a given SKU.
- **Trigger**: Creation of a new SKU in SAP.
- **Systems Involved**: SAP, Apriso MES.
- **Flow**: SAP sends the SKU definition to the MES. The MES "dresses" the SKU with the necessary BOM components, routing alternatives, and production versions based on standard operating procedures (SOPs). This information is then sent back to SAP for costing and master data management.

### 9.2. UC2 – Order Confirmation & Master Production Schedule

- **Purpose**: To provide a reliable confirmation date for a sales order and to create the master production schedule.
- **Trigger**: Creation or update of a sales order in SAP.
- **Systems Involved**: SAP, Quintiq CP, Apriso MES.
- **Flow**: The Company Planner in CP uses available inventory, future inventory (from the casting scheduler), and sales quotas to create or update flexi orders. A planning run is executed to determine the proposed confirmation date, which is sent back to SAP.

### 9.3. UC3 – Order Combination & Firm Work Order Generation

- **Purpose**: To optimize material usage by combining multiple orders and to generate firm work orders for execution.
- **Trigger**: Manual trigger by the Order Combiner.
- **Systems Involved**: Quintiq OC, Quintiq CP, Apriso MES, SAP.
- **Flow**: The Order Combiner in OC combines flexi orders from CP onto available physical, planned, or virtual materials. This process generates optimized cutting patterns and adapts the routing. The output is a set of firm work orders that are sent to the scheduler and the MES.

### 9.4. UC4 – Quality Decision (KKB) Management

- **Purpose**: To manage coils that are put on hold for a quality decision (KKB status).
- **Trigger**: A quality issue is identified during production.
- **Systems Involved**: Apriso MES, Quintiq Schedulers, Quintiq Planners, SAP.
- **Flow**: The coil is put on hold in the MES. A quality decision is made to either scrap, reuse, continue, or rework the coil. Each path triggers a specific workflow that updates the WO status, inventory, and schedule in the respective systems.

### 9.5. UC5 – Scheduling

- **Purpose**: To create a detailed, sequenced production schedule for the short-term horizon.
- **Trigger**: Manual trigger by the scheduler.
- **Systems Involved**: Quintiq CRSCH, Quintiq CP, Apriso MES.
- **Flow**: The scheduler in CRSCH sequences and batches firm work orders based on sequencing rules, constraints, and planning windows. The resulting schedule is published to the MES for execution.

### 9.6. UC6 – Execution

- **Purpose**: To execute the production schedule and capture real-time feedback from the shop floor.
- **Trigger**: Continuous process.
- **Systems Involved**: Apriso MES, Quintiq Schedulers, Quintiq Planners, SAP.
- **Flow**: The MES manages the execution of work orders. It captures feedback on inventory changes, WO status changes, and downtimes. This feedback is sent in real-time to the planning systems to enable responsive rescheduling and to SAP for inventory and production updates.

### 9.7. UC7 – Casting Campaign Creation

- **Purpose**: To plan, schedule, and execute the casting campaigns.
- **Trigger**: Casting demand from the S&OP process.
- **Systems Involved**: Quintiq MCSCH, Quintiq MP, Quintiq CP, Quintiq CMP, Apriso MES, SAP.
- **Flow**: This use case is broken down into three sub-processes:
    - **UC7.1 Create Casting Schedule**: The MCSCH creates the initial campaign plan based on disaggregated demand.
    - **UC7.2 Update Casting Schedule**: The MCSCH updates the campaign based on new information and feedback.
    - **UC7.3 Execute Casting Schedule**: The MES executes the campaign, and feedback is sent to the planning systems.

### 9.8. UC8 – Other Use Cases [Open]

This use case is a placeholder for other critical processes that require detailed mapping, including the Order Acceptance Process, Dummy Coil Management, and Transfer Order Generation. These will be detailed in a future version of this document.

## 10. Open Items / Decisions Needed

This section summarizes the open items, unresolved issues, and decisions that need to be addressed to finalize the solution architecture. These items have been extracted from the original presentation and are tracked here to ensure their resolution.

### 10.1. Critical Open Items

These are high-impact items that require immediate attention.

| ID | Item | Impact | Details | Action Required |
|---|---|---|---|---|
| **OI-01** | **UC8 – Other Use Cases** | High | The scope of several critical use cases (e.g., Order Acceptance, Dummy Coil Management) is not yet defined. | Schedule workshop with Delmia Quintiq IPC team to detail these use cases. |
| **OI-02** | **KKB for Casted Campaigns** | High | The process for handling scrap and campaign adjustments due to quality issues in casting is unclear. | Clarify with Casting Scheduler team and update UC7. |
| **OI-03** | **Technical Architecture Project** | High | The management of the integration project is marked as [Removed] and needs clarification. | Clarify integration project scope and timeline with the integration team. |

### 10.2. Items Under Review

These items are currently under internal or customer review.

| ID | Item | Status | Details | Action Required |
|---|---|---|---|---|
| **OI-04** | **Recycle WO Lifecycle** | QA Review | The proposed lifecycle for recycling work orders needs approval from the QA team. | Schedule QA review meeting. |
| **OI-05** | **Maintenance WO Lifecycles** | QA Review | The lifecycles for casting and cold rolling maintenance need QA approval. | Schedule QA review meeting. |
| **OI-06** | **COL History Tracking** | Open | The approach for tracking the history of customer order lines (COL) for BI purposes is not defined. | Coordinate with Assan BI and CP teams. |
| **OI-07** | **KKB Status in CP** | Open | The implementation approach for showing KKB status in the Company Planner needs to be defined. | Clarify with CP team and define data model. |

### 10.3. Proposed Items Awaiting Feedback

A significant portion of the solution architecture is marked as **[Proposed]** and is awaiting customer review and feedback. This includes the glossary, supply chain definitions, planning decisions, data flows, and all detailed use cases. Collecting feedback on these items is a critical next step.

### 10.4. Decision Log

The following table tracks the key decisions that need to be made:

| Decision ID | Topic | Status | Owner | Due Date |
|---|---|---|---|---|
| D001 | UC8 Use Cases Scope | Open | Delmia IPC | TBD |
| D002 | KKB for Casted Campaigns | Open | Casting Scheduler | TBD |
| D003 | COL History Tracking | Open | Assan BI / CP | TBD |
| D004 | KKB Status in CP | Open | CP Team | TBD |
| D005 | Technical Architecture Project | Open | Integration Team | TBD |

## Appendix A: Traceability Matrix

This appendix provides a traceability matrix that maps the slides from the original PowerPoint presentation to the sections of this document. This ensures that all content from the presentation has been covered and provides a reference for navigating between the two.

### Slide to Section Mapping

| Slide # | Slide Title | Status | Document Section | Key Diagrams |
|---|---|---|---|---|
| 1-2 | Title & Program Overview | [Q-IS] | Executive Summary | N/A |
| 5 | Glossary | [Proposed] | Glossary | N/A |
| 7 | Objectives and how to use this document | [Proposed] | Objectives & How to Use | N/A |
| 8 | Scope Variations | [Proposed] | Scope & Scope Variations | N/A |
| 10 | Assan Supply Chain Definition (Generic) | [Proposed] | Supply Chain & Solution Scope | 02-supply-chain-generic.mmd |
| 11 | Assan Supply Chain Definition (with Plants) | [Proposed] | Supply Chain & Solution Scope | 03-supply-chain-plants.mmd |
| 12 | Assan Supply Chain Definition (Coil & Sheet) | [Proposed] | Supply Chain & Solution Scope | 02-supply-chain-generic.mmd |
| 13 | Resources in Scope | [Proposed] | Supply Chain & Solution Scope | N/A |
| 15 | Planning Decisions Overview | [Proposed] | Planning Lifecycle & Data Flow | 04-planning-decisions-overview.mmd |
| 18 | Data Flow – Architecture (To-Be) | [Proposed] | Technical Infrastructure | 01-overall-architecture.mmd, 05-to-be-data-flow.mmd |
| 19-29 | Planning Decisions & Data Flows | [Proposed] | Planning Lifecycle & Data Flow | 06-10-planning-data-flows.mmd |
| 30 | Planning Horizons | [Proposed] | Planning Lifecycle & Data Flow | 11-planning-horizons-gantt.mmd |
| 32-33 | WO Lifecycle (CR-Sheet-Foil-Paint) | [Proposed] | Work Order Lifecycle | 12-wo-lifecycle-cr-sheet-foil-paint.mmd |
| 34-35 | WO Lifecycle (MC) | [Proposed] | Work Order Lifecycle | 13-wo-lifecycle-mc.mmd |
| 36 | WO Lifecycle (Recycle) | [QA Review] | Work Order Lifecycle | 14-recycle-lifecycle.mmd |
| 37 | WO Lifecycle (Maintenance - Casting) | [QA Review] | Work Order Lifecycle | 15-maintenance-rolls-casting.mmd |
| 38 | WO Lifecycle (Maintenance - Cold Rolling) | [QA Review] | Work Order Lifecycle | 16-maintenance-rolls-cold-rolling.mmd |
| 42 | Technical Infrastructure Legend | [Proposed] | Technical Infrastructure | N/A |
| 45-75 | Use Cases (UC1-UC8) | [Proposed] / [Open] | Use Cases | N/A |

### Status Legend

- **[Q-IS]**: Same as Q IS, no change from previous version
- **[Proposed]**: Under customer consideration, released to customer
- **[Agreed]**: Agreed by both Delmia Quintiq and Customer
- **[QA Review]**: Under QA consideration, needs review
- **[Open]**: Under IPC consideration, not yet proposed
