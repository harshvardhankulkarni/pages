# Chemsol — Zoho Creator Workflow Blueprint: Implementation Plan

## Core Process Flow

```
SO (Sales Order) → Costing Team (RM + Cost check)
  → MR Draft (Project Cost Baseline: Material + Application + Transportation + Tools)
    → Production Verified (MR qty vs SO system req via BOM)
      → Costing Approved (TOTAL project cost approved)
        → MR Released [⛔ CRITICAL GATE]
          → MIS (Store issues RM to Production)
            → Production (Planning → BMR → RM Consumption → Packing)
              → FGHM (FG Handover with inline acceptance)
                → FG Stock Updated

← Side: Procurement (PR → PO → GRN → QC) when inventory insufficient
← Side: Inventory Management (RM stock + FG stock)
```

## 1. Overview

**Client**: Chemsol — Flooring/construction materials company (Epoxy, PU, Demarcation)
**Platform**: Zoho Creator
**Core Modules**: 15 modules across 6 phases
**Departments**: Sales, Costing, Purchase, Store, Production, QC, Project Manager
**Warehouses**: Wadki, Main, Neelo, Gurgaon, Bangalore, Client Site

### System Code Prefixes
| Code | Meaning | Example |
|------|---------|---------|
| EP | Epoxy Flooring | EP01 (1mm), EP02 (2mm) |
| PU | PU Flooring | PU01 (1mm) |
| DEM | Demarcation Line | — |
| ANTI | Anti Static | — |
| ESD | ESD Flooring | — |
| FIL | Filling | — |
| COV | Coving | — |

---

## 2. Phase 1 — Master Data (Foundation)

Build first — all transactional forms depend on these.

### 2.1 Purchase Item Muster
**Purpose**: Central item repository — RM, FG, Packaging, Tools, Consumable

| # | Field | Type | Req | Notes |
|---|-------|------|-----|-------|
| 1 | Category | Dropdown | * | 1.RM, 2.Packaging, 3.Tools & Consumable, 4.FG, 5.Maintenance, 6.Capital |
| 2 | Item Code | Autogen | * | Auto based on category |
| 3 | Item Name | Text | * | — |
| 4 | UOM | Dropdown | * | Nos / Kg / Ltr / Mtr / Kit |
| 5 | HSN Code | Text | * | For GST |
| 6 | GST % | Number | | — |
| 7 | Min Stock | Number | * | Reorder threshold |
| 8 | Max Stock | Number | | — |
| 9 | Standard Rate | Currency | | Hidden from non-Purchase/Store |
| 10 | Preferred Supplier | Multi-lookup | | From Supplier Master |
| 11 | Lead Time | Number (Days) | | — |
| 12 | Status | Dropdown | * | Active / Inactive |

**AutoFetch target**: PR, PO, MR, MIS, GRN, FGHM, BOM, QC

### 2.2 System Master
**Purpose**: Flooring system definitions

| # | Field | Type | Req |
|---|-------|------|-----|
| 1 | System Code | Text (autogen) | * |
| 2 | System Name | Text | * |
| 3 | Description | Multi-line | |
| 4 | Status | Active / Inactive | * |

### 2.3 System Composition (System → FG Mapping)
**Purpose**: Defines which FGs make up each System (e.g., EP01 = FG-001 + FG-002)

**Header:**
| # | Field | Type | Req |
|---|-------|------|-----|
| 1 | Comp No | Autogen (SC-YYYY-XXXX) | * |
| 2 | System Code | Lookup (System Master) | * |
| 3 | System Name | AutoFetch | * |
| 4 | Revision No | Text | |
| 5 | Date | Date (Today) | * |
| 6 | Status | Draft / Approved / Released | * |

**Line Items (N FGs per System):**
| # | Field | Type | Req |
|---|-------|------|-----|
| 1 | FG Product Code | Lookup (Item Muster - FG) | * |
| 2 | FG Name | AutoFetch | * |
| 3 | Qty per System Unit | Number | * |
| 4 | UOM | AutoFetch | * |
| 5 | Rate per FG Unit | Currency | |

### 2.4 BOM / FG Formulation (FG → RM Mapping)
**Purpose**: Defines which RMs make up each FG with ratios

