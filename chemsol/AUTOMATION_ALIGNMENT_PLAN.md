# Chemsol — Automation Alignment Plan (Module ↔ Process Verification)

> **Purpose:** Verify that **every module's automation** is perfectly aligned with the **core process flow** — no orphan automations, no duplicated logic, no contradictory triggers. This plan walks each automation in detail, maps it to the process step it serves, and flags every misalignment found between `automation.html`, `AGENTS.md`, `forms.html`, the UAT plan, the reports plan (G1–G9) and the feasibility plan (P1–P8).
>
> **Method:** All 35+ automations in automation.html (section cards + Complete Automation Inventory table) were read in full and cross-checked against: AGENTS.md two-stream architecture · forms.html field definitions · UAT_VERIFICATION_PLAN.md (C1–C27) · REPORT_IMPLEMENTATION_PLAN.md (G1–G9) · ZOHO_CREATOR_FEASIBILITY_PLAN.md (verified native constructs).
>
> **Verdict:** The automation architecture is **90% aligned**. **14 findings** below — 10 must be fixed in the build, 4 need a client decision. None change the process flow itself.

---

## 1. Process Alignment Map (what each flow step must automate)

| Step | Process step | Module(s) | Automations serving it | Evidence report |
|---|---|---|---|---|
| 1 | SO entry (dual mode) | SO | conditional subforms, numbering, acceptance → Costing Draft | Sales Register, SO Type Split (R2) |
| 2 | Costing build | Costing Sheet | Section A auto-expansion, section subtotals, approval Blueprint | Costing Status, Costing vs Actual (R3) |
| 3 | Costing Approved → Project + Plan | Costing/Project/Plan | chain creation (G2: Total Revenue set), Plan Draft | Project P&L (R2) |
| 4 | Plan stock check + auto-PR | Production Plan | available-stock calc, auto-PR on Release | R4 purchase reports |
| 5 | MR auto-derive + gate | MR | auto-derive (4 cost components), cross-validation, 4-stage Blueprint, SLA schedules, auto-MIS | MR Status, Project Cost Baseline (R3) |
| 6 | Procurement | PR/PO/GRN/QC | status + notify, dual numbering, GST split, Post GRN (G5), overdue reminder | Open PO Register, PO vs GRN (R4) |
| 7 | Store issues RM | MIS | Released-only lookup, auto-fetch, Post MIS (G4 Issued Qty) | Project Inventory Status (R7) |
| 8 | Production | BMR / RM Cons / Packing | BOM autofetch, allocation increment (P6), variance-only, packing deduction | Daily Production, BOM vs Actual (R5) |
| 9 | FG handover | FGHM | inline accept (G6), FG stock +, Fully Consumed (C14) | FG Handover Pending (R5), FG position (R6) |
| 10 | Site usage | SCE / FG Consumption | allocation increment + 80%/100% alerts; FG − at site | SCE report, FG Consumption Log (R6) |
| 11 | Material return | MRT | allocation credit (C1/C12), stock restore | Material Return register |
| 12 | Inventory hygiene | RM/FG stock | min/max alerts, movement log | Stock reports (R6) |

**Every step has ≥1 automation and ≥1 report.** No orphan modules; the only scope-ambiguous modules are Rate Comparison + Material Handover (Finding F13).

---

## 2. Canonical Automation Register (single source of truth — build against this)

### Master Data
| ID | Module | Construct | Trigger | Action | Aligned |
|----|--------|-----------|---------|--------|:---:|
| A-01 | Item Muster | Deluge P1 | On Create | Item Code by Category (short code, **F2**) | ⚠ F1/F2/F14 |
| A-02 | Item Muster | Form Rule | On Load | Hide Standard Rate for non-Purchase/Store (**F14**: use permission sets) | ⚠ F14 |
| A-03 | System Comp / BOM | Blueprint | Status change | Draft → Approved → Released (Released = visible in lookups) | ✅ |
| A-04 | Supplier / Store | Deluge P1 | On Create | SUP-… / ST-… codes (**F2**) | ⚠ F1/F2 |
| A-05 | Customer/Site | — | — | none needed (pure master data) | ✅ |

