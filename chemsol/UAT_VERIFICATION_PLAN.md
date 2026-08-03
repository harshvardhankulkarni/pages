# Chemsol — UAT Verification Plan (Full Process Walkthrough)

> **Purpose:** Verify the complete ERP process end-to-end with one scenario — SO → Costing → Project → Procurement → MR → MIS → Production → FGHM → Site → P&L. Every field gets a real value; every automation has an expected outcome; every report has a check.
>
> **How to use:** In Zoho Creator (.in console), follow steps 1→N in order, entering the sample values. Tick boxes as you verify. Any mismatch → note it in the section and add to the Change Log at the bottom before continuing.
>
> **Rule of thumb:** If the actual result differs from the "Expected" line, the bug is in the doc or the build — log it, don't ignore it.

---

## Test Scenario (one job, flows through everything)

| Item | Value |
|------|-------|
| Customer | Acme Logistics Pvt Ltd |
| Site | Acme DC — Chakan, Pune |
| System | EP02 (2 mm Epoxy Flooring) |
| Area | 500 sqm |
| SO Rate | ₹350 / sqm |
| SO Total | **₹175,000** |
| Sales Type | **Supply+Apply** (Project-creating path) |

### Master data to seed first (once)

**Item Muster (RM):**

| Code | Name | Category | UOM | Rate | HSN | GST% | Min | Max | Lead (days) |
|------|------|----------|-----|------|-----|------|-----|-----|------|
| RM-001 | Epoxy Resin A | RM | Kg | ₹220 | 3907 | 18% | 50 | 500 | 7 |
| RM-002 | Hardener B | RM | Kg | ₹340 | 3907 | 18% | 30 | 400 | 7 |

**Item Muster (FG):**

| Code | Name | UOM | Rate |
|------|------|-----|------|
| FG-002 | Epoxy Primer Coat | Kg | ₹480 |
| FG-003 | Epoxy Top Coat | Kg | ₹520 |

**System Master:** EP02 = "2mm Epoxy Flooring" — Status: **Released**

**System Composition (EP02 → FG, per sqm):**

| System | FG | Qty/sqm |
|--------|----|---------|
| EP02 | FG-002 Epoxy Primer | 0.30 kg |
| EP02 | FG-003 Epoxy Top Coat | 0.50 kg |

**BOM / FG Formulation (FG → RM, per kg of FG output):** (Status: **Released**)

| FG | RM | Ratio |
|----|----|-------|
| FG-002 | RM-001 Epoxy Resin A | 0.67 kg |
| FG-002 | RM-002 Hardener B | 0.33 kg |
| FG-003 | RM-001 Epoxy Resin A | 0.70 kg |
| FG-003 | RM-002 Hardener B | 0.30 kg |

**Supplier:** SUP-0001 = "ResinCorp Polymers" (GSTIN, PAN, payment terms 30 days)

**Store:** ST-01 = "Wadki" (bin location subform: Bin A-1)

**RM Inventory opening (Wadki):** RM-001 = **200 kg**, RM-002 = **400 kg**

**Expected RM requirement math (for later cross-checks):**
- RM-001: FG-002 500×0.201 = 100.5 kg + FG-003 500×0.349 = 174.5 kg → **275 kg** (BOM ratio × area — same model as Costing Section A)
- RM-002: FG-002 500×0.099 = 49.5 kg + FG-003 500×0.150 = 75 kg → **124.5 → 125 kg**
- FG output (EP02 system composition): FG-002 500×0.30 = **150 kg**, FG-003 500×0.60 = **300 kg** (C22 — matches FGHM Step 7e + R5 448 kg)

---

## STEP 1 — Sales Order (SO)

**Create** `SO-2026-0001` — Sales Type = **Supply+Apply**

| Field | Value |
|-------|-------|
| SO Date | Today |
| Employee Name | Sales Rep 1 |
| Customer Code | CUS-0001 (lookup → autofetch Org/GST/Contact) |
| Client Org | Acme Logistics Pvt Ltd |
| GST / PAN | 27AACCA1234F1Z8 / AACC1234F |
| Regd Address | Mumbai HQ, Bandra East |
| Site Name / Address | Acme DC — Chakan, Pune |
| Site Manager | R. Sharma / 98200xxxxx |
| Project Type | Industrial |
| Payment Terms | 30% advance, 70% on completion |
| Transportation Scope | Own |
| Lead Time | 10 days |
| Warranty | 2 years |
| Commission | Checkbox ON → 2% |
| **Status** | **Draft** → then **Accepted** (G1) |

**Subform A — System Lines:**

| System Code | Name | Thickness | Area | UOM | Rate | Amount |
|-------------|------|-----------|------|-----|------|--------|
| EP02 | 2mm Epoxy Flooring | 2mm | 500 | SqM | ₹350 | **₹175,000** |

