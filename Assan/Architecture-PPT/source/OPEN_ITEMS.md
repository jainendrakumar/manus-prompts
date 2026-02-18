# Open Items and Decisions Needed

## Critical Open Items [Open]

### 1. UC8 – Other Use Cases [Open]
**Status**: Not yet detailed  
**Impact**: High - Additional processes need to be defined  
**Details**: The following use cases need detailed process and data flow explanations:
- Order Acceptance Process
- Dummy Coil Management Process
- Transfer Order Generation
- Pricing & Costing – contribution margin calculation (DP/MP) – Scope needs to be defined, appears DP-specific
- SAP-MP-DP-CP Overall flow for Sales order management
- Quote management – Needs coordination between DP & CP teams for Quota update and SAP publication
- Sales order entry – Covered in UC2
- Additional processes to be identified

**Action Required**: Schedule workshop with Delmia Quintiq IPC team to detail these use cases

---

### 2. KKB (Quality Decision) for Casted Campaigns [Open]
**Status**: Unresolved  
**Impact**: High - Affects casting campaign planning  
**Details** (from Slide 69):
- What happens to input material calculated if campaign has some coils that become scrap?
- How will existing campaign be extended?
- How is the coil casted on different width?

**Action Required**: Clarify with Casting Scheduler team and update UC7.1-7.3

---

### 3. COL History Tracking and BI Publishing [Open]
**Status**: Unresolved  
**Impact**: Medium - Affects reporting and analytics  
**Details** (from Slide 58):
- How to track the history of COL (e.g., why it became late)?
- Can it be published to Assan BI?
- Which COL attributes should be published?

**Action Required**: Coordinate with Assan BI team and CP team

---

### 4. KKB Status in Company Planner [Open]
**Status**: Unresolved  
**Impact**: Medium - Affects order tracking  
**Details** (from Slide 58):
- CP needs to know the KKB status on WOs
- Expected to be added to COL "Comment" in CP
- Implementation approach needs clarification

**Action Required**: Clarify with CP team and define data model

---

## Items Under QA Review [QA Review]

### 1. Work Order Lifecycle (Recycle) [QA Review]
**Status**: Under QA consideration  
**Impact**: Medium - Affects scrap material handling  
**Details**: Recycle WO lifecycle needs QA approval from IPC/SwE/ORS teams

**Action Required**: Schedule QA review meeting

---

### 2. Work Order Lifecycle (Maintenance for Rolls - Casting) [QA Review]
**Status**: Under QA consideration  
**Impact**: Medium - Affects casting operations  
**Details**: Roll changeover and maintenance scheduling needs QA approval

**Action Required**: Schedule QA review meeting

---

### 3. Work Order Lifecycle (Maintenance for Rolls - Cold Rolling) [QA Review]
**Status**: Under QA consideration  
**Impact**: Medium - Affects cold rolling operations  
**Details**: Roll changeover and pre-processing time management needs QA approval

**Action Required**: Schedule QA review meeting

---

## Items Under IPC Consideration [Open]

### 1. Technical Architecture [Removed]
**Status**: Removed from current version  
**Impact**: High - Integration management needs clarification  
**Details** (from Slide 43):
- Integration will be managed as separate project in parallel to MES & APS projects
- Refer to QAD (Quintiq Architecture Design) for detailed technical integration
- Currently marked as [Removed] - needs reinstatement or clarification

**Action Required**: Clarify integration project scope and timeline

---

### 2. Data Flow – Architecture (As-Is) [Proposed]
**Status**: Proposed but may need updates  
**Impact**: Medium - Current state documentation  
**Details** (from Slide 16):
- As-Is data flow includes ERP and external tables (excels)
- May need updates based on actual current implementation

**Action Required**: Validate with Assan IT team

---

## Proposed Items Awaiting Customer Review [Proposed]

The following sections are marked [Proposed] and are awaiting customer review and feedback:

1. **Glossary** (Slide 5)
2. **Objectives and how to use this document** (Slide 7)
3. **Scope Variations** (Slide 8)
4. **Assan Supply Chain Definition (Generic)** (Slide 10)
5. **Assan Supply Chain Definition (with Plants)** (Slide 11)
6. **Assan Supply Chain Definition (Coil & Sheet)** (Slide 12)
7. **Resources in Scope** (Slide 13)
8. **Planning Decisions** (Slides 15, 19-28)
9. **Data Flow – Architecture (To-Be)** (Slide 18)
10. **Planning Horizons** (Slide 30)
11. **Work Order Lifecycles (CR-Sheet-Foil-Paint, MC)** (Slides 32-35)
12. **Dependencies between solutions in scope** (Slide 40)
13. **Technical Infrastructure Legend** (Slide 42)
14. **All Use Cases (UC1-UC7)** (Slides 46-73)

**Action Required**: Collect customer feedback and schedule review meetings

---

## Items Agreed [Agreed]

Currently, no sections are marked as [Agreed]. All sections require either customer review or internal QA/IPC review.

---

## Items Same as Q IS [Q-IS]

The following sections have no changes from the previous Q IS version:

1. **Change Log** (Slide 3)
2. **Chapter Status** (Slide 4)
3. **Contents** (Slides 6, 9, 14, 39, 41, 44, 47, 50, 53, 56, 59, 61, 63, 65, 67, 70, 72, 74)

---

## Critical Path Items

### Phase 1: Immediate Actions (Next 2 weeks)
1. Schedule customer review meeting for [Proposed] items
2. Schedule QA review for [QA Review] items
3. Clarify UC8 scope with IPC team

### Phase 2: Short-term (2-4 weeks)
1. Resolve KKB for casted campaigns
2. Define COL history tracking approach
3. Clarify KKB status in CP data model
4. Validate As-Is data flow with Assan IT

### Phase 3: Medium-term (1-2 months)
1. Finalize technical architecture project scope
2. Complete all use case detailing
3. Achieve [Agreed] status for all sections

---

## Decision Log

| Decision ID | Topic | Status | Owner | Due Date |
|------------|-------|--------|-------|----------|
| D001 | UC8 Use Cases Scope | Open | Delmia IPC | TBD |
| D002 | KKB for Casted Campaigns | Open | Casting Scheduler | TBD |
| D003 | COL History Tracking | Open | Assan BI / CP | TBD |
| D004 | KKB Status in CP | Open | CP Team | TBD |
| D005 | Technical Architecture Project | Open | Integration Team | TBD |

---

## Notes

- This document is part of the Overall Solution Architecture documentation (v1.0, dated 17/02/26)
- All items are tracked and will be updated as decisions are made
- Status tags follow the chapter status convention defined in Slide 4
- For detailed information on each item, refer to the corresponding slide numbers listed above

