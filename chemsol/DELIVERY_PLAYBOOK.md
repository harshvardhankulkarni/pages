# Chemsol — Rapid Delivery Playbook (Build → Client Go-Live)

> **Goal:** Deliver the full Chemsol ERP to the client with working automation + detailed reports in the shortest realistic time.
>
> **Targets:** ~25 working days (1 builder) · ~15 working days (2 builders, parallel streams). If the client has existing sample data, import it during Phase 5 — never before (schema must be final first).
>
> **Inputs (already done, no re-research needed):**
> - `ZOHO_CREATOR_FEASIBILITY_PLAN.md` — every construct pre-verified against official Zoho docs; use ONLY these patterns
> - `automation.html` §"Implementation Order" + §"Common Deluge Patterns" — build order + copy-paste templates
> - `REPORT_IMPLEMENTATION_PLAN.md` — G1–G9 schema changes + R0–R7 report spec
> - `UAT_VERIFICATION_PLAN.md` — one end-to-end scenario with expected values; the only test script needed
> - `forms.html` / `BRD_PRD_RFP.md` — field-level source of truth

---

## 1. Speed Strategy (the rules that make this fast)

| # | Rule | Why |
|---|------|-----|
| S1 | **Schema-first:** when building ANY form, add all report/automation fields in the same pass (Status, Received Qty, Rate/Amount on lines, section subtotals). Never retrofit later | The G1–G9 gap list in REPORT_IMPLEMENTATION_PLAN.md cost a whole phase; retrofit is the #1 schedule killer |
| S2 | **Pattern library before forms:** Day 1 builds the 8 shared Deluge patterns (P1–P8 from feasibility plan) as custom functions (`numberSeries()`, `updateAllocation()`, `updateStock()`, `consumeAllocation()`, `autoPR()`, `expandCosting()`, `crossValidate()`, `postGRN()`) | Every later form reuses them — no re-writing |
| S3 | **Vertical slices, not horizontal:** Stream A (PR→PO→GRN→QC) works end-to-end by Day 4. Then Stream B core (SO→Costing→MR→MIS). Working loops early = de-risked delivery | Proven conventions early, everything else is copy-paste |
| S4 | **MR gate first in Stream B:** Blueprint (Draft→Pending Production Verification→Verified→Approved→Released) built and tested before downstream forms | Every downstream form (MIS, BMR, FGHM) depends on MR statuses |
| S5 | **Reports go live per-department** as soon as that form set is built (R4 after procurement, R5 after production…) — not batched at the end | Client sees progress weekly; feedback lands while forms are still warm |
| S6 | **UAT is continuous:** run the UAT_VERIFICATION_PLAN scenario at every gate, not at the end | C1–C27 class bugs get caught the day they're built |
| S7 | **2-builder parallel split:** Builder A = Stream A (procurement + inventory + R4/R6); Builder B = Stream B (project + costing + production + site + R1–R3/R5/R7). Shared master data done together Day 1–2 | Only true parallelization available; the two streams are independent by design |
| S8 | **No experiments during build:** only constructs from the feasibility plan; anything new = research task with its own timebox | Unverified features are the #2 schedule killer |

---

## 2. Phase Plan (working days)

Legend: `✅ verify with UAT scenario step` · `🔁 reuse pattern`

### Phase 0 — Scaffold + Shared Core (Days 1–2)

| Day | Deliverable | Uses |
|-----|-------------|------|
| 1 | App created (.in). **All 6 master-data forms** (Item Muster, Supplier, System, System Composition, BOM, Customer/Site) with lookup filters + autofetch. Roles skeleton | feasibility §2 · forms.html §1 |
| 1–2 | **Shared custom functions P1–P8** (number series, stock, allocation, costing expansion, cross-validation, auto-PR, post-GRN, post-MIS). Verified email sender configured | feasibility §4 |
| 2 | No_Series config form (P1) + numbering on all forms that need prefixes | P1 |

**Gate G0:** master data + numbering functions tested. UAT steps: seed items/suppliers/systems/BOM.

### Phase 1 — Stream A slice: PR→PO→GRN→QC (Days 3–4)

| Day | Deliverable | Uses |
|-----|-------------|------|
| 3 | PR (autofetch, dept from login) + Rate Comparison (5-supplier subform) | P1 numbering |
| 3–4 | PO (conditional **RMWAD/RM** series P8, GST split formula, status) → GRN (partial checkbox, **Post GRN button** = postGRN(), G5 fields) → QC | P1, P8 · forms.html §4 |
| 4 | R4 reports (Open PO Register, PO vs GRN Pending, Vendor Performance) + Purchase dashboard | reports.html R4 |