**Expected automation:**
- [ ] `Total Amount` = ₹175,000 (formula = Σ line Amounts)
- [ ] Sales Type = Supply+Apply → only Subform A visible (Subform B hidden)
- [ ] Set Status = Accepted
- [ ] Costing Sheet **Draft** auto-created for this SO (per flow: SO acceptance → Costing; Project comes later at Costing Approval — see Change Log **C2** if your build creates a Project here)

**Verify:** Sales Register (R2) shows the SO; SO Type Split Pie = 100% Supply+Apply.

---

## STEP 2 — Costing Sheet (auto-expanded)

**Open** `CST-2026-0001` (auto-created from SO)

| Header | Value |
|--------|-------|
| SO Reference | SO-2026-0001 (autofetch: System Lines, Area, Customer) |
| Costing Status | Draft → Under Review → **Approved** |

**Section A — Material Cost (auto-expanded, expected 4 lines):**

| System | FG | RM | UOM | BOM Ratio | Area | Required Qty | Rate | Material Cost |
|--------|-----|-----|-----|-----------|------|-------------|------|--------------|
| EP02 | FG-002 | RM-001 | Kg | 0.201 | 500 | 100.5 | ₹220 | ₹22,110 |
| EP02 | FG-002 | RM-002 | Kg | 0.099 | 500 | 49.5 | ₹340 | ₹16,830 |
| EP02 | FG-003 | RM-001 | Kg | 0.349 | 500 | 174.5 | ₹220 | ₹38,390 |
| EP02 | FG-003 | RM-002 | Kg | 0.150 | 500 | 75.0 | ₹340 | ₹25,500 |

**Section A Material Total (G3)** = ₹22,110 + 16,830 + 38,390 + 25,500 = **₹103,000**

**Section B — Application Cost:**

| Activity | UOM | Qty/Area | Rate | Amount |
|----------|-----|----------|------|--------|
| Surface preparation + Primer coat | SqM | 500 | ₹35 | ₹17,500 |
| Top coat application | SqM | 500 | ₹25 | ₹12,500 |

**Section B Application Total** = **₹30,000**

**Section C — Transportation Cost:**

| From | To | Mode | Trips | Rate/Trip | Amount |
|------|----|------|-------|-----------|--------|
| ST-01 Wadki | Chakan site | Third Party | 3 | ₹2,500 | ₹7,500 |

**Section C Transport Total** = **₹7,500**

**Section D — Tools & Tackles:** Item "Mixing + Trowel kit" Qty 1 × ₹3,500 → **₹3,500**

**Section E — Overhead:** "Site supervision misc" → **₹2,000**

**Total Costing Amount (G3)** = 103,000 + 30,000 + 7,500 + 3,500 + 2,000 = **₹146,000**

**Expected automation:**
- [ ] Section A pre-populated from SO × System Composition × BOM — zero manual entry of RM lines
- [ ] Required Qty = BOM Ratio × Area for all 4 lines (5% tolerance check vs SO)
- [ ] Approval → auto-create **Project + Production Plan (Draft)** (NOT at SO step — see C2)
- [ ] Costing status stuck > 24 hr → escalation notification to admin (test by leaving one record in Under Review)

**Verify:** Costing Sheet Status (R3) → 1 Approved, Total Costing Amount ₹146,000.

---

## STEP 3 — Project + Production Plan (auto-created on Costing Approval)

### 3a. Project `PRJ-2026-0001`

| Field | Value |
|-------|-------|
| Project ID | PRJ-2026-0001 (autogen) |
| Project Name | Acme DC Chakan — 2mm Epoxy |
| SO Reference | SO-2026-0001 |
| Client / Site | Acme Logistics — Chakan, Pune |
| Project Manager | PM-1 |
| Execution Base | 100 sqm/day |
| Start / End Date | Today / +6 days |
| Status | In Progress |
| **Total Revenue (G2)** | **₹175,000** (set from SO at creation — see C2) |
| **Total Actual Cost (G2)** | ₹144,000 — auto-set when MR Released (later step) |
| **P&L (G2)** | formula — updates after MR Release |

**Task Budget subform (G2)** — fill all 5 categories:

| Category | Description | Budget Qty | Rate | Budget Amount | Actual Qty | Actual Amount |
|----------|-------------|-----------|------|---------------|-----------|---------------|
| Transport | Site to warehouse trips | 3 | ₹2,500 | ₹7,500 | 3 | ₹7,500 |
| Execution | Labour (primer + top coat) | 500 | ₹60 | ₹30,000 | 500 | ₹30,000 |
| Manpower | Site supervisor days | 6 | ₹1,200 | ₹7,200 | 6 | ₹7,200 |
| Tools | Trowel/mixer kit | 1 | ₹3,500 | ₹3,500 | 1 | ₹3,500 |
| Overhead | Misc site cost | 1 | ₹2,000 | ₹2,000 | 1 | ₹2,000 |

