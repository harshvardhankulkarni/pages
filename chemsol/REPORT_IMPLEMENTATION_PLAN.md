# Chemsol — Reports & Dashboards Implementation Plan

> **Source of truth.** Follow this document phase by phase. After each phase: verify → commit → push to `origin/main`.

---

## Part 1 — Gap Analysis (Field/Module Changes)

These gaps are **blocking prerequisites**. Phase 0 resolves them all before any report is built.

| # | Form | Gap | Needed For | Fix |
|---|------|-----|------------|-----|
| G1 | **SO (2A)** | No `Status` field | R2 Sales Register, SO Type Split | Add dropdown `Status`: Draft / Accepted / Completed / Cancelled |
| G2 | **Project (2B)** | No Revenue/P&L formula; **Task Budget subform missing** (BRD expects it) | Project P&L (R2), category-wise P&L, "Task Budget Actuals pending" notification | Add `Total Revenue` (AutoFetch SO Total), `Total Actual Cost` (auto from MR/SCE/BMR), `P&L` formula; add **Task Budget subform** (Category, Description, Budget Qty, Rate, Budget Amount, Actual Qty, Actual Amount) |
| G3 | **Costing Sheet (3A)** | No explicit section subtotal fields or Total Costing Amount | Costing Status, Costing vs Actual (R3) | Add 5 section subtotal formulas (A–E) + `Total Costing Amount` formula |
| G4 | **MR (3C)** | `Total MR Cost` not a real field; Allocation has no `Issued Qty` | R3 Project Cost Baseline; Project Inventory Status | Add `Total MR Cost` formula (Material + Application + Transport + Tools); add `Issued Qty` (auto) on Allocation, updated by MIS-Post Deluge |
| G5 | **PO (4B)** | No `Status`; line items no Received/Balance/Receipt Status; no Delivery Days | Open PO Register, PO vs GRN Pending, Vendor Performance (R4) | Add `Status` dropdown; line fields `Received Qty` (auto), `Balance Qty` (formula), `Receipt Status` (formula: Pending/Partial/Complete); add `Delivery Days` computed at GRN submit (GRN Date − PO Delivery Date) |
| G6 | **FGHM (5F)** | No `Status` (Pending Acceptance / Accepted) | R5 FG Handover Pending | Add `Status` dropdown, auto-set on inline acceptance |
| G7 | **RM/FG Inventory (6A/6B)** | No `Standard Rate` on ledger | Inventory Valuation (R6) | AutoFetch `Standard Rate` from Item Muster |
| G8 | **SCE (6D) + BMR (5C) lines** | No Rate/Amount on line items | Costing vs Actual Variance, P&L (R3) | Add `Rate` (AutoFetch Standard Rate from Item Muster) + `Amount` (formula: Qty × Rate) per line |
| G9 | **Reports guide** | FG Consumption Log + Project FG Position (form 6C exists) missing from R6 | R6 completeness | Add 2 report rows to reports.html R6 |

**No changes needed:** Item Muster (Standard Rate ✓), System Master, BOM, Supplier, Customer/Site, Store Master, MR Allocation (Assigned/Ratio/80% Flag/Consumed/Consumption% ✓), PR, GRN, QC, Production Job, RM Consumption, Packing, MIS, MRT, Stock Movement Log — all report-ready as-is.

---

## Part 2 — Phased Build

### Phase 0 — Schema Changes (G1–G9) ✅ DONE

**All field additions. Reports depend on them. Build order:**

1. **G1 — SO `Status` dropdown:** Draft / Accepted / Completed / Cancelled
2. **G2 — Project additions:**
   - `Total Revenue` (AutoFetch: SO.Total Amount — set on SO acceptance)
   - `Total Actual Cost` (AutoFetch: MR.Total MR Cost — set on MR Released)
   - `P&L` formula: `Total Revenue − Total Actual Cost`
   - **Task Budget subform** (Category dropdown: Transport / Execution / Manpower / Tools / Overhead; Description; Budget Qty; Rate; Budget Amount formula; Actual Qty; Actual Amount formula)
3. **G3 — Costing Sheet subtotals:** Section A Material Total (formula), Section B Application Total, Section C Transport Total, Section D Tools Total, Section E Overhead Total, `Total Costing Amount` (formula: Σ all 5)
4. **G4 — MR additions:**
   - `Total MR Cost` formula: `Material Cost + Application Amount + Transport Amount + Tools Amount`
   - Allocation `Issued Qty` (Number, auto-updated) — set by Deluge on MIS-Post
