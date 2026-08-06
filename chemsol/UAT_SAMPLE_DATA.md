# Chemsol ERP — Complete UAT Sample Data

> **Purpose:** End-to-end test data for every module. 5 flows covering all streams, all fields, all automations.
>
> **Rule:** Each flow is self-contained — master data → SO → Costing → MR → MIS → Production → FGHM → Site → Return → P&L. Follow flows 1-5 in order (later flows depend on master data seeded in Flow 1).

---

## MASTER DATA (Seed Once — Used by All Flows)

### 1A. Purchase Item Muster (12 items)

| # | Category | Item Code | Item Name | UOM | HSN | GST% | Min Stock | Max Stock | Std Rate | Preferred Supplier | Lead Time | Status |
|---|----------|-----------|-----------|-----|-----|------|-----------|-----------|----------|-------------------|-----------|--------|
| 1 | RM | RM-001 | Epoxy Resin A | Kg | 3907 | 18 | 50 | 500 | ₹220 | SUP-0001 | 7 | Active |
| 2 | RM | RM-002 | Hardener B | Kg | 3907 | 18 | 30 | 400 | ₹340 | SUP-0001 | 7 | Active |
| 3 | RM | RM-003 | PU Resin C | Kg | 3909 | 18 | 40 | 300 | ₹280 | SUP-0002 | 10 | Active |
| 4 | RM | RM-004 | PU Hardener D | Kg | 3909 | 18 | 25 | 200 | ₹310 | SUP-0002 | 10 | Active |
| 5 | RM | RM-005 | Demarcation Pigment | Kg | 3213 | 18 | 20 | 150 | ₹180 | SUP-0003 | 5 | Active |
| 6 | FG | FG-001 | Epoxy Primer Coat | Kg | 3907 | 18 | 30 | 200 | ₹480 | — | — | Active |
| 7 | FG | FG-002 | Epoxy Top Coat | Kg | 3907 | 18 | 50 | 300 | ₹520 | — | — | Active |
| 8 | FG | FG-003 | PU Top Coat | Kg | 3909 | 18 | 40 | 250 | ₹560 | — | — | Active |
| 9 | FG | FG-004 | Demarcation Line Paint | Kg | 3213 | 18 | 15 | 100 | ₹420 | — | — | Active |
| 10 | Packaging | PKG-001 | 20 Kg HDPE Bucket | Nos | 3923 | 18 | 100 | 1000 | ₹85 | SUP-0004 | 3 | Active |
| 11 | Tools | TLS-001 | Trowel Set (3 pcs) | Kit | 8205 | 18 | 10 | 50 | ₹1,200 | SUP-0005 | 14 | Active |
| 12 | RM | RM-006 | Anti-Static Additive | Kg | 3403 | 18 | 10 | 80 | ₹450 | SUP-0001 | 12 | Active |

### 1B. System Master (4 systems)

| System Code | System Name | Description | Status |
|-------------|-------------|-------------|--------|
| EP01 | 1mm Epoxy Flooring | Thin-film epoxy for light traffic | Active |
| EP02 | 2mm Epoxy Flooring | Medium-duty epoxy coating | Active |
| PU01 | 2mm PU Flooring | Polyurethane chemical-resistant | Active |
| DEM01 | Demarcation Lines | Safety line marking | Active |

### 1C. System Composition (System → FG mapping)

| System Code | FG Code | FG Name | Qty per SqM | UOM | Rate per FG |
|-------------|---------|---------|-------------|-----|-------------|
| EP01 | FG-001 | Epoxy Primer Coat | 0.20 | Kg | ₹480 |
| EP01 | FG-002 | Epoxy Top Coat | 0.40 | Kg | ₹520 |
| EP02 | FG-001 | Epoxy Primer Coat | 0.30 | Kg | ₹480 |
| EP02 | FG-002 | Epoxy Top Coat | 0.60 | Kg | ₹520 |
| PU01 | FG-003 | PU Top Coat | 0.50 | Kg | ₹560 |
| DEM01 | FG-004 | Demarcation Line Paint | 0.10 | Kg | ₹420 |

### 1D. BOM / FG Formulation (FG → RM mapping with ratios)

| FG Code | FG Name | RM Code | RM Name | Qty per FG Unit | Waste% | Total Qty |
|---------|---------|---------|---------|-----------------|--------|-----------|
| FG-001 | Epoxy Primer | RM-001 | Epoxy Resin A | 0.6700 | 2 | 0.6834 |
| FG-001 | Epoxy Primer | RM-002 | Hardener B | 0.3333 | 2 | 0.3400 |
| FG-002 | Epoxy Top Coat | RM-001 | Epoxy Resin A | 0.5817 | 2 | 0.5933 |
| FG-002 | Epoxy Top Coat | RM-002 | Hardener B | 0.2500 | 2 | 0.2550 |
| FG-003 | PU Top Coat | RM-003 | PU Resin C | 0.6000 | 2 | 0.6120 |
| FG-003 | PU Top Coat | RM-004 | PU Hardener D | 0.4000 | 2 | 0.4080 |
| FG-004 | Demarcation | RM-005 | Demarcation Pigment | 0.8500 | 3 | 0.8755 |
| FG-004 | Demarcation | RM-006 | Anti-Static Additive | 0.1500 | 3 | 0.1545 |

> **Note:** BOM ratios are 4dp precision (0.3333 not 0.33). This is critical — C28 finding.

### 1E. Supplier Master (5 suppliers)

| Supplier Code | Supplier Name | GSTIN | PAN | Contact Person | Mobile | Email | Address | Bank | Payment Terms | Credit Days | Status |
|---------------|---------------|-------|-----|----------------|--------|-------|---------|------|---------------|-------------|--------|
| SUP-0001 | ResinChem Supplies | 27AABCR1234A1Z5 | AABCR1234A | Rajesh Patel | 9876543210 | rajesh@resinchem.in | Plot 12, MIDC, Pune | SBI 1234567890 | Net 30 | 30 | Active |
| SUP-0002 | PolyChem Industries | 27BBBCC5678B1Z8 | BBBCC5678B | Anita Desai | 9876543211 | anita@polychem.in | Unit 5, Ambad, Nashik | HDFC 9876543210 | Net 30 | 30 | Active |
| SUP-0003 | ColorTech Pigments | 27CCCDD9012C1Z1 | CCCDD9012C | Mohan Sharma | 9876543212 | mohan@colortech.in | 23, Industrial Area, Jalna | ICICI 5678901234 | Net 15 | 15 | Active |
| SUP-0004 | PackRight Solutions | 27DDDEE3456D1Z4 | DDDEE3456D | Priya Kulkarni | 9876543213 | priya@packright.in | 7, Talegaon, Pune | Axis 3456789012 | Net 7 | 7 | Active |
| SUP-0005 | ToolMaster India | 27EEFFG7890E1Z7 | EEFFG7890E | Suresh Jadhav | 9876543214 | suresh@toolmaster.in | 45, Bhosari, Pune | PNB 2345678901 | Net 45 | 45 | Active |