**Verify:** Project Status List (R2), Task Budget vs Actual (R2) shows ₹50,200 budget total.

### 3b. Production Plan `PLAN-2026-0001`

| Header | Value |
|--------|-------|
| Costing Sheet No | CST-2026-0001 (lookup — Approved only) |
| Project ID | autofetch |
| Planning Period | Week |
| Plant | Wadki |
| Plan Status | Draft → **Released** |

**Line items (auto-fetched from Costing §A):**

| RM | Total Required | Available Stock (physical − other MR allocations) | Shortage | Source |
|----|---------------|---------------------------------------------------|----------|--------|
| RM-001 | 275 kg | 200 kg (no unreleased MRs yet) | **75 kg** | Purchase |
| RM-002 | 125 kg | 400 kg | 0 | Stock |

**Expected automation:**
- [ ] Available Stock for RM-001 = 200 (physical) − 0 (other allocations) = 200
- [ ] `Shortage` = 75 kg for RM-001, `Procurement Triggered` checkbox auto-ON
- [ ] **Plan Released → auto-PR for RM-001 75 kg** (Stream A starts — go to STEP 4)
- [ ] Plan must be Released before MR can be auto-created

**Verify:** Plan Shortage Summary (R3) → RM-001 75 kg.

---

## STEP 4 — Stream A Procurement: PR → PO → GRN → QC (for the 75 kg shortage)

### 4a. PR `PR-2026-0001` (auto-created from Plan Release)

| Field | Value |
|-------|-------|
| Project ID | PRJ-2026-0001 (project-tagged; Stream A stock PRs have no Project ID — this one does because it came from the Plan) |
| Department | autofetch from login (Production) |
| Status | Draft → Pending Approval → **Approved** |

| Item | Qty | UOM | Lead Time |
|------|-----|-----|-----------|
| RM-001 | 75 | Kg | 7 (autofetch) |

**Verify:** PR Status Report (R4) → 1 Approved.

### 4b. PO `RMWAD-2026-0001` (Coding RM → RMWAD series) — actually RM-001 is coding → RMWAD ✓

| Field | Value |
|-------|-------|
| RM Type | Coding → PO series **RMWAD-YYYY-XXXX** (form rule) |
| Supplier | SUP-0001 (autofetch Name/GSTIN/Address) |
| Project ID | PRJ-2026-0001 |
| PR Reference | PR-2026-0001 |
| **Status (G5)** | Draft → **Sent** |
| Bill To | Wadki |

| Item | Qty | Rate | Basic | GST 18% | Total |
|------|-----|------|-------|---------|-------|
| RM-001 | 75 | ₹220 | ₹16,500 | ₹2,970 | **₹19,470** |

**Footer:** Basic ₹16,500 · CGST ₹1,485 · SGST ₹1,485 (intra-state) · Delivery Date +7 days · Payment Terms 30 days · Scope of Transport Supplier

**Expected automation:**
- [ ] GST split auto-computes (₹2,970 total)
- [ ] Line fields `Received Qty` = 0, `Balance Qty` = 75, `Receipt Status` = Not Started (G5)

**Verify:** Open PO Register (R4) → shows this PO (Status ≠ Fully Received / Cancelled).

### 4c. GRN `GRN-2026-0001`

| Field | Value |
|-------|-------|
| PO Ref | RMWAD-2026-0001 (autofetch items) |
| Warehouse | Wadki |
| Partial GRN checkbox | OFF (full receipt) |

| Item | Ordered | Received | QC Status |
|------|---------|----------|-----------|
| RM-001 | 75 | 75 | Pass |

Transport subform: 1 trip, supplier's own.

**Click "Post GRN" — expected automation (G5 hook `GRN_Post_PO_Update`):**
- [ ] PO line `Received Qty` = 75, `Balance Qty` = 0, `Receipt Status` = Complete
- [ ] PO `Status` auto-updates → **Fully Received**
- [ ] `Delivery Days` = GRN Date − PO Delivery Date (e.g., 5)
- [ ] RM Inventory: RM-001 stock +75 → **275 kg** (only after posting — timestamp logged)
- [ ] Stock Movement Log entry: GRN in +75

**Verify:** PO vs GRN Pending (R4) → RM-001 no longer listed (Balance 0); Vendor Performance (R4) → Delivery Days avg = 5.

### 4d. QC `QC-2026-0001`