**Gate G1:** purchase loop works end-to-end; UAT procurement steps pass.

### Phase 2 — Stream B core: SO→Costing→Plan (Days 5–8)

| Day | Deliverable | Uses |
|-----|-------------|------|
| 5 | SO with Sales Type swap (field rule: Subform A System Lines vs Subform B FG Lines), Status field (G1) | field rules |
| 6–7 | **Costing Sheet — the biggest automation:** Section A auto-expansion from SO×System Comp×BOM (expandCosting() P2), 5 section subtotal formulas (G3), Blueprint Approval → auto-create Project + Production Plan draft (P3) | P2, P3 |
| 8 | Production Plan: Available Stock = physical − Σunreleased MR assignments (P4), Released → auto-PR (autoPR() P8) | P4, P8 |

**Gate G2:** SO→Costing→Project chain works. UAT: SO + Costing steps pass with expected ₹144,000 baseline.

### Phase 3 — MR gate + MIS (Days 9–10)

| Day | Deliverable | Uses |
|-----|-------------|------|
| 9 | MR auto-derived (4 cost components pre-filled), Material Allocation subform (Assigned/Ratio/80% flag/Issued/Consumed), **cross-validation >5% flag >10% block (P5)** | P2, P5 |
| 10 | MR **Blueprint 5-state gate** (≤50 stmt transitions) + schedules (2 hr reminder, 2 hr escalate, 1 hr auto-release) + release → auto-MIS draft (P3). R3 report seeds | Blueprint · schedules |

**Gate G3:** THE critical gate works. UAT: MR steps + cross-validation + SLA schedule checks pass.

### Phase 4 — Production + FGHM (Days 11–12)

| Day | Deliverable | Uses |
|-----|-------------|------|
| 11 | Production Job + BMR (RM lines from BOM, Rate/Amount per line G8, consumeAllocation() P6) + RM Consumption (variance check only) + Packing (packaging deduction) | P6 |
| 12 | FGHM with **inline accept = report custom button** (P7: mark allocation fully consumed + FG stock +) + R5 reports + Production dashboard | P7 |

**Gate G4:** full production loop live. UAT: MIS→BMR→FGHM steps pass (275/125 kg).

### Phase 5 — Site ops + P&L + Inventory (Days 13–14)

| Day | Deliverable | Uses |
|-----|-------------|------|
| 13 | SCE (hourly/daily per area; Rate/Amount G8; consumeAllocation() P6; **80%/100% alerts**) + Material Return (credit allocation, restore stock, good/damaged) | P6 |
| 14 | Project P&L real-time (R2/R3), Project Inventory Status, R6/R7 (incl. FG Consumption Log + Project FG Position from G9), Costing vs Actual variance. **Start data import of client sample data** | reports.html |

**Gate G5:** everything in the flow exists. Full UAT scenario run start-to-finish (passes 1–N from UAT_VERIFICATION_PLAN.md).

### Phase 6 — Reports polish + security (Days 15–16)

| Day | Deliverable |
|-----|-------------|
| 15 | Department dashboards complete (Purchase/Store/Production/Costing/Site R0–R7), drill-downs, print templates (PO with GST split, MR, FGHM) |
| 16 | Roles & permission sets per department (per-plan limit check), conditional field visibility, admin lock on released records. Security walkthrough |

### Phase 7 — UAT hardening (Days 17–19)

- Full UAT scenario repeated **twice**, all findings logged to UAT_VERIFICATION_PLAN.md change log
- Schedule triggers tested with forward-dated records (2 hr / 2 hr / 1 hr / 24 hr escalations)
- Concurrency test: two users posting GRN/MIS simultaneously (checks P1 counter + stock updates)

### Phase 8 — Client delivery (Days 20–22)

| Day | Activity |
|-----|----------|
| 20 | Deploy to **stage** → client UAT session #1 (walk the scenario live) |
| 21 | Fix client feedback → session #2 (freeze) |
| 22 | Training (2 h per department: Costing, Purchase, Store, Production, Site) + user manual handover + **sign-off** |

### Phase 9 — Go-live + hypercare (Days 23–25)

- Move app to **live**; verify sample data import; first 3 live jobs supervised
- Daily check-ins Day 23–25; open issues tracked in the UAT change log
- Handover: admin credentials, Zoho support ticket access, this playbook + feasibility plan as the build bible

