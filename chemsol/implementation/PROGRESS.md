# Implementation Progress — implement → verify → fix → reverify loop

> Each phase: implement (Deluge + sim) → run `verify/flow_sim.py` → fix findings → rerun green → move forward. Current status at the bottom.

## Harness

`verify/flow_sim.py` mirrors every automation's business logic (patterns P1–P8, findings F1–F14 applied) and executes the canonical UAT scenario (UAT_VERIFICATION_PLAN steps 1–10) with 68 assertions grouped by delivery phase.

## Loop runs

| Run | Date | Result | Findings → fixes |
|-----|------|--------|------------------|
| 1 | 03-Aug-2026 | **38 pass / 11 fail** | Initial run against doc seed. Root causes: C28 (BOM ratios 0.33/0.58 rounded → 49.5 kg/174.0 kg broke Section A ₹103,000, ΣBOM 400, cross-validation); C29 (FGHM `Fully Consumed` expectation contradicted the ≥100% rule); sim bugs: per-RM aggregation overwrite, MIS Issued Qty never set before Post, SLA placeholder, cross-val float rounding |
| 2 | 03-Aug-2026 | **45 pass / 5 fail** | UAT master data fixed (0.3333/0.5817), Step 7e expectation corrected, C28+C29 logged in UAT change log; sim harness fixed (aggregation, MIS issue, real SLA asserts, rounding) |
| 3 | 03-Aug-2026 | **50 pass / 0 fail** | Sim seed synced to corrected master data — all green |
| 4 | 03-Aug-2026 | **68 pass / 0 fail** | Remaining verification completed: real clock SLA (2h reminder / 1h auto-release), per-item cross-val mutations (+6%/+11%, C31), SO→Costing auto-create (A-07), Costing 24h escalation, real Delivery Days (5), G8 rate/amount asserts on BMR+SCE, R1–R7 report sweep, 5-state MR Blueprint model. H-5: SLA reminder tests ran after the MR had left Draft — reordered (sim-only bug) |

## Phase-by-phase verification (run 4)

| Phase | Asserts | Result | What it proves |
|-------|---------|--------|----------------|
| P0 shared core | 1 | ✅ | P1 independent counters (SO/RMWAD/RM) |
| P1 procurement | 9 | ✅ | RMWAD series, GST split (₹16,500/₹2,970/CGST-SGST ₹1,485/₹19,470), G5 fields (0/75/Not Started → 75/0/Complete), delayed stock posting (200→275), PO Fully Received, Delivery Days 5 (GRN 17 Jan − delivery 12 Jan), movement log, QC |
| P2 SO→Costing→Plan | 12 | ✅ | SO ₹175,000; SO Accepted → Costing Sheet Draft auto-created (A-07); Section A 4 lines 275/125 kg = ₹103,000; sheet ₹146,000; >24h Under Review escalation; chain creation (Revenue ₹175,000 at Project); Plan available 200/400, shortage 75 kg → auto-PR |
| P3 MR gate | 14 | ✅ | 4 components ₹144,000 (Sec E excluded); ratios 68.75/31.25; per-item cross-val 0% pass, +6% flag, +11% block (C31); 5-state Blueprint path; SLA 2h reminder once (no re-reminder, none before 2h) + 1h auto-release (none before); Project cost ₹144,000, P&L +₹31,000; MIS draft (header+lines, F5) |
| P4 production | 13 | ✅ | Post MIS → stock 0/275, Issued 275/125, 2 log rows; BMR 36.5/39.6 → 100/99.6; G8 BMR rate×qty = ₹22,110/₹16,830; 80% + 100% alerts fired once; RC variance-only (C25); packing deducts packaging only; FGHM → FG +148/+300, `Fully Consumed` stays OFF (C29) |
| P5 site + inventory | 7 | ✅ | SCE 8a whole-submit rejected (103.6%); MRT credit (265/114.5, returned 10/10, stock 10/285); SCE 8c accepted (100%/95.6%); G8 SCE ₹2,200/₹1,700; FG consumption → 0/20; min/max reorder fires |
| P7 final state | 5 | ✅ | Remaining 10 / 15.5 (= Assigned − Consumed + Returned); P&L +₹31,000; R6 stock 10/285; no negative stock anywhere |
| REP reports | 7 | ✅ | R1–R7 sweep: master seeds, Sales Register (₹175,000/In Progress/Task Budget ₹50,200), Costing 1 Approved ₹146,000 + MR Released ₹144,000 + 80% alerts, PO Register empty + Vendor Performance 5 days, MIS 275/125 + Today's Production 448 kg, RM stock 10/285 + valuation ₹99,100 + SCE log 1, dashboard traceability |

## Findings logged this loop

| # | Finding | Fix | Status |
|---|---------|-----|--------|
| C28 | BOM master-data ratios were 2-dp rounded (0.33, 0.58) → Section A 49.5/174.0 kg, ₹102,720, ΣBOM 399 — all canonical downstream numbers broke | UAT master data → 0.3333 / 0.5817; rounding rule documented (round to 1 dp, amount = required × rate) | ✅ APPLIED, sim green |
| C29 | Step 7e expected `Fully Consumed` at FGHM accept but rule = ALL lines ≥ 100% (RM-002 = 99.6%) | UAT Step 7e expectation corrected; sim asserts flag stays OFF; code comment in fghmAccept.deluge | ✅ APPLIED, sim green |
| C31 | Cross-validation was aggregate-level but UAT Step 5 mutates ONE line (+6%/+11%) — single-line error drowned in Σ. Rule refined to per-RM line: `|Assigned − BOM expected| ÷ expected`, >5% flag, >10% block | crossValidate.deluge + sim per-item; mutation tests pass (+6% flag / +11% block / revert clean) | ✅ APPLIED, sim green |
| H-1..H-4 | Sim harness bugs (aggregation overwrite, MIS Issued unset, SLA placeholder, float rounding) | Harness fixed — not product defects | ✅ |
| H-5 | SLA reminder tests ran AFTER MR had left Draft (5-state block moved it to Production Verified) → reminder never fired | Test block reordered: Draft reminder first, then transitions | ✅ |

## Implementation status

| Phase | Deluge files | Verified | Console paste-in (Zoho .in) |
|-------|--------------|----------|----------------------------|
| 0 shared | numberSeries, stockMoveRM, stockMoveFG, checkAllocationAlert | ✅ 1/1 | ⏳ manual |
| 1 procurement | poSeriesPrefix, poGstSplit, postGRN, prStatusNotify | ✅ 9/9 | ⏳ manual |
| 2 costing | expandCosting, costingApproveChain, getAvailableStock, planReleaseAutoPR | ✅ 12/12 | ⏳ manual |
| 3 MR gate | mrDerive, crossValidate, mrReleaseAutoMIS, mrSlaSchedules | ✅ 14/14 | ⏳ manual |
| 4 production | postMIS, consumeAllocation, bmrSubmit, fghmAccept, packingDeduct | ✅ 13/13 | ⏳ manual |
| 5 site | sceSubmit, materialReturn, fgConsumption, inventoryAlerts | ✅ 7/7 | ⏳ manual |
| 7 UAT | — (sim IS the UAT run) | ✅ 5/5 | ⏳ console UAT + findings F10 |

**Loop complete — 68/68 green (run 4: remaining verification completed — SLA timing, per-item cross-val C31, SO→Costing A-07, 24h escalation, Delivery Days, G8 rates, R1–R7 sweep). Next:** paste into Zoho Creator (.in) per playbook phases; console-level items still open: F10 Blueprint auto-transition verify, Q1–Q9 clarifications, sender email verification.