5. **G5 — PO additions:**
   - Header `Status` dropdown: Draft / Approved / PO Sent / Completed / Closed
   - Line item `Received Qty` (Number, auto-updated) — set by Deluge on GRN-Post
   - Line item `Balance Qty` formula: `Ordered Qty − Received Qty`
   - Line item `Receipt Status` formula: Pending / Partial / Complete
   - Header `Delivery Days` (Number) — computed at GRN submit: `GRN Date − PO Delivery Date`
6. **G6 — FGHM `Status` dropdown:** Pending Acceptance / Accepted (auto-set on inline acceptance)
7. **G7 — RM/FG Inventory:** Add `Standard Rate` field (AutoFetch from Item Muster)
8. **G8 — SCE + BMR line items:** Add `Rate` (AutoFetch from Item Muster) + `Amount` formula per line
9. **G9 — reports.html:** Add FG Consumption Log + Project FG Position rows to R6

**Deluge hooks to write:**

| Hook | Trigger | Action |
|------|---------|--------|
| `MIS_Post_Allocation_Update` | MIS "Post MIS" button click | For each MIS line item → update MR Allocation `Issued Qty += Issued Qty` (Project ID + Item Code match) |
| `GRN_Post_PO_Update` | GRN "Post GRN" button click | For each GRN line item → update PO line `Received Qty += Received Qty`; recalculate `Balance Qty` and `Receipt Status`; compute `Delivery Days` |
| `FGHM_Accepted_Status` | FGHM inline acceptance submit | Set FGHM `Status` = "Accepted" |
| `Project_Revenue_Set` | SO acceptance (Supply+Apply) | Set Project `Total Revenue` = SO.Total Amount |
| `Project_Cost_Set` | MR Released | Set Project `Total Actual Cost` = MR.Total MR Cost |

**Verification:** Each field/form visible in Creator builder; Deluge hooks fire on test records. Git commit `reports: phase 0 schema changes`.

---

### Phase 1 — Master Data Reports (M1) ✅ DONE

**Module:** Master Data — 7 forms, 8 reports (R1 build guide complete — reports.html)

| Report | Creator Type | Source Form | Group By | Aggregations | Filters | Gap Dep |
|--------|-------------|-------------|----------|-------------|---------|---------|
| Item Catalog | Detail | Purchase Item Muster | — | — | Status = Active | — |
| Items by Category | Summary | Purchase Item Muster | Category | COUNT(Item Code), SUM(Max Stock) | — | — |
| System Master List | Detail | System Master | — | — | Status = Active | — |
| System → FG Composition | Detail | System Composition | System Code | — | Status = Approved/Released | — |
| FG → RM BOM Matrix | Detail | BOM / FG Formulation | FG Code | — | Status = Approved/Released | — |
| Supplier List | Detail | Supplier Master | — | — | Status = Active | — |
| Customer / Site List | Detail | Customer / Site Master | — | — | Status = Active | — |
| Store & Bin Register | Detail | Store Master | Store Type | — | — | — |

**Verification:** 8 reports created, seeded data returns correct rows/groups. Push.

---

### Phase 2 — Sales & Project Reports (M2)

**Module:** Sales Order, Project, Task Budget — 8 reports

| Report | Creator Type | Source Form | Group By | Aggregations | Filters | Gap Dep |
|--------|-------------|-------------|----------|-------------|---------|---------|
| Sales Register | Detail | Sales Order | — | — | Date range, Sales Type, Status | G1 |
| SO Value by Customer | Summary | Sales Order | Customer Code | SUM(Total Amount), COUNT(SO No) | — | — |
| SO Type Split | Chart (Pie) | Sales Order | Sales Type | SUM(Total Amount) | — | — |
| SO Value Trend | Chart (Line) | Sales Order | SO Date (month) | SUM(Total Amount) | Date range | — |
| Project Status List | Detail | Project | Status | — | — | — |
| Open Projects by PM | Summary | Project | Project Manager | COUNT(Project ID), SUM(Project Cost) | Status = Planned/In Progress | — |
| Project P&L Real-time | Summary | Project | Project ID | SUM(Total Revenue), SUM(Total Actual Cost), SUM(P&L) | — | G2 |
| Task Budget vs Actual | Summary | Project Task Budget subform | Category | SUM(Budget Amount), SUM(Actual Amount) | Project ID | G2 |

**Verification:** SO Register filters by new Status; P&L formula math correct; Task Budget returns per-category. Push.

---

### Phase 3 — Costing/Plan/MR Reports (M3)

**Module:** Costing Sheet, Production Plan, MR, MR Allocation — 12 reports

