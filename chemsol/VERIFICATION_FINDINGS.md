# Chemsol — Structure Verification Findings (2026-08-06)

> Full-structure audit: **31 forms · 488 fields · 43 automations (A-01…A-43) · 26 Deluge files · 59 reports · 8 dashboards · 53 widgets** — cross-checked against the canonical process loop by 4 parallel audits (T1 fields, T2 automations, T3 reports, T4 loop map; full detail in `implementation/verify/audit/audit_1..4_*.md`). All BLOCKER/FIX claims independently re-verified by the orchestrator before this document.
>
> **Baseline:** `flow_sim.py` 72/72 green before fixes. Every loop stage (12/12) has ≥1 automation and ≥1 report. Alignment verdict: structure aligns with the loop; **4 BLOCKERs + 14 FIXes found, all corrected in this run** (statuses below).

---

## BLOCKERS (build would be wrong — all fixed)

| # | Rule | Problem | Evidence (verified) | Fix applied |
|---|------|---------|---------------------|-------------|
| B1 | MR single line table (F4) | MR spec still shows TWO tables: "Line Items (N items)" **+** "Material Allocation Subform". Canonical = Material Allocation ONLY (all automations A-15/18/33/38/40 read/write Allocation). Ghost `MR_Line_Items` would be built. | forms.html:736-756 + :758-800; IMPLEMENTATION_PLAN.md:387-427; automation.html:588; AUTOMATION_ALIGNMENT_PLAN.md:106,124 | ✅ Line-Items table removed from forms.html + IMPL (replaced with single-table note); MR.csv legacy layout documented as do-not-build |
| B2 | PO Project ID optional (Stream A) | IMPLEMENTATION_PLAN.md:505 marks PO Project ID `*` REQUIRED. Stream A POs have no project; forms.html:912 already optional. | IMPL:505 vs forms.html:912, reports.html:207, AGENTS.md:54 | ✅ IMPL `*` removed → "Optional — project-tagged procurement only" |
| B3 | GRN Project ID optional (Stream A) | GRN Project ID `*` REQUIRED at forms.html:974 + IMPL:541. Stream A GRNs (stock procurement) have no project. | forms.html:974; IMPL:541; chemsol/AGENTS.md:15,67 | ✅ Both docs → Optional (AutoFetch from PO; blank for Stream A) |
| B4 | Costing §A Required Qty formula | Three formulas in docs: forms.html:589 `BOM Ratio × Area`; IMPL:282 `BOM Qty × Area × (1+Waste%)`; Deluge/AGENTS convention `round(Area × CompQty/sqm × Ratio, 1)` (this is what flow_sim asserts — 275/125 kg, ₹103,000). First-time builder cannot tell which wins. | forms.html:589; IMPL:282; root AGENTS.md Deluge conventions; flow_sim.py:84-93 | ✅ All docs → `Required_Qty = round(Area × CompQty/sqm × Ratio, 1)`; Waste% declared informational (absorbed in full-precision ratios), not applied in §A |

---

## FIXES (misalignments — all applied)