**Header:**
| # | Field | Type | Req |
|---|-------|------|-----|
| 1 | BOM No | Autogen | * |
| 2 | FG Code | Lookup (Item Muster - FG) | * |
| 3 | FG Name | AutoFetch | * |
| 4 | Date | Date (Today) | * |
| 5 | Status | Draft / Approved / Released | * |

**Line Items (N RMs per FG):**
| # | Field | Type | Req |
|---|-------|------|-----|
| 1 | RM Item Code | Lookup (Item Muster - RM) | * |
| 2 | RM Name | AutoFetch | * |
| 3 | UOM | AutoFetch | * |
| 4 | Qty per FG Unit | Number | * |
| 5 | Waste % | Number | |
| 6 | Total Qty | Formula | * |

### 2.5 Supplier Master
**Purpose**: Vendor database

| # | Field | Type | Req |
|---|-------|------|-----|
| 1 | Supplier Code | Autogen | * |
| 2 | Supplier Name | Text | * |
| 3 | GSTIN | Text | * |
| 4 | PAN No | Text | * |
| 5 | Contact Person | Text | * |
| 6 | Mobile No | Phone | * |
| 7 | Email | Email | * |
| 8 | Address | Multi-line | * |
| 9 | Bank Name / Account No / IFSC | Text | * |
| 10 | Payment Terms | Text | * |
| 11 | Credit Days | Number | * |
| 12 | Status | Active / Inactive | * |

### 2.6 Store Master
**Purpose**: Warehouse definitions

| # | Field | Type | Req |
|---|-------|------|-----|
| 1 | Store Code | Autogen | * |
| 2 | Store Name | Text | * |
| 3 | Store Type | Dropdown | * | RM Store / FG Store / QC Store / Site Store |
| 4 | Location | Text | * |
| 5 | Status | Active / Inactive | * |

**Bin Location** (inline subform): Rack No, Shelf No, Bin No, Status

### 2.7 User Access & Approval Matrix
**Purpose**: Define roles, departments, approval limits

**User Access:**
| Field | Type | Req |
|-------|------|-----|
| User Name | User lookup | * |
| Department | Dropdown | * | Purchase / Sales / Store / Production / QC / Project Manager / Account & Finance |
| Role | Entry / Review / Approve / Admin | * |
| Status | Active / Inactive | * |

**Approval Matrix:**
| Field | Type | Req |
|-------|------|-----|
| Department | Dropdown | * |
| Document Type | PR / PO / MR | * |
| Min Amount / Max Amount | Currency | * |
| Approver 1 / 2 / 3 | User lookup | * |

---

## 3. Phase 2 — Sales & Project

### 3.1 Sales Order (SO)
**Purpose**: Create customer orders. On acceptance (Supply+Apply), auto-creates Project.
**Department**: Sales

**Header:**
| # | Field | Type | Req |
|---|-------|------|-----|
| 1 | Sales Type | Dropdown | * | Supply+Apply (creates Project) / Supply Only (direct FG sale) |
| 2 | SO No | Autogen | * |
| 3 | SO Date | Date (Today) | * |
| 4 | Employee Name | Text | * |
| 5 | Customer Code | Lookup | |
| 6 | Client Org / Contact / GST / PAN | Text | * |
| 7 | Regd Address | Multi-line | * |
| 8 | Site Name / Address | Text / Multi-line | * |
| 9 | Site Manager / Contact | Text / Phone | |
| 10 | Project Type | Dropdown | | Industrial / Commercial |
| 11 | Total Amount | Formula | * |
| 12 | Payment Terms | Text | |
| 13 | Transportation Scope / Amount | Dropdown / Currency | |
| 14 | Lead Time | Number (Days) | |
| 15 | PO/BOQ Attachment | File upload | |
| 16 | Warranty | Text | |
| 17 | Commission | Checkbox → % or Fix Amount | |

**Subform A — System Lines** (when Sales Type = Supply+Apply):
| # | Field | Type |
|---|-------|------|
| 1 | System Code | Lookup (System Master) → AutoFetch Name |
| 2 | Thickness | Text |
| 3 | Area | Number |
| 4 | UOM | Dropdown |
| 5 | Rate | Currency |
| 6 | Amount | Formula = Area × Rate |