### 1F. Customer / Site Master (4 customers)

| Customer Code | Client Org | Contact Person | Mobile | Email | GSTIN | PAN | Regd Address | Site Name | Site Address | Site Manager | Status |
|---------------|------------|----------------|--------|-------|-------|-----|-------------|-----------|-------------|-------------|--------|
| CUST-0001 | Acme Logistics Pvt Ltd | Vikram Mehta | 9988776655 | vikram@acmelog.in | 27AACCA1234F1Z8 | AACC1234F | 101, Viman Nagar, Pune | Acme DC — Chakan | Plot 5, Chakan MIDC | Ravi Kumar | Active |
| CUST-0002 | Bharat Manufacturing Ltd | Neha Gupta | 9988776656 | neha@bharatmfg.in | 27BBBDB2345G1Z1 | BBDB2345G | 202, Andheri East, Mumbai | Bharat Plant — Pune | 12, Hinjewadi Phase 3 | Amit Singh | Active |
| CUST-0003 | CleanRoom Technologies | Arjun Nair | 9988776657 | arjun@cleanroom.in | 27CCCCC3456H1Z4 | CCCCC3456 | 15, Electronic City, Bangalore | CleanRoom Unit — Whitefield | 8, Whitefield Main Rd | Deepa Menon | Active |
| CUST-0004 | Delta Infrastructures | Sanjay Patil | 9988776658 | sanjay@deltainfra.in | 27DDDDD4567I1Z7 | DDDDD4567 | 30, Baner Road, Pune | Delta Warehouse — Lonavala | KM 55, Mumbai-Pune Highway | Kavita Deshmukh | Active |

### 1G. Store Master (3 stores)

| Store Code | Store Name | Store Type | Location | Status |
|------------|------------|------------|----------|--------|
| ST-01 | Wadki Main Store | RM Store | Wadki, Pune | Active |
| ST-02 | FG Warehouse | FG Store | Wadki, Pune | Active |
| ST-03 | Quality Lab Store | QC Store | Wadki, Pune | Active |

**Bin Locations (ST-01):**

| Rack No | Shelf No | Bin No | Status |
|---------|----------|--------|--------|
| A | 1 | A-1 | Active |
| A | 2 | A-2 | Active |
| B | 1 | B-1 | Active |

### 1H. RM Inventory Opening Stock (ST-01 Wadki)

| Item Code | Item Name | Opening Stock | Store |
|-----------|-----------|---------------|-------|
| RM-001 | Epoxy Resin A | 500 Kg | ST-01 |
| RM-002 | Hardener B | 400 Kg | ST-01 |
| RM-003 | PU Resin C | 300 Kg | ST-01 |
| RM-004 | PU Hardener D | 200 Kg | ST-01 |
| RM-005 | Demarcation Pigment | 150 Kg | ST-01 |
| RM-006 | Anti-Static Additive | 80 Kg | ST-01 |

---

## FLOW 1 — Full Stream B: EP02 2mm Epoxy (500 sqm) → Acme Logistics

> **Scenario:** Standard epoxy flooring project. Tests full flow: SO → Costing → Project → MR → MIS → Production → FGHM → Site Consumption → Material Return → P&L.

### Step 1: Sales Order (SO-2026-0001)

| Field | Value |
|-------|-------|
| Sales Type | Supply+Apply |
| SO No | SO-2026-0001 (autogen) |
| SO Date | 05-Jan-2026 |
| Employee Name | Rahul Verma |
| Customer Code | CUST-0001 (lookup → auto-fetch Acme Logistics) |
| Client Org / Contact / GST / PAN | Acme Logistics Pvt Ltd / Vikram Mehta / 27AACCA1234F1Z8 / AACC1234F |
| Regd Address | 101, Viman Nagar, Pune |
| Site Name / Address | Acme DC — Chakan / Plot 5, Chakan MIDC |
| Site Manager / Contact | Ravi Kumar / 9988776601 |
| Project Type | Industrial |
| Total Amount | ₹1,75,000 (formula: 500 × 350) |
| Payment Terms | 50% advance, 50% on completion |
| Transportation Scope | Supplier |
| Lead Time | 15 |
| Status | Accepted |

**Subform A — System Lines:**

| System Code | System Name | Thickness | Area | UOM | Rate | Amount |
|-------------|-------------|-----------|------|-----|------|--------|
| EP02 | 2mm Epoxy Flooring | 2mm | 500 | SqM | ₹350 | ₹1,75,000 |

### Step 2: Costing Sheet (CST-2026-0001)

**Header:**

| Field | Value |
|-------|-------|
| Costing Number | CST-2026-0001 (autogen) |
| Costing Date | 06-Jan-2026 |
| SO Reference | SO-2026-0001 |
| Project Name | Acme DC — Chakan Epoxy |
| Customer | Acme Logistics Pvt Ltd |
| Costing Status | Approved |

**Section A — Material Cost (auto-expanded from SO × System Composition × BOM):**

| System | FG Code | FG Name | RM Code | RM Name | UOM | BOM Ratio | Area | Required Qty | Rate | Material Cost |
|--------|---------|---------|---------|---------|-----|-----------|------|-------------|------|---------------|
| EP02 | FG-001 | Epoxy Primer | RM-001 | Epoxy Resin A | Kg | 0.6700 | 500 | 100.5 | ₹220 | ₹22,110 |
| EP02 | FG-001 | Epoxy Primer | RM-002 | Hardener B | Kg | 0.3333 | 500 | 50.0 | ₹340 | ₹17,000 |
| EP02 | FG-002 | Epoxy Top Coat | RM-001 | Epoxy Resin A | Kg | 0.5817 | 500 | 174.5 | ₹220 | ₹38,390 |
| EP02 | FG-002 | Epoxy Top Coat | RM-002 | Hardener B | Kg | 0.2500 | 500 | 75.0 | ₹340 | ₹25,500 |
| | | | | | | | | **Section A Total** | | **₹1,03,000** |

> **Math check:** RM-001 = 100.5 + 174.5 = 275 Kg. RM-002 = 50.0 + 75.0 = 125 Kg. Total RM = 400 Kg.

**Section B — Application Cost:**

| Description | Qty/Area | Rate | Amount |
|-------------|----------|------|--------|
| Surface Preparation | 500 SqM | ₹20 | ₹10,000 |
| Epoxy Application (2 coats) | 500 SqM | ₹35 | ₹17,500 |
| Curing & Finishing | 500 SqM | ₹15 | ₹7,500 |
| | | **Section B Total** | **₹35,000** |

**Section C — Transportation Cost:**

| Description | Qty | Rate | Amount |
|-------------|-----|------|--------|
| Material Transport — Pune to Chakan | 1 | ₹3,000 | ₹3,000 |
| Equipment Transport | 1 | ₹2,000 | ₹2,000 |
| | | **Section C Total** | **₹5,000** |

**Section D — Tools & Tackles:**

| Description | Qty | Rate | Amount |
|-------------|-----|------|--------|
| Trowel Set (TLS-001) | 5 Kit | ₹1,200 | ₹6,000 |
| Mixing Buckets | 10 Nos | ₹250 | ₹2,500 |
| | | **Section D Total** | **₹8,500** |

**Section E — Overhead & Miscellaneous:**

| Description | Amount |
|-------------|--------|
| Site Supervision (5 days) | ₹12,500 |
| Contingency (2%) | ₹3,000 |
| | **Section E Total** | **₹15,500** |

**Total Costing Amount = ₹1,03,000 + ₹35,000 + ₹5,000 + ₹8,500 + ₹15,500 = ₹1,67,000**

### Step 3: Project (auto-created on Costing Approved)

| Field | Value |
|-------|-------|
| Project ID | PRJ-2026-0001 (autogen) |
| SO Reference | SO-2026-0001 |
| Project Name | Acme DC — Chakan Epoxy |
| Address | Plot 5, Chakan MIDC, Pune |
| Project Manager | Amit Sharma |
| Execution Base | Area Basis |
| Start Date | 15-Jan-2026 |
| End Date | 20-Jan-2026 |
| Project Cost | ₹1,67,000 |
| Status | In Progress |
| Total Revenue | ₹1,75,000 (from SO) |
| Total Actual Cost | ₹1,67,000 (from MR) |
| P&L | ₹8,000 |

**Systems Subform:**

| System Code | Area | UOM | Description |
|-------------|------|-----|-------------|
| EP02 | 500 | SqM | 2mm Epoxy Flooring — full area |

**Task Budget Subform:**

| Category | Description | Budget Qty | Rate | Budget Amount | Actual Qty | Actual Amount |
|----------|-------------|------------|------|---------------|------------|---------------|
| Transport | Material + Equipment | 2 trips | ₹2,500 | ₹5,000 | 2 | ₹5,000 |
| Execution | Surface prep + application | 500 SqM | ₹35 | ₹17,500 | 500 | ₹17,500 |
| Manpower | 3 applicators × 5 days | 15 man-days | ₹800 | ₹12,000 | 15 | ₹12,000 |
| Tools | Trowels, buckets | 1 set | ₹8,500 | ₹8,500 | 1 | ₹8,500 |
| Overhead | Supervision + contingency | 1 | ₹15,500 | ₹15,500 | 1 | ₹15,500 |

### Step 4: Production Plan (auto-created on Costing Approved)

| Field | Value |
|-------|-------|
| Plan Number | PP-2026-0001 (autogen) |
| Project ID | PRJ-2026-0001 |
| Costing Reference | CST-2026-0001 |
| Plan Status | Released |

**Line Items (stock check):**

| RM Code | RM Name | Required Qty | Available Stock | Other Allocations | Net Available | Shortage | Auto-PR |
|---------|---------|-------------|-----------------|-------------------|---------------|----------|---------|
| RM-001 | Epoxy Resin A | 275 Kg | 500 Kg | 0 | 500 Kg | 0 | No |
| RM-002 | Hardener B | 125 Kg | 400 Kg | 0 | 400 Kg | 0 | No |

> **No shortage** — stock sufficient. No auto-PR triggered.

### Step 5: MR (auto-derived from Costing Sheet + Production Plan)

**Header:**

| Field | Value |
|-------|-------|
| MR Number | MR-2026-0001 (autogen) |
| Project ID | PRJ-2026-0001 |
| Costing Reference | CST-2026-0001 |
| Material Cost | ₹1,03,000 (Section A) |
| Application Amount | ₹35,000 (Section B) |
| Transportation Amount | ₹5,000 (Section C) |
| Tools Amount | ₹8,500 (Section D) |
| Total MR Cost | ₹1,51,500 (formula: 103000+35000+5000+8500) |
| MR Status | Released |

**MR 5-state journey:**
1. Draft → 2. Pending Production Verification → 3. Production Verified → 4. Costing Approved → 5. Released

**Material Allocation Subform:**

| Item Code | Item Name | Assigned Qty | Ratio % | 80% Alert | Issued Qty | Consumed Qty | Returned Qty | Remaining |
|-----------|-----------|-------------|---------|-----------|------------|--------------|--------------|-----------|
| RM-001 | Epoxy Resin A | 275 Kg | 68.75% | OFF | 0 | 0 | 0 | 275 |
| RM-002 | Hardener B | 125 Kg | 31.25% | OFF | 0 | 0 | 0 | 125 |

> **Cross-validation:** Per-RM, Assigned vs SO Area × BOM expected. Both lines = 0% deviation (pass). >5% would flag, >10% would block (C31).

### Step 6: MIS (auto-created on MR Released)

**Header:**

| Field | Value |
|-------|-------|
| MIS Number | MIS-2026-0001 (autogen) |
| MR Reference | MR-2026-0001 |
| Project ID | PRJ-2026-0001 |
| Date | 12-Jan-2026 |
| Store | ST-01 — Wadki Main Store |
| Status | Posted |

**Line Items:**

| Item Code | Item Name | Required Qty | Issued Qty | Balance Qty | Unit |
|-----------|-----------|-------------|------------|-------------|------|
| RM-001 | Epoxy Resin A | 275 Kg | 275 Kg | 0 | Kg |
| RM-002 | Hardener B | 125 Kg | 125 Kg | 0 | Kg |

