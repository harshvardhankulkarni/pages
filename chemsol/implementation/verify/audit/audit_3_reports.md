# Audit 3 — Reports & Dashboards

**Scope:** Reporting layer of the Chemsol Zoho Creator ERP repo. Cross-checks every report R1–R7 (type, source form, group-by, aggregations, filters, gap deps), the 8 R7 department dashboards (every widget), and schema-gap fields G1–G9, across `reports.html`, `REPORT_IMPLEMENTATION_PLAN.md`, `implementation/verify/flow_sim.py`, `forms.html`, and the `files/*.csv` exports.

**Evidence keys:** `RH` = chemsol/reports.html · `RP` = chemsol/REPORT_IMPLEMENTATION_PLAN.md · `FS` = chemsol/implementation/verify/flow_sim.py · `FH` = chemsol/forms.html · `IP` = chemsol/IMPLEMENTATION_PLAN.md · `AG` = chemsol/AGENTS.md · `CSV` = chemsol/files/*.csv

**Counts:** 59 reports defined (R1=8, R2=8, R3=12, R4=8, R5=10, R6=13). R7 = 8 dashboards / 53 widgets. G-gaps G1–G9 tracked: 2 gaps only PARTIALLY present in the field spec (G5 header Total Amount; G7 FG Category) — both BLOCKER/FIX.

---

## 1. Report register R1–R7

### R1 — Master Data Reports (Phase M1)

| Report | Source Form | Creator Type (+chart subtype) | Group By | Aggregations | Filters | Gap Dep | Evidence |
|---|---|---|---|---|---|---|---|
| Item Catalog | Purchase Item Muster | Detail | — | — | Status = Active | — | RH:359, RP:75 |
| Items by Category | Purchase Item Muster | Summary | Category | COUNT(Item Code), SUM(Max Stock) | — | — | RH:360, RP:76 |
| System Master List | System Master | Detail | — | — | Status = Active | — | RH:361, RP:77 |
| System → FG Composition | System Composition | Detail | System Code | — | Status = Approved/Released | — | RH:362, RP:78 |
| FG → RM BOM Matrix | BOM / FG Formulation | Detail | FG Code | — | Status = Approved/Released | — | RH:363, RP:79 |
| Supplier List | Supplier Master | Detail | — | — | Status = Active | — | RH:364, RP:80 |
| Customer / Site List | Customer / Site Master | Detail | — | — | Status = Active | — | RH:365, RP:81 |
| Store & Bin Register | Store Master | Detail | Store Type | — | — | — | RH:366, RP:82; FH:356 Store Type, FH:362 Bin Location subform |

**R1 ↔ plan agreement:** all 8 rows identical between RH:359–366 and RP:75–82. ✓

### R2 — Sales & Project Reports (Phase M2)

| Report | Source Form | Creator Type | Group By | Aggregations | Filters | Gap Dep | Evidence |
|---|---|---|---|---|---|---|---|
| Sales Register | Sales Order | Detail | — | — | Date range, Sales Type, Status | G1 | RH:382, RP:94; SO Status FH:419 |
| SO Value by Customer | Sales Order | Summary | Customer Code | SUM(Total Amount), COUNT(SO No) | — | — | RH:383, RP:95; Customer Code FH:406 |
| SO Type Split | Sales Order | Chart (Pie) | Sales Type | SUM(Total Amount) | — | — | RH:384, RP:96 |
| SO Value Trend | Sales Order | Chart (Line) | SO Date (month) | SUM(Total Amount) | Date range | — | RH:385, RP:97 |
| Project Status List | Project | Detail | Status | — | — | — | RH:386, RP:98 |
| Open Projects by PM | Project | Summary | Project Manager | COUNT(Project ID), SUM(Project Cost) | Status = Planned / In Progress | — | RH:387, RP:99; FH:478/481/482 |
| Project P&L Real-time | Project | Summary | Project ID | SUM(Total Revenue), SUM(Total Actual Cost), SUM(P&L) | — | G2 | RH:388, RP:100; FH:483–485 |
| Task Budget vs Actual | Project — Task Budget subform | Summary | Category | SUM(Budget Amount), SUM(Actual Amount) | Project ID | G2 | RH:389, RP:101; FH:501–516 |

**R2 ↔ plan agreement:** all 8 rows match (RH:382–389 vs RP:94–101). ✓

### R3 — Costing / Plan / MR Reports (Phase M3)

| Report | Source Form | Creator Type | Group By | Aggregations | Filters | Gap Dep | Evidence |
|---|---|---|---|---|---|---|---|
| Costing Sheet Status | Costing Sheet | Summary | Costing Status | COUNT(Costing No), SUM(Total Costing Amount) | — | G3 | RH:405, RP:113; FH:564 Costing Number, FH:569 Costing Status, FH:655 Total |
| Costing Register | Costing Sheet | Detail | — | — | Date range, Status | — | RH:406, RP:114 |
| Production Plan Register | Production Plan | Detail | — | — | Plan Status | — | RH:407, RP:115 |
| Plan Shortage Summary | Production Plan (line items) | Summary | RM Item Code | SUM(Shortage) | Shortage > 0 | — | RH:408, RP:116; FH:696 Shortage |
| MR Status Tracking | MR | Summary | MR Status | COUNT(MR Number) | — | — | RH:409, RP:117; FH:727/735 |
| MR Status per Project | MR | Pivot | Row: Project ID, Col: MR Status | COUNT(MR Number) | — | — | RH:410, RP:118 |
| Project Cost Baseline | MR | Summary | Project ID | SUM(Total MR Cost), SUM(Material + Application + Transportation + Tools) | — | G4 | RH:411, RP:119; FH:833 |
| Material Allocation vs Consumption | MR Allocation (subform) | Detail | Project ID | — | — | G4 | RH:412, RP:120; FH:760–779 |
| 80% Alert List | MR Allocation | Detail | — | — | Consumption % ≥ 80 AND Alert Flag = ON | — | RH:413, RP:121; FH:775/773 |
| Allocation Exhausted | MR Allocation | Detail | — | — | Consumption % ≥ 100 | — | RH:414, RP:122 |
| Costing vs Actual Variance | MR + SCE (lines) + BMR (lines) | Summary | Project ID | SUM(Total MR Cost), SUM(SCE Amount), SUM(BMR Amount) | — | G3, G8 | RH:415, RP:123; FH:1156–1157, FH:1483–1484 |
| Project Inventory Status | MR Allocation | Pivot | Row: Project ID, Col: Item Code | SUM(Assigned), SUM(Issued), SUM(Consumed), SUM(Returned) | — | G4 | RH:416, RP:124; FH:777–779 |

**R3 ↔ plan agreement:** all 12 rows match (RH:405–416 vs RP:113–124). ✓

### R4 — Procurement Reports, Stream A (Phase M4)

| Report | Source Form | Creator Type | Group By | Aggregations | Filters | Gap Dep | Evidence |
|---|---|---|---|---|---|---|---|
| PR Status Report | PR | Summary | Status | COUNT(PR Number) | — | — | RH:432, RP:136; FH:874 PR Status |
| Open PO Register | PO | Detail | — | — | Status ≠ Fully Received / Cancelled | G5 | RH:433, RP:137; FH:914 PO Status |
| PO Value by Supplier | PO | Summary | Supplier Code | SUM(Total Amount), COUNT(PO Number) | — | G5 (header Total Amount) | RH:434, RP:138; header Total Amount MISSING in FH/CSV (F1) |
| Purchase by Item Group | PO (line items) | Summary | ⚠ Item Category (RH) vs Item Code (RP) | SUM(Total Amount) | Date range | G5 | RH:435, RP:139; PO lines have no Category field (F3) |
| PO vs GRN Pending | PO line items | Detail | — | — | Balance Qty > 0 | G5 | RH:436, RP:140; FH:933 Balance Qty |
| Vendor Performance | PO | Summary | Supplier | COUNT(PO), AVG(Delivery Days) | — | G5 | RH:437 (⚠ "GRN date − PO date"), RP:141, FH:951 (GRN Date − Delivery Date) (F4) |
| GRN Register | GRN | Detail | — | — | Date range | — | RH:438, RP:142 |
| QC Results | QC | Summary | QC Status | COUNT(QC Number), SUM(Accepted Qty) | — | — | RH:439, RP:143; FH:1042 QC Status, FH:1040 Accepted Qty |

**R4 ↔ plan agreement:** 8 rows, but two mismatches — `Purchase by Item Group` group-by (Item Category vs Item Code, F3) and `Vendor Performance` delivery-days definition (F4).

### R5 — Production Reports (Phase M5)

| Report | Source Form | Creator Type | Group By | Aggregations | Filters | Gap Dep | Evidence |
|---|---|---|---|---|---|---|---|
| MIS Register | MIS | Detail | — | — | Date range, MR No | — | RH:455, RP:155 |
| MIS Issued vs Required | MIS (line items) | Summary | Item Code | SUM(Required Qty), SUM(Issued Qty) | Project ID, MR No | — | RH:456, RP:156; FH:1085–1088 |
| Pending MIS (Balance > 0) | MIS (line items) | Detail | — | — | Balance Qty > 0 | — | RH:457, RP:157; FH:1088 |
| Today's Production | BMR | Summary | FG Code | SUM(Yield / FG Output) | Date = Today | — | RH:458, RP:158; FH:1155; ⚠ sim proxies via FGHM accepted (F12) |
| Production Job Status | Production Job | Summary | Status | COUNT(Job No) | — | — | RH:459, RP:159; FH:1117 |
| Open Production Jobs | Production Job | Detail | — | — | Status = Scheduled / In Progress | — | RH:460, RP:160; FH:1117 |
| Daily Production Trend | BMR | Chart (Bar) | Date | SUM(FG Output) | Date range | — | RH:461, RP:161 |
| BMR vs BOM Variance | RM Consumption Entry | Detail | ⚠ FG Code (RH) vs BMR Reference (RP) | — | — | — | RH:462, RP:162; FG Code NOT on RM Consumption form (F5) |
| Production Efficiency | Packing Entry | Summary | FG Code | SUM(Packed Qty) | — | — | RH:463, RP:163; FH:1199 Packed Qty |
| FG Handover Pending | FGHM | Detail | — | — | Status = Pending Acceptance | G6 | RH:464, RP:164; FH:1223 |

**R5 ↔ plan agreement:** one mismatch — `BMR vs BOM Variance` group-by (FG Code vs BMR Reference, F5).

### R6 — Inventory / Site / Return Reports (Phase M6)

| Report | Source Form | Creator Type | Group By | Aggregations | Filters | Gap Dep | Evidence |
|---|---|---|---|---|---|---|---|
| RM Stock Status | RM Inventory | Detail | — | — | Reorder Status filter | — | RH:480, RP:176; FH:1329 |
| FG Stock Status | FG Inventory | Detail | — | — | Status filter | — | RH:481, RP:177; FH:1383 |
| Inventory Valuation | RM + FG Inventory | Summary | Category | SUM(Closing Stock × Standard Rate) | — | G7 | RH:482, RP:178; FH:1321/1376; FG ledger has NO Category (F2) |
| Reorder Alerts | RM Inventory | Detail | — | — | Reorder Status = Below Min | — | RH:483, RP:179 |
| Stock Movement Log | Stock Movement Transaction Log | Detail | Item Code | — | Date range, In/Out | — | RH:484, RP:180; FH:1528–1535 |
| Site Consumption Log | Site Consumption Entry | Detail | — | — | Project ID, Date, Work Area | — | RH:485, RP:181 |
| Consumption by Work Area | SCE (line items) | Summary | Project ID, Work Area | SUM(Qty Consumed) | — | — | RH:486, RP:182 |
| Consumption by RM Item | SCE (line items) | Summary | RM Item Code | SUM(Qty Consumed) | Project ID | — | RH:487, RP:183 |
| Consumption vs Allocation | MR Allocation | Pivot | Row: Project ID, Col: Item Code | SUM(Consumed Qty) | — | — | RH:488, RP:184 |
| Material Return Report | Material Return Entry | Detail | — | — | Project ID, Reason, Condition | — | RH:489, RP:185; FH:1508 Reason (header), FH:1521 Condition (line) |
| Returns by Condition | MRT (line items) | Summary | Condition | SUM(Return Qty) | — | — | RH:490, RP:186 |
| FG Consumption Log | FG Consumption Entry | Detail | — | — | Project ID, FG Code, Date | G9 | RH:491, RP:187; FH:1266–1283 |
| Project FG Position | FGHM + FG Consumption | Summary | Project ID, FG Code | FG Received − FG Consumed (SUM Received / SUM Consumed / SUM Remaining) | — | G9 | RH:492, RP:188; FH:1448 (FGHM.Accepted − Project_FG_Consumption.Used) |

**R6 ↔ plan agreement:** all 13 rows match (RH:480–492 vs RP:176–188). ✓

**R7 — Dashboards:** build matrix RH:498–519; per-phase dashboard table RP:198–207. Phase report counts in RP match R1–R6 counts (8/8/12/8/10/13). ✓

---

## 2. Dashboard widget map (R7)

Sources: RH:143–323 (department dashboards) + RH:508–515 (widget build table) + RP:200–207 (Phase M7 table).

| Dashboard | Widget | Widget Type | Referenced report | Exists? |
|---|---|---|---|---|
| **Purchase** | Total Purchase This Month | KPI | Purchase by Item Group (R4) | ⚠ group-by field issue (F3) |
| | Open POs | KPI | Open PO Register (R4) | ✓ |
| | Pending PR Approvals | KPI | PR Status Report (R4) | ✓ |
| | Purchase by Item Group | Chart (Bar) | R4 | ⚠ group-by field issue (F3) |
| | Vendor Delivery | Chart (Bar) | Vendor Performance (R4) | ✓ (F4 formula note) |
| | Open PO Register · PO vs GRN Pending | Report | R4 | ✓ |
| **Sales** | SO Count · SO Value (YTD) | KPI | Sales Register (R2) | ✓ |
| | SO Value Trend (Line) | Chart | R2 | ✓ |
| | SO Type Split (Pie) | Chart | R2 | ✓ |
| | Sales Register · Project Status | Report | R2 | ⚠ "Project Status" vs report name "Project Status List" (F13) |
| **MR / Costing** | MR Count by Stage | KPI | MR Status Tracking (R3) | ✓ |
| | Total MR Cost | KPI | Project Cost Baseline (R3) | ✓ |
| | MR Status (Funnel) | Chart | MR Status Tracking (R3) | ✓ |
| | Costing Status (Pie) | Chart | Costing Sheet Status (R3) | ✓ |
| | MR Status Tracking · Material Allocation vs Consumption | Report | R3 | ✓ |
| **Store** | RM Stock Value | KPI | RM Stock Status (R6) | ✓ |
| | Below-Min Items | KPI | Reorder Alerts (R6) | ✓ |
| | Stock by Category (Pie) | Chart | RM/FG Inventory group-by Category | ⚠ FG ledger has no Category (F2) |
| | Reorder Alerts (Bar) | Chart | R6 | ✓ |
| | RM Stock Status · FG Stock Status · Stock Movement Log | Report | R6 | ✓ |
| **Production** | Batches Today · Open Jobs · Pending MIS | KPI | Production Job / MIS (R5) | ✓ |
| | Daily Production (Bar) | Chart | Daily Production Trend (R5) | ✓ |
| | Job Status (Pie) | Chart | Production Job Status (R5) | ✓ |
| | MIS Register · Production Job Status · BMR vs BOM Variance | Report | R5 | ✓ (F5 group-by note) |
| **Site Supervisor** | Consumption Today · Active 80% Alerts | KPI | SCE / 80% Alert List (R6/R3) | ✓ |
| | Consumption by Area (Bar) · Consumption by RM (Bar) | Chart | R6 (Work Area / RM Item) | ✓ |
| | Site Consumption Log · Material Return Report | Report | R6 | ✓ |
| **Costing** | Costing Approvals · Project P&L Sum | KPI | Costing Sheet Status / Project P&L (R3/R2) | ✓ |
| | Costing vs Actual (Bar) · Project Inventory (Bar) | Chart | R3 | ✓ (cross-form caveat F9) |
| | Project Inventory Status · Costing vs Actual Variance | Report | R3 | ✓ |
| **Project Management** | Open Projects · Active POs per Project | KPI | Project Status List / PO | ⚠ contradicts plan "Open POs — Stream A" (F7) |
| | Project Status (Pie) · MR Status per Project (Bar) | Chart | R2 / R3 | ✓ |
| | Project Status · MR Status per Project · 80% Alert List | Report | R2 / R3 | ✓ (name variant F13) |

**Broken / at-risk references:** (1) Store "Stock by Category (Pie)" depends on FG Inventory `Category` — NOT in field spec (F2); (2) PM KPI "Active POs per Project" (RH:515) contradicts RP:207 "Open POs (POs carry no Project ID — Stream A)" — PO does carry an optional Project ID (FH:912), so both are possible but the two docs disagree (F7). All other widget → report references resolve to an existing R1–R6 report.

---

## 3. Gap-field check (G1–G9)

| Gap | Fields added | Present in forms.html / CSV? | Where (file:line) |
|---|---|---|---|
| G1 | SO `Status` dropdown (Draft / Accepted / Completed / Cancelled) | ✅ Present | FH:419 (SO header #18); CSV Sales_Order_Master.csv; used by R2 Sales Register (RH:382) |
| G2 | Project `Total Revenue` (AutoFetch SO Total) + `Total Actual Cost` (AutoFetch MR Total) + `P&L` formula + **Task Budget subform** | ✅ Present | FH:483, FH:484, FH:485; Task Budget subform FH:501–516 (Category / Description / Budget Qty / Rate / Budget Amount / Actual Qty / Actual Amount) |
| G3 | Costing Sheet 5 section subtotals (A–E) + `Total Costing Amount` formula | ✅ Present | FH:595 Section A Material Total, FH:610 B, FH:627 C, FH:641 D, FH:653 E, FH:655 Total Costing Amount; Costing Status FH:569, Costing Number FH:564 |
| G4 | MR `Total MR Cost` formula + Allocation `Issued Qty` (auto) | ✅ Present | FH:833 Total MR Cost; FH:777 Issued Qty (plus Returned Qty FH:778, Remaining FH:779 — C1 extras) |
| G5 | PO header `Status` + line `Received Qty` / `Balance Qty` / `Receipt Status` + header `Delivery Days` + header `Total Amount` | ⚠ **PARTIAL — header Total Amount MISSING** | Present: FH:914 Status, FH:932 Received, FH:933 Balance, FH:934 Receipt Status, FH:951 Delivery Days. Missing: numeric header Total Amount (RP:49 G5 requires Basic_Total + GST_Total) — forms.html footer has only Basic Total / CGST / SGST / IGST / Total Amount (Words) (FH:943–947); PO.csv footer identical → **F1** |
| G6 | FGHM `Status` dropdown (Pending Acceptance / Accepted) | ✅ Present | FH:1223 |
| G7 | RM/FG Inventory `Standard Rate` + FG ledger `Category` lookup | ⚠ **PARTIAL — FG Category MISSING** | Present: FH:1321 RM Standard Rate, FH:1376 FG Standard Rate, FH:1319 RM Category. Missing: Category on FG ledger (FH:1372–1384 lists no Category) → **F2** |
| G8 | SCE + BMR line `Rate` (AutoFetch) + `Amount` (formula) | ✅ Present (rate source wording differs) | FH:1156–1157 BMR Rate/Amount, FH:1483–1484 SCE Rate/Amount; RP:52 says "AutoFetch Standard Rate from Item Muster", forms.html says "AutoFetch (MR Allocation Rate)" — same value, different source path (**F8**) |
| G9 | reports.html R6: add FG Consumption Log + Project FG Position rows | ✅ Present | RH:491–492; form 5G FG Consumption Entry FH:1248–1290; Project FG Consumption Tracking (6C) FH:1406–1448 |

**G-fields MISSING from the field spec:**
- **G5 → PO header `Total Amount`** — not in forms.html or PO.csv (F1). Blocks R4 `PO Value by Supplier` (SUM(Total Amount)).
- **G7 → FG Inventory `Category`** — not in forms.html FG ledger 6B (F2). Blocks R6 `Inventory Valuation` group-by Category and Store "Stock by Category" chart.

All other G-fields (G1, G2, G3, G4, G6, G8, G9) are fully present in the field spec.

---

## 4. Findings log

| # | Severity | Description | Evidence |
|---|---|---|---|
| F1 | **BLOCKER** | G5 requires PO header `Total Amount` formula (= Basic_Total + GST_Total) for R4 `PO Value by Supplier`; forms.html footer has only Basic Total / CGST / SGST / IGST / Total Amount (Words), and PO.csv footer shows the same. No numeric header total → report unbuildable as spec'd. | RP:49, RH:434, FH:938–952, CSV PO.csv |
| F2 | **FIX** | G7 requires `Category` on FG Inventory; forms.html 6B fields (FH:1372–1384) have Standard Rate but NO Category. Breaks R6 Inventory Valuation group-by (RH:482) and Store dashboard Stock-by-Category pie (RH:511, RP:203). RM ledger already has it (FH:1319) — same fix applies. | RP:19, FH:1372–1384, RH:482/511 |
| F3 | **FIX** | `Purchase by Item Group` group-by differs: reports.html = "Item Category" (RH:435), plan M4 = "Item Code" (RP:139). PO line items AutoFetch only Name/HSN/GST%/UOM (FH:924) — no Category field on PO lines, so neither group-by is directly buildable. | RH:435, RP:139, FH:924 |
| F4 | **FIX** | `Vendor Performance` delivery-days definition differs: reports.html = "GRN date − PO date" (RH:437); G5 + forms.html = "GRN Date − Delivery Date" (FH:951, RP:48); flow_sim computes GRN 17 Jan − delivery 12 Jan = 5 days (FS:404–405). reports.html formula text is wrong; sim and field spec agree. | RH:437, FH:951, RP:48, FS:404–405 |
| F5 | **FIX** | `BMR vs BOM Variance` group-by differs: reports.html = FG Code (RH:462); plan M5 = BMR Reference (RP:162). RM Consumption Entry form has no FG Code field (FH:1175–1179 — Reference to BMR, Item-wise RM, Actual Qty, Standard Qty, Variance), so FG Code grouping requires a join via BMR. | RH:462, RP:162, FH:1175–1179 |
| F6 | INFO | Two G5 header PO Status values in RP vs FH: RP:44 lists "Draft / Sent / Partially Received / Fully Received / Cancelled" — matches FH:914 exactly. (Checked; no conflict — retained for completeness of the register.) | RP:44, FH:914 |
| F7 | INFO | Project Management KPI: reports.html = "Active POs per Project" (RH:515); plan M7 = "Open POs (POs carry no Project ID — Stream A)" (RP:207). PO has an optional Project ID field (FH:912), so "Active POs per Project" is only possible for tagged POs; the two docs are contradictory on the same KPI. | RH:515, RP:207, FH:912 |
| F8 | INFO | G8 rate source wording: plan says "AutoFetch Standard Rate from Item Muster" (RP:52); forms.html says "AutoFetch (MR Allocation Rate)" for both BMR (FH:1156) and SCE (FH:1483). Same value, different documented source path — non-blocking but should be aligned. | RP:52, FH:1156/1483 |
| F9 | INFO | Three R3/R6 "Summary" reports name 2–3 source forms (Costing vs Actual Variance = MR+SCE+BMR; Inventory Valuation = RM+FG; Project FG Position = FGHM+FG Consumption). Native Creator reports are single-form; cross-form aggregation is only possible via Deluge-consolidated tables. RP:242–244 (Creator-Native Note) acknowledges this for G4/G5/G8 fields; Project FG Position has a dedicated auto-created 6C tracking form (FH:1406–1448) that mitigates it. Build risk for the other two. | RH:415/482/492, RP:242–244, FH:1406 |
| F10 | INFO | `Costing vs Actual Variance` has 3 aliases: report row "Costing vs Actual Variance" (RH:415, RP:123), dashboard/core-list "Costing Sheet vs Actual Report" (RH:287, AG:189), widget "Costing vs Actual" (RH:514). Same report, inconsistent naming across docs. | RH:415/287/514, AG:189 |
| F11 | INFO | 80% alert report has 3 aliases: "80% Alert List" (RH:413, RP:121), "80% Consumption Alerts" widget (RH:197), "80% Consumption Alert Dashboard" core list (RH:202, 267). Naming noise only. | RH:413/197/202, RP:121 |
| F12 | INFO | flow_sim "Today's Production 448 kg" is computed from FGHM accepted quantities (148 + 300, FS:569), but R5 `Today's Production` report aggregates BMR `Yield / FG Output` (RH:458, FH:1155). The sim BMR records carry no yield field, so the assertion uses a proxy source — semantically the production-output metric, but not the report's exact source. All other REP assertions match their report specs exactly. | FS:567–569, RH:458 |
| F13 | INFO | "Project Status" widget names (RH:509, RH:515, RP:207) vs registered report name "Project Status List" (RH:386, RP:98). Also Production Job field is "Job Number" (FH:1108) while reports say COUNT(Job No) (RH:459). Cosmetic. | RH:386/509/515, FH:1108 |

**flow_sim.py REP sweep conformance (FS:552–576):** every REP assertion matches the R1–R7 specs — R1 seeds (FS:553–555); R2 Sales Register 175,000 / Project In Progress / Task Budget 50,200 (FS:556–558); R3 Costing 1 Approved 146,000 / MR Released 144,000 baseline / ≥2 80% alerts (FS:559–561); R3 variance planned 144,000 vs actual BMR+SCE 106,730 → 37,270 (FS:562–564); R4 Open PO Register empty / Vendor Performance AVG 5 days (FS:565–566); R5 MIS 275/125 issued / FG Handover Pending empty (FS:567–569); R6 RM stock 10/285, valuation 10×220 + 285×340 = 99,100, SCE log 1 accepted, FG position FG-003 20 (FS:570–574); R7 dashboard sources traceable (FS:575–576). No failed assertions.

---

## Summary

- **59 reports** registered (R1=8, R2=8, R3=12, R4=8, R5=10, R6=13), **8 R7 dashboards**, **53 dashboard widgets**.
- **reports.html ↔ REPORT_IMPLEMENTATION_PLAN.md:** fully agree on 55 of 59 report rows; 4 substantive disagreements (F3 group-by, F4 delivery-days formula, F5 group-by, F7 PM KPI wording).
- **G1–G9 field check:** 7 gaps fully present in the field spec; **2 partially missing — G5 PO header Total Amount (F1, BLOCKER) and G7 FG Inventory Category (F2, FIX)**.
- **flow_sim.py REP assertions:** all consistent with the report specs (2 minor INFO notes F12).
- **Output file:** `chemsol/implementation/verify/audit/audit_3_reports.md`
