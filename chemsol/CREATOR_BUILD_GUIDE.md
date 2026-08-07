# Chemsol — Zoho Creator Build Guide (Verified Structure Reference)

> Written for a developer building this ERP in Zoho Creator for the **first time**. Every loop stage below lists: the forms you must build, every field with its **exact Zoho Creator field type**, every automation (construct → trigger → action → Deluge file), and every report (type → source form → group-by → aggregations → filters). All content verified against the source-of-truth stack (see Part 8) on 2026-08-06.
>
> STATUS: full structure audit completed 2026-08-06 (4 parallel audits: fields / automations / reports / loop-map). Findings consolidated in `chemsol/VERIFICATION_FINDINGS.md`; detailed audit workbooks in `chemsol/implementation/verify/audit/`.

## How to use this guide

- Build forms in the order of Parts 2 → 3 → 4 (master data first, then transactional, then cross-cutting).
- Field names in `code` are the **exact API names** used by the Deluge scripts (`forms.html` is the naming authority).
- "Auto by Deluge <file>" in the Notes column = the field is **written by automation** — make it read-only / non-user-editable in the console.
- The **process loop** in Part 1 is the backbone. Every stage must exist end-to-end: forms → automation → report. The loop-map audit confirmed **12/12 stages pass** the ≥1 automation + ≥1 report gate.
- After each part, run the console checks listed in Part 7, then the simulator (`flow_sim.py`, currently **77/77 green**).
- Zoho Creator field-type vocabulary used below: **Text** (single line), **Multi-line Text**, **Number**, **Currency**, **Percent**, **Date**, **Date/Time**, **Checkbox**, **Dropdown**, **Lookup** (linked record), **Formula** (computed), **Auto Number** (creator autonumber), **Subform** (child table), **User** (user picker), **Email**, **URL**, **File Upload**, **Image**, **Phone**.

---

## Part 0 — Platform setup (do once, ~2 hours)

1. [ ] Create the app **"Chemsol"** in Zoho Creator (accounts.zoho.in; the .in data center is the deployment target).
2. [ ] Create the **No_Series counter form** (fields: `Prefix` Text, `Year` Number, `Last_Number` Number). Every prefixed document reads/writes it via the `numberSeries({prefix: ...})` Deluge function (A-43). **Do not use Creator's built-in Auto Number** for document numbers — the spec's numbering series are centralized here so prefixes and resets are controllable.
3. [ ] Master-data forms (Part 2.0) — these must exist before any transactional form because lookups reference them.
4. [ ] Permission sets (F14): only Purchase and Store roles may see `Standard_Rate` on item forms; Costing sees rates on the Costing Sheet; everyone else sees hidden/read-only rates.
5. [ ] Departments (User Access & Approval Matrix): Purchase, Sales, Store & Logistics, Account & Finance, Admin, Project Coordinator, Project Manager 1/2/3, Production, Quality.
6. [ ] Warehouses (Store Master records): Wadki, Main, Neelo, Gurgaon, Bangalore, Client Site.
7. [ ] System codes for item prefixes: EP = Epoxy, PU = PU Flooring, DEM = Demarcation, ANTI = Anti Static, ESD, FIL = Coving; RM-xxx raw materials, FG-xxx finished goods.

---

## Part 1 — The process loop at a glance

```
SO (Sales Order)                                ← Stage 1 (dual mode: Supply+Apply vs Supply Only)
  → Costing Sheet (5 sections, auto-expanded)   ← Stage 2 (A-09 expandCosting)
    → Costing Approved → Project + Production Plan  ← Stage 3 (A-11 chain)
      → Plan Released → stock check → auto-PR   ← Stage 4 (A-13/A-14)
        → MR auto-derived + cross-validated     ← Stage 5 (A-15/A-16)
          → MR 5-state gate + SLA reminders     ← Stage 6 (A-17/A-19/A-20)
            → MR Released → auto-MIS            ← Stage 7 (A-18)
              → MIS posted → RM stock −         ← Stage 7 (A-31)
                → Production (Job→BMR→Consumption→Packing→FGHM)  ← Stage 8 (A-32…A-37)
                  → Site Consumption (SCE)      ← Stage 9 (A-38)
                    → Material Return (MRT)     ← Stage 9 (A-40)
                      → Project Close → P&L     ← Stage 10 (A-12/G2)

Stream A side loop (no Project ID): PR → PO → GRN → QC   ← A-21…A-29
Cross-cutting: master data, stock ledger, movement log, alerts, SLA, notifications
```

Stages map: **1** SO entry · **2** Costing Sheet · **3** Costing Approved → Project+Plan · **4** Plan Released → auto-PR · **5** MR derive+cross-validate · **6** MR 5-state gate · **7** MIS + store issue · **8** Production · **9** SCE + MRT · **10** Project Close → P&L · **SA** Stream A · **X** Cross-cutting.

---

## Part 2 — Loop stages (Stream B, project-rooted)

### Stage 1 — Sales Order entry (dual mode)

**Forms to build:** `Sales Order Master` (with **Subform A System Lines** + **Subform B FG Lines**), `Customer/Site Master`.

**Sales Order Master — header fields (28):**

| # | Field | Creator field type | Req | Notes |
|---|-------|--------------------|-----|-------|
| 1 | `SO_Number` | Text | * | Written by `numberSeries({prefix:"SO"})` (SO-YYYY-XXXX); read-only |
| 2 | `Sales_Type` | Dropdown: Supply+Apply / Supply Only | * | **G1** — decides which subform shows (A-06) |
| 3 | `SO_Date` | Date | * | |
| 4 | `Customer_Code` | Lookup (Customer/Site Master) | * | AutoFetch: name, address, GST |
| 5 | `Site_Address` | Lookup (Customer/Site Master) | * | Delivery site |
| 6 | `Sales_Type_2`…`14` | Text / Dropdown / Date | | SO terms: payment, delivery, validity, remarks |
| 15 | `Project_ID` | Lookup (Project) | | Filled at Costing approval (Stage 3); blank on Supply Only |
| 16 | `Status` | Dropdown: Draft / Accepted / Completed / Cancelled | * | **G1** — used by R2 Sales Register |
| 17 | `Total_Amount` | Formula | | = SUM(Subform A line Amount) or SUM(Subform B line Amount) |
| 18 | `Accepted_At` | Date/Time | | A-07 sets it |

**Subform A — System Lines (7 fields):** `System_Code` Lookup (System Master), `System_Name` Text (AutoFetch), `Area` Number (sqm), `Rate` Currency, `CompQty` Number (auto from System Composition), `Amount` Formula (= Area × Rate), `Remarks` Text.
**Subform B — FG Lines (6 fields):** `FG_Code` Lookup (FG from Item Muster), `FG_Name` Text (AutoFetch), `Quantity` Number, `Rate` Currency, `Amount` Formula, `Remarks` Text.

**Automations (Stage 1):**
- **A-06** (SO dual-mode subform swap): Form workflow On Load / On Submit — if `Sales_Type = Supply Only` show Subform B, else Subform A. Deluge: inline.
- **A-07** (SO accept → Costing Sheet Draft): On Record Modified, criteria `Status = Accepted` → create Costing Sheet Draft with SO reference. Deluge: `costing/expandCosting.deluge` (accept branch). **C2**: Project is NOT created here — only at Costing approval.
- **A-08** (line Amount + Total): Formula fields (no Deluge needed; verify they compute).

**Reports (Stage 1) — R2 family (8):**

| Report | Creator type | Source form | Group-by | Aggregations | Filters |
|--------|-------------|-------------|----------|--------------|--------|
| Sales Register | Detail | Sales Order Master | — | — | Date range, Sales Type, Status |
| SO Value by Customer | Summary | Sales Order Master | Customer Code | SUM(Total Amount), COUNT(SO No) | — |
| SO Type Split | Chart (Pie) | Sales Order Master | Sales Type | SUM(Total Amount) | — |
| SO Value Trend | Chart (Line) | Sales Order Master | SO Date (month) | SUM(Total Amount) | Date range |
| Project Status List | Detail | Project | — | — | — |
| Open Projects by PM | Summary | Project | Project Manager | COUNT(Project ID), SUM(Project Cost) | Status = Planned / In Progress |
| Project P&L Real-time | Summary | Project | Project ID | SUM(Total Revenue), SUM(Total Actual Cost), SUM(P&L) | — |
| Task Budget vs Actual | Summary | Project — Task Budget subform | Category | SUM(Budget Amount), SUM(Actual Amount) | Project ID |

---

### Stage 2 — Costing Sheet (5 sections/subforms, auto-expanded)

**Form to build:** `Costing Sheet` (header + Section A..E subforms + totals).

**Header (9 fields):**
`Costing_Number` Text (CST-YYYY-XXXX, numberSeries, read-only) · `SO_Reference` Lookup (Sales Order Master) * · `Costing_Status` Dropdown: Draft / Under Review / Approved / Rejected * · `Prepared_By` User (AutoLookup login) * · `Reviewed_By` Lookup (User) · `Revision_No` Number · `Project_ID` Lookup (Project) (filled at approval) · `Date` Date · `Remarks` Text.

**Section A — Material Cost Subform (`Costing_Material_Lines` — FG-based, NO RM rows):**
`System_Code` Lookup (Item Master) · `System_Name` Text (AutoFetch) · `FG_Code` Lookup (Item Master — FG) · `FG_Name` Text (AutoFetch) · `UOM` Text (AutoFetch) · `Area` Number (from SO) · `Qty_Per_Sqm` Number (from System Composition) · `Required_FG_Qty` Formula = `round(Area × Qty_Per_Sqm, 1)` · `Unit_Rate` Currency (AutoFetch BOM roll-up: Σ Ratio × Standard_Rate) · `Material_Cost` Formula = `Required_FG_Qty × Unit_Rate`.
*Note:* Section A lists FG products with BOM roll-up rates. It contains **NO Raw Material (RM)** rows.

**Section B — Application Cost Subform (`Costing_Application_Lines`):** `Work_Area` Text, `Description` Text, `Rate` Currency, `Qty` Number, `Amount` Formula.
**Section C — Transport Cost Subform (`Costing_Transport_Lines`):** vehicle/site fields + `Amount` Formula.
**Section D — Tools & Tackles Subform (`Costing_Tools_Lines`):** tool fields + `Amount` Formula.
**Section E — Overhead & Misc Subform (`Costing_Overhead_Lines`):** `Label` Text, `Amount` Currency (never included in MR cost — C20).
**Totals:** `Sec_A_Total` Formula, `Sec_B_Total` Formula, `Sec_C_Total` Formula, `Sec_D_Total` Formula, `Sec_E_Total` Formula, `Total_Costing_Amount` Formula = A+B+C+D+E (G3).

**Automations (Stage 2):**
- **A-09** (Section A expansion): On Record Created / Recalculate → expand SO × System Composition into `Costing_Material_Lines` FG lines (with rates calculated from BOM roll-up). Deluge: `costing/expandCosting.deluge`.
- **A-10** (approval Blueprint): Costing Status Blueprint Draft → Under Review → Approved / Rejected (Approved requires Section A non-empty).
- **A-08-adjacent / costingSlaEscalate**: schedule every 30 min — Costing stuck in Under Review > **4 hr → reminder email; > 24 hr → escalation to Costing Head** (F11). Deluge: `costing/costingSlaEscalate.deluge`.