| Field | Value |
|-------|-------|
| GRN Ref | GRN-2026-0001 |
| Viscosity / Density / Color / Moisture | within spec |
| Accepted Qty | 75 |
| Packaging Quality | Good |
| QC Status | Passed |

**Verify:** QC Results (R4) → 1 Passed, Accepted Qty 75.

---

## STEP 5 — MR (auto-derived — CRITICAL GATE)

**Auto-created** `MR-2026-0001` from Costing Sheet + Released Plan. All 4 cost components pre-filled — zero manual entry.

| Header | Value |
|--------|-------|
| Project ID | PRJ-2026-0001 |
| Requisition Type | Production |
| Priority | High |
| MR Status | Draft → Pending Production Verification → Production Verified → Costing Approved → **Released** |

**MR Cost Components (pre-filled):** Material ₹103,000 · Application ₹30,000 · Transport ₹7,500 · Tools ₹3,500

**Total MR Cost (G4)** = **₹144,000** (4 components: 103,000 + 30,000 + 7,500 + 3,500 — Section E Overhead stays Costing-Sheet-only, C20)

**Material Allocation subform (auto-populated from MR lines):**

| Item | Assigned Qty | Rate | Material Cost | Ratio % | 80% Flag |
|------|-------------|------|---------------|---------|----------|
| RM-001 | 275 | ₹220 | ₹60,500 | 68.75% | ON |
| RM-002 | 125 | ₹340 | ₹42,500 | 31.25% | ON |

**Cross-validation (SO ↔ BOM ↔ MR):**
- [ ] Σ(Assigned) = 275 + 125 = 400 kg vs Σ(SO Area × BOM) = 400 kg → diff 0% → no flag (test: change one Assigned Qty by 6% → flag fires; 11% → block)

**Expected automation:**
- [ ] On **Released** → `Project.Total Actual Cost` = ₹144,000, P&L = **+₹31,000** (G2 hook `Project_Cost_Set`)
- [ ] On **Released** → MIS **Draft** auto-created
- [ ] SLAs: Draft > 2 hr reminder, Verified > 2 hr escalation, Approved > 1 hr auto-release

**Verify:** MR Status Tracking (R3) → 1 Released; Project P&L Real-time (R2) → Revenue 175,000 − Cost 144,000 = +31,000; Project Cost Baseline (R3) → ₹144,000.

---

## STEP 6 — MIS (auto-created on MR Release)

**Open** `MIS-2026-0001` — MR lookup restricted to Released only.

| Header | Value |
|--------|-------|
| MIS Number | autogen |
| Date | Today |
| Batch Number | B-001 |

| Line | Item | Required (from MR) | Issued | Balance |
|------|------|-------------------|--------|---------|
| 1 | RM-001 | 275 | 275 | 0 |
| 2 | RM-002 | 125 | 125 | 0 |

Footer: Issued By (Store), Handover To (Production), Remark.

**Click "Post MIS" — expected automation:**
- [ ] RM Inventory: RM-001 275→**0 kg**, RM-002 400→**275 kg**
- [ ] MR Allocation `Issued Qty` (G4 hook `MIS_Post_Allocation_Update`): RM-001 +275, RM-002 +125
- [ ] Stock Movement Log: 2 × MIS out entries

**Verify:** MIS Register + Pending MIS (R5) → Balance 0 so not in Pending; MIS Issued vs Required (R5) → 275/275, 125/125.

---

## STEP 7 — Production: Job → BMR → RM Consumption → Packing → FGHM

### 7a. Production Job `JOB-2026-0001`

| Field | Value |
|-------|-------|
| Project ID | PRJ-2026-0001 |
| FG Code | FG-002 Epoxy Primer |
| Planned Qty | 150 kg |
| Period | Week |
| Status | Scheduled → **In Progress** |

### 7b. BMR `BMR-2026-0001` (Primer batch)

| Header | Value |
|--------|-------|
| Production Job Ref | JOB-2026-0001 |
| Project ID | autofetch |
| Batch No | B-001 |
| FG Code | FG-002 |

| Line | RM | Qty Consumed | UOM | Rate (G8 — from MR Allocation) | Amount (G8) |
|------|----|-------------|-----|------|-----------|
| 1 | RM-001 | 100.5 | Kg | ₹220 | ₹22,110 |
| 2 | RM-002 | 49.5 | Kg | ₹340 | ₹16,830 |

**Expected automation:**
- [ ] Allocation Consumed Qty: RM-001 +100.5, RM-002 +49.5
- [ ] Consumption %: RM-001 = 36.5%, RM-002 = 39.6% → no alert yet