**Subform B — FG Lines** (when Sales Type = Supply Only):
| # | Field | Type |
|---|-------|------|
| 1 | FG Code | Lookup (Item Muster - FG) → AutoFetch Name |
| 2 | Qty | Number |
| 3 | UOM | AutoFetch |
| 4 | Rate | Currency |
| 5 | Amount | Formula = Qty × Rate |

**Automation:**
- Sales Type controls subform visibility (show/hide rule)
- Supply+Apply on acceptance → auto-create Project (Stream B root)
- Supply Only → NO Project, direct FG dispatch only
- System lines define System→FG→RM composition that drives backend consumption

### 3.2 Project
**Purpose**: Root entity — every downstream form links here. Auto-created from SO.
**Department**: Project Manager / Coordinator

| # | Field | Type | Req |
|---|-------|------|-----|
| 1 | Project ID | Autogen | * |
| 2 | SO Reference | Lookup | * |
| 3 | Project Name | Text | * |
| 4 | Address | Multi-line | * |
| 5 | Project Manager | User lookup | * |
| 6 | Execution Base | Dropdown | * | Area Basis / Day Basis |
| 7 | Start Date / End Date | Date | * |
| 8 | Project Cost | Currency | * |
| 9 | Status | Dropdown | * | Planned / In Progress / Completed / On Hold |

**Systems Subform:**
| # | Field | Type |
|---|-------|------|
| 1 | System Code | Lookup (System Master) |
| 2 | Area | Number |
| 3 | UOM | Dropdown |
| 4 | Description | Text |

---

## 4. Phase 3 — Costing & Material Requisition (MR)

### 4.1 MR — Material Requisition [CRITICAL GATE]
**Purpose**: MR is the **complete project implementation cost baseline** — four cost components (Material + Application + Transportation + Tools & Tackles) summing to Total MR Cost. Costing approves this TOTAL cost. MR is NOT just RM allocation.
**Department**: Production / R&D

**MR Status Workflow (The Critical Approval Gate):**
```
Draft → Production Verified → Costing Approved → Released
  │           │                      │              │
  │      Production checks       Costing           ⛔ Gate
  │      MR qty vs SO system     approves TOTAL    passed →
  │      req (via BOM × SO qty)  project cost      MIS can proceed
```

**Header:**
| # | Field | Type | Req | Notes |
|---|-------|------|-----|-------|
| 1 | MR Number | Autogen (MR-YYYY-XXXX) | * | — |
| 2 | MR Date | Date (Today) | * | — |
| 3 | Project ID | Lookup (Project Master) | * | Links MR to Project |
| 4 | Requisition Type | Dropdown | * | Production / R&D |
| 5 | Batch Number | Text | | — |
| 6 | Department | AutoFetch from login | * | — |
| 7 | Requested By | Text (Employee Name) | * | — |
| 8 | Priority | Low / Medium / High / Urgent | * | — |
| 9 | **MR Status** | **Draft / Production Verified / Costing Approved / Released** | * | **CRITICAL — controls downstream flow** |

**Line Items (N items):**
| # | Field | Type |
|---|-------|------|
| 1 | Item Code | Lookup (Item Muster) |
| 2 | Item Name | AutoFetch |
| 3 | Category | AutoFetch |
| 4 | UOM | AutoFetch |
| 5 | Available Stock | AutoFetch (real-time) |
| 6 | Required Qty | Number |
| 7 | Remarks | Multi-line |

**MR = Complete Project Implementation Cost Baseline:**

MR carries **four cost components** that sum to **Total MR Cost** — the project implementation cost baseline that **Costing approves**:

1. **Material Cost** — from Material Allocation subform (Σ Assigned Qty × Rate)
2. **Application Cost** — labour/execution on site
3. **Transportation Cost** — material transport to site
4. **Tools & Tackles** — equipment needed

**Total MR Cost = Material + Application + Transportation + Tools & Tackles**

**Material Allocation Subform (feeds Material Cost — per-project RM allocation):**
| # | Field | Type | Notes |
|---|-------|------|-------|
| 1 | Item Code | Lookup (RM) | Auto-populated from MR lines |
| 2 | Item Name | AutoFetch | — |
| 3 | UOM | AutoFetch | — |
| 4 | Assigned Qty | Number | Allocation baseline, defaults from Required Qty |
| 5 | Rate | Currency | Per-unit RM rate |
| 6 | Material Cost | Formula | = Assigned Qty × Rate |
| 7 | Allocation Ratio % | Formula | = Assigned Qty ÷ Σ Assigned Qty × 100 |
| 8 | 80% Threshold Alert Flag | Checkbox | Default ON |
| 9 | Consumed Qty | Number (auto) | Incremented by BMR/RM Consumption entries |
| 10 | Consumption % | Formula | = Consumed Qty ÷ Assigned Qty × 100 |
| 11 | Alert Triggered | Checkbox (readonly) | Auto-set at Consumption % ≥ 80% |

**Application Cost Subform (labour/execution):**
| # | Field | Type |
|---|-------|------|
| 1 | Activity | Text (e.g., surface prep, laying) |
| 2 | UOM | Dropdown |
| 3 | Qty / Area | Number |
| 4 | Rate | Currency |
| 5 | Amount | Formula = Qty × Rate |

**Transportation Cost Subform (material to site):**
| # | Field | Type |
|---|-------|------|
| 1 | From | Text (warehouse) |
| 2 | To | Text (site) |
| 3 | Vehicle / Trips | Text / Number |
| 4 | Rate | Currency |
| 5 | Amount | Formula = Trips × Rate |

**Tools & Tackles Subform:**
| # | Field | Type |
|---|-------|------|
| 1 | Item | Text/Lookup |
| 2 | Qty | Number |
| 3 | Rate | Currency |
| 4 | Amount | Formula = Qty × Rate |

**Automation Rules:**
- MR Status workflow: Draft (on create) → Production Verified → Costing Approved → Released
- **Without Released MR, there is no MIS, no Production, no project execution**
- Consumption entries increment Consumed Qty on matching MR Allocation (matched by Project ID + Item Code)
- **80% Alert**: When Consumption % ≥ 80% and Alert Flag is ON → pop-up + dashboard banner + email to Project Manager
- MRs stuck in Draft > 7 days → reminder. In Production Verified > 3 days → escalation to Costing

---

## 5. Phase 4 — Procurement (As Needed)

Procurement runs when production needs materials not in stock.

### 5.1 PR — Purchase Requisition
**Department**: Production
**Linked to**: Project (when procurement is for a project)

**Header:**
| # | Field | Type | Req |
|---|-------|------|-----|
| 1 | PR Number | Autogen | * |
| 2 | PR Date | Date (Today) | * |
| 3 | Project ID | Lookup | * |
| 4 | Reference | Text | |
| 5 | Department | AutoFetch from login | * |
| 6 | Status | Draft / Pending Approval / Approved / Rejected | * |

**Line Items:**
| # | Field | Type |
|---|-------|------|
| 1 | Item Code | Lookup (Item Muster) ↔ bidirectional autofill with Name |
| 2 | Item Name | AutoFetch |
| 3 | Qty | Number |
| 4 | UOM | AutoFetch |
| 5 | Lead Time | AutoFetch (Days, from Item Muster) |

**Automation:** Status = Draft → Pending Approval (on submit) → Approved. Notification to Purchase dept.

### 5.2 PO — Purchase Order
**Department**: Purchase
**Purpose**: Official order to supplier with GST split

**Header:**
| # | Field | Type | Req |
|---|-------|------|-----|
| 1 | RM Type | Coding / Non Coding | * |
| 2 | PO Number | Autogen (RM-YYYY-XXXX / RMWAD-YYYY-XXXX) | * |
| 3 | PO Date | Date (Today) | * |
| 4 | Supplier Code | Lookup (Supplier Master) → AutoFetch Name, GSTIN, Address | * |
| 5 | Project ID | Lookup (Project Master) | * |
| 6 | PR Reference | Lookup | |
| 7 | Bill To / Ship To | Dropdown | * |

**Line Items:**
| # | Field | Type |
|---|-------|------|
| 1 | Item Code | Lookup (Item Muster) |
| 2 | Item Name / HSN | AutoFetch |
| 3 | Quantity / Rate | Number / Currency |
| 4 | Basic Amount | Formula = Qty × Rate |
| 5 | GST % | AutoFetch from Item Muster |
| 6 | GST Amount | Formula = Basic × GST% |
| 7 | Total Amount | Formula = Basic + GST |

**Footer (Auto-calculated):**
| Field | Formula |
|-------|---------|
| Basic Total | SUM of line Basic Amounts |
| CGST / SGST | Each = GST/2 (intra-state) |
| IGST | Full GST (inter-state) |
| Total Amount (Words) | Auto-convert |
| Delivery Date / Payment Terms | Mandatory |
| Scope of Transport | Supplier / Own |