> **Post MIS effect:** RM stock: RM-001 500→225, RM-002 400→275. Allocation Issued Qty: RM-001 = 275, RM-002 = 125. Stock Movement Log: 2 rows (RM-001 out 275, RM-002 out 125).

### Step 7: Production

#### 7a. Production Job (PJ-2026-0001)

| Field | Value |
|-------|-------|
| Job Number | PJ-2026-0001 |
| Project ID | PRJ-2026-0001 |
| MR Reference | MR-2026-0001 |
| FG Code | FG-001 + FG-002 |
| Planned Qty | 150 Kg (FG-001) + 300 Kg (FG-002) |
| Status | In Progress |

#### 7b. BMR — Batch Manufacturing Record (BMR-2026-0001)

| Field | Value |
|-------|-------|
| BMR Number | BMR-2026-0001 |
| Project ID | PRJ-2026-0001 |
| Job Reference | PJ-2026-0001 |
| FG Code | FG-001 (Epoxy Primer) |
| Batch Qty | 150 Kg |
| Date | 14-Jan-2026 |

**BMR Line Items (RM consumed):**

| RM Code | RM Name | BOM Standard | Actual Consumed | Variance | Rate | Amount |
|---------|---------|-------------|-----------------|----------|------|--------|
| RM-001 | Epoxy Resin A | 100.5 Kg | 102.0 Kg | +1.5 Kg | ₹220 | ₹22,440 |
| RM-002 | Hardener B | 50.0 Kg | 49.5 Kg | -0.5 Kg | ₹340 | ₹16,830 |

> **BMR effect on Allocation:** Consumed Qty: RM-001 = 102.0, RM-002 = 49.5. Remaining: RM-001 = 173, RM-002 = 75.5. 80% alert: RM-001 = 37.1% (OFF), RM-002 = 39.6% (OFF).

#### 7c. RM Consumption Entry (variance check only — NO allocation increment)

| Field | Value |
|-------|-------|
| BMR Reference | BMR-2026-0001 |
| RM Code | RM-001 |
| BOM Standard | 100.5 Kg |
| Actual | 102.0 Kg |
| Variance | +1.5 Kg (+1.5%) |

> **Key:** RM Consumption Entry is variance-check only. It does NOT increment Consumed Qty (avoids double-count with BMR).

#### 7d. Packing Entry

| Field | Value |
|-------|-------|
| Project ID | PRJ-2026-0001 |
| FG Code | FG-001 |
| Packed Qty | 150 Kg |
| Packaging Material | PKG-001 (20 Kg HDPE Bucket) |
| Buckets Used | 8 |

> **Packing effect:** Deducts 8 × PKG-001 from RM inventory. Does NOT affect FG allocation.

#### 7e. FGHM — FG Handover (FGH-2026-0001)

| Field | Value |
|-------|-------|
| FGH Number | FGH-2026-0001 |
| Project ID | PRJ-2026-0001 |
| Date | 14-Jan-2026 |
| FG Product Code | FG-001 |
| FG Product Name | Epoxy Primer Coat |
| Accepted Qty | 150 Kg |
| Status | Accepted |

> **FGHM effect:** FG Stock FG-001 += 150. Stock Movement Log: 1 row. Allocation: RM-001 Consumed = 102/275 (37.1%), RM-002 = 49.5/125 (39.6%). Fully Consumed = OFF (neither line ≥ 100%).

**Second BMR (FG-002 Epoxy Top Coat):**

| RM Code | BOM Standard | Actual | Rate | Amount |
|---------|-------------|--------|------|--------|
| RM-001 | 174.5 Kg | 173.0 Kg | ₹220 | ₹38,060 |
| RM-002 | 75.0 Kg | 75.5 Kg | ₹340 | ₹25,670 |

**Second FGHM (FG-002):**

| FG Code | Accepted Qty | Status |
|---------|-------------|--------|
| FG-002 | 300 Kg | Accepted |

> **After both FGHMs:** RM-001 Consumed = 102+173 = 275/275 (100%). RM-002 Consumed = 49.5+75.5 = 125/125 (100%). Fully Consumed = ON (ALL lines ≥ 100%).

### Step 8: Site Consumption Entry (SCE-2026-0001)

| Field | Value |
|-------|-------|
| SCE Number | SCE-2026-0001 |
| Project ID | PRJ-2026-0001 |
| Date | 15-Jan-2026 |
| Work Area | Zone A — Storage Area |

**Line Items:**

| RM Code | Qty Consumed | System/FG Ref | Consumption Type | Rate | Amount |
|---------|-------------|---------------|------------------|------|--------|
| RM-001 | 10 Kg | EP02/FG-002 | Actual | ₹220 | ₹2,200 |
| RM-002 | 5 Kg | EP02/FG-002 | Actual | ₹340 | ₹1,700 |

> **SCE effect:** Increments Consumed Qty on MR Allocation. RM-001: 275+10 = 285 (exceeds assigned 275 — BLOCKED at submit). This entry is REJECTED at 103.6%.

**Corrected SCE (SCE-2026-0002) — within limits:**

| RM Code | Qty Consumed | Rate | Amount |
|---------|-------------|------|--------|
| RM-001 | 5 Kg | ₹220 | ₹1,100 |
| RM-002 | 2 Kg | ₹340 | ₹680 |

> **After corrected SCE:** RM-001 Consumed = 275+5 = 280 (exceeds 275 — still BLOCKED). Site consumption after full BMR already exhausted allocation. Real-world: SCE only fires for on-site usage, not factory BMR.

**Final valid SCE (SCE-2026-0003) — after MRT creates headroom:**

(After Material Return below returns 10 Kg each, allocation changes.)

### Step 9: Material Return (MRT-2026-0001)

| Field | Value |
|-------|-------|
| MRT Number | MRT-2026-0001 |
| Project ID | PRJ-2026-0001 |
| Date | 16-Jan-2026 |
| Store | ST-01 — Wadki Main Store |

**Line Items:**

| RM Code | Return Qty | Reason | Condition | Rate | Amount |
|---------|-----------|--------|-----------|------|--------|
| RM-001 | 10 Kg | Excess material | Good | ₹220 | ₹2,200 |
| RM-002 | 10 Kg | Excess material | Good | ₹340 | ₹3,400 |