---

## 3. Automation Build Checklist (in build order — from automation.html)

| # | Automation | Form | Phase |
|---|-----------|------|-------|
| 1 | Auto numbering (P1) | all | 0 |
| 2 | Form rules: Sales Type swap, lookup filters (MIS→Released MRs only), PO from PR, BMR RM list from BOM | SO, MIS, PO, BMR | 1–4 |
| 3 | Formula fields: totals, GST split, Balance Qty, Receipt Status, Allocation %, variance | all | 1–5 |
| 4 | **Blueprint MR gate** (Draft→Verified→Approved→Released) | MR | 3 |
| 5 | Workflow rules: SO→Costing Sheet (Project on Costing Approved), stock updates, auto-PR, 80% alert | SO, GRN, MIS, FGHM, SCE | 1–5 |
| 6 | Custom buttons: Post GRN, Post MIS, FGHM accept | GRN, MIS, FGHM | 1–4 |
| 7 | Schedules: SLA escalations, GRN overdue 7d, min/max stock alerts | MR, GRN, Inventory | 3–5 |
| 8 | Custom functions P1–P8 | shared | 0 |
| 9 | Print templates (PO GST split, MR, FGHM, Costing Sheet) | PO, MR, FGHM, Costing | 6 |

## 4. Reports Checklist (R0–R7 + G9 additions)

| Report | Dashboard | Phase |
|--------|-----------|-------|
| Open PO Register, PO vs GRN Pending, Vendor Performance (R4) | Purchase | 1 |
| Sales Register, SO Type Split (R2) | Sales | 2 |
| Costing Status, Costing vs Actual, Project Cost Baseline (R3) | Costing | 3 |
| Daily Production, BOM vs Actual, FG Handover Pending (R5) | Production | 4 |
| FG Consumption Log, Project FG Position (R6 + G9) | Store | 5 |
| Project Inventory Status, 80% Utilization, MR Status drill-through (R7) | PM/Costing | 5 |
| Project P&L real-time, Task Budget vs Actual | PM | 5 |
| Site Consumption hourly/daily, Material Return register | Site | 5 |

## 5. Delivery Gates (definition of done per phase)

| Gate | Exit criteria |
|------|---------------|
| G0 | Master data + numbering + shared functions tested; UAT seed data in |
| G1 | PR→PO→GRN→QC end-to-end; R4 live; partial GRN + stock posting verified |
| G2 | SO→Costing (₹144,000) → Project + Plan auto-chain works |
| G3 | MR gate: cross-validation blocks >10% (per-RM, C31), 5-state blueprint, SLA schedules, auto-MIS |
| G4 | Production loop live: MIS→BMR→Packing→FGHM accept (275/125 kg, FG stock +) |
| G5 | Full UAT scenario passes end-to-end (all ledger numbers tie, P&L +₹31,000) |
| G6 | Client UAT passed, training done, **sign-off received** |
| G7 | Live, hypercare complete, handover pack delivered |

## 6. Risk Register (killers, with countermeasures)

| Risk | Impact | Counter |
|------|--------|---------|
| Client scope additions mid-build | schedule | Freeze at G2; additions logged as Phase-2 items |
| Sample-data import corrupts schema | data integrity | Import only at Phase 5 after schema freeze (G5) |
| P1 counter collision under concurrency | wrong document numbers | No_Series lock pattern; concurrency test at Phase 7 |
| Schedule SLA testing skipped | silent failures | Forward-dated records in UAT (Phase 7) |
| Client has no Creator admin | handover blocked | Request admin credentials at kickoff, not go-live |
| Plan tier too small (records/API) | throttling | Resolve Q1/Q4 from feasibility plan BEFORE Day 1 |

## 7. Handover Pack (deliver to client at G7)

1. Admin + user credentials matrix · 2. This playbook · 3. Feasibility plan (build bible) · 4. UAT plan with signed-off change log · 5. Training manual (2 h per department) · 6. Zoho support ticket access · 7. Hypercare calendar (Days 23–25)

---

## 8. Sign-off

| Item | Status |
|------|--------|
| Plan ready for build kickoff | ✅ |
| Feasibility clarifications Q1–Q9 answered | ⏳ **required before Day 1** |
| Builder assigned (1 or 2 builders → pick 25-day or 15-day track) | ⏳ client/kickoff |
| Sample data available for Phase 5 import | ⏳ confirm at kickoff |