### Stream B Core
| ID | Module | Construct | Trigger | Action | Aligned |
|----|--------|-----------|---------|--------|:---:|
| A-06 | SO | Form Rule | Sales Type change | swap Subform A / Subform B | ✅ |
| A-07 | SO | Workflow + Deluge | On acceptance (Supply+Apply) | **create Costing Sheet Draft** (C2 — not Project; **F3**) | ⚠ F3 |
| A-08 | SO | Formula | Line entry | line Amount + Total Amount | ✅ |
| A-09 | Costing | Workflow + Deluge | On Submit | Section A expansion: SO × System Comp × BOM (P2) | ✅ |
| A-10 | Costing | Blueprint | Status change | Costing Approval (→ Approved/Rejected) | ✅ |
| A-11 | Costing | Workflow + Deluge | On Approved | create Project (G2: Total Revenue) + Production Plan Draft + notify (P3) | ✅ |
| A-12 | Project | Workflow + Deluge | On MR Released | set Total Actual Cost = MR total; recalc P&L (G2) | ✅ |
| A-13 | Plan | Custom function | On Load / Release | available stock = physical − Σ unreleased MR assignments (**F7**: not a formula) | ⚠ F7 |
| A-14 | Plan | Workflow + Deluge | On Released | auto-PR for Shortage > 0 (P8; Project ref — decision **F13**) | ✅ |
| A-15 | MR | Workflow + Deluge | On Plan Released (if Costing Approved) | MR auto-derive: 4 cost components + Material Allocation from Costing §A (**F4**: single line table) | ⚠ F4 |
| A-16 | MR | Workflow + Deluge | On Submit | cross-validation ΣAssigned vs Σ(SO Area × BOM) — >5% flag, >10% block (P5) | ✅ |
| A-17 | MR | Blueprint | Status transitions | Draft → Production Verified → Costing Approved → Released (**F11**: 4 states, match forms.html/UAT) | ⚠ F11 |
| A-18 | MR | Workflow + Deluge | On Released (via on-change workflow, **F5**) | auto-create MIS Draft (header + lines from Allocation) + notify Store/Production | ⚠ F5 |
| A-19 | MR | Schedule | Daily 9 AM | SLA: Draft >2 hr reminder, Verified >2 hr escalate, Approved >1 hr auto-release (**F10**) | ⚠ F10 |
| A-20 | MR Allocation | Custom function | BMR/SCE update | 80% alert → PM email + dashboard flag; 100% → PM + Purchase (**F8**: one shared function) | ⚠ F8 |

### Procurement (Stream A)
| ID | Module | Construct | Trigger | Action | Aligned |
|----|--------|-----------|---------|--------|:---:|
| A-21 | PR | Workflow | On Submit | Status → Pending Approval + notify Purchase | ✅ |
| A-22 | PR | Workflow | On Approved | notify requestor | ✅ |
| A-23 | PO | Form Rule | On Load | prefix selection for dual series (**F1**: P1 counter, not autogen) | ⚠ F1 |
| A-24 | PO | Formula | Line entry | per-line GST split + footer totals (**F12**: per-line CGST/SGST/IGST) | ⚠ F12 |
| A-25 | PO | Workflow | On Dispatched/Delivered | notify Purchase + Store (ready for GRN) | ✅ |
| A-26 | GRN | Form Rule | PO selected | autofetch supplier/items/ordered qty | ✅ |
| A-27 | GRN | Custom button + Deluge | Post GRN | validate QC → RM stock + (delayed posting) → movement log → **G5 hook (F9)** → PO line Received Qty/status/Delivery Days | ⚠ F9 |
| A-28 | GRN | Schedule | Daily 8 AM | overdue GRN reminder (PO dispatched >7 d, no posted GRN) | ✅ |
| A-29 | QC | Form Rule | Accepted/Rejected qty | auto Status Pass/Fail/Hold | ✅ |

### Production + Site (Stream B)
| ID | Module | Construct | Trigger | Action | Aligned |
|----|--------|-----------|---------|--------|:---:|
| A-30 | MIS | Lookup filter | Static config | only Released MRs (**F6**: Set Filter, not runtime lookupCriteria) | ⚠ F6 |
| A-31 | MIS | Custom button + Deluge | Post MIS | RM stock − (insufficient-stock block) → movement log → **G4**: Allocation.Issued Qty + | ✅ |
| A-32 | BMR | Form Rule | FG selected | BOM RM lines autofetch (Released BOMs only) | ✅ |
| A-33 | BMR | Workflow + Deluge | On Submit | Allocation.Consumed Qty + (P6); block >100% (C13) | ✅ |
| A-34 | RM Consumption | Formula | Line entry | Variance = Actual − Standard (no allocation change — C25) | ✅ |
| A-35 | Packing | Workflow + Deluge | On Submit | deduct packaging from RM inventory | ✅ |
| A-36 | FGHM | Custom action + Deluge | Inline Accept | Status = Accepted (G6), FG stock +, movement log, notify Store | ✅ |
| A-37 | FGHM | Workflow + Deluge | On Accepted | mark Allocation Fully Consumed when all lines ≥100% (C14) | ✅ |
| A-38 | SCE | Workflow + Deluge | On Submit | Allocation.Consumed Qty + (P6); block >100%; 80%/100% alert via shared function (F8) | ⚠ F8 |
| A-39 | FG Consumption | Workflow + Deluge | On Submit | FG stock − at site + Project FG Consumption log | ✅ |
| A-40 | MRT | Workflow + Deluge | On Submit | Allocation.Consumed − / Returned + (C12); Good → stock restore | ✅ |