**Reports (Stage 2) — R3 first 3:**
- Costing Sheet Status — Summary — Costing Sheet — group Costing_Status — COUNT(Costing No), SUM(Total Costing Amount).
- Costing Register — Detail — Costing Sheet — filters Date range, Status.
- Production Plan Register — Detail — Production Plan — filter Plan Status.

---

### Stage 3 — Costing Approved → Project + Production Plan

**Forms:** `Project` (header + **Systems subform** + **Task Budget subform**), `Production Plan` (header + lines subform).

**Project header (15 fields):** `Project_ID` Text (PRJ-YYYY-XXXX, numberSeries, read-only) · `Project_Name` Text * · `Project_Manager` User * · `Client` Lookup (Customer/Site) · `Site` Lookup · `Project_Status` Dropdown: Planned / In Progress / Completed / On Hold * · `Total_Revenue` Currency (**G2** — AutoFetch = SO Total, set by A-11) · `Total_Actual_Cost` Currency (**G2** — AutoFetch = MR Total, set by A-12 at MR Release) · `P_L` Formula = Total_Revenue − Total_Actual_Cost (**G2** — real-time, not just at close) · `SO_Reference` Lookup · `Start_Date` / `End_Date` Date · `Budget_Total` Currency · `Remarks` Text · `Created_At` Date/Time.

**Task Budget subform (7):** `Category` Dropdown (Material/Application/Transport/Tools/Labour/Other) · `Description` Text · `Budget_Qty` Number · `Rate` Currency · `Budget_Amount` Formula · `Actual_Qty` Number · `Actual_Amount` Formula.

**Production Plan header (8):** `Plan_Number` Text (PLAN-YYYY-XXXX) · `Plan_Status` Dropdown: Draft / Released * · `Project_ID` Lookup (Project) · `Costing_Ref` Lookup (Costing Sheet) · `Plan_Date` Date · `Total_Shortage` Number (auto) · `Released_At` Date/Time · `Remarks` Text.
**Plan lines (8):** `FG_Code` Lookup (Item Muster — FG category) · `FG_Name` Text (AutoFetch from FG_Code) · `Plan_Qty` Number (from Costing §A Required_FG_Qty) · `UOM` Text (AutoFetch from Item Muster via FG_Code) · `Available_FG_Stock` Number (AutoFetch from FG Inventory) · `Shortage` Formula = max(0, Plan_Qty − Available_FG_Stock) · `Source` Dropdown: Stock / Purchase / Both · `Procurement_Triggered` Checkbox (auto).

**Automations (Stage 3):**
- **A-11** (chain creation): On Record Modified (Costing Sheet), criteria Costing_Status = Approved → **create Project + Production Plan Draft in ONE chain**, set Project.Total_Revenue = SO Total, notify Production + PM email. Deluge: `costing/costingApproveChain.deluge`. **C2: Project is created here — single creation point, never before.**
- **A-12** (Project cost set / G2): on MR Released, Project.Total_Actual_Cost = MR Total. Deluge: `mrGate/mrReleaseAutoMIS.deluge` (G2 hook).

**Reports (Stage 3):** R2 Project Status List / Open Projects by PM / Project P&L Real-time / Task Budget vs Actual (see Stage 1 table) + R3 Production Plan Register (see Stage 2).

---

### Stage 4 — Plan Released → Available Stock check → auto-PR

**Automations (Stage 4):**
- **A-13** (getAvailableStock): custom function — Available = physical stock − Σ(Assigned Qty from all **unreleased** MRs) — prevents double-allocation. Deluge: `costing/getAvailableStock.deluge`.
- **A-14** (auto-PR): On Record Modified (Production Plan), criteria Plan_Status = Released → for each FG line where FG Shortage > 0, explode BOM to derive RM requirements = FG Shortage × BOM Ratio; check available RM stock; create **PR (Purchase Requisition)** draft lines for RM shortages, set Procurement_Triggered = true. Deluge: `costing/planReleaseAutoPR.deluge`.

**Reports (Stage 4):**
- Plan Shortage Summary — Summary — Production Plan line items — group FG Code — SUM(Shortage) — filter Shortage > 0 (FG-level shortage).
- PR Status Report — Summary — PR — group Status — COUNT(PR Number).

---

### Stage 5 — MR auto-derive + cross-validation

**Form:** `Material Requisition (MR)` — header + **Material Allocation subform (17 fields)** + Application/Transport/Tools cost subforms + Total. **Single line table rule (F4): MR has NO separate Line Items table — Material Allocation is the one and only line table.**

**MR header (11):** `MR_Number` Text (MR-YYYY-XXXX, read-only) · `Project_ID` Lookup (Project) * · `MR_Status` Dropdown **5-state**: Draft / Pending Production Verification / Production Verified / Costing Approved / Released * (C30/F11 — never a 4-state build) · `SO_Reference` Lookup · `Costing_Ref` Lookup · `MR_Date` Date · `Last_Status_Change` Date/Time (auto, C32) · `SLA_Reminder_Sent` Checkbox (auto, C32 — guard: fires once) · `Total_MR_Cost` Formula (G4) · `Remarks` Text · `Auto_Generated` Checkbox.

**Material Allocation subform (17):**
`Item_Code` Lookup (Item Muster — RM) · `Item_Name` Text (AutoFetch) · `Category` Text (AutoFetch) · `UOM` Text (AutoFetch) · `Assigned_Qty` Number * (defaults from Costing §A) · `Allocation_Ratio` Formula (= Assigned / Σ Assigned) · `Rate` Currency (from Costing §A) · `Amount` Formula · `Issued_Qty` Number (auto, A-31) · `Consumed_Qty` Number (auto, A-33/A-38) · `Returned_Qty` Number (auto, A-40) · `Remaining_Qty` Formula = Assigned − Consumed + Returned · `Consumption_Percentage` Formula = Consumed/Assigned×100 · `80%_Alert_Flag` Checkbox (auto, A-20) · `100%_Alert_Flag` Checkbox (auto, A-20) · `Variance_Percentage` Number (auto, A-16 — **per line, C31**) · `Variance_Flag` Checkbox (auto, A-16 — **per line, C31**).