> **MRT effect:** Consumed Qty: RM-001 = 280-10 = 270, RM-002 = 125-10 = 115. Returned Qty: RM-001 = 10, RM-002 = 10. Remaining: RM-001 = 275-270+10 = 15, RM-002 = 125-115+10 = 20. Stock: RM-001 225+10 = 235, RM-002 275+10 = 285.

**Damaged Return (MRT-2026-0002):**

| RM Code | Return Qty | Reason | Condition | Stock Restore |
|---------|-----------|--------|-----------|---------------|
| RM-001 | 5 Kg | Damaged in transit | Damaged | NO (credits allocation only) |

> **Damaged return:** Consumed Qty decremented (allocation credit) but stock NOT restored. RM-001 Consumed = 270-5 = 265, Remaining = 15+5 = 20. Stock stays at 235.

### Step 10: FG Consumption Entry (at site)

| Field | Value |
|-------|-------|
| Project ID | PRJ-2026-0001 |
| FG Code | FG-001 |
| Qty Consumed | 150 Kg |
| Date | 17-Jan-2026 |

> **FG Consumption effect:** FG Stock FG-001 -= 150. Project FG Consumption log created.

### Step 11: Project Close & P&L

| Metric | Value |
|--------|-------|
| Revenue (from SO) | ₹1,75,000 |
| Material Cost (Section A) | ₹1,03,000 |
| Application Cost | ₹35,000 |
| Transportation Cost | ₹5,000 |
| Tools Cost | ₹8,500 |
| Overhead Cost | ₹15,500 |
| **Total Cost** | **₹1,67,000** |
| **P&L** | **₹8,000** |

**Final Inventory State:**

| RM Code | Assigned | Consumed | Returned | Remaining | Stock |
|---------|----------|----------|----------|-----------|-------|
| RM-001 | 275 | 265 | 15 | 20 | 245 |
| RM-002 | 125 | 115 | 10 | 20 | 295 |

---

## FLOW 2 — Stream B: PU01 2mm PU Flooring (300 sqm) → Bharat Manufacturing

> **Scenario:** PU flooring project. Tests different system, different supplier, different customer. Tests 80% alert threshold.

### Step 1: Sales Order (SO-2026-0002)

| Field | Value |
|-------|-------|
| Sales Type | Supply+Apply |
| SO Date | 10-Jan-2026 |
| Employee Name | Sneha Kulkarni |
| Customer Code | CUST-0002 |
| Client Org | Bharat Manufacturing Ltd |
| Site Name | Bharat Plant — Pune |
| Project Type | Industrial |
| Payment Terms | Net 30 |
| Status | Accepted |

**Subform A — System Lines:**

| System Code | Area | Rate | Amount |
|-------------|------|------|--------|
| PU01 | 300 | ₹420 | ₹1,26,000 |

### Step 2: Costing Sheet (CST-2026-0002)

**Section A — Material Cost:**

| System | FG Code | RM Code | BOM Ratio | Area | Required Qty | Rate | Material Cost |
|--------|---------|---------|-----------|------|-------------|------|---------------|
| PU01 | FG-003 | RM-003 | 0.6000 | 300 | 90.0 | ₹280 | ₹25,200 |
| PU01 | FG-003 | RM-004 | 0.4000 | 300 | 60.0 | ₹310 | ₹18,600 |
| | | | | | **Section A Total** | | **₹43,800** |

**Sections B-E Total:** ₹22,000 (Application) + ₹4,000 (Transport) + ₹5,000 (Tools) + ₹10,000 (Overhead) = ₹41,000

**Total Costing Amount = ₹84,800**

### Step 3: Project (PRJ-2026-0002)

| Field | Value |
|-------|-------|
| Project Name | Bharat Plant PU Flooring |
| Project Manager | Amit Singh |
| Project Cost | ₹84,800 |
| Total Revenue | ₹1,26,000 |
| P&L | ₹41,200 |

### Step 4: Production Plan

| RM Code | Required | Available | Shortage | Auto-PR |
|---------|----------|-----------|----------|---------|
| RM-003 | 90 Kg | 300 Kg | 0 | No |
| RM-004 | 60 Kg | 200 Kg | 0 | No |

### Step 5: MR (MR-2026-0002)

**Material Allocation:**

| Item Code | Assigned Qty | Ratio % | 80% Alert |
|-----------|-------------|---------|-----------|
| RM-003 | 90 Kg | 60% | OFF |
| RM-004 | 60 Kg | 40% | OFF |

### Step 6: MIS (MIS-2026-0002)

| RM Code | Required | Issued |
|---------|----------|--------|
| RM-003 | 90 Kg | 90 Kg |
| RM-004 | 60 Kg | 60 Kg |

### Step 7: Production — BMR (BMR-2026-0002)

| RM Code | BOM Standard | Actual | Rate | Amount |
|---------|-------------|--------|------|--------|
| RM-003 | 90.0 Kg | 88.5 Kg | ₹280 | ₹24,780 |
| RM-004 | 60.0 Kg | 61.0 Kg | ₹310 | ₹18,910 |

**After BMR:** RM-003 Consumed = 88.5/90 (98.3%). RM-004 Consumed = 61/60 (101.7% — BLOCKED, exceeds 100%).

**Corrected BMR:** RM-004 Actual = 59.5 Kg. Consumed = 59.5/60 (99.2%).

### Step 7b: 80% Alert Test

After BMR: RM-003 = 98.3% → 80% alert FIRES. PM receives pop-up + email + dashboard flag.

### Step 8: FGHM (FGH-2026-0002)

| FG Code | Accepted Qty | Status |
|---------|-------------|--------|
| FG-003 | 150 Kg | Accepted |

> Fully Consumed = OFF (RM-003 = 98.3%, RM-004 = 99.2% — neither ≥ 100%).

### Step 9: Site Consumption (SCE-2026-0002)

| RM Code | Qty Consumed | Rate | Amount |
|---------|-------------|------|--------|
| RM-003 | 1.5 Kg | ₹280 | ₹420 |

> After SCE: RM-003 = 90/90 (100%). RM-004 = 59.5/60 (99.2%). Fully Consumed still OFF.

### Step 10: Material Return (MRT-2026-0003)

| RM Code | Return Qty | Condition |
|---------|-----------|-----------|
| RM-004 | 0.5 Kg | Good |

> After MRT: RM-004 = 59/60 (98.3%). Returned = 0.5. Remaining = 1. Stock += 0.5.

---

## FLOW 3 — Stream A: Stock Procurement (PR → PO → GRN → QC)

> **Scenario:** No project. Pure stock procurement. Tests dual PO numbering, GST split, partial GRN, vendor performance.

