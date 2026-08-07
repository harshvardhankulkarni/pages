# Chemsol ERP — Detailed Change Log

**Compiled:** 2026-08-07 | **Source of truth:** `IMPLEMENTATION_PLAN.md`, `forms.html`, `CREATOR_BUILD_GUIDE.md`, `CREATOR_FIELD_MAP.json`, `CHEMSOL_V2_DS_EDITS.md`, `AUTOMATION_PORT_MAP.md`, `GAP_ANALYSIS_CREATOR_EXPORT.md`, `COMPLETE_REMEDIATION_GUIDE.md`
**Verification:** `python chemsol/implementation/verify/flow_sim.py` → **82 passed, 0 failed**

This log lists every change made across the planning docs and the Zoho Creator `.ds` schema, split into three work streams:
1. **Field type changes** — what type each field was given and why.
2. **Field add / update / remove in modules** — schema edits per module.
3. **Automation changes** — the Deluge/workflow edits tied to these fields.

Each entry states **what to change** and **how** (the real Zoho form/grid/field name + where to wire it).

---

## Legend

- **.ds** — edit was applied to the Zoho Creator export file `chemsol/Chemsol V2.ds` (schema pass).
- **Console** — must be wired manually in the Zoho Creator console (automations/blueprints/dashboards can't be expressed in `.ds`).
- **doc** — spec-only change in the plan/build-guide/forms documents.
- Field names use the **real app names** from `CREATOR_FIELD_MAP.json` (these often differ from the plan-era names in `implementation/deluge/*`).

---

## PART 1 — Field Type Changes

These were done in two passes: the **V17 field-type clarity pass** (docs: 69 cells in IMPLEMENTATION_PLAN.md, 75 in forms.html, 34 in build-guide) and the **`.ds` schema pass** (actual export types).

### 1.1 Plan-era type standardization (docs, done)
Every former `AutoFetch`/blurry field now declares an explicit Zoho Creator type.

| Module / Grid | Field | Old (implied) | New (explicit) | Where |
|---|---|---|---|---|
| SO → System Lines | System Name | AutoFetch | **Text · AutoFetch** | forms.html, IMPL |
| SO → FG Lines | FG Name | AutoFetch | **Text · AutoFetch** | forms.html, IMPL |
| SO → FG Lines | UOM | AutoFetch | **Text · AutoFetch** | forms.html, IMPL |
| System Composition | Status | Free values | **Dropdown**: Active / Inactive | IMPL |
| System Composition | FG Name | AutoFetch | **Text · AutoFetch** | forms.html, IMPL |
| BOM / FG Formulation | Status | Free values | **Dropdown**: Draft / Approved / Released | IMPL |
| BOM / FG Formulation | FG/RM Name, UOM | AutoFetch | **Text · AutoFetch** | forms.html, IMPL |
| Item Muster | Status | Free values | **Dropdown**: Active / Inactive | IMPL |
| Supplier / Customer / Store | Status | Free values | **Dropdown**: Active / Inactive | IMPL |
| Material (all) | UOM | AutoFetch | **Text · AutoFetch** (from Item Muster) | forms.html |
| Costing Sheet | Costing Status | Free values | **Dropdown**: Draft / Under Review / Approved / Rejected | IMPL |
| Costing Sheet | Project ID | — | **Lookup (Project)** · auto-created on Costing approval | IMPL |
| Production Plan | Status | Free values | **Dropdown**: Draft / Reviewed / Released | IMPL |
| PR | Department | AutoFetch-from-login | **Dropdown · AutoFetch from login** | IMPL |
| PR line items | Item Name / UOM / Lead Time | AutoFetch | **Text** (Name/UOM), **Number** (Lead Time) | forms.html |
| PO ROOT | RM Type | Free | **Dropdown**: Coding / Non Coding | IMPL |
| PO line items | Item Name/HSN, Category, UOM | AutoFetch | **Text · AutoFetch** | forms.html |
| PO line items | GST % | AutoFetch | **Percent · AutoFetch** | forms.html |
| GRN | Project ID | AutoFetch from PO | **Lookup (Project) · AutoFetch from PO** | IMPL |
| GRN line items | Item Code/Name, Ordered Qty | AutoFetch | **Lookup** (Item), **Number** (Qty) | forms.html |
| GRN | QC Status | Free | **Dropdown**: Pending / Pass / Fail | IMPL |
| QC | QC Status | Free | **Dropdown**: Pass / Fail / Hold | IMPL |
| MR line items | Item, Category, Required Qty | AutoFetch | **Lookup** (Item), **Text** (Category), **Number** (Qty) | forms.html |
| Production Job | Status | Free values | **Dropdown**: Draft / Scheduled / In Progress / Completed | IMPL |
| Production Job | Project ID | AutoFetch | **Lookup (Project) · AutoFetch** | IMPL |
| BMR | RM name/UOM | AutoFetch | **Text · AutoFetch** | forms.html |
| BMR | Standard Qty | AutoFetch | **Number · AutoFetch** | forms.html |
| Site Consumption | Batch No | AutoFetch | **Text · AutoFetch** | forms.html |

### 1.2 `.ds` schema type fixes (real app, done in `Chemsol V2.ds`)
The export had raw Material Cost fields typed as **text**, which breaks all costing math. Changed to **decimal**:

| Module | Grid | Field | Old type | New type |
|---|---|---|---|---|
| Costing_Sheet | Material_Cost | BOM_Ratio | text | **decimal** |
| Costing_Sheet | Material_Cost | Area_sqm | text | **decimal** |
| Costing_Sheet | Material_Cost | Required_Qty | text | **decimal** |
| Costing_Sheet | (main) | Project_ID | text | **picklist lookup → Project_Master(ID)** (display Project_ID) |

> **Why decimal:** text ratios silently break Section A totals and the SO↔BOM↔MR cross-validation. Keep BOM ratios at 4dp (0.3333, 0.5817), never rounded to 2dp (C28).

---

## 2 — Fields added

| # | Module (form) | Grid | Added field | Type / purpose | Where |
|---|---|---|---|---|---|
| 1 | Costing_Sheet | Material_Cost | **CompQty_sqm** | decimal; Section A formula `Required_Qty = round(Area × CompQty/sqm × BOM_Ratio, 1)` | `.ds` |
| 2 | Material_Requisition | MR_Change_History | **Changed_Field, Old_Value, New_Value, Changed_At, Changed_By** | audit trail subform for MR changes (client 2026-08-06) | Console + `mrChangeHistory.deluge` |
| 3 | Costing_Sheet | (main) | **Prepared_By** (required), **Reviewed_By** (optional) | user lookup fields | `.ds` |
| 4 | Material_Issue_Slip | (main) | **Issued By / Handover To** | user fields (plan §6.3) | Console |
| 5 | GRN | (main) | **Partial GRN checkbox** + line-level `Received` | partial receiving | Console |
| — | **NEW FORM User_Access** | — | User_Name(user), Department, Role (Entry/Review/Approve/Admin), Status (Active/Inactive) — all mandatory | plan §2.7 | `.ds` |
| — | **NEW FORM Approval_Matrix** | — | Department, Document_Type (PR/PO/MR), Min_Amount, Max_Amount, Approver_1/2/3 (User) | plan §2.7 | `.ds` |

### Why these were added
- `CompQty/sqm` was missing entirely — the §A costing formula referenced it. Added as the notional "FG per sqm" column so Section A can auto-expand FG products in the FG-based costing model.
- `MR_Change_History` + notifies Production/Inventory on any MR edit (new client requirement 2026-08-06).
- `Prepared_By`/`Reviewed_By` and the two new forms (`User_Access`, `Approval_Matrix`) close the Access-Control gap in plan §2.7 (approval matrix keyed by department + document type + amount band).

---

## 3 — Field Update (rename / type / value corrections)

| # | Module | Field | Change | Why | Where |
|---|---|---|---|---|---|
| 1 | Material_Requisition | `MR_Status` value | `" Released"` → `"Released"` (removed leading space) | The value had a leading space that mismatched the Blueprint `stages` named `"Released"` — broke all status-driven lookups and the auto-release schedule | `.ds` |
| 2 | Material_Requisition | `Material_Cost`/`Required_Qty` etc. | cost fields kept as-is on FG-based costing | — | — |

---

## 4 — Field Remove (ghost schema)

### 4.1 Remove GHOST grid `MR_Line_Items` (critical, done)
The MR form had **two** line tables; the plan says only **`Material_Allocation`** is the line table. The ghost `MR_Line_Items` grid and everything referencing it were removed:

| Removed item | Reason |
|---|---|
| `MR_Line_Items` grid (2 subform fields) | duplicate line table — `MR` now uses **only** `Material_Allocation1` |
| `MR_Line_Items_Count` | count field for the ghost grid |
| empty `'Update_material_allocatio'` stub | dead automation on the ghost grid |
| `Autofetch3` | dead autofetch on 1 |
| `Line_item_count7` count-loop for `MR_Line_Items` | retained only the `Material_Allocation` count |
| `disable MRS_Line_Items.Category/UOM;` lines | dead disable lines |
| two report columns referencing `MR_Line_Items` | repointed to Material_Allocation |

**Verified:** `MR_Line_Items` now has **0 references** in `Chemsol V2.ds`. mrDerive / crossValidate / flow_sim read `Material_Allocation1` only.

### 4.2 De-dup candidates (decision pending, Console)
The `.ds` also carries forms **not in the plan**; keep only if required:
- `Project_FG_Consumption_Tracking` (not in plan — keep as report or remove)
- `Rework_Register`, `Rate_Comparison`, `Finish_Goods`, `Task_Budget_FG_Bin`, `Delivery_Challan_Store_Mapping` — annotate "excluded in plan §11"; de-dupe if not required.
- A stock movement/ledger tables are **manual-entry** — plan requires them **derived** (see automation section).

---

## 4 — Numbering & naming changes

| # | Entity | Old | New | Where |
|---|---|---|---|---|
| 1 | App name | `ChemSol` | **`Chemsol V2`** | `.ds` |
| 2 | All 12 series | `PREFIX-####` | **`PREFIX-YYYY-####`** | `.ds` |
| 3 | Project | `Proj-` | **`PRJ-`** | `.ds` |
| 4 | BOM | `ITEM-` | **`BOM-`** | `.ds` |
| 5 | Customer | `Cust-` | **`CUST-`** | `.ds` |
| 6 | QC | `Qc-` | **`QC-`** | `.ds` |
| 7 | Production Order / Job | `ProOrd-` | **`JOB-`** | `.ds` |
| 8 | Production Plan | *(no auto-number)* | **`PLAN-YYYY-####`** from `Plan_Auto_Number` | `.ds` |
| 9 | PO / MR / SO | PO `RMWAD-`(coding) / `RM-`(non-coding); others `PREFIX-YYYY-` | add **`-YYYY-`** segment | `.ds` |

**Numbering note:** the plan counter (`No_Series`) does not exist in the real app. All numbering is `Auto Number` fields + per-form mapping workflows (e.g. `Auto_Num_*`). Any derived number must use the target form's own autonumber, not a custom counter.

---

## 5 — Automation changes (client change round 2026-08-06)

These are the logic changes tied directly to the FG-based costing + FG-wise planning + MR change-history client requirements. All mirrored in `verify/flow_sim.py` (sim 82/82).

| # | Automation (Deluge file) | Change | What now happens | How |
|---|---|---|---|---|
| **A1** | `costing/expandCosting.deluge` | **FG-based costing** | Costing Section A lists **FG products** (not RM rows). Each FG line: `fgQty = round(Area × Qty_Per_Sqm, 1)`; `fgRate = Σ(BOM_Ratio × RM Standard_Rate)`; `amount = fgQty × fgRate`. Rows carry: System_Code, System_Name, FG_Code, FG_Name, UOM="Kg", Area, Qty_Per_sqm, Required_FG_Qty, Unit_Rate, Material_Cost. | Console on Costing_Sheet before-save |
| **A1-change** | `costing/expandCosting.deluge` | **No SO approval process** | Costing Sheet auto-created directly from SO (Supply+Apply). SO approval step removed; Project is still created only at Costing approval. | SO status logic dropped |
| **A4** | `costing/planReleaseAutoPR.deluge` | **FG-wise planning + auto-PR** | Plan lines are **FG products**. On Plan Released: for each FG line lookup BOM, derive RM req = `fgLine.Plan_Qty × bom.Ratio`, diff against `getAvailableStock`, create PR only if shortage > 0. **De-dupe**: only one submitted PR per (Project_ID, RM_Code); if a submitted PR already exists, append the line to it instead of creating a duplicate PR. | Console |
| **MR derive** | `mrGate/mrDerive.deluge` | **MR allocates RM from FG costing via BOM roll-up** | MR no longer reads Costing Material lines directly (they are now FG rows). Instead: for each FG cost line, look up BOM, sum RM qty per RM code (`rmAllocMap`), then create Material_Allocation rows with `Item_Code/Name, Assigned_Qty, Rate, Material_Cost, Allocation_Ratio_Percent, Remaining`. 4 cost components (Material/Application/Transport/Tools; §E excluded) preserved. | Before-save on MR |
| **NEW** | `mrGate/mrChangeHistory.deluge` (new file) | **MR Change History + Dept notification** | On MR "Record Modified": log any changed field (Field_Name, Old/New, Changed_At, Changed_By) to `MR_Change_History` subform; if any change, `sendmail` to Production + Inventory dept emails with a change table. | On Record Modified (MR_Master) |
| **R4** | reports | **Subform-focused reports** | Open-PR report now returns `PR_Line_Items` subform details (e.g., RM-001, Qty 75) instead of header-only. | Report query; no Deluge |

### Automation wiring status (A1–A17) — what remains to wire in Console
Three of the 17 automations are already written as custom Deluge nodes in `Chemsol V2.ds`. The rest must be built in the Console (`.ds` can't carry them safely).

| # | Automation | Real form/grid | Event | Status |
|---|---|---|---|---|
| A1 | Costing §A auto-expand | Costing_Sheet.`Material_Cost` | before-save | Console (paste `expandCosting`) |
| A2 | Costing Approved → auto-create Project | Costing_Sheet → Project_Master | on success | Console |
| A3 | Costing → auto-create Production Plan (+lines) | → Production_Planning + `Line_Items` | on success | Console |
| A4 | Plan Released → auto-PR | → Purchase_Requisition + `PR_Line_Items` | on success | Console |
| A5 | MR auto-derive + 4 costs | MR `Material_Allocation1` | before-save | Console (`mrDerive.deluge`) |
| A6 | MR Released → auto-MIS | MR success → MIS | Blueprint "Released" | Console |
| A7 | SO↔BOM↔MR cross-validate(>5% flag/>10% block) | MR_Alloc `Variance_Flag` | on add/edit | Console |
| A8 | **Post-MIS stock deduct + log** | RM ledger + Stock_Movement_Log | on success | ✅ wired in `.ds` |
| A9 | 80%/100% allocation alerts | Allocation fields | schedule+submit | Console |
| A10 | SLA timers/escalation + auto-release | MR + Costing schedules | schedule | Console |
| A11 | **GRN → RM stock + log** | RM ledger + Log | on success | ✅ wired in `.ds` |
| A12 | MIS issue → allocation Issued_Qty | MR alloc row | on success | Console |
| A13 | BMR/RM/Site consumption → Consumed_Qty | MR alloc row | on success | Console |
| A14 | FGHM accept → FG stock + Full_Consumed(ALL ≥100%) | FG ledger + allocation | on success | Console |
| A15 | **Material return → credit stock + log** | RM ledger + Log | on success | ✅ wired in `.ds` |
| A16 | BMR → RM consumption ledger | RM ledger | on success | Console |
| A17 | Available Stock = physical − Σ(unreleased MR alloc) | Production_Planning | on load | Console |

**Consumption keys:** resolve to MR `Material_Allocation` row by `Project_ID + Item_Code`. `Fully_Consumed` only fires when **all** allocation lines ≥ 100% (C29).

---

## 6 — What to apply and how (action checklist)

### In the `.ds` (already done, verify import)
- [ ] Import `chemsol/Chemsol V2.ds` into a throwaway app to confirm Creator's parser accepts it. One syntax error fails the whole import.
- [ ] Confirm all field-type fixes (Costing BOM_Ratio/Area/Required → decimal), `CompQty_sqm`, `Project_ID`→lookup, `Prepared_By`/`Reviewed_By`, new forms A8/A11/A15 stock-post nodes.

### In the Console (manual — the real production path)
1. **Lock `Variable` counter form** (remove from Menu, admin-only) — can't be done in `.ds`.
2. **A2–A6** creation chain: Costing Approval → Project + Plan (A2/A3) → Plan Release auto-PR (A4) → MR auto-derive (A5) → MR Released → auto-MIS (A6).
3. **A7/A12/A13** per-RM cross-validate + consumption increments; **A14** FG `Fully_Consumed`; **A10 SLA** single-fire guard (C32); **A17** available stock.
4. **Notifications/SMTP:** all `sendmail` currently in comments (`/* ... */`). Un-comment + install SMTP connection binding to company mailbox; route PR/PO/MIS/returns→Purchase, Costing/MR/SLA→PM, 80/100%→PM+Purchase.
5. **Dashboards:** build 6 (Inventory, MR status board, live stock, 80/100% alerts, Costing vs Actual, Procurement lag) in Dashboard workbench.
6. **Derived ledgers:** convert manual RM/FG ledgers to derived/report, or keep system-updated via A8/A11/A14/A15.

### On the repo (logic mirrors — always keep in sync)
1. Every Deluge change above already mirrored in `chemsol/implementation/verify/flow_sim.py`. Run `python flow_sim.py` → **must stay 82/82**. If any FAIL → fix Deluge + sim → rerun → log in PROGRESS.md.
2. Keep the mapping sheet JSON (`CREATOR_FIELD_MAP.json`) in sync when adding/removing fields — it's the authoritative field-name/type reference used by the port-map and gap-analysis.
3. Cross-reference findings with `C##`/`F##` in PROGRESS.md.

---

*End of change log. Compiled from the plan docs, the `Chemsol V2.ds` edit run, and the client change round of 2026-08-06.*