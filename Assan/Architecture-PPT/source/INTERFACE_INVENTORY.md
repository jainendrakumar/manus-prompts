
# Interface Inventory

This document provides a detailed inventory of the interfaces between the systems in the Assan Alüminyum Dijitaliz Program. It serves as a reference for understanding the data flows and integration patterns that connect SAP, Quintiq, and Apriso.

## Interface Summary

The following table provides a high-level summary of the key interfaces in the solution architecture.

| Interface ID | Source System | Target System | Data Object(s) | Frequency | Integration Pattern |
|---|---|---|---|---|---|
| **IF-001** | SAP ERP | Quintiq/Apriso | Master Data (Products, BOMs, Routings) | As needed | QDM / File |
| **IF-002** | SAP ERP | Quintiq/Apriso | Inventory Levels | Real-time | QDM / Point-to-Point |
| **IF-003** | SAP ERP | Quintiq CP | Sales Orders | Real-time | QDM / Point-to-Point |
| **IF-004** | Quintiq DP | Quintiq MP | Unconstrained Demand, FG Forecast | Monthly | Internal |
| **IF-005** | Quintiq MP | Quintiq MCSCH | Casting Demand | Daily/Weekly | Internal |
| **IF-006** | Quintiq MP | Quintiq CP | Material Plan, Constrained Demand | Daily/Weekly | Internal |
| **IF-007** | Quintiq MCSCH | Quintiq CP | Casted Coil Forecast, Campaign WOs | Daily | Internal |
| **IF-008** | Quintiq CP | Quintiq OC | Flexi WOs, Virtual Materials | Daily | Internal |
| **IF-009** | Quintiq OC | Quintiq CRSCH | Firm WOs, Adapted Routings | Hourly/Daily | Internal |
| **IF-010** | Quintiq Schedulers | Apriso MES | Detailed Schedules, Sequencing Info | Hourly | QDM / Point-to-Point |
| **IF-011** | Apriso MES | Quintiq Suite | Production Feedback, WO Status | Real-time | QDM / Point-to-Point |
| **IF-012** | Apriso MES | SAP ERP | Production Confirmations, Inventory | Real-time | QDM / Point-to-Point |

## Interface Details

This section provides a more detailed description of each interface.

### IF-001: Master Data (SAP to Quintiq/Apriso)

- **Description**: This interface synchronizes master data from SAP ERP, the system of record, to the Quintiq and Apriso platforms. This ensures that all systems are working with a consistent set of master data.
- **Data Objects**: Product definitions (SKUs), Bills of Materials (BOMs), routings, resource master data, and other supporting definitions.
- **Frequency**: As needed, typically when there are changes to the master data in SAP.
- **Integration Pattern**: A combination of QDM for structured data and file-based transfer for bulk data.

### IF-002: Inventory Levels (SAP to Quintiq/Apriso)

- **Description**: This interface provides real-time visibility of inventory levels from SAP to the planning and execution systems. This is critical for accurate planning and scheduling.
- **Data Objects**: Inventory levels for raw materials, WIP, and finished goods at all stocking points.
- **Frequency**: Real-time or near real-time.
- **Integration Pattern**: QDM or a point-to-point connection to ensure low latency.

### IF-003: Sales Orders (SAP to Quintiq CP)

- **Description**: This interface sends new and updated sales orders from SAP to the Quintiq Company Planner (CP) to drive the order confirmation and master production scheduling process.
- **Data Objects**: Customer Order Lines (COLs) with requested dates and quantities.
- **Frequency**: Real-time or near real-time.
- **Integration Pattern**: QDM or a point-to-point connection.

### IF-004: Demand Forecast (Quintiq DP to MP)

- **Description**: This internal Quintiq interface provides the unconstrained demand forecast from the Demand Planner to the Macro Planner.
- **Data Objects**: Unconstrained forecast at the product family level.
- **Frequency**: Monthly, as part of the S&OP cycle.
- **Integration Pattern**: Internal Quintiq data flow.

### IF-005: Casting Demand (Quintiq MP to MCSCH)

- **Description**: This interface sends the aggregated casting demand from the Macro Planner to the Casting Scheduler to drive the casting campaign planning process.
- **Data Objects**: Casting demand at the MP code level.
- **Frequency**: Daily or weekly.
- **Integration Pattern**: Internal Quintiq data flow.

### IF-006: Material Plan (Quintiq MP to CP)

- **Description**: This interface provides the overall material plan from the Macro Planner to the Company Planner to guide the creation of flexi work orders.
- **Data Objects**: Material plan, constrained demand.
- **Frequency**: Daily or weekly.
- **Integration Pattern**: Internal Quintiq data flow.

### IF-007: Casted Coil Forecast (Quintiq MCSCH to CP)

- **Description**: This interface provides the Company Planner with a forecast of the expected output from the casting campaigns.
- **Data Objects**: Casted coil forecast, campaign work orders.
- **Frequency**: Daily.
- **Integration Pattern**: Internal Quintiq data flow.

### IF-008: Flexi WOs (Quintiq CP to OC)

- **Description**: This interface sends flexible work orders from the Company Planner to the Order Combiner for pattern optimization and firm WO generation.
- **Data Objects**: Flexi WOs, virtual materials.
- **Frequency**: Daily.
- **Integration Pattern**: Internal Quintiq data flow.

### IF-009: Firm WOs (Quintiq OC to CRSCH)

- **Description**: This interface sends firm work orders from the Order Combiner to the Cold Rolling Scheduler for detailed sequencing and scheduling.
- **Data Objects**: Firm WOs, adapted routings.
- **Frequency**: Hourly or daily.
- **Integration Pattern**: Internal Quintiq data flow.

### IF-010: Detailed Schedules (Quintiq Schedulers to Apriso MES)

- **Description**: This interface sends the detailed production schedules from the Quintiq scheduling modules (MCSCH and CRSCH) to the Apriso MES for execution.
- **Data Objects**: Detailed schedules with start/end times, sequencing information, and batching information.
- **Frequency**: Hourly.
- **Integration Pattern**: QDM or a point-to-point connection.

### IF-011: Production Feedback (Apriso MES to Quintiq Suite)

- **Description**: This is a critical feedback loop that provides real-time information from the shop floor to the entire Quintiq planning and scheduling suite. This enables responsive replanning and schedule adjustments.
- **Data Objects**: Production feedback, work order status changes, inventory updates, and downtime information.
- **Frequency**: Real-time.
- **Integration Pattern**: QDM or a point-to-point connection.

### IF-012: Production Confirmations (Apriso MES to SAP ERP)

- **Description**: This interface sends final production confirmations and inventory updates from the MES to SAP to close out work orders and update the system of record.
- **Data Objects**: Production confirmations, material consumptions, and final inventory levels.
- **Frequency**: Real-time.
- **Integration Pattern**: QDM or a point-to-point connection.