**Printable PO** with T&C, company logo, total in words.

### 5.3 GRN — Goods Receipt Note
**Department**: Store / Purchase

**Header:**
| # | Field | Type | Req |
|---|-------|------|-----|
| 1 | GRN Number | Autogen (after posting) | * |
| 2 | GRN Date | Date (Today) | * |
| 3 | PO Number | Lookup → AutoFetch Supplier, Items, Qty | * |
| 4 | Project ID | AutoFetch from PO | * |
| 5 | Vehicle Number | Text | * |
| 6 | Warehouse | Dropdown | * | Wadki / Main / Neelo / Gurgaon / Bangalore / Client Site |
| 7 | Invoice Number / Date | Text / Date | * |

**Line Items (Checkbox for partial GRN):**
| # | Field | Type |
|---|-------|------|
| 1 | ✅ Checkbox | Checkbox (select items for partial GRN) |
| 2 | Item Code / Name | AutoFetch from PO |
| 3 | Ordered Qty / Received Qty | AutoFetch / Number |
| 4 | QC Status | Pending / Pass / Fail |
| 5 | Packing Quality | Good / Damaged / Partial |

**Transport Subform** (visible when PO Scope = Own): Transporter, Charges, Local Transport, Loading/Unloading

**Stock Rule:** Qty added to stock **only after posting**. Timestamp logged. Partial GRN via checkbox.

### 5.4 QC / QA
**Department**: QC

| # | Field | Type | Req |
|---|-------|------|-----|
| 1 | QC Number | Autogen | * |
| 2 | Date | Date (Today) | * |
| 3 | GRN Number | Lookup | * |
| 4 | Item No / Name | AutoFetch from GRN | * |
| 5 | Inspection Date | Date | |
| 6 | Viscosity / Density / Color / Moisture | Text (result) | |
| 7 | Accepted Qty / Rejected Qty | Number | * |
| 8 | QC Status | Pass / Fail / Hold | * |
| 9 | Remarks | Multi-line | * |

---

## 6. Phase 5 — Inventory & Production

### 6.1 MIS — Material Issue Slip
**Department**: Store
**Purpose**: Issue RM from Store to Production. Procedes only after MR Released.

| # | Field | Type | Req |
|---|-------|------|-----|
| 1 | MR No | Lookup (MR — only Released MRs shown) | * |
| 2 | MIS Number | Autogen (against MR) | * |
| 3 | Date | Date (Today) | * |
| 4 | Batch Number | Text | |

**Line Items** (auto-fetched from MR):
| # | Field | Type |
|---|-------|------|
| 1 | Item Code / Name | AutoFetch |
| 2 | Category | AutoFetch |
| 3 | Required Qty | AutoFetch |
| 4 | Issued Qty | Number |
| 5 | Balance Qty | Formula = Required − Issued |
| 6 | Issued By / Handover To | Text (Supervisor Name) |

**Automation:** Stock deducted from inventory on MIS posting. Only creatable after MR Released.

### 6.2 Production Planning
**Department**: Production
**Purpose**: Plan FG production based on Project requirements

| # | Field | Type | Req |
|---|-------|------|-----|
| 1 | Planning No | Autogen | * |
| 2 | Planning Date | Date | * |
| 3 | Project ID | Lookup | * |
| 4 | MR Sheet No | Lookup | * |
| 5 | Planning Period | Week / Month | * |
| 6 | Plant | Dropdown | |
| 7 | Planner Name | User lookup | * |
| 8 | Status | Draft / Approved / Released | * |

### 6.3 BMR — Batch Manufacturing Record
**Department**: Production
**Purpose**: Record actual batch production — consume RM to produce FG

| # | Field | Type | Req |
|---|-------|------|-----|
| 1 | BMR No | Autogen | * |
| 2 | Production Order Ref | Lookup | * |
| 3 | Project ID | Lookup (from Production Order) | * |
| 4 | Batch No | Text | * |
| 5 | Date | Date | * |
| 6 | System Code / FG Code | Lookup | * |