**BMR `BMR-2026-0002` (Top coat batch):** FG-003, consumes RM-001 174.5 + RM-002 75 → now RM-001 consumed 275/275 = **100%**, RM-002 124.5/125 = 99.6%
- [ ] **80% alert fires on first line past 80%** (pop-up + dashboard banner + email to PM)
- [ ] **100% alert** "Allocation Exhausted" → PM + Purchase notified

### 7c. RM Consumption Entry `RC-2026-0001` (variance check — see C25)

| Field | Value |
|-------|-------|
| Reference BMR | BMR-2026-0001 |
| Item | RM-001 |
| Actual Qty | 100.5 |
| Standard Qty | 100.5 (from BOM) |
| Variance | 0 |

**C25:** RC does **NOT** increment Consumed Qty — BMR-0001 already recorded this batch's consumption. RC is the Actual vs BOM-Standard variance record (feeds BMR vs BOM Variance report).

**Verify:** BMR vs BOM Variance (R5) → variance 0.

### 7d. Packing Entry `PK-2026-0001`

| Field | Value |
|-------|-------|
| FG Code | FG-002 |
| Packed Qty | 148 kg (150 − 2 damaged) |
| Packing Material | drum + label (deducted from inventory) |

### 7e. FGHM `FGH-2026-0001` — inline acceptance

| Header | Value |
|--------|-------|
| Project ID | PRJ-2026-0001 |
| Batch No | B-001 |
| **Status (G6)** | **Pending Acceptance** → auto-**Accepted** on inline acceptance |

| Line | FG | FG Qty | Damaged | Accepted (formula) | QC |
|------|-----|--------|---------|--------------------|----|
| 1 | FG-002 | 150 | 2 | 148 | Pass |
| 2 | FG-003 | 300 | 0 | 300 | Pass |

**Expected automation (G6 hook `FGHM_Accepted_Status`):**
- [ ] FGHM Status auto-set = **Accepted**
- [ ] FG Inventory: FG-002 +148, FG-003 +300
- [ ] Stock Movement Log: 2 × FGHM in entries
- [ ] MR Allocation `Fully Consumed` flagged when all lines ≥ 100% (see Change Log **C1** — field may be missing)
- [ ] Notification to Store

**Verify:** FG Handover Pending (R5) → empty (nothing pending); Today's Production (R5) → 448 kg; Production Efficiency (R5) → 148 + 300 packed.

---

## STEP 8 — Site Consumption Entry (SCE) + Material Return

### 8a. SCE `SCE-2026-0001` — first attempt REJECTED

| Header | Value |
|--------|-------|
| Project ID | PRJ-2026-0001 |
| Work Area | Zone A — Loading Bay |
| Date / Time Slot | Today / Morning |
| Supervisor | Site Sup 1 |

| Line | RM | Qty Consumed | UOM | Type | Rate (G8 — from MR Allocation) | Amount (G8) |
|------|----|-------------|-----|------|-----|-----------|
| 1 | RM-001 | 10 | Kg | Wastage | ₹220 | ₹2,200 |
| 2 | RM-002 | 5 | Kg | Actual | ₹340 | ₹1,700 |

**Expected automation (C21):**
- [ ] RM-001 +10 → 285/275 = **103.6%** → line REJECTED (C5 block): "Allocation Exhausted — return material first"
- [ ] RM-002 +5 → 129.5/125 = **103.6%** → also over — **whole submit rejected** (both lines must be ≤ 100%)
- [ ] Resolution matched by `Project ID + Item Code` — never a generic pool
- [ ] System/FG Reference field triggers BOM expansion when used

**Correct path:** return excess first via MRT (8b) — both RMs are at 100% / 99.6%, so any positive SCE line needs headroom.

### 8b. Material Return `MRT-2026-0001` (two lines — creates headroom)

| Field | Value |
|-------|-------|
| Project ID | PRJ-2026-0001 |
| Line 1 | RM-001, Return Qty 10 kg, Condition Good, Reason "Excess issue" |
| Line 2 | RM-002, Return Qty 10 kg, Condition Good, Reason "Excess issue" |

**Expected automation (C21):**
- [ ] RM-001 Consumed −10 → 265/275 = **96.4%**; `Returned Qty` (C1) = 10
- [ ] RM-002 Consumed −10 → 114.5/125 = **91.6%**; `Returned Qty` (C1) = 10
- [ ] RM Inventory: RM-001 +10 → **10 kg**, RM-002 +10 → **285 kg** (Good restores stock)
- [ ] Damaged condition → only damaged count, no stock restore

**Verify:** Material Return Report + Returns by Condition (R6) → 10 + 10 kg Good.

### 8c. SCE `SCE-2026-0002` — accepted after returns

| Line | RM | Qty Consumed | UOM | Type | Rate (G8) | Amount (G8) |
|------|----|-------------|-----|------|-----------|-----|
| 1 | RM-001 | 10 | Kg | Wastage | ₹220 | ₹2,200 |
| 2 | RM-002 | 5 | Kg | Actual | ₹340 | ₹1,700 |