| Report | Creator Type | Source Form | Group By | Aggregations | Filters | Gap Dep |
|--------|-------------|-------------|----------|-------------|---------|---------|
| Costing Sheet Status | Summary | Costing Sheet | Costing Status | COUNT(Costing No), SUM(Total Costing Amount) | — | G3 |
| Costing Register | Detail | Costing Sheet | — | — | Date range, Status | — |
| Production Plan Register | Detail | Production Plan | — | — | Plan Status | — |
| Plan Shortage Summary | Summary | Production Plan (lines) | RM Item Code | SUM(Shortage) | Shortage > 0 | — |
| MR Status Tracking | Summary | MR | MR Status | COUNT(MR Number) | — | — |
| MR Status per Project | Pivot | MR | Row: Project ID, Col: MR Status | COUNT(MR Number) | — | — |
| Project Cost Baseline | Summary | MR | Project ID | SUM(Total MR Cost), SUM(Material + App + Transport + Tools) | — | G4 |
| Material Allocation vs Consumption | Detail | MR Allocation | Project ID | — | — | G4 |
| 80% Alert List | Detail | MR Allocation | — | — | Consumption % ≥ 80 AND Alert Flag = ON | — |
| Allocation Exhausted | Detail | MR Allocation | — | — | Consumption % ≥ 100 | — |
| Costing vs Actual Variance | Summary | MR + SCE + BMR | Project ID | SUM(Total MR Cost), SUM(SCE Amount), SUM(BMR Amount) | — | G3, G8 |
| Project Inventory Status | Pivot | MR Allocation | Row: Project ID, Col: Item Code | SUM(Assigned), SUM(Issued), SUM(Consumed), SUM(Returned) | — | G4 |

**Verification:** MR Status funnel chart; 80% Alert drilldown; Inventory Status shows Issued column. Push.

---

### Phase 4 — Procurement Reports (M4)

**Module:** PR, PO, GRN, QC — 8 reports

| Report | Creator Type | Source Form | Group By | Aggregations | Filters | Gap Dep |
|--------|-------------|-------------|----------|-------------|---------|---------|
| PR Status Report | Summary | PR | Status | COUNT(PR Number) | — | — |
| Open PO Register | Detail | PO | — | — | Status ≠ Completed/Closed | G5 |
| PO Value by Supplier | Summary | PO | Supplier Code | SUM(Total Amount), COUNT(PO Number) | — | — |
| Purchase by Item Group | Summary | PO (lines) | Item Category | SUM(Total Amount) | Date range | — |
| PO vs GRN Pending | Detail | PO (lines) | — | — | Balance Qty > 0 | G5 |
| Vendor Performance | Summary | PO | Supplier | COUNT(PO), AVG(Delivery Days) | — | G5 |
| GRN Register | Detail | GRN | — | — | Date range | — |
| QC Results | Summary | QC | QC Status | COUNT(QC Number), SUM(Accepted Qty) | — | — |

**Verification:** PO Register shows new Status filter; PO vs GRN Pending works with Balance Qty; Vendor Performance returns AVG delivery days. Push.

---

### Phase 5 — Production Reports (M5)

**Module:** MIS, Production Job, BMR, RM Consumption, Packing, FGHM — 10 reports

| Report | Creator Type | Source Form | Group By | Aggregations | Filters | Gap Dep |
|--------|-------------|-------------|----------|-------------|---------|---------|
| MIS Register | Detail | MIS | — | — | Date range, MR No | — |
| MIS Issued vs Required | Summary | MIS (lines) | Item Code | SUM(Required Qty), SUM(Issued Qty) | Project ID, MR No | — |
| Pending MIS (Balance > 0) | Detail | MIS (lines) | — | — | Balance Qty > 0 | — |
| Today's Production | Summary | BMR | FG Code | SUM(Yield / FG Output) | Date = Today | — |
| Production Job Status | Summary | Production Job | Status | COUNT(Job No) | — | — |
| Open Production Jobs | Detail | Production Job | — | — | Status = Scheduled/In Progress | — |
| Daily Production Trend | Chart (Bar) | BMR | Date | SUM(FG Output) | Date range | — |
| BMR vs BOM Variance | Detail | RM Consumption | FG Code | — | — | — |
| Production Efficiency | Summary | Packing | FG Code | SUM(Packed Qty) | — | — |
| FG Handover Pending | Detail | FGHM | — | — | Status = Pending Acceptance | G6 |

**Verification:** FGHM Pending filter works; MIS Balance > 0 correct. Push.

---

### Phase 6 — Inventory/Site/Return Reports (M6)

**Module:** RM/FG Inventory, Stock Movement Log, SCE, MRT, Project FG — 13 reports