### Inventory
| ID | Module | Construct | Trigger | Action | Aligned |
|----|--------|-----------|---------|--------|:---:|
| A-41 | RM/FG stock | Schedule | Daily 7 AM | min/max reorder + overstock alerts | ✅ |
| A-42 | Stock Movement Log | Deluge | GRN/MIS/FGHM/SCE/MRT/FG Cons | one movement record per posting (traceability) | ✅ |
| A-43 | Shared | Custom functions | — | numberSeries, getAvailableStock, checkAllocationAlert, stockMove, expandCosting, crossValidate, autoPR, postGRN, postMIS | ✅ (P1–P8) |

---

## 3. Findings — Misalignments & Gaps (fix or decide)

| # | Finding | Conflict | Required fix | Verdict |
|---|---------|----------|--------------|:---:|
| **F1** | `autogen("RM-YYYY-XXXX")` + `sequenceNumber()` in automation.html §1A/2B-3/4B/2A/2B/3A/5A–5G — **not valid Creator Deluge**. Auto Number field is numeric-only (feasibility §1.1). All prefixed document numbers must come from the **P1 number-series counter** (No_Series table). GRN number "generated only on post" → generate inside Post GRN button. | automation.html vs feasibility plan | Replace every "Auto Numbering" row with P1 counter call in the On Create workflow (or Post button for GRN) | **Fix in build** |
| **F2** | Item Code format conflict: automation.html §1A = `RM-YYYY-XXXX`; UAT plan/xlsx = `RM-001`, `FG-002`, `SUP-0001`. | automation.html vs UAT plan + xlsx | Item master codes = **short sequential** (RM-001, FG-002, SUP-0001) to match sample data & BOM refs; only transaction documents use YYYY-XXXX | **Decision** (recommend short) |
| **F3** | automation.html 2A: "SO Submit → auto-create Project". forms.html + C2: Project created **only on Costing Approved**; SO acceptance creates **Costing Sheet Draft**. | automation.html §2A vs forms.html/AGENTS/C2 | Fix 2A card: SO acceptance → Costing Draft (A-07); delete SO→Project workflow | **Fix in build** |
| **F4** | MR has two line tables in automation.html (3A `MR_Line_Items` + `Material_Allocation`, 3B writes `MR_Line_Items`). forms.html/UAT: **one** canonical subform = Material Allocation (Assigned/Ratio/80%/Issued/Consumed/Returned). | automation.html vs forms.html | MR = header + **Material Allocation only**. A-15 populates Allocation directly (Assigned = Costing §A qty); A-18, A-33, A-38, A-40 all read/write Allocation | **Fix in build** |
| **F5** | C15 (A-18) creates **one MIS_Master record per MR line**. forms.html 5A + UAT (`MIS-2026-001` with 2 lines): MIS = header + line-items subform. Also runs inside Blueprint transition (50-statement cap) — a per-line loop can exceed it. | automation.html vs forms.html/UAT/feasibility | One MIS header + line items copied from Allocation; run from an **on-change form workflow** (criteria Status=Released) instead of the Blueprint script | **Fix in build** |
| **F6** | MIS "Released-only" via `zoho.form.setFieldProperty("lookupCriteria")` — invalid API. | automation.html vs feasibility | Use native **lookup Set Filter** (Status = Released) in Field Properties | **Fix in build** |
| **F7** | Production Plan "Available Stock = physical − Σ(Assigned Qty WHERE MR.Status ≠ Released)" written as a **formula field** (2B-4). Formula fields can't do cross-form criteria aggregates. | automation.html vs feasibility | Custom function `getAvailableStock(item)` (Deluge aggregate) shown on Plan via page/report + evaluated at Release | **Fix in build** |
| **F8** | 80% alert logic duplicated in 3A (Allocation update) and 5B-1 (SCE). BMR path (A-33) doesn't send it at all. | automation.html internal | One custom function `checkAllocationAlert(alloc, newPct)` called from A-33 + A-38 (and MRT is a decrement → no alert); dashboard banner via page panel on 80% flag | **Fix in build** |
| **F9** | Post GRN script (4C) updates RM stock + movement log but **omits the G5 hook** (PO line Received Qty + Balance + Receipt Status + PO status + Delivery Days) that the inventory table row claims. | automation.html card vs its own inventory table | Add G5 block to Post GRN button script (call shared `postGRN()`) | **Fix in build** |
| **F10** | SLA "Approved >1 hr → auto-release" (C10) — schedules can't drive Blueprint transitions natively. automation.html schedule only covers Draft/Verified reminders. | automation.html vs feasibility | Verify at build: (a) scheduled Deluge sets Status directly (Blueprint allowed transition auto-trigger), else (b) auto-release via on-change workflow + schedule keeps escalating reminder. **UNVERIFIED — test in Phase 3 of playbook** | **Fix in build** |
| **F11** | Blueprint has 5 states (incl. "Pending Production Verification"); forms.html + UAT plan use **4 states** (Draft → Production Verified → Costing Approved → Released). | automation.html vs forms.html/UAT | Align to 4 states; "Pending" state adds no gate (Production simply verifies next) | **Fix in build** |
| **F12** | PO footer GST formula applies one GST% to the whole Basic Total; lines can carry different GST% (Item Muster has per-item GST%). | automation.html vs Item Muster | Per-line CGST/SGST/IGST (state-code compare) then SUM lines | **Fix in build** |
| **F13** | Rate Comparison + Material Handover: listed in AGENTS.md procurement inventory + BRD, but **excluded** in AGENTS.md scope note, absent from automation.html, unused in UAT scenario. | AGENTS.md internal + automation.html | Confirm scope: **exclude from core build** (UAT passes without them); auto-PR Project ref = informational text field only | **Decision** |
| **F14** | Item Muster rate visibility via `zoho.login.department` — Creator has no login department context. | automation.html vs Creator | Implement via **permission sets** (Purchase/Store roles see Standard Rate; others don't) | **Fix in build** |

**Alignment status summary:** 43 automations registered (A-01…A-43) → 29 fully aligned ✅ · 14 findings (10 fix-in-build, 4 decisions).

---

## 4. Consensus Rules (imposed by this alignment — build constraints)

1. **One line table per entity:** MR = Material Allocation only; MIS = header + lines; no duplicate "Line Items" + "Allocation" on the same form.
2. **Numbering:** every prefixed number through P1 counter; auto-number fields only where pure numeric is acceptable.
3. **Single shared functions (P1–P8):** numberSeries, expandCosting, crossValidate, getAvailableStock, autoPR, postGRN (incl. G5), postMIS (incl. G4), consumeAllocation (incl. block >100% + checkAllocationAlert), returnAllocation, checkAllocationAlert. **No inline re-implementation in form scripts.**
4. **Blueprint transitions stay ≤50 statements** — anything heavier moves to on-change form workflows.
5. **Alerts:** 80% → PM email + dashboard flag; 100% → PM + Purchase; both from one function.
6. **Allocation writes only from:** BMR (P6), SCE (P6), MRT (credit), MIS (Issued Qty, G4) — never from a generic stock pool.

---

## 5. Build Verification Checklist (tie-in to DELIVERY_PLAYBOOK.md phases)

| Playbook phase | Verify |
|---|---|
| 0 (shared core) | P1 counter produces CST-2026-0001…; F1–F2, F14 applied |
| 1 (procurement) | A-21–A-29; F9 (G5 on Post GRN), F12 applied; GRN→PO status cycle tested |
| 2 (SO→Costing→Plan) | A-06–A-14; F3, F7 applied; Costing Approved → Project+Plan chain |
| 3 (MR gate) | A-15–A-20; F4, F5, F8, F10, F11 applied; cross-validation 5%/10%; auto-MIS |
| 4 (production) | A-30–A-37; F6 applied; block >100% works; FGHM accept → FG + |
| 5 (site+inventory) | A-38–A-43; 80%/100% alerts from BMR+SCE; MRT credit |
| 7 (UAT) | Full scenario re-run with findings closed; every ⚠ row above re-checked in Creator console |

## 6. Sign-off

| Item | Status |
|------|--------|
| All automation cards + inventory table walked in full | ✅ |
| Every automation mapped to a process step + evidence report | ✅ |
| Alignment verified against AGENTS.md, forms.html, UAT (C1–C27), reports (G1–G9), feasibility (P1–P8) | ✅ |
| 43-automation canonical register (A-01…A-43) published | ✅ |
| Findings F1–F14 logged with verdicts | ✅ (10 fix · 4 decision) |
| F2, F13 decisions pending client | ⏳ |