**Expected automation:**
- [ ] RM-001 +10 → 275/275 = **100%** ✓ accepted (headroom from 8b)
- [ ] RM-002 +5 → 119.5/125 = **95.6%** ✓ accepted
- [ ] 80% alert already fired (flag ON); no new alert above 100%

**Final project allocation state:** RM-001 Assigned 275 / Issued 275 / Consumed 275 / Returned 10 / Remaining **10** · RM-002 Assigned 125 / Issued 125 / Consumed 119.5 / Returned 10 / Remaining **15.5**

---

## STEP 9 — FG Consumption + Project FG Position

### 9a. FG Consumption Entry `FGC-2026-0001`

| Field | Value |
|-------|-------|
| Project ID | PRJ-2026-0001 |
| FGHM Reference | FGH-2026-0001 (autofetch FG items) |
| Task Date / Site Location | Today / Chakan site |
| Supervisor | Site Sup 1 |

| Line | FG | Qty Used |
|------|-----|----------|
| 1 | FG-002 | 148 |
| 2 | FG-003 | 280 |

**Expected automation:**
- [ ] FG Inventory: FG-002 148→**0**, FG-003 300→**20**
- [ ] Project FG position: FG-002 received 148 / consumed 148 / remaining 0; FG-003 300 / 280 / **20**

**Verify:** FG Consumption Log + Project FG Position (R6 — G9 rows) → FG-003 remaining 20 kg on site.

---

## STEP 10 — Project Close → P&L

| Field | Value |
|-------|-------|
| Project Status | In Progress → **Completed** |
| P&L (G2) | Total Revenue ₹175,000 − Total Actual Cost ₹144,000 = **+₹31,000** |

**Verify:**
- [ ] Project P&L Real-time (R2) → +₹31,000
- [ ] Project Inventory Status (R3 Pivot) → RM-001 Assigned 275 / Issued 275 / Consumed 275 / Returned 10 / Remaining **10**; RM-002 125 / 125 / 119.5 / 10 / **15.5** (C21 — 8a rejected, returns + re-submit)
- [ ] Costing vs Actual Variance (R3) → planned ₹144,000 vs actual (BMR + SCE amounts)
- [ ] Dashboard widgets: MR/Costing, Production, Site Supervisor, Project Management all render from this data

---

## Report Coverage Check (walk every R-section with this data)

| Report | Expected row(s) |
|--------|-----------------|
| R1 Item Catalog / Supplier / Customer | EP02, RM-001/2, FG-002/3, SUP-0001, CUS-0001 |
| R2 Sales Register, SO Value by Customer, Project Status, Task Budget | SO ₹175k; PRJ; budget ₹50,200 |
| R3 Costing Status, MR Status, Cost Baseline, 80% Alert List, Inventory Status | ₹144k MR baseline (Costing Sheet ₹146k incl. Overhead); Released; alerts fired in Step 7b |
| R4 Open PO Register, PO vs GRN Pending, Vendor Performance | PO Fully Received; no pending; 5 days |
| R5 MIS Register, Today's Production, FG Handover Pending | MIS 275/125; 448 kg; empty |
| R6 RM/FG Stock, Valuation (Closing × Rate), SCE logs, Project FG Position | RM-001 10, RM-002 285 (after MRT 8b); SCE logs 8a(blocked)+8c; FG-003 20 |
| R7 all 8 dashboards | KPI cards + charts render |

---

## ⚠️ CHANGE LOG — items found during planner walkthrough