| # | Area | Problem | Evidence | Fix applied |
|---|------|---------|----------|-------------|
| F1 | MR states | 4-state residue: IMPL:890 (Week 4-6), reports.html:195 (dashboard label), forms.html:1672-1677 (§6G diagram) | Canonical 5-state: forms.html:735, C30/F11 | ✅ All 3 → 5-state wording |
| F2 | SO → Project | IMPL:881 "SO → Project automation" residue; canonical = SO acceptance → Costing Draft, Project on Costing Approved (C2/F3/C6) | IMPL:881 vs IMPL:976, forms.html:382, automation.html:1635 | ✅ → "SO → Costing Sheet automation" |
| F3 | P&L formula | Project P&L diverges across docs: G2 = Revenue − MR Total Actual Cost (forms.html:484-485, sim +₹31,000); "Costing Sheet Total − consumption − procurement" (AGENTS.md:188, IMPL:916/1007); Task-Budget actuals (forms.html:517, no automation). First-time builder ambiguity. | forms.html:484-485; chemsol/AGENTS.md:188; IMPL:916 | ✅ G2 (MR-based) kept as THE Project.P&L; cost-variant relabelled "Costing vs Actual Variance (R3)"; Task-Budget actuals marked future feed (C4) |
| F4 | PO Total Amount (G5) | R4 `PO Value by Supplier` needs numeric PO header Total Amount; forms.html footer + PO.csv have only Basic/CGST/SGST/IGST/Amount-in-Words. | reports.html:434; forms.html:938-952; REPORT_PLAN:17,49 | ✅ forms.html + IMPL PO footer + line items: added numeric `Total Amount` (= Basic_Total + CGST + SGST + IGST) + per-line CGST/SGST/IGST + Supplier_State (F12 parity) |
| F5 | FG Inventory Category (G7) | FG ledger lacks `Category` → R6 Inventory Valuation group-by + Store "Stock by Category" pie unbuildable. | forms.html:1372-1384; reports.html:482,511 | ✅ Category field added to FG Inventory spec (AutoFetch from Item Muster) |
| F6 | Vendor Performance formula | reports.html:437 "GRN date − PO date" vs forms.html:951/plan/sim "GRN Date − Delivery Date" (=5 days, sim-asserted). | reports.html:437; forms.html:951; flow_sim.py:404-405 | ✅ reports.html → "GRN Date − Delivery Date" |
| F7 | Purchase by Item Group | group-by: reports.html "Item Category" vs plan "Item Code"; PO lines carry no Category. | reports.html:435; plan:139; forms.html:924 | ✅ Aligned to **Item Code** (buildable); Category AutoFetch added to PO line items as optional group-by source |
| F8 | BMR vs BOM Variance | group-by: reports.html "FG Code" vs plan "BMR Reference"; RM Consumption form has no FG Code field. | reports.html:462; plan:162; forms.html:1175-1179 | ✅ Aligned to **BMR Reference** |
| F9 | MIS numbering | IMPL:827 "Auto against MR" vs automation.html "MIS-YYYY-XXXX". | IMPL:827; automation.html:1074 | ✅ IMPL + reports.html → MIS-YYYY-XXXX |
| F10 | Fully Consumed wording | IMPL:425 "set when Consumed ≥ Assigned (100%)" per line vs ALL-lines rule (C29, sim-asserted). | IMPL:425; forms.html:799; flow_sim.py:168-171 | ✅ IMPL → "set only when ALL allocation lines ≥ 100%" |
| F11 | Costing escalation SLA | IMPL:1027 "8 hr escalation" vs 24h (A-08 costingSlaEscalate, sim 25h check). | IMPL:1027 vs flow_sim.py:267-274 | ✅ IMPL → 24h escalation (4h reminder kept) |
| F12 | Notifications §8.7 gaps | Deluge missing: Costing-Approved → Production+PM email (A-11); MIS Posted → Production; MRT → Store; MR Released email lacks PM; no <20%-remaining check. | IMPL:846-867; costingApproveChain (no sendmail); postMIS.deluge:42-43; materialReturn.deluge:40; inventoryAlerts.deluge | ✅ 5 Deluge files updated + sim mirrored (new asserts) |
| F13 | Costing header fields | Prepared By / Reviewed By / Revision No only in IMPL, absent forms.html. | IMPL:267-269 vs forms.html:564-569 | ✅ Added to forms.html |
| F14 | User Access & Approval Matrix | Spec exists only in IMPL §2.7, absent forms.html. | IMPL:2.7; Screens.csv:12-13 | ✅ Added to forms.html master-data section |

---

## FIX-AT-CONSOLE (Creator runtime notes — documented in build guide, not silently rewritten)

