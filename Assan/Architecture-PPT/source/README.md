# Assan Alüminyum Dijitaliz Program - Solution Architecture Documentation

This repository contains the comprehensive solution architecture documentation for the Assan Alüminyum Advanced Planning and Scheduling (APS) and Manufacturing Execution System (MES) program, also known as the Dijitaliz Program.

## Contents

### Main Documentation

- **SOLUTION_ARCHITECTURE.md** - The primary solution architecture document covering all aspects of the integrated system.
- **OPEN_ITEMS.md** - A detailed list of open items, unresolved issues, and decisions that need to be made.
- **INTERFACE_INVENTORY.md** - A comprehensive inventory of all interfaces between systems.
- **TRACEABILITY_MATRIX.md** - A mapping of PowerPoint slides to documentation sections.

### Diagrams

The `diagrams/` directory contains 16 Mermaid diagrams illustrating the architecture, data flows, and lifecycles:

1. **01-overall-architecture.mmd** - Overall solution architecture showing all systems and their interactions.
2. **02-supply-chain-generic.mmd** - Generic supply chain definition with stocking points and work orders.
3. **03-supply-chain-plants.mmd** - Supply chain with plant-specific differentiation (Tuzla and Dilovași).
4. **04-planning-decisions-overview.mmd** - Planning decisions hierarchy and horizons.
5. **05-to-be-data-flow.mmd** - To-be data flow architecture between SAP, Quintiq, and Apriso.
6. **06-casting-campaign-data-flow.mmd** - Casting campaign planning data flow.
7. **07-mps-data-flow.mmd** - Master production schedule data flow.
8. **08-order-combination-data-flow.mmd** - Order combination data flow.
9. **09-scheduling-data-flow.mmd** - Scheduling data flow.
10. **10-mes-data-flow.mmd** - Manufacturing execution system data flow.
11. **11-planning-horizons-gantt.mmd** - Planning horizons Gantt chart.
12. **12-wo-lifecycle-cr-sheet-foil-paint.mmd** - CR-Sheet-Foil-Paint work order lifecycle.
13. **13-wo-lifecycle-mc.mmd** - Melting & Casting work order lifecycle.
14. **14-recycle-lifecycle.mmd** - Recycle work order lifecycle.
15. **15-maintenance-rolls-casting.mmd** - Maintenance for rolls (casting) lifecycle.
16. **16-maintenance-rolls-cold-rolling.mmd** - Maintenance for rolls (cold rolling) lifecycle.

## Key Components

The solution integrates the following systems:

- **SAP ERP** - System of Record for master data, sales orders, and inventory.
- **DELMIA Quintiq** - Advanced Planning and Scheduling (APS) modules:
  - Demand Planner (DP)
  - Macro Planner (MP)
  - Company Planner (CP)
  - Order Combiner (OC)
  - Casting Scheduler (MCSCH)
  - Cold Rolling Scheduler (CRSCH)
  - Charge Mix Planner (CMP)
- **DELMIA Apriso** - Manufacturing Execution System (MES)
- **Quintiq Data Manager (QDM)** - Integration middleware

## Document Status

This documentation is marked as **[Proposed]** and is awaiting customer review and feedback. Several items are marked as **[Open]** or **[QA Review]** and require further clarification or approval.

## How to Use This Documentation

1. Start with the **SOLUTION_ARCHITECTURE.md** for a comprehensive overview.
2. Refer to the **TRACEABILITY_MATRIX.md** to navigate between the original PowerPoint and this documentation.
3. Use the **OPEN_ITEMS.md** to track pending decisions and clarifications.
4. Review the **INTERFACE_INVENTORY.md** for detailed integration specifications.
5. Examine the diagrams in the `diagrams/` directory for visual representations of the architecture and processes.

## Document Information

- **Version**: 1.0
- **Date**: February 18, 2026
- **Authors**: Manus AI (Documentation Generation)
- **Original Architects**: Ersin Demirok, Koert Munich, Dawid Kawa

## License

This documentation is proprietary to Assan Alüminyum and Dassault Systèmes. All rights reserved.

---

For questions or feedback regarding this documentation, please contact the project team.