| # | Change | Status |
|---|--------|--------|
| **C1** | MR Allocation subform missing **`Returned Qty`** (auto, MRT-post), **`Remaining`** formula (= Assigned − Consumed + Returned) and **`Fully Consumed`** checkbox (FGHM acceptance) | ✅ **APPLIED** — forms.html 3C rows 13–15, automation.html MRT + FGHM hooks |
| **C2** | Project creation trigger contradiction (SO acceptance vs Costing Approved) — resolved: **SO acceptance → Costing Sheet (Draft); Costing Approved → Project + Production Plan** (single creation point); `Project_Revenue_Set` fires at Project creation | ✅ **APPLIED** — forms.html 2A text, automation.html SO workflow + Revenue hook |
| **C3** | Costing vs Actual Variance (R3): Detail vs Summary mismatch | ✅ **APPLIED** — reports.html R3 now Summary: SUM(Total MR Cost), SUM(SCE Amount), SUM(BMR Amount) |
| **C4** | Task Budget subform `Actual Qty`/`Actual Amount` have **no automation source** — manual entry | ⏳ **NOTE** — keep manual for now; P&L uses MR Total Actual Cost; revisit in later phase |
| **C5** | SCE could over-consume past 100% of assignment | ✅ **APPLIED — decision: BLOCK.** Any consumption entry (SCE / BMR / RM Consumption) pushing Consumption % > 100% is rejected: "Allocation Exhausted — return material first". Applied to forms.html (SCE note + MR backend rule) and automation.html (SCE hook). Step 8a below updated. |
| **C6** | C2 fix was only applied to forms.html 2A — 6 more files still said "SO acceptance → auto-creates Project" (forms.html intro/badge, implementation-plan.html ×2, IMPLEMENTATION_PLAN.md ×2, data-model.html ×2, BRD ×2) | ✅ **APPLIED** — all swept to "SO acceptance → Costing Sheet (Draft); Project on Costing Approved" |
| **C7** | automation.html summary had **no hook for "MR Released → auto-create MIS Draft"** and no **100% "Allocation Exhausted" escalation** row (AGENTS.md promises both) | ✅ **APPLIED** — added MR "On Released → auto-create MIS Draft + notify Store/Production" and 100% escalation to the 80% alert row |
| **C8** | Remaining formula stale in IMPLEMENTATION_PLAN.md + implementation-plan.html ("Assigned − Consumed", missing + Returned) | ✅ **APPLIED** — both now `Assigned − Consumed + Returned` (C1); SCE automation note also gained C5 block text |
| **C9** | PO Status value set mismatch: forms.html = Draft/Sent/Partially Received/Fully Received/Cancelled; plan G5 = Draft/Approved/PO Sent/Completed/Closed; R4 filters referenced "≠ Completed/Closed" which doesn't exist in the set | ✅ **APPLIED** — plan G5 aligned to forms.html set; Open PO Register filters in both docs → "Status ≠ Fully Received / Cancelled" |
| **C10** | MR SLA conflict: automation.html + reports.html still had old "Draft > 7 days / Prod Verified > 3 days" while AGENTS.md, IMPLEMENTATION_PLAN and implementation-plan.html specify tight SLAs (2 hr Draft → reminder, 2 hr Verified → escalation, 1 hr Approved → auto-release) | ✅ **APPLIED** — automation.html Deluge snippets + summary row and reports.html notification rows all → 2 hr / 2 hr / 1 hr with C10 notes |
| **C11** | flow.html Project mockup Status select used "Active / On Hold / Completed" — canonical Project Status set is "Planned / In Progress / Completed / On Hold" (forms.html, IMPLEMENTATION_PLAN, BRD, report filters) | ✅ **APPLIED** — flow.html aligned to canonical set |
| **C12** | automation.html MRT Deluge snippet decremented `Consumed_Qty` but never incremented `Returned_Qty` — violating C1 (Remaining = Assigned − Consumed + Returned would be wrong) | ✅ **APPLIED** — Deluge now updates both `Consumed_Qty −` and `Returned_Qty +`; workflow step description updated |
| **C13** | automation.html SCE + BMR Deluge snippets updated `Consumed_Qty` unconditionally — no >100% rejection despite the C5 decision (summary rows said BLOCK, code didn't implement it) | ✅ **APPLIED** — both snippets now `throw "Allocation Exhausted … return material first"` before any update when new Consumption % > 100 |
| **C14** | FGHM "On Accept" Deluge summary row existed but NO actual code snippet to mark MR Allocation `Fully_Consumed = Yes` when all RM lines ≥ 100% | ✅ **APPLIED** — added Deluge snippet that checks all allocations for the project and sets `Fully_Consumed = true` when all at ≥ 100% |
| **C15** | MR Released → auto-create MIS Draft had a summary row + blueprint notification but NO actual Deluge `createRecord` code — AGENTS.md promises "MR Released → auto-MIS" | ✅ **APPLIED** — blueprint Release transition now has the action; added full Deluge snippet creating one MIS Draft record per MR line (Issued 0, Status Draft) + email |
| **C16** | FGHM code referenced `Overall_Status` field but canonical field is `Status` (Pending Acceptance / Accepted, G6) — and no code actually SET Status = Accepted on inline acceptance | ✅ **APPLIED** — FGHM On-Accept snippets now set `Status = "Accepted"` (G6 hook FGHM_Accepted_Status) and use `Status` in comments; no more `Overall_Status` |
| **C17** | MIS Deluge sets `Status` ("Draft" on auto-create, "Posted" on Post MIS button) but MIS form spec (forms.html, IMPLEMENTATION_PLAN, implementation-plan.html) had NO Status field | ✅ **APPLIED** — added `Status` dropdown (Draft / Posted) to all three MIS form specs with C17 note |
| **C18** | 80% alert field-name mismatch: auto-populate Deluge sets `80%_Alert_Flag` but alert workflow + SCE snippet checked `Alert_Flag` — workflow would never fire | ✅ **APPLIED** — all checks now use `80%_Alert_Flag` (matching forms.html "80% Threshold Alert Flag") |
| **C19** | SO↔BOM↔MR cross-validation Deluge writes `Variance_Flag`/`Variance_Percentage` but NO form spec had these fields; IMPLEMENTATION_PLAN + implementation-plan.html MR Allocation tables also still missing G4/C1 rows 12–15 (forms.html had them) | ✅ **APPLIED** — added rows 12–17 (Issued Qty, Returned Qty, Remaining, Fully Consumed, Variance %, Variance Flag) to all three MR Allocation specs |
| **C20** | Sample-data arithmetic error: Costing Sheet Total = ₹146,000 (incl. Section E Overhead ₹2,000) but MR auto-derives only 4 components = ₹144,000; planner had MR Total = ₹146,000 and P&L = +₹29,000 — should be ₹144,000 / **+₹31,000**. Overhead is Costing-worksheet-only, never in the MR cost baseline | ✅ **APPLIED** — all planner MR Total / Project.Total Actual Cost / P&L / R3 baseline numbers fixed to ₹144,000 / +₹31,000; Costing Sheet Total stays ₹146,000 (overhead noted as Costing-only) |
| **C21** | Step 8 math broken: RM-002 +5 → 129.5/125 = 103.6% also over-consumes (both lines blocked), but "correct path" only fixed RM-001; 8b's "119.5/125 = 95.6%" assumed the blocked entry was accepted; Step 10 pivot + R6 stock numbers inconsistent | ✅ **APPLIED** — rewrote as 8a (attempt REJECTED, both lines over) → 8b MRT (RM-001 10 + RM-002 10 returns, creates headroom; stock RM-001 10 / RM-002 285) → 8c SCE accepted (275/275 = 100%, 119.5/125 = 95.6%); Step 10 pivot + R6 updated to final state |
| **C22** | RM requirement math implied FG-003 output = 250 kg (500×0.50×0.30) but FGHM (Step 7e) + R5 use FG-003 = 300 kg (EP02 composition 0.60 kg/sqm) — Today's Production 448 kg = 148 + 300 only works with 300 | ✅ **APPLIED** — math block rewritten on the Costing Section A model (BOM ratio × area) + EP02 composition 0.30/0.60 → FG-002 150 kg, FG-003 300 kg |
| **C23** | flow.html FGHM mockup used number prefix `FGHM-2026-001` — canonical is `FGH-` (forms.html, automation.html numbering, planner Step 7e/9a) | ✅ **APPLIED** — flow.html aligned to `FGH-2026-001` |
| **C24** | Numbering Series Reference tables incomplete vs canonical set (automation.html detail steps): forms.html missing CST/PLAN/SCE/MRT/SUP; BRD missing JOB/SCE/MRT/SUP; implementation-plan.html missing SUP | ✅ **APPLIED** — all three tables completed (CST, PLAN, JOB, PR, PO×2, GRN, MR, MIS, FGH, QC, SO, PRJ, SC, BOM, BMR, SCE, MRT, CUST, SUP) |
| **C25** | Double-count risk: AGENTS.md/BRD/IMPLEMENTATION_PLAN stated "BMR, RM Consumption, Packing — ALL increment Consumed Qty", but planner math (Step 7/8) treats BMR + SCE as the only incrementing events — RC-2026-0001 is variance-only, and adding it would push RM-001 to 136% and break Step 8 | ✅ **APPLIED** — consumption model clarified everywhere: BMR + SCE increment; RM Consumption Entry = BOM variance check (no increment); Packing = packaging material deduction only; planner 7c annotated |

**New findings during UAT walkthrough → append here, then fix docs before building.**

---

## Sign-off

**Doc-level verification (loop pass 1):** every step's fields exist in forms.html, every expected automation has a hook in automation.html, every verify report is spec'd in reports.html R1–R7 → all 10 steps + report sweep **doc-verified ✓** (see REPORT_IMPLEMENTATION_PLAN Phase 8).

**Console execution (Zoho Creator .in) — remaining manual work:**

| Step | Tested | Signed off |
|------|--------|------------|
| 1 SO | | |
| 2 Costing | | |
| 3 Project + Plan | | |
| 4 PR→PO→GRN→QC | | |
| 5 MR gate | | |
| 6 MIS | | |
| 7 Production → FGHM | | |
| 8 SCE + MRT | | |
| 9 FG Consumption | | |
| 10 Close + P&L | | |
| Report sweep R1–R7 | | |
| Change Log items applied | ✅ | |