**Line Items:**
| # | Field | Type |
|---|-------|------|
| 1 | RM Item Code | Lookup (Item Muster - RM) |
| 2 | RM Item Name | AutoFetch |
| 3 | Batch No (RM) | Text |
| 4 | Qty Consumed | Number |
| 5 | UOM | AutoFetch |
| 6 | Yield / FG Output | Number |

### 6.4 RM Consumption Entry

| # | Field | Type |
|---|-------|------|
| 1 | Reference to BMR | Lookup |
| 2 | Item-wise RM | Lookup |
| 3 | Actual Qty | Number |
| 4 | Standard Qty | AutoFetch (from BOM) |
| 5 | Variance | Formula = Actual − Standard |

### 6.5 Packing Entry

| # | Field | Type |
|---|-------|------|
| 1 | BMR Reference | Lookup |
| 2 | FG Product | Lookup |
| 3 | Packed Qty | Number |
| 4 | Packing Material Consumed | Lookup + Qty |
| 5 | Batch No | Text |

### 6.6 FGHM — FG Handover Master
**Department**: Production
**Purpose**: Handover FG to store/site with inline acceptance

| # | Field | Type | Req |
|---|-------|------|-----|
| 1 | FGH No | Autogen | * |
| 2 | Project ID | Lookup (Project Master) | * |
| 3 | Handover Date | Date (Today) | * |
| 4 | Batch No | Text | * |

**Line Items:**
| # | Field | Type |
|---|-------|------|
| 1 | FG Product Code | Lookup (Item Muster - FG) |
| 2 | FG Product Name | AutoFetch |
| 3 | FG Qty | Number |
| 4 | UOM | AutoFetch |
| 5 | QC Status | Pass / Fail / Hold |
| 6 | Damaged Qty / Accepted Qty | Number (inline acceptance) |
| 7 | Handed Over By / Received By | Text |
| 8 | Remark | Multi-line |

**Automation:** On FGHM submission → Notification to Store. FG Stock updated.

---

## 7. Phase 6 — Inventory Management

### 7.1 RM Inventory
- Stock increased on GRN posting
- Stock decreased on MIS posting
- Stock alerts at Min/Max thresholds

### 7.2 FG Inventory
- Stock increased on FGHM inline acceptance
- Stock decreased on dispatch (Supply Only sales)

### 7.3 MR→MIS→FG Stock Flow
```
MR Released
  → MIS Created (items auto-fetched from MR)
    → MIS Posted (RM Stock −)
      → Production (BMR → RM Consumption → Packing)
        → FGHM Created
          → FGHM Inline Accepted (FG Stock +)
```

---

## 8. Automation & Business Rules

### 8.1 MR Status Workflow (Critical Approval Gate)
```
MR Draft → [Production Verifies: checks MR qty vs SO system req via BOM]
  → Production Verified → [Costing Approves: approves TOTAL project cost]
    → Costing Approved → Released
      → ⛔ Gate passed: MIS → Production → FGHM can proceed
```

### 8.2 Consumption → Project-Assigned RM
- Every consumption entry (BMR/RM Consumption) resolves to MR Allocation line matched by `Project ID + Item Code`
- No generic pool deduction for project-tagged consumption
- Site consumption entries are expanded into RMs at BOM ratios, then increment `Consumed Qty`

### 8.3 80% Consumption Alert
- When Consumption % ≥ 80% AND 80% Threshold Alert Flag = ON
- Pop-up + dashboard banner + email to Project Manager
- At 100%: "Allocation Exhausted" alert fires to Project Manager + Purchase

### 8.4 Autofetch Rules
| Source | Target Forms | Fetched Fields |
|--------|-------------|----------------|
| Item Code | PR, PO, MR, MIS, GRN, FGHM, BOM, QC | Name, UOM, Category, HSN, GST%, Lead Time |
| Supplier Code | PO, GRN | Name, GSTIN, Address, Contact |
| PO No | GRN | Supplier, Items, Ordered Qty |
| MR No | MIS | Items, Required Qty |
| Project ID | PR, PO, GRN, MR, MIS, Production, FGHM | Project Name, Manager |
| System Code | SO, BOM, Project | System Name |

### 8.5 Numbering Series
| Document | Format |
|----------|--------|
| PR | PR-YYYY-XXXX |
| PO (Coding) | RMWAD-YYYY-XXXX |
| PO (Non-Coding) | RM-YYYY-XXXX |
| GRN | GRN-YYYY-XXXX |
| MR | MR-YYYY-XXXX |
| MIS | Auto against MR |
| FGH | FGH-YYYY-XXXX |
| QC | QC-YYYY-XXXX |