### Step 1: Purchase Requisition (PR-2026-0001)

| Field | Value |
|-------|-------|
| PR Number | PR-2026-0001 (autogen) |
| Department | Purchase |
| Date | 03-Jan-2026 |
| Requestor | Suresh Jadhav |
| Justification | Reorder — RM-001 below min stock |

**Line Items:**

| Item Code | Item Name | Category | UOM | Qty | Lead Time |
|-----------|-----------|----------|-----|-----|-----------|
| RM-001 | Epoxy Resin A | RM | Kg | 300 | 7 |
| RM-002 | Hardener B | RM | Kg | 150 | 7 |

### Step 2: Rate Comparison

| Supplier | Price/Kg | Credit Terms | Delivery |
|----------|----------|-------------|----------|
| SUP-0001 ResinChem | ₹215 | 30 days | 7 days |
| SUP-0002 PolyChem | ₹225 | 45 days | 10 days |
| SUP-0003 ColorTech | ₹230 | 15 days | 5 days |

**Selected:** SUP-0001 — ₹215/Kg (best price)

### Step 3: Purchase Order (PO-2026-0001)

**Header:**

| Field | Value |
|-------|-------|
| PO Number | RMWAD-2026-0001 (Coding material — RMWAD series) |
| PR Reference | PR-2026-0001 |
| Supplier Code | SUP-0001 |
| Supplier Name | ResinChem Supplies |
| Date | 04-Jan-2026 |
| Delivery Date | 11-Jan-2026 |
| Payment Terms | Net 30 |
| Transport Scope | Supplier |
| Status | Sent |
| Total Amount | ₹96,750 (Basic) + ₹17,415 (GST) = ₹1,14,165 |

**Line Items:**

| Item Code | Item Name | HSN | Qty | Rate | Basic Amount | GST% | CGST | SGST | IGST | Total |
|-----------|-----------|-----|-----|------|-------------|------|------|------|------|-------|
| RM-001 | Epoxy Resin A | 3907 | 300 Kg | ₹215 | ₹64,500 | 18% | ₹5,805 | ₹5,805 | — | ₹76,110 |
| RM-002 | Hardener B | 3907 | 150 Kg | ₹215 | ₹32,250 | 18% | ₹2,903 | ₹2,903 | — | ₹38,055 |

> **GST Split (F12):** Same-state (Maharashtra) → CGST + SGST. Inter-state → IGST. Per-line calculation.

### Step 4: GRN — Partial (GRN-2026-0001)

| Field | Value |
|-------|-------|
| GRN Number | GRN-2026-0001 (autogen — generated on Post) |
| PO Reference | RMWAD-2026-0001 |
| Date | 11-Jan-2026 |
| Warehouse | ST-01 — Wadki Main Store |
| Partial GRN | Yes (checkbox) |

**Line Items:**

| Item Code | Ordered Qty | Received Qty | QC Status | Packing Quality |
|-----------|-------------|-------------|-----------|-----------------|
| RM-001 | 300 Kg | 200 Kg | Pending | Good |
| RM-002 | 150 Kg | 150 Kg | Pending | Good |

> **Post GRN effect:** RM-001 stock: 500+200 = 700. RM-002 stock: 400+150 = 550. PO line RM-001: Received=200, Balance=100, Receipt Status=Partial. PO line RM-002: Received=150, Balance=0, Receipt Status=Complete. PO Status=Partially Received. Stock Movement Log: 2 rows. Delivery Days: 11-04 = 7 days.

### Step 5: GRN — Complete (GRN-2026-0002)

| Field | Value |
|-------|-------|
| PO Reference | RMWAD-2026-0001 |
| Date | 14-Jan-2026 |
| Partial GRN | No |

**Line Items:**

| Item Code | Ordered | Received | QC Status |
|-----------|---------|----------|-----------|
| RM-001 | 300 Kg | 100 Kg | Pending |

> **Post GRN effect:** RM-001 stock: 700+100 = 800. PO line RM-001: Received=300, Balance=0, Receipt Status=Complete. PO Status=Fully Received.

### Step 6: QC (QC-2026-0001)

| Field | Value |
|-------|-------|
| GRN Reference | GRN-2026-0001 |
| Date | 11-Jan-2026 |
| Viscosity | 4500 cP (Pass) |
| Density | 1.12 g/cm³ (Pass) |
| Color | Off-white (Pass) |
| Moisture | 0.3% (Pass) |
| Accepted Qty | 200 Kg |
| Rejected Qty | 0 Kg |
| QC Status | Pass |

### Final Inventory After Flow 3:

| RM Code | Before | +GRN1 | +GRN2 | After |
|---------|--------|-------|-------|-------|
| RM-001 | 500 | +200 | +100 | 800 Kg |
| RM-002 | 400 | +150 | — | 550 Kg |

---

## FLOW 4 — Stream B with Shortage: EP01 1mm Epoxy (800 sqm) → CleanRoom Technologies

> **Scenario:** Large-area project that triggers stock shortage → auto-PR → procurement cycle. Tests the Available Stock formula and auto-PR on Plan Release.

### Step 1: Sales Order (SO-2026-0003)

| Field | Value |
|-------|-------|
| Sales Type | Supply+Apply |
| SO Date | 15-Jan-2026 |
| Customer | CUST-0003 — CleanRoom Technologies |
| Site | CleanRoom Unit — Whitefield, Bangalore |
| Project Type | Industrial |

**Subform A — System Lines:**

| System Code | Area | Rate | Amount |
|-------------|------|------|--------|
| EP01 | 800 | ₹300 | ₹2,40,000 |

### Step 2: Costing Sheet (CST-2026-0003)

**Section A — Material Cost:**

| FG Code | RM Code | BOM Ratio | Area | Required Qty | Rate | Material Cost |
|---------|---------|-----------|------|-------------|------|---------------|
| FG-001 | RM-001 | 0.6700 | 800 | 107.2 | ₹220 | ₹23,584 |
| FG-001 | RM-002 | 0.3333 | 800 | 53.3 | ₹340 | ₹18,122 |
| FG-002 | RM-001 | 0.5817 | 800 | 186.1 | ₹220 | ₹40,942 |
| FG-002 | RM-002 | 0.2500 | 800 | 100.0 | ₹340 | ₹34,000 |
| | | | | **Section A Total** | | **₹1,16,648** |