| # | Issue | Detail | Pattern to use in Creator console |
|---|-------|--------|----------------------------------|
| C1 | `MR_Allocation` used as a queryable/updatable form (8 files) | Subforms are NOT standalone forms in Creator; `lookupRecords(MR_Allocation,…)`/`updateRecord` on a subform fails at runtime. flow_sim models it as an entity, masking this. | Query **MR_Master** by Project_ID (+ MR_Number), iterate `MR_Allocation` rows for the Item_Code match, then `updateRecord MR_Master` re-PUTting the modified subform rows (keep row IDs). Or promote Material Allocation to a real form linked to MR (aligns with the pivot reports). Applies to: postMIS, consumeAllocation, sceSubmit, materialReturn, fghmAccept, checkAllocationAlert, getAvailableStock |
| C2 | `Project_ID`/`MR_Ref` filters on MR_Allocation don't exist | 17-field subform spec has no parent-ref columns (they live on MR_Master header) | Resolution filters go through the parent MR lookup (C1 pattern). Do NOT add duplicate Project_ID to subform rows. |
| C3 | crossValidate variance write target | Script wrote header-level Variance_Flag/% but spec defines them per allocation line (rows 16-17) | **Fixed in script** → per-line compute + per-line flags (matches sim C31); header `throw` on >10% kept |
| C4 | Deluge API-name registry | Snake_case names (MR_Allocation, 80%_Alert_Flag…) are a convention; no label→API registry exists; two aliases live on (`Costing_Sheet_Ref` vs `Costing_Sheet_No`; `Costing_Material_Lines` vs `Costing_Section_A`) | Standardize at console: one internal name per form/field, registry row per field in the build guide Part 8 |

---

## DECISIONS (client, not changed here)

| # | Item | Options | Recommendation |
|---|------|---------|----------------|
| D1 (F2) | Master codes format | short (RM-001/FG-002/SUP-0001 — UAT data) vs YYYY-XXXX (transaction-style) | Short sequential for masters; YYYY-XXXX for transaction docs only |
| D2 (F13) | Rate Comparison + Material Handover scope | Excluded from core loop (AGENTS.md) vs still in Excel/BRD | Exclude from core build; keep Rate Comparison as standalone reference only; Material Handover = Store-side manual process, no automation |
| D3 | Excel drift | `files/*.csv` (xlsx exports) stale vs docs: legacy MR layout, no Costing/Plan/SCE/MRT/inventory sheets, Sheet2/Sheet4/Project/Screens = mockups, FGAN sheet negated (inline acceptance), "Administration" category, "Suppy+Apply" typos | Regenerate Excel from forms.html when docs freeze; treat forms.html/automation.html/reports.html as build source of truth |

---

## INFO (documented, no change)

- 43 cross-source field discrepancies logged in audit_1 (typos: "HNS"→HSN, "Suppy+Apply"; extra CSV fields to keep: Supplier Pincode/Type, GRN Client-Site conditional, QC Packaging Quality, PO UOM/Mode of Transport, PR Approved By; numbering gaps: SUP-…, FGC-… series).
- 3 report aliases each for `Costing vs Actual Variance` and `80% Alert List`; "Project Status List" vs "Project Status" widget naming; Production Job field "Job Number" vs COUNT(Job No) — cosmetic.
- R3/R6 cross-form Summary reports (MR+SCE+BMR; RM+FG; FGHM+FG Cons) need Deluge-consolidated tables in Creator (native reports are single-form) — mitigated by G4/G5/G8 denormalized fields + Project FG tracking form; console UAT must validate.
- `Today's Production` sim assertion uses FGHM-accepted qty as proxy for BMR yield (R5 aggregates BMR Yield/FG Output) — sim seed lacks yield; flagged, not a spec conflict.
- Stream A PR/PO/GRN Project ID semantics: optional-tagged (see B2/B3) — AGENTS.md absolute wording aligned.
- Available Stock semantics verified consistent across all docs (unreleased MRs = status ≠ Released; "other" implied for own drafts).
- Roles: IMPL §10 (13 granular roles) vs 8-role UAT set — compatible; AGENTS.md:181 dept list is a different classification (Finance/Coordinator not role-mapped) — aligned note.

---

## Verification of this run

- [x] Every BLOCKER/FIX re-verified at source (file:line) by orchestrator before fixing
- [x] Doc fixes applied: forms.html, IMPLEMENTATION_PLAN.md, reports.html, chemsol/AGENTS.md, root AGENTS.md
- [x] Deluge fixes applied: crossValidate (per-line variance), 5 notification gaps; F-02/F-03 console patterns documented in-file
- [x] flow_sim.py mirrored (notifications asserts) → **76/76 green**
- [x] Audit artifacts: `implementation/verify/audit/audit_1_fields.md` (488 fields), `audit_2_automations.md`, `audit_3_reports.md` (59 reports), `audit_4_loop_map.md` (12 stages)
- [ ] Console UAT in Zoho Creator (.in) — pending (F10 blueprint transitions, C1 patterns)