### 8.6 Stock Management Rules
- **GRN posting**: Qty added to stock only after posting; timestamp logged
- **MIS posting**: Qty deducted from stock
- **FGHM inline acceptance**: FG qty added to stock after inline acceptance
- **Material Return**: Qty added back to stock
- **Min/Max stock**: Alert when stock crosses thresholds

### 8.7 Notification Triggers
| Event | Notifies | Type |
|-------|----------|------|
| PR Submitted | Purchase (pending approval) | In-app |
| PR Approved | Production user | In-app |
| PO Ready | Purchase dept | In-app |
| GRN Overdue | Purchase + Store | In-app |
| MR Submitted (Draft → Pending Verification) | Production dept | In-app |
| MR Production Verified (→ Pending Costing Approval) | Costing dept | In-app |
| MR Released | Store + Production | In-app + Email |
| FGHM Submitted | Store & Logistics | Pop-up |
| 80% Consumption Alert | Project Manager | Pop-up + Email |

---

## 9. Implementation Timeline

### Week 1-2: Master Data Foundation
- Purchase Item Muster, System Master, Supplier Master, Store Master
- System Composition, BOM Formulation
- User Access & Approval Matrix
- Configure lookup relationships

### Week 3-4: Sales & Project
- Sales Order with conditional subforms (System Lines / FG Lines)
- Project (auto-created from SO)
- SO → Project automation

### Week 5-6: Costing & MR (Critical Gate)
- MR with 4 cost components (Material, Application, Transportation, Tools)
- Material Allocation subform with Assigned Qty, Ratio %, 80% Alert
- MR Status workflow: Draft → Production Verified → Costing Approved → Released
- Verification actions (Production Verify, Costing Approve)
- 80% Consumption Alert automation

### Week 7-8: Procurement (As Needed)
- PR with Project tagging
- PO with dual numbering (RM/RMWAD), GST split
- GRN with partial checkbox, transport subform
- QC/QA linked to GRN

### Week 8-9: Production & Inventory
- MIS linked to MR (only Released MRs)
- Production Planning, BMR, RM Consumption, Packing
- FGHM with inline acceptance
- RM + FG inventory management
- Stock update automations (GRN → RM+, MIS → RM−, FGHM → FG+)

### Week 9-10: Reports & Dashboards
- Purchase Dept dashboard
- Store Dept dashboard (RM + FG stock)
- Production Dept dashboard
- MR Status tracking report
- 80% Consumption Alert dashboard
- Project Material Allocation report

### Week 10-11: Integration & UAT
- Test all autofetch relationships
- Test MR workflow gates (cannot proceed without Released)
- Test stock updates on GRN/MIS/FGHM
- Test 80% consumption alerts
- Test partial GRN
- UAT with departmental users
- Go-live

---

## 10. Roles & Permissions

| Role | Access |
|------|--------|
| Admin | Full access — all forms, reports, settings |
| Sales - Entry | Create/Edit: SO, Customer Master |
| Costing | Approve MR (Costing Approved status). View: MR, reports |
| Production - Entry | Create/Edit: MR (Draft), BMR, Production Planning, RM Consumption, Packing, FGH, PR |
| Production - Verify MR | Verify MR — sets MR Status = Production Verified |
| Purchase - Entry | Create/Edit: PR, PO, GRN |
| Purchase - Approve | Approve: PR, PO within limits |
| Store - Entry | Create/Edit: GRN, MIS, FGHM |
| QC - Entry | Create/Edit: QC/QA |
| Store - Review | View: Inventory stock, GRN, PO |
| Project Manager | Create/Edit: Projects. View: Stock, PO status, MR status |

---

## 11. Forms Not in Core Loop (Removed)

The following are **excluded** from this implementation as they fall outside the SO→Costing→Production→Procurement→Inventory→MR→MIS→FG Handover core loop:
- Service Team module (Area → Work → Invoice)
- Service Invoice
- Finance (Supplier Credit Note, Customer Invoice/AR)
- Logistics (Delivery Challan, Outward)
- Vehicle & Transport
- Rate Comparison (simplified — standalone reference only)