**MR cost subforms:** Application (5), Transport (5), Tools (4) — mirror Costing Sections B/C/D amounts; **Section E is never included** (C20).

**Automations (Stage 5):**
- **A-15** (mrDerive): custom function — MR auto-derived from Costing Sheet: 4 cost components (Material/Application/Transport/Tools) + Material Allocation rows from Costing §A — **zero manual re-entry**. Deluge: `mrGate/mrDerive.deluge`.
- **A-16** (crossValidate): On Submit (MR) — per-RM: `diff = |Assigned − BOM expected| / expected × 100`. Any line > 10% → **block** (throw); any line > 5% → set `Variance_Flag` on **that line only** (C31 — per-RM, not aggregate). Deluge: `mrGate/crossValidate.deluge` (per-line write pattern).

**Reports (Stage 5) — R3:**
- MR Status Tracking — Summary — MR — group MR_Status — COUNT(MR Number).
- MR Status per Project — **Pivot** — Row: Project ID, Col: MR Status — COUNT(MR Number).
- Project Cost Baseline — Summary — MR — group Project ID — SUM(Total MR Cost) + 4 components (G4).
- Material Allocation vs Consumption — Detail — MR Allocation — group Project ID (G4).
- 80% Alert List — Detail — MR Allocation — filter Consumption_Percentage ≥ 80 AND 80%_Alert_Flag = ON.
- Allocation Exhausted — Detail — MR Allocation — filter Consumption_Percentage ≥ 100.
- Project Inventory Status — **Pivot** — Row: Project ID, Col: Item Code — SUM(Assigned/Issued/Consumed/Returned) (G4).

---

### Stage 6 — MR 5-state approval gate + SLA

**Blueprint (A-17):** MR_Status 5-state Blueprint: Draft → Pending Production Verification → Production Verified → Costing Approved → Released. Only canonical transitions allowed (C30/F11).

**Automations (Stage 6):**
- **A-17** Blueprint transitions as above.
- **A-19** (mrSlaSchedules): schedule every 30 min — Draft > 2 hr → reminder (once, SLA_Reminder_Sent guard); Production Verified > 2 hr → escalation; Costing Approved > 1 hr → auto-release. Deluge: `mrGate/mrSlaSchedules.deluge` (F10). **SLA reminder fires once — don't remove the guard (C32).**
- **A-18** (MR Released → auto-MIS Draft): On Record Modified, MR_Status = Released → create MIS Draft (header + lines from Material Allocation, NOT one record per line — F5), email store + production + PM. Deluge: `mrGate/mrReleaseAutoMIS.deluge`.
- **A-20** (checkAllocationAlert): shared custom function — 80% alert (pop-up + dashboard + email within 1 min of breach); 100% "Allocation Exhausted" → PM + Purchase. Deluge: `shared/checkAllocationAlert.deluge`.

**Reports (Stage 6):** MR Status Tracking / MR Status per Project / 80% Alert List / Allocation Exhausted (Stage 5 table) + R7 MR/Costing dashboard.

---

### Stage 7 — MIS (auto-created) → Store issues RM

**Form:** `Material Issue Slip (MIS)` — header (5) + MIS_Line_Items subform (6) + footer (3).

**Header:** `MIS_Number` Text (**MIS-YYYY-XXXX** — F9; autogen at MR Release, read-only) · `MR_Ref` Lookup (MR — filtered Released only, F6) * · `Project_ID` Lookup (Project) * · `Date` Date · `Status` Dropdown: Draft / Posted (C17).
**Lines (6):** `Item_Code` Lookup · `Item_Name` Text (AutoFetch) · `Required_Qty` Number (from Allocation) · `Issued_Qty` Number · `Balance_Qty` Formula = Required − Issued · `UOM` Text (AutoFetch).
**Footer (3):** `Posted_By` User · `Posted_Time` Date/Time · `Remarks` Text.

**Automations (Stage 7):**
- **A-18** auto-creates the MIS Draft on MR Release (see Stage 6).
- **A-30** (Released-only lookup filter): MIS MR_Ref Lookup restricted to MR_Status = Released (F6).
- **A-31** (postMIS): Report custom button "Post MIS" — validate stock ≥ Issued (else block), RM stock −, Issued_Qty + on allocation (G4), movement log rows, Status → Posted, email Production. Deluge: `production/postMIS.deluge`.

**Reports (Stage 7) — R5:**
- MIS Register — Detail — MIS — filters Date range, MR No.
- MIS Issued vs Required — Summary — MIS line items — group Item Code — SUM(Required), SUM(Issued) — filters Project ID, MR No.
- Pending MIS — Detail — MIS line items — filter Balance_Qty > 0.

---

### Stage 8 — Production (Job → BMR → RM Consumption → Packing → FGHM)