> **Total RM Required:** RM-001 = 107.2+186.1 = 293.3 Kg. RM-002 = 53.3+100.0 = 153.3 Kg.

**Sections B-E Total:** ₹48,000 + ₹8,000 + ₹12,000 + ₹18,000 = ₹86,000

**Total Costing = ₹2,02,648**

### Step 3: Project (PRJ-2026-0003)

| Field | Value |
|-------|-------|
| Project Name | CleanRoom Whitefield Epoxy |
| Project Manager | Deepa Menon |
| Project Cost | ₹2,02,648 |
| Total Revenue | ₹2,40,000 |
| P&L | ₹37,352 |

### Step 4: Production Plan — SHORTAGE DETECTED

| RM Code | Required | Physical Stock | Other Allocations (PRJ-0001 unreleased MR) | Net Available | Shortage | Auto-PR |
|---------|----------|---------------|---------------------------------------------|---------------|----------|---------|
| RM-001 | 293.3 Kg | 800 Kg | 0 (PRJ-0001 MR released) | 800 Kg | 0 | No |
| RM-002 | 153.3 Kg | 550 Kg | 0 | 550 Kg | 0 | No |

> **Wait** — after Flow 1 consumption, stock is: RM-001 = 245 Kg (after returns), RM-002 = 295 Kg. But Flow 3 added stock: RM-001 = 800, RM-002 = 550. Net available = 800 - 0 = 800 (RM-001), 550 - 0 = 550 (RM-002). No shortage.

**Let's test shortage with a different scenario:** Assume stock is lower.

| RM Code | Required | Available Stock | Net Available | Shortage | Auto-PR |
|---------|----------|-----------------|---------------|----------|---------|
| RM-001 | 293.3 Kg | 200 Kg | 200 Kg | 93.3 Kg | YES → PR-2026-0002 |
| RM-002 | 153.3 Kg | 100 Kg | 100 Kg | 53.3 Kg | YES → PR-2026-0003 |

### Step 4b: Auto-PRs Created on Plan Release

**PR-2026-0002:**

| Field | Value |
|-------|-------|
| PR Number | PR-2026-0002 |
| Department | Purchase |
| Source | Auto-generated from Production Plan shortage |
| Project Ref | PRJ-2026-0003 (informational) |

| Item Code | Required | Available | Shortage | PR Qty |
|-----------|----------|-----------|----------|--------|
| RM-001 | 293.3 | 200 | 93.3 | 100 Kg (rounded up) |

**PR-2026-0003:**

| Item Code | Required | Available | Shortage | PR Qty |
|-----------|----------|-----------|----------|--------|
| RM-002 | 153.3 | 100 | 53.3 | 60 Kg (rounded up) |

### Step 5: MR (MR-2026-0003)

**Material Allocation:**

| Item Code | Assigned Qty | Ratio % | 80% Alert |
|-----------|-------------|---------|-----------|
| RM-001 | 293.3 Kg | 65.6% | OFF |
| RM-002 | 153.3 Kg | 34.4% | OFF |

### Steps 6-10: (Same pattern as Flow 1 — MIS → Production → FGHM → SCE → MRT)

### Cross-Validation Test (C31):

**Mutation test — RM-001 Assigned changed to 310 Kg (+5.7%):**
- New deviation: |310 - 293.3| / 293.3 = 5.7% → **FLAGGED** (>5%)
- MR stays in Draft, warning shown

**Mutation test — RM-001 Assigned changed to 326 Kg (+11.2%):**
- New deviation: |326 - 293.3| / 293.3 = 11.2% → **BLOCKED** (>10%)
- MR cannot proceed past Draft

---

## FLOW 5 — Edge Cases & Mixed Scenarios

> **Scenario:** Tests partial GRN rollback, damaged material return, 100% allocation exhaustion, and Supply Only SO.

### 5A: Supply Only SO (NO Project)

**SO-2026-0004:**

| Field | Value |
|-------|-------|
| Sales Type | Supply Only |
| SO Date | 20-Jan-2026 |
| Customer | CUST-0004 — Delta Infrastructures |
| Total Amount | ₹56,000 |

**Subform B — FG Lines (no System Lines):**

| FG Code | FG Name | Qty | UOM | Rate | Amount |
|---------|---------|-----|-----|------|--------|
| FG-003 | PU Top Coat | 100 Kg | Kg | ₹560 | ₹56,000 |

> **No Project created.** No Costing Sheet. No MR. Direct FG dispatch.

### 5B: Partial GRN Rollback

**GRN-2026-0003 (partial):**

| PO Reference | Item | Ordered | Received |
|-------------|------|---------|----------|
| RMWAD-2026-0001 | RM-001 | 300 | 50 |

> Post GRN: RM-001 stock += 50. PO line Partial. PO stays Partially Received.

**Rollback scenario:** If GRN is rejected after posting:
- Stock decremented by 50
- PO line Received Qty decremented
- Stock Movement Log: reversal entry

### 5C: 100% Allocation Exhaustion Test

**After Flow 2 BMR + SCE:** RM-003 = 90/90 (100%). 100% alert fires → PM + Purchase notified. "Allocation Exhausted" banner on dashboard.

### 5D: Over-Consumption Block

**SCE attempting to consume beyond allocation:**

| RM Code | Assigned | Already Consumed | Attempted | Result |
|---------|----------|-----------------|-----------|--------|
| RM-001 | 275 Kg | 270 Kg | 10 Kg | BLOCKED (280 > 275) |

> System rejects: "Consumption exceeds allocated quantity. Return unused material first."

### 5E: Material Return — Damaged (No Stock Restore)

**MRT-2026-0004:**

| RM Code | Qty | Condition | Stock Restore | Allocation Credit |
|---------|-----|-----------|---------------|-------------------|
| RM-005 | 5 Kg | Damaged | NO | YES (Consumed -= 5) |

> Damaged returns credit the allocation (reduce Consumed Qty) but do NOT restore to available stock. Separate damaged stock tracking.

### 5F: Auto Numbering Series Verification