| Report | Creator Type | Source Form | Group By | Aggregations | Filters | Gap Dep |
|--------|-------------|-------------|----------|-------------|---------|---------|
| RM Stock Status | Detail | RM Inventory | — | — | Reorder Status filter | — |
| FG Stock Status | Detail | FG Inventory | — | — | Status filter | — |
| Inventory Valuation | Summary | RM Inventory + FG Inventory | Category | SUM(Closing Stock × Standard Rate) | — | G7 |
| Reorder Alerts | Detail | RM Inventory | — | — | Reorder Status = Below Min | — |
| Stock Movement Log | Detail | Stock Movement Log | Item Code | — | Date range, In/Out | — |
| Site Consumption Log | Detail | SCE | — | — | Project ID, Date, Work Area | — |
| Consumption by Work Area | Summary | SCE (lines) | Project ID, Work Area | SUM(Qty Consumed) | — | — |
| Consumption by RM Item | Summary | SCE (lines) | RM Item Code | SUM(Qty Consumed) | Project ID | — |
| Consumption vs Allocation | Pivot | MR Allocation | Row: Project ID, Col: Item Code | SUM(Consumed Qty) | — | — |
| Material Return Report | Detail | MRT | — | — | Project ID, Reason, Condition | — |
| Returns by Condition | Summary | MRT (lines) | Condition | SUM(Return Qty) | — | — |
| FG Consumption Log | Detail | FG Consumption Entry | — | — | Project ID, Date | — |
| Project FG Position | Summary | Project FG Consumption | Project ID, FG Code | SUM(Received), SUM(Consumed), SUM(Remaining) | — | — |

**Verification:** Valuation math (Closing × Rate); FG Position shows received/consumed/remaining. Push.

---

### Phase 7 — Dashboard Widgets (M7)

**8 department dashboards — build widgets referencing reports from Phases 1–6.**

| Dashboard | KPI Cards (Summary Report Metric) | Charts | Report Widgets |
|-----------|----------------------------------|--------|----------------|
| **Purchase** | Total Purchase This Month · Open POs · Pending PR Approvals | Purchase by Item Group (Bar) · Vendor Delivery (Bar) | Open PO Register · PO vs GRN Pending |
| **Sales** | SO Count · SO Value (YTD) | SO Value Trend (Line) · SO Type Split (Pie) | Sales Register · Project Status |
| **MR / Costing** | MR Count by Stage · Total MR Cost | MR Status (Funnel) · Costing Status (Pie) | MR Status Tracking · Material Allocation vs Consumption |
| **Store** | RM Stock Value · Below-Min Items | Stock by Category (Pie) · Reorder Alerts (Bar) | RM Stock Status · FG Stock Status · Stock Movement Log |
| **Production** | Batches Today · Open Jobs · Pending MIS | Daily Production (Bar) · Job Status (Pie) | MIS Register · Production Job Status · BMR vs BOM Variance |
| **Site Supervisor** | Consumption Today · Active 80% Alerts | Consumption by Area (Bar) · Consumption by RM (Bar) | Site Consumption Log · Material Return Report |
| **Costing** | Costing Approvals · Project P&L Sum | Costing vs Actual (Bar) · Project Inventory (Bar) | Project Inventory Status · Costing vs Actual Variance |
| **Project Management** | Open Projects · Active POs per Project | Project Status (Pie) · MR Status per Project (Bar) | Project Status · MR Status per Project · 80% Alert List |

**Verification:** Every KPI card/chart/report widget renders; drilldown links work; dept access correct. Push.

---

### Phase 8 — Cross-Module Verification

**Full end-to-end test with dummy data:**

1. Create SO (Supply+Apply) → verify Costing Sheet auto-expands → Approved → Project + Production Plan created (G2 Task Budget visible)
2. Production Plan Released → auto-PR for shortages → PO → GRN (G5 Received/Balance/Delivery Days fire) → QC
3. MR auto-derived → Production Verified → Costing Approved → Released (G4 Total MR Cost + Issued Qty ready)
4. MIS posted → G4 Issued Qty updates on Allocation; G8 Rate+Amount on BMR lines
5. Production: BMR → RM Consumption → Packing → FGHM (G6 Status auto-sets to Accepted)
6. SCE (G8 Rate+Amount) → MRT → FG Consumption
7. Open every report in R1–R7 → verify rows, aggregation, filters
8. Open every dashboard → verify KPI cards, charts, widgets

**Final:** update `reports.html` with G9 (FG reports). Commit + push.

---

## Verification Standard (per module)

1. **Seed** ≥3 test records with known values
2. **Run** every report → check correct rows, group-by, aggregation math, filter results
3. **Dashboard** widgets render from module reports
4. **Access** correct department (Purchase/Store/Production/Costing/Site)
5. **Git** commit + push to `origin/main`

---

## Creator-Native Note

All cross-form aggregates use **Deluge-updated fields** (G4/G5/G8), not Zoho Analytics. Every field addition is a native Creator field (AutoFetch, Formula, or Number updated by Deluge). No external tools.