**Forms (5):**
1. **Production Job** (10): `Job_Number` Text (JOB-YYYY-XXXX) · `Project_ID` Lookup · `MR_Ref` Lookup (AutoFetch from MR) · `FG_Code` Lookup · `Planned_Qty` Number · `Status` Dropdown: Scheduled / In Progress / Completed · `Start_Date`/`Due_Date` Date · `Assigned_To` User · `Remarks` Text. (Numbering + MR-autofetch only — register as A-44/A-45 in AUTOMATION_ALIGNMENT_PLAN; orphan #8.)
2. **BMR** (6 header + 8 line): `BMR_Number` Text (BMR-YYYY-XXXX) · `Project_ID` Lookup · `FG_Code` Lookup (AutoFetch BOM lines — A-32) · `BMR_Status` Dropdown · `Date` Date · `Batch_Number` Text. Lines (8): `RM_Item_Code` Lookup · `RM_Name` Text (AutoFetch) · `Standard_Qty` Number (BOM) · `Qty_Consumed` Number * · `Rate` Currency (AutoFetch — G8) · `Amount` Formula (G8) · `UOM` Text (AutoFetch) · `Remarks`.
3. **RM Consumption Entry** (5): `Consumption_No` Text (RC-YYYY-XXXX) · `BMR_Reference` Lookup (BMR) * · `RM_Item_Code` Lookup · `Actual_Qty` Number · `Variance` Formula = Actual − Standard (**does NOT increment allocation — C25**).
4. **Packing Entry** (5): `Packing_No` Text · `Project_ID` Lookup · `FG_Code` Lookup · `Packed_Qty` Number · `Packaging_Material_Items` subform (Packing deducts packaging from inventory only — A-35).
5. **FGHM** (5 header + 10 line): `FGHM_Number` Text (FGH-YYYY-XXXX) · `Project_ID` Lookup · `FGHM_Status` Dropdown: Pending Acceptance / Accepted (**G6**) · `Date` Date · `Accepted_At` Date/Time (G6). Lines (10): `FG_Product_Code` Lookup · `FG_Name` Text (AutoFetch) · `FG_Qty` Number · `Damaged_Qty` Number · `Accepted_Qty` Formula = FG_Qty − Damaged_Qty · `UOM` Text (AutoFetch) · `Rate`/`Amount` · `Remarks` · `Reject_Reason` Text. **No separate FGAN form — inline acceptance only (forms.html:1214).**

**Automations (Stage 8):**
- **A-32** (BMR BOM autofetch): On Load — FG_Code → BOM lines prefilled. Deluge: `production/bmrSubmit.deluge`.
- **A-33** (BMR consume): BMR submit → Consumed_Qty + on allocation via `consumeAllocation`, block > 100% (C13). Deluge: `production/consumeAllocation.deluge`.
- **A-34** (RC variance formula): RM Consumption Entry → Variance formula (C25). Deluge: `production/bmrSubmit.deluge` (variance branch).
- **A-35** (packing deduction): Packing Entry submit → packaging stock −. Deluge: `production/packingDeduct.deluge`.
- **A-36** (FGHM inline accept): Report button "Accept" — Status → Accepted, FG stock + (stockMoveFG), notify. Deluge: `production/fghmAccept.deluge`.
- **A-37** (Fully Consumed): FGHM accept checks **ALL** project allocations ≥ 100% before setting `Fully_Consumed = true` — one line at 99.6% keeps it OFF (C14/C29).

**Reports (Stage 8) — R5:**
- Today's Production — Summary — BMR — group FG Code — SUM(Yield/FG Output) — filter Date = Today.
- Production Job Status — Summary — Production Job — group Status — COUNT(Job No).
- Open Production Jobs — Detail — Production Job — filter Status = Scheduled / In Progress.
- Daily Production Trend — Chart (Bar) — BMR — group Date — SUM(FG Output) — Date range.
- BMR vs BOM Variance — Detail — RM Consumption Entry — **group BMR Reference** (F8 — FG Code is not on the form).
- Production Efficiency — Summary — Packing Entry — group FG Code — SUM(Packed Qty).
- FG Handover Pending — Detail — FGHM — filter Status = Pending Acceptance (G6).

---

### Stage 9 — Site Consumption Entry + Material Return

**Forms (2):**
1. **Site Consumption Entry (SCE)** (7 header + 7 line): `Consumption_No` Text (**SCE-YYYY-XXXX**) · `Project_ID` Lookup * · `Work_Area` Text * · `Date` Date/Time * · `Entry_Type` Dropdown: Hourly / Daily · `Posted_By` User · `Status` Dropdown: Draft / Posted. Lines (7): `RM_Item_Code` Lookup · `RM_Name` Text (AutoFetch) · `Qty_Consumed` Number * · `Consumption_Type` Dropdown: Actual / Wastage / Rework * · `Rate` Currency (AutoFetch — G8) · `Amount` Formula (G8) · `UOM` Text (AutoFetch).
2. **Material Return Entry (MRT)** (6 header + 5 line): `Return_No` Text (**MRT-YYYY-XXXX**) · `Project_ID` Lookup * · `Warehouse` Dropdown (6 stores) * · `Return_Date` Date · `Reason` Text · `Status` Dropdown: Draft / Posted. Lines (5): `RM_Item_Code` Lookup · `RM_Name` Text (AutoFetch) · `Return_Qty` Number * · `Condition` Dropdown: Good / Unused / Damaged / Expired * · `UOM` Text (AutoFetch).

**Automations (Stage 9):**
- **A-38** (SCE): On Submit — validate **ALL** lines first (if ANY line > 100% the WHOLE submit is rejected — C21); Consumed_Qty + per line; 80%/100% alerts via A-20 (C5/C13/C18). Deluge: `site/sceSubmit.deluge` + `production/consumeAllocation.deluge`.
- **A-40** (MRT): On Submit — Return_Qty ≤ Consumed_Qty (else throw); Consumed_Qty −, Returned_Qty + (C12); Good/Unused → stock restore via stockMoveRM; Damaged/Expired → no stock credit; email Store. Deluge: `site/materialReturn.deluge`.
- **F12 §8.7 notifications**: <20% allocation remaining → PM + Purchase early-warning (daily check in `site/inventoryAlerts.deluge`).

**Reports (Stage 9) — R6:**
- Site Consumption Log — Detail — SCE — filters Project ID, Date, Work Area.
- Consumption by Work Area — Summary — SCE lines — group Project ID, Work Area — SUM(Qty Consumed).
- Consumption by RM Item — Summary — SCE lines — group RM Item Code — SUM(Qty Consumed) — filter Project ID.
- Consumption vs Allocation — **Pivot** — MR Allocation — Row: Project ID, Col: Item Code — SUM(Consumed Qty).
- Material Return Report — Detail — MRT — filters Project ID, Reason, Condition.
- Returns by Condition — Summary — MRT lines — group Condition — SUM(Return Qty).

---

### Stage 10 — Project Close → P&L

**Automation:** A-12 sets Project.Total_Actual_Cost at MR Released (G2) → P&L formula (Total_Revenue − Total_Actual_Cost) is real-time all along; Project Close sets Project_Status = Completed + close notification (reports.html:686).

**Reports:** Project P&L Real-time (R2), Costing vs Actual Variance (R3 — Summary — MR + SCE lines + BMR lines — group Project ID — SUM(Total MR Cost), SUM(SCE Amount), SUM(BMR Amount) — G3/G8), R7 Costing + Project Management dashboards.

---

## Part 3 — Stream A side loop (no Project ID required)

PR → PO → GRN → QC. **Project ID is OPTIONAL on PR/PO/GRN** (B2/B3 — project-tagged procurement only; Stream A stock purchases leave it blank).

**PR (7 header + 6 line):** `PR_Number` Text (PR-YYYY-XXXX) · `Department` Dropdown (auto from login) · `PR_Status` Dropdown: Draft / Pending Approval / Approved / Rejected · `Project_ID` Lookup (**optional**) · `Requested_By` User · `Date` Date · `Remarks`. Lines (6): `Item_Code` Lookup · `Item_Name` Text (AutoFetch) · `Qty` Number · `UOM` Text (AutoFetch) · `Lead_Time` Number (AutoFetch) · `Remarks`.

**PO (10 header + 14 line + 10 footer):** `PO_Number` Text (**RMWAD-YYYY-XXXX** coding / **RM-YYYY-XXXX** non-coding — A-23 dual prefix) · `PO_Type` Dropdown: Coding / Non-Coding · `PR_Reference` Lookup · `Supplier_Code` Lookup (Supplier Master — AutoFetch name/GST/address) · `Supplier_State` Text (GST split basis) · `Project_ID` Lookup (**optional** — B2) · `PO_Status` Dropdown: Draft / Sent / Partially Received / Fully Received / Cancelled (**G5**) · `PO_Date` Date · `Delivery_Date` Date · `Delivery_Days` Number (**G5** = GRN Date − Delivery Date).
Lines (14): `Item_Code` Lookup → AutoFetch Name/HSN/GST%/UOM/**Category** · `Item_Name_HSN` Text (AutoFetch) · `Category` Text (AutoFetch) (optional group-by source — F7) · `Quantity` Number · `Rate` Currency · `Basic_Amount` Formula = Qty×Rate · `GST_Percent` Percent (AutoFetch) · `GST_Amount` Formula · `CGST` Formula (= GST/2) · `SGST` Formula · `IGST` Formula · `Total_Amount` Formula = Basic+GST · `Received_Qty` Number (**G5**) · `Balance_Qty` Formula = Qty − Received (**G5**) · `Receipt_Status` Formula: Complete/Partial/Not Started (**G5**).
Footer (10): `Basic_Total` Formula · `CGST_Total` Formula · `SGST_Total` Formula · `IGST_Total` Formula · `Total_Amount` Formula = Basic + CGST + SGST + IGST (**G5 — added 2026-08-06, F1**) · `Total_Amount_Words` Formula · `Scope_of_Transport` Text · `Mode_of_Transport` Dropdown · `Payment_Terms` Text · `Remarks`.

**GRN (11 header + 7 line + 4 Transport subform):** `GRN_Number` Text (GRN-YYYY-XXXX) · `PO_Reference` Lookup * (AutoFetch items) · `Warehouse` Dropdown (Wadki/Main/Neelo/Gurgaon/Bangalore/Client Site) * · `Project_ID` Lookup (**optional** — inherited from PO, B3) · `GRN_Date` Date * · `Supplier` Text (AutoFetch) · `Invoice_No` Text · `Invoice_Date` Date · `QC_Status` Dropdown: Pending / Pass / Fail / Hold · `Packing_Quality` Dropdown · `Transporter_Details` Text. Lines (7): `Item_Code` · `Item_Name` Text (AutoFetch) · `Ordered_Qty` Number (AutoFetch) · `Received_Qty` Number * · `Qty_Checked` Checkbox (partial GRN marker) · `Condition` Dropdown · `Remarks`. Transport subform (4): `Vehicle_No` Text · `Driver_Name` Text · `LR_No` Text · `Delivery_Note` Text.

**QC/QA (6 + 8):** `QC_Number` Text (QC-YYYY-XXXX) · `GRN_Reference` Lookup * · `QC_Status` Dropdown: Pass / Fail / Hold * · `Inspected_By` User · `Date` Date · `Remarks`. Inspection fields (8): viscosity, density, color, moisture, curing, adhesion, appearance, `Accepted_Qty` Number.

**Automations (Stream A):**
- **A-21** (PR submit → Pending Approval + notify): On Submit (PR) — Status → Pending Approval, email approver. Deluge: `procurement/prStatusNotify.deluge`.
- **A-22** (PR approved → notify): On Record Modified — Approved → email requester.
- **A-23** (PO dual series): PO_Type Coding → RMWAD prefix, else RM (F1). Deluge: `procurement/poSeriesPrefix.deluge`.
- **A-24** (per-line GST split): CGST/SGST (intra-state) vs IGST (inter-state) by Supplier_State (F12). Deluge: `procurement/poGstSplit.deluge`.
- **A-25** (PO dispatched → notify): On Record Modified, Sent → email store. *(Spec-only — implement as an Email step; no deluge file yet — PARTIAL.)*
- **A-26** (GRN autofetch): On Load (GRN) — PO_Reference → lines autofilled.
- **A-27** (Post GRN): GRN submit → RM stock + **delayed posting** (only when QC passes), movement log, G5 hooks (Received/Balance/Status/Delivery_Days), PO status update. Deluge: `procurement/postGRN.deluge`.
- **A-28** (GRN overdue schedule): daily — PO not received by Delivery_Date → escalation email. *(Spec-only — PARTIAL.)*
- **A-29** (QC auto status): QC submit → GRN QC_Status mirror.

**Reports (Stream A) — R4 (8):**
- PR Status Report — Summary — PR — group Status — COUNT(PR Number).
- Open PO Register — Detail — PO — filter Status ≠ Fully Received / Cancelled (G5).
- PO Value by Supplier — Summary — PO — group Supplier Code — SUM(Total Amount), COUNT(PO Number) (G5 — needs header Total Amount, F1 fixed).
- Purchase by Item Group — Summary — PO line items — **group Item Code** (F7; Category AutoFetch added as optional) — SUM(Total Amount) — Date range.
- PO vs GRN Pending — Detail — PO line items — filter Balance_Qty > 0 (G5).
- Vendor Performance — Summary — PO — group Supplier — COUNT(PO), AVG(Delivery Days = **GRN Date − Delivery Date** — F6).
- GRN Register — Detail — GRN — filter Date range.
- QC Results — Summary — QC — group QC_Status — COUNT(QC Number), SUM(Accepted Qty).

---

## Part 4 — Cross-cutting systems

1. **P1 numbering series** (`shared/numberSeries.deluge`): SO-YYYY-XXXX · CST-YYYY-XXXX · PRJ-YYYY-XXXX · PLAN-YYYY-XXXX · MR-YYYY-XXXX · PR-YYYY-XXXX · RMWAD-YYYY-XXXX (coding PO) · RM-YYYY-XXXX (non-coding PO) · GRN-YYYY-XXXX · QC-YYYY-XXXX · MIS-YYYY-XXXX · JOB-YYYY-XXXX · BMR-YYYY-XXXX · RC-YYYY-XXXX · FGH-YYYY-XXXX · SCE-YYYY-XXXX · MRT-YYYY-XXXX · FGC-YYYY-XXXX · SUP-0001 / ST-01 codes. Item codes: EP/PU/DEM/ANTI/ESD/FIL systems.
2. **Stock Movement Transaction Log** (8 fields, `shared/stockMoveRM.deluge` + `stockMoveFG.deluge`): `Movement_Type` Dropdown (GRN/MIS/MATERIAL_RETURN/FGHM/FG_CONSUMPTION/OPENING) · `Item_Code` Lookup · `Item_Name` Text (AutoFetch) · `Quantity` Number (signed) · `Direction` Dropdown: In/Out · `Store` Lookup · `Document_Ref` Text · `Timestamp` Date/Time. **Every stock move writes one row (A-42).**
3. **80%/100% alerts** (`shared/checkAllocationAlert.deluge`): 80% → pop-up + dashboard + email within 1 min; 100% → PM + Purchase "Allocation Exhausted".
4. **Min/max reorder** (`site/inventoryAlerts.deluge`): daily 7 AM schedule — Current_Stock < Min → Store email; > Max → Store + Purchase; FG same.
5. **SLA schedules**: MR 2h reminder (once) / 2h escalate / 1h auto-release (`mrGate/mrSlaSchedules.deluge`); Costing 4h reminder / 24h escalate (`costing/costingSlaEscalate.deluge`).
6. **Notification triggers (IMPL §8.7)** — wired 2026-08-06 (F12): Costing Approved → Production+PM (costingApproveChain) · MR Released → Store+Production+**PM** (mrReleaseAutoMIS) · MIS Posted → Production (postMIS) · Material Return → Store (materialReturn) · <20% remaining → PM+Purchase (inventoryAlerts).

---

## Part 5 — Reporting layer R1–R7 + 8 dashboards

**Full register: 59 reports + 8 dashboards + 53 widgets.** R1 (8 master) / R2 (8 sales+project) / R3 (12 costing-plan-MR) / R4 (8 procurement) / R5 (10 production) / R6 (13 inventory-site). R1–R4, R6 match the plan doc exactly; R5 has the BMR-reference group-by fix (F8). Full tables in Stage sections above.

**R7 — 8 department dashboards (build table):**

| Dashboard | Widgets (KPI / Chart / Report) |
|-----------|-------------------------------|
| Purchase | Total Purchase This Month · Open POs · Pending PR Approvals · Purchase by Item Group (Bar) · Vendor Delivery (Bar) · Open PO Register · PO vs GRN Pending |
| Sales | SO Count · SO Value YTD · SO Value Trend (Line) · SO Type Split (Pie) · Sales Register · Project Status List |
| MR/Costing | MR Count by Stage · Total MR Cost · MR Status (Funnel) · Costing Status (Pie) · MR Status Tracking · Material Allocation vs Consumption |
| Store | RM Stock Value · Below-Min Items · Stock by Category (Pie) · Reorder Alerts (Bar) · RM Stock Status · FG Stock Status · Stock Movement Log |
| Production | Batches Today · Open Jobs · Pending MIS · Daily Production (Bar) · Job Status (Pie) · MIS Register · Production Job Status · BMR vs BOM Variance |
| Site Supervisor | Consumption Today · Active 80% Alerts · Consumption by Area (Bar) · Consumption by RM (Bar) · Site Consumption Log · Material Return Report |
| Costing | Costing Approvals · Project P&L Sum · Costing vs Actual (Bar) · Project Inventory (Bar) · Project Inventory Status · Costing vs Actual Variance |
| Project Management | Open Projects · Open POs (project-tagged) · Project Status (Pie) · MR Status per Project (Bar) · Project Status · MR Status per Project · 80% Alert List |

---

## Part 6 — Verification findings & resolutions (2026-08-06 run)

**BLOCKERS — all resolved in docs + deluge + sim:**
- **B1 (F4)** MR dual line tables (ghost `MR_Line_Items`) removed from `forms.html` + `IMPLEMENTATION_PLAN.md` — single Material Allocation table only.
- **B2** PO Project ID made optional (was required) — Stream A compatibility.
- **B3** GRN Project ID made optional, inherited from PO.
- **B4 (C28)** Costing §A formula aligned to `round(Area × CompQty/sqm × Ratio, 1)`; Waste% marked informational; BOM ratios stay 4dp.
- **B5 (G5/F1)** PO header numeric `Total_Amount` formula added (needed by R4 PO Value by Supplier).

**FIXES applied:**
- F1 4-state MR residue → 5-state everywhere (forms.html diagram, IMPL:890, reports.html MR dashboard label).
- F2 SO→Project residue → SO→Costing; Project creation only at Costing Approved (C2).
- F4 Vendor Performance formula → "GRN Date − Delivery Date" (was "GRN date − PO date").
- F5 FG Inventory `Category` field added (G7 — Inventory Valuation + Store chart group-by).
- F7 Purchase by Item Group → group by Item Code; PO line `Category` Text (AutoFetch) added (optional group-by).
- F8 BMR vs BOM Variance → group by BMR Reference.
- F9 MIS numbering → MIS-YYYY-XXXX (forms.html, IMPL, reports.html).
- F10 `Fully_Consumed` wording → ALL-lines condition (C29).
- F11 Costing SLA → 4h reminder / 24h escalation (was 8h/48h).
- F12 Notifications wired in deluge + mirrored in flow_sim (5 new asserts: costing-approved, mr-released+PM, mis-posted, mrt, low-remaining).
- F13 Costing header Prepared By / Reviewed By / Revision No added; User Access & Approval Matrix section added to forms.html.
- F14 Numbering table: MIS/FGC series added; SUP/FGC series documented.

**INFO / console-level (documented, not code-changed):**
- F-02/F-03: `MR_Allocation` is a subform, not a form — `lookupRecords`/`updateRecord` on it fails in Creator. Pattern note added to 7 deluge files: resolve via `MR_Master` (Project_ID + MR_Number), iterate `Material_Allocation` rows, re-PUT subform on parent (keep row IDs). `flow_sim.py` models allocation as an entity (this is why the sim masks the issue).
- F-05: crossValidate rewritten to per-line variance write (spec + sim already per-line, C31).
- Excel gap: `files/*.csv` lack sheets for Costing/Plan/SCE/MRT/inventory — `forms.html` is now the effective field source of truth; Excel is legacy.
- FGAN / Rate Comparison / Material Handover / Rework Register: excluded or needs-decision (see VERIFICATION_FINDINGS.md + audit_4 orphans log).

---

## Part 7 — Console build checklist (paste order)

1. **Phase 0** shared: `shared/numberSeries.deluge`, `shared/stockMoveRM.deluge`, `shared/stockMoveFG.deluge`, `shared/checkAllocationAlert.deluge` → build master-data forms first.
2. **Phase 1** procurement: `poSeriesPrefix`, `poGstSplit`, `postGRN`, `prStatusNotify` → PR/PO/GRN/QC forms.
3. **Phase 2** costing: `expandCosting`, `costingApproveChain`, `getAvailableStock`, `planReleaseAutoPR`, `costingSlaEscalate` → Costing/Plan forms.
4. **Phase 3** MR gate: `mrDerive`, `crossValidate`, `mrReleaseAutoMIS`, `mrSlaSchedules` → MR form + 5-state Blueprint.
5. **Phase 4** production: `postMIS`, `consumeAllocation`, `bmrSubmit`, `fghmAccept`, `packingDeduct` → MIS/BMR/RC/Packing/FGHM forms.
6. **Phase 5** site: `sceSubmit`, `materialReturn`, `fgConsumption`, `inventoryAlerts` → SCE/MRT/FG Consumption forms.
7. **Reports**: build R1 → R6 in order, then R7 dashboards (widget map above).
8. **Verify**: `python chemsol/implementation/verify/flow_sim.py` → **77/77 green**; tick UAT steps in `chemsol/UAT_VERIFICATION_PLAN.md`.

---

## Part 8 — Source-of-truth index

| Layer | File | Role |
|-------|------|------|
| Field names (API) | `chemsol/forms.html` | **Naming authority** for Deluge field references |
| Automation register | `chemsol/AUTOMATION_ALIGNMENT_PLAN.md` | A-01…A-43 register + consensus rules |
| Reporting spec | `chemsol/REPORT_IMPLEMENTATION_PLAN.md` | R1–R7, G1–G9 gap fields |
| Field-level spec | `chemsol/IMPLEMENTATION_PLAN.md` | Module-by-module build spec |
| Excel exports | `chemsol/files/*.csv` | Legacy screen-layout exports (stale for newer modules) |
| Deluge scripts | `chemsol/implementation/deluge/**` | 26 paste-in scripts (6 subdirs) |
| Oracle | `chemsol/implementation/verify/flow_sim.py` | 77/77 — mirrors ALL business logic |
| Audits | `chemsol/implementation/verify/audit/` | audit_1 fields · audit_2 automations · audit_3 reports · audit_4 loop-map |
| Findings | `chemsol/VERIFICATION_FINDINGS.md` | Consolidated BLOCKER/FIX/INFO log |
| Progress | `chemsol/implementation/PROGRESS.md` | Phase loop log |