| Document | Series | Example | Notes |
|----------|--------|---------|-------|
| SO | Autogen | SO-2026-0001 | Sequential |
| Costing | CST-YYYY-XXXX | CST-2026-0001 | P1 counter |
| Project | PRJ-YYYY-XXXX | PRJ-2026-0001 | P1 counter |
| MR | MR-YYYY-XXXX | MR-2026-0001 | P1 counter |
| MIS | MIS-YYYY-XXXX | MIS-2026-0001 | P1 counter |
| PO (Coding) | RMWAD-YYYY-XXXX | RMWAD-2026-0001 | P1 counter |
| PO (Non-coding) | RM-YYYY-XXXX | RM-2026-0001 | P1 counter |
| PR | PR-YYYY-XXXX | PR-2026-0001 | P1 counter |
| GRN | GRN-YYYY-XXXX | GRN-2026-0001 | Generated on Post |
| QC | QC-YYYY-XXXX | QC-2026-0001 | P1 counter |
| BMR | BMR-YYYY-XXXX | BMR-2026-0001 | P1 counter |
| FGHM | FGH-YYYY-XXXX | FGH-2026-0001 | P1 counter |
| SCE | SCE-YYYY-XXXX | SCE-2026-0001 | P1 counter |
| MRT | MRT-YYYY-XXXX | MRT-2026-0001 | P1 counter |

---

## AUTOMATION VERIFICATION CHECKLIST

Use this table to verify each automation fires correctly during UAT:

| A-ID | Automation | Trigger | Expected Result | Flow |
|------|-----------|---------|----------------|------|
| A-06 | SO Sales Type swap | Sales Type change | Subform A/B visibility toggles | 1,2,3,4,5A |
| A-07 | SO → Costing Draft | SO acceptance (Supply+Apply) | Costing Sheet Draft created | 1,2,4 |
| A-08 | SO line calc | Line entry | Amount = Qty × Rate, Total = Σ | 1,2,3,4,5A |
| A-09 | Section A expansion | Costing Submit | RM lines auto-populated from SO×Comp×BOM | 1,2,4 |
| A-10 | Costing Approval | Status change | Blueprint: Draft → Under Review → Approved | 1,2,4 |
| A-11 | Costing → Project+Plan | Costing Approved | Project + Production Plan created | 1,2,4 |
| A-12 | Project cost set | MR Released | Total Actual Cost = MR total | 1,2,4 |
| A-13 | Available Stock calc | Plan Release | Physical − Σ unreleased MR allocations | 4 |
| A-14 | Plan → auto-PR | Plan Released | PR created for each Shortage > 0 | 4 |
| A-15 | MR auto-derive | Plan Released + Costing Approved | MR created with 4 cost components | 1,2,4 |
| A-16 | Cross-validation | MR Submit | Per-RM deviation check (5% flag, 10% block) | 4 |
| A-17 | MR 5-state | Status transitions | Draft → Pending Verif → Verified → Approved → Released | 1,2,4 |
| A-18 | MR → auto-MIS | MR Released | MIS Draft created with allocation lines | 1,2,4 |
| A-19 | SLA schedules | Daily 9 AM | Draft >2h reminder, Verified >2h escalate, Approved >1h release | 1,2,4 |
| A-20 | 80% alert | Consumption entry | PM email + dashboard flag when ≥80% | 2 |
| A-21 | PR submit | PR Submit | Status → Pending Approval | 3 |
| A-23 | PO dual series | PO Load | RMWAD for coding, RM for non-coding | 3 |
| A-24 | PO GST split | Line entry | Per-line CGST/SGST/IGST | 3 |
| A-27 | Post GRN | GRN button | Stock +, Movement Log, G5 fields (Received/Balance/Status/Delivery Days) | 3 |
| A-29 | QC auto-status | Qty entry | Pass/Fail/Hold | 3 |
| A-30 | MIS Released-only | MIS Load | Only Released MRs in lookup | 1,2,4 |
| A-31 | Post MIS | MIS button | Stock −, Movement Log, G4 Issued Qty + | 1,2,4 |
| A-33 | BMR submit | BMR Submit | Allocation.Consumed Qty +, block >100% | 1,2,4 |
| A-36 | FGHM accept | Inline Accept | FG Stock +, Movement Log, Status = Accepted | 1,2,4 |
| A-37 | Fully Consumed | FGHM Accept | Flag ON only when ALL lines ≥100% | 1 |
| A-38 | SCE submit | SCE Submit | Allocation.Consumed +, block >100%, alerts | 2 |
| A-40 | MRT submit | MRT Submit | Allocation.Consumed −, Returned +, stock restore (if Good) | 1,2 |
| A-41 | Min/Max alerts | Daily 7 AM | Reorder alerts for below-min items | All |

---

## REPORTS VERIFICATION

After each flow, verify these reports return correct data:

| Report | Source | Expected Data | Flow |
|--------|--------|---------------|------|
| Sales Register | SO | SO-2026-0001 to 0004 with correct Status | 1,2,4,5A |
| SO Value by Customer | SO | Acme ₹1.75L, Bharat ₹1.26L, CleanRoom ₹2.40L, Delta ₹56K | 1,2,4,5A |
| Costing Sheet Status | Costing | 3 Approved, 0 Rejected | 1,2,4 |
| Project P&L | Project | PRJ-0001 P&L ₹8K, PRJ-0002 ₹41.2K, PRJ-0003 ₹37.4K | 1,2,4 |
| MR Status Tracking | MR | All Released | 1,2,4 |
| Project Cost Baseline | MR | Sum of Total MR Cost per project | 1,2,4 |
| 80% Alert List | MR Allocation | RM-003 (Flow 2) at 98.3% | 2 |
| Open PO Register | PO | Status ≠ Fully Received | 3 |
| PO vs GRN Pending | PO lines | Balance Qty > 0 | 3 |
| Vendor Performance | PO | SUP-0001: 7 days avg delivery | 3 |
| MIS Register | MIS | All posted | 1,2,4 |
| Today's Production | BMR | FG-001 150Kg, FG-002 300Kg, FG-003 150Kg | 1,2 |
| FG Handover Pending | FGHM | Status = Pending Acceptance (before accept) | 1,2 |
| RM Stock Status | RM Inventory | RM-001, RM-002 current levels | 1,2,3 |
| Inventory Valuation | RM+FG | Closing Stock × Standard Rate | 1,2,3 |
| Site Consumption Log | SCE | All entries per project | 1,2 |
| Material Return Report | MRT | All returns with condition | 1,2,5E |
| Project Inventory Status | MR Allocation | Assigned vs Consumed vs Returned vs Remaining | 1,2,4 |
| Costing vs Actual Variance | MR+SCE+BMR | Planned (Costing) vs Actual (BMR+SCE) | 1,2 |

---

*Document generated: 05-Aug-2026 | Covers: 18+ modules, 43 automations, 59 reports, 5 complete flows*
