# Chemsol — Zoho Creator Implementation & Process Plan (27-Module Architecture)

## 1. Project Overview

**Client**: Chemsol — Flooring/construction materials company  
**Platform**: Zoho Creator  
**Domain**: Epoxy Flooring, PU Flooring, Demarcation Systems, Anti-Static Flooring, Coving  
**Modules**: 27 modules across 11 phases (1A→1K) — Foundation, Budget, Spend, Procurement, Revenue/Manufacturing, Reports, AP/AR, Finance & Compliance, Governance, Approvals/SoD, Billing & Order Closure  
**Users**: Purchase, Sales, Store & Logistics, Account & Finance, Admin, Project Coordinator, Project Managers (3)

---

## 2. System Architecture & Integration Map

Two streams — Stream A (Pre-Project) no Project ID, Stream B (Project-Centric) Project ID on all forms:

```
=== STREAM A (Pre-Project — No Project ID) ===
Purchase Dept → PR → PO → GRN → QC → Material Handover → Store Inventory

=== STREAM B (Project-Centric — Project ID on all forms) ===
Sales Order → Project
  │  Project baseline = SO + MR (SO = revenue, MR = complete project implementation cost baseline — total cost: Material + Application + Transportation + Tools & Tackles — that Costing approves)
  ▼
MR [Project Cost Baseline: Material + Application + Transportation + Tools & Tackles] → Draft → Production Verified → Costing Approved (TOTAL cost) → Released
  │  ⛔ Without Released MR → STOP (no MIS, no Production, no Logistics)
  ▼
MIS (consumes from Store)
Project → Production Planning → BMR → Packing → FGHM
Project → Logistics (DC → Outward)
Project → Service Team → Finance → Close

=== GLOBAL MASTER DATA ===
Item Master ← → Supplier Master
System Master ← → System Composition
BOM / FG Formulation
Customer/Site Master, Store Master
```

### System Code Prefixes
| Code | Meaning | Example |
|------|---------|---------|
| EP | Epoxy Flooring | EP01 (1mm), EP02 (2mm) |
| PU | PU Flooring | PU01 (1mm) |
| DEM | Demarcation Line | — |
| NUM | Numbering | — |
| ARR | Arrow Marking | — |
| ANTI | Anti Static Flooring | — |
| ESD | ESD Flooring | — |
| FIL | Filling | — |
| COV | Coving | — |

### Departments
- Purchase
- Sales
- Store & Logistics
- Account & Finance
- Admin
- Project Coordinator
- Project Manager 1 / 2 / 3

### Warehouses (Dropdown)
1. Wadki w/h
2. Main w/h 1
3. Neelo w/h 2
4. Gurgaon
5. Bangalore
6. Client Site (conditional: show textbox for Client/Site Name)

---

## 3. Phase 1 — Master Data Setup (Foundation)

Build first — all other forms depend on these.

### 3.1 Purchase Item Muster
**Purpose**: Central item repository for all RM, PM, FG, consumables  
**Type**: Form + Report (for AutoFetch lookups)

| # | Field | Type | Mandatory | Notes |
|---|-------|------|-----------|-------|
| 1 | Category of Purchase Item | Dropdown | Yes | 1.RM, 2.Packaging Material, 3.Tools & Consumable, 4.Maintenance & Utility, 5.Capital & Assets, 6.Administration |
| 2 | Purchase Item Code | Text (autogen) | Yes | Auto-generate based on category |
| 3 | Purchase Item Name | Text | Yes | — |
| 4 | UOM | Dropdown | Yes | 1.Nos, 2.Kg, 3.Ltr, 4.Mtr, 5.Kit |
| 5 | HSN Code | Text | Yes | — |
| 6 | GST % | Number | No | — |
| 7 | Min Stock | Number | Yes | — |
| 8 | Max Stock | Number | No | — |
| 9 | Standard Rate | Currency | No | — |
| 10 | Preferred Supplier | Multi-select lookup | No | Lookup from Supplier Master |
| 11 | Lead Time | Number (Days) | No | — |
| 12 | Status | Dropdown | Yes | Active / Inactive |

**AutoFetch target**: PR items, PO items, MR items, GRN items, QC items, FGHM items

### 3.2 System Master
**Purpose**: Define flooring systems (e.g., EP01 for 1mm epoxy)

| # | Field | Type | Mandatory | Notes |
|---|-------|------|-----------|-------|
| 1 | System Code | Text | Yes | e.g., EP01, PU02 |
| 2 | System Name | Text | Yes | e.g., "1mm Epoxy Flooring" |
| 3 | Description | Multi-line | No | — |
| 4 | Status | Dropdown | Yes | Active / Inactive |

**AutoFetch target**: System Composition, Sales/Work Order (system code lookup)

### 3.3 System Composition (1C)
**Purpose**: Which FGs make up each system (System→FG mapping). E.g., EP01 = Floorchem 300 Matt [R] + Floorchem 300 Matt [H]  
**Type**: Form with subform (line items)

**Header:**
| # | Field | Type | Mandatory | Notes |
|---|-------|------|-----------|-------|
| 1 | Composition ID | Autogen | Yes | — |
| 2 | System Code | Lookup | Yes | From System Master |
| 3 | System Name | AutoFetch | Yes | Autofill from System Code |
| 4 | Revision No | Text | No | — |
| 5 | Date | Date | Yes | Today's Date |
| 6 | Status | Dropdown | Yes | Draft / Approved / Released |

**Line items (System → FG mapping):**
| # | Field | Type | Mandatory | Notes |
|---|-------|------|-----------|-------|
| 1 | FG Product Code | Lookup | Yes | From Item Muster (FG items only) |
| 2 | FG Product Name | AutoFetch | Yes | Autofill from FG Code |
| 3 | UOM | AutoFetch | Yes | From Item Muster |
| 4 | Qty per System Unit | Number | Yes | FG qty needed per 1 unit of system |
| 5 | Rate | Currency | Yes | FG unit rate for SO pricing |

**Hierarchy note**: This is the **middle layer** of the 3-layer hierarchy: System (SO) → FG (System Composition) → RM (BOM Formulation). MR works at RM level only.

### 3.4 BOM / FG Formulation (1D)
**Purpose**: Which RMs make up each FG with ratios (FG→RM mapping). E.g., Floorchem 300 Matt [R] = RK Resin 32% + BA 27.3% + Talc 20% + ...  
**Type**: Form with subform (line items)

**Header:**
| # | Field | Type | Mandatory | Notes |
|---|-------|------|-----------|-------|
| 1 | BOM No | Autogen | Yes | — |
| 2 | FG Product Code | Lookup | Yes | From Item Muster (FG items only) |
| 3 | FG Product Name | AutoFetch | Yes | Autofill from FG Code |
| 4 | Revision No | Text | No | — |
| 5 | Date | Date | Yes | Today's Date |
| 6 | Status | Dropdown | Yes | Draft / Approved / Released |

**Line items (FG → RM formulation):**
| # | Field | Type | Mandatory | Notes |
|---|-------|------|-----------|-------|
| 1 | RM Item Code | Lookup | Yes | From Item Muster (RM items only) |
| 2 | RM Item Name | AutoFetch | Yes | Autofill from RM Code |
| 3 | UOM | AutoFetch | Yes | From Item Muster |
| 4 | Qty per 100 Kg FG | Number | Yes | RM consumption per 100 Kg FG batch (e.g., 32 Kg RK Resin) |
| 5 | Ratio % | Formula | Yes | Qty / Σ Qty × 100 (auto-calculated) |
| 6 | Waste % | Number | No | — |
| 7 | Total Qty | Formula | Yes | Qty + Waste% |

**Hierarchy note**: MR requisitions RM only. MR qty = BOM ratio × FG qty × System qty from SO.

### 3.4 Supplier Master
**Purpose**: Vendor management

| # | Field | Type | Mandatory | Notes |
|---|-------|------|-----------|-------|
| 1 | Supplier Code | Autogen | Yes | Auto-generate on new registration |
| 2 | Supplier Name | Text | Yes | — |
| 3 | Supplier Type | Dropdown | No | — |
| 4 | GSTIN | Text | Yes | — |
| 5 | PAN No | Text | Yes | — |
| 6 | Contact Person | Text | Yes | — |
| 7 | Mobile No | Phone | Yes | Alternate number |
| 8 | Email ID | Email | Yes | — |
| 9 | Address | Multi-line | Yes | — |
| 10 | Pincode | Text | No | — |
| 11 | Bank Name | Text | Yes | — |
| 12 | Account No | Text | Yes | — |
| 13 | IFSC Code | Text | Yes | — |
| 14 | Payment Terms | Text | Yes | — |
| 15 | Credit Days | Number | Yes | — |
| 16 | Status | Dropdown | Yes | Active / Inactive |

**AutoFetch target**: PO, Rate Comparison, GRN

### 3.5 Customer/Site Master
**Purpose**: Client organization and contact details

| # | Field | Type | Mandatory | Notes |
|---|-------|------|-----------|-------|
| 1 | Customer Code | Autogen | Yes | — |
| 2 | Client Org Name | Text | Yes | — |
| 3 | Contact Person | Text | Yes | — |
| 4 | Contact No | Phone | Yes | — |
| 5 | Alt Contact No | Phone | Yes | — |
| 6 | Email | Email | Yes | — |
| 7 | GST No | Text | Yes | — |
| 8 | PAN | Text | Yes | — |
| 9 | Regd Address | Multi-line | Yes | — |
| 10 | Billing Address | Multi-line | No | — |
| 11 | Shipping Address | Multi-line | No | — |
| 12 | Site Name | Text | No | — |
| 13 | Site Address | Multi-line | No | — |
| 14 | Site Manager Incharge | Text | No | — |
| 15 | Contact No (Site) | Phone | No | — |
| 16 | Status | Dropdown | Yes | Active / Inactive |

**AutoFetch target**: Sales Order Master, FGHM, Project

### 3.6 Store Master
**Purpose**: RM/FG/QC/Site store definitions

| # | Field | Type | Mandatory | Notes |
|---|-------|------|-----------|-------|
| 1 | Store Code | Autogen | Yes | — |
| 2 | Store Name | Text | Yes | — |
| 3 | Store Type | Dropdown | Yes | RM Store / FG Store / QC Store / Site Store |
| 4 | Location | Text | Yes | — |
| 5 | Status | Dropdown | Yes | Active / Inactive |

**Bin Location** — Rack/Shelf/Bin mapping is a **subform within Store Master**, not a separate form. Each store has N bin locations with Rack No, Shelf No, Bin No, Status.

### 3.8 User Access
**Purpose**: Define approvers, departments, and access levels

| # | Field | Type | Mandatory | Notes |
|---|-------|------|-----------|-------|
| 1 | User Name | User lookup | Yes | Zoho Creator user |
| 2 | Department | Dropdown | Yes | Purchase, Sales, Store & Logistics, Account & Finance, Admin, Project Coordinator, Project Manager 1/2/3 |
| 3 | Role | Dropdown | Yes | Entry / Review / Approve / Admin |
| 4 | Email | Email | AutoFetch | From user profile |
| 5 | Status | Dropdown | Yes | Active / Inactive |

### 3.9 Approval Matrix
**Purpose**: Define PR/PO limits and approvers per department

| # | Field | Type | Mandatory | Notes |
|---|-------|------|-----------|-------|
| 1 | Department | Dropdown | Yes | — |
| 2 | Document Type | Dropdown | Yes | PR / PO / Rate Comparison / GRN / MR |
| 3 | Min Amount | Currency | Yes | — |
| 4 | Max Amount | Currency | Yes | — |
| 5 | Approver 1 | User lookup | Yes | — |
| 6 | Approver 2 | User lookup | No | If amount exceeds level 1 |
| 7 | Approver 3 | User lookup | No | If amount exceeds level 2 |

---

## 4. Phase 2 — Procurement Module (PR → PO → GRN → QC)

### 4.1 Purchase Requisition (PR)
**Department**: Production & R&D

**Header:**
| # | Field | Type | Mandatory | Notes |
|---|-------|------|-----------|-------|
| 1 | PR Number | Autogen | Yes | — |
| 2 | PR Date | Date | Yes | Today's Date (default) |
| 3 | Reference | Text | No | Manual reference |
| 4 | Department | AutoFetch | Yes | As per user login (Production / R&D) |
| 5 | Approved By | User lookup | No | Filled after approval |
| 6 | Status | Dropdown | Yes | Draft / Pending Approval / Approved / Rejected |

**Line items (subform):**
| # | Field | Type | Mandatory | Notes |
|---|-------|------|-----------|-------|
| 1 | Sr | Number | Yes | Auto |
| 2 | Item Code | Lookup | Yes | From Purchase Item Muster (autofill if Item Name filled) |
| 3 | Item Name | AutoFetch | Yes | Autofill if Item Code filled |
| 4 | Qty | Number | Yes | — |
| 5 | Item Description | Multi-line | No | — |
| 6 | UOM | AutoFetch | Yes | From Item Muster |
| 7 | Lead Time | AutoFetch | Days | From Item Muster |

**Automation rules:**
- Item Code ↔ Item Name bidirectional autofill
- UOM autofill from Item Code/Item Name
- Lead Time autofill from Item Muster
- Status: Draft → Pending Approval (on submit) → Approved (after approval)
- Notification to Purchase dept on approval

**Reports:** Pending PR Approval (notification)

### 4.2 Rate Comparison Sheet
**Department**: Purchase

| # | Field | Type | Mandatory | Notes |
|---|-------|------|-----------|-------|
| 1 | Date | Date | Yes | Today's Date |
| 2 | PR Reference No | Lookup | Yes | From PR Master |
| 3 | Product No | AutoFetch | Yes | From PR items |
| 4 | Product Name | AutoFetch | Yes | From PR items |
| 5 | Supplier 1 | Lookup (Supplier) | Yes | + Price + Credit |
| 6 | Supplier 2 | Lookup (Supplier) | No | + Price + Credit |
| 7 | Supplier 3 | Lookup (Supplier) | No | + Price + Credit |
| 8 | Supplier 4 | Lookup (Supplier) | No | + Price + Credit |
| 9 | Supplier 5 | Lookup (Supplier) | No | + Price + Credit |
| 10 | Finalised Supplier | Lookup | Yes | Selected from above 5 |
| 11 | Final Rate | Currency | Yes | — |
| 12 | PO No | Text | No | Linked after PO creation |
| 13 | PO Release Date | Date | No | — |
| 14 | Remark | Multi-line | No | — |

**Automation rules:**
- Supplier dropdown → lookup from Supplier Master
- Each supplier row: dropdown for supplier name, text for price, text for credit
- Notification "Rate Comparison Data Missing" to Purchase dept if data incomplete
- After PO created, PO No field auto-updated

### 4.3 Purchase Order (PO)
**Department**: Purchase

**Header:**
| # | Field | Type | Mandatory | Notes |
|---|-------|------|-----------|-------|
| 1 | RM Type | Dropdown | Yes | 1.Coding, 2.Non Coding |
| 2 | PO Number | Autogen | Yes | **IMPORTANT**: Different series — RM prefix for Non-Coding, RMWAD prefix for Coding materials |
| 3 | PO Date | Date | Yes | Today's Date |
| 4 | Supplier Code | Lookup | Yes | From Supplier Master |
| 5 | Supplier Name | AutoFetch | Yes | Autofill from Supplier Code |
| 6 | PR Reference | Lookup | No | From PR |
| 7 | Bill To | Dropdown | Yes | Address list |
| 8 | Ship To | Dropdown | Yes | Address list |

**Line items (subform):**
| # | Field | Type | Mandatory | Notes |
|---|-------|------|-----------|-------|
| 1 | Sr No | Number | Yes | Auto |
| 2 | Item Code | Lookup | Yes | From Purchase Item Muster |
| 3 | Item Name | AutoFetch | Yes | — |
| 4 | HSN | AutoFetch | Yes | From Item Muster |
| 5 | Quantity | Number | Yes | — |
| 6 | UOM | AutoFetch | Yes | From Item Muster |
| 7 | Rate | Currency | Yes | — |
| 8 | Basic Amount | Formula | Yes | Qty × Rate |
| 9 | GST % | AutoFetch | Yes | From Item Muster |
| 10 | GST Amount | Formula | Yes | Basic × GST% |
| 11 | Total Amount | Formula | Yes | Basic + GST |

**Footer:**
| # | Field | Type | Mandatory | Notes |
|---|-------|------|-----------|-------|
| 12 | Basic Total | Formula | — | Sum of Basic Amount |
| 13 | CGST | Formula | — | Sum of GST/2 |
| 14 | SGST | Formula | — | Sum of GST/2 |
| 15 | IGST | Formula | — | Sum of GST (if inter-state) |
| 16 | Total Amount (Words) | Formula | — | In words |
| 17 | Delivery Date | Date | Yes | — |
| 18 | Payment Terms | Text | Yes | — |
| 19 | Scope of Transport | Dropdown | Yes | Supplier / Own |
| 20 | Mode of Transport | Dropdown | Yes | — |

**Terms & Conditions** (printable PO):
```
Please acknowledge acceptance of this order.
Always quote our Purchase Order No. on all Challans, Bills, Correspondence.
Please supply the following material as per the instructions & specifications given in this order.
Deliveries will be accepted on any working days except national holidays, within working hours only.
Mention batch nos. on your Invoice & attach certificate of analysis along with material safety data sheets, wherever applicable.
Bill will not be accepted without e-way bill. If the material is not approved by our Quality Department as per COA/Test Report, the material will be returned to you. We will charge you the transportation charges for the same.
```

**Item description** requires a sub-textbox within the line items for additional item description.

**Automation rules:**
- PO Number auto-generated based on RM Type (Coding → RMWAD series, Non-Coding → RM series)
- Supplier details AutoFetch on supplier selection
- Price can come from Rate Comparison or manual input
- GST split into CGST/SGST for intra-state, IGST for inter-state (conditional logic)
- Printable PO layout with T&C

### 4.4 Goods Receipt Note (GRN)
**Department**: Purchase / Store

**Header:**
| # | Field | Type | Mandatory | Notes |
|---|-------|------|-----------|-------|
| 1 | GRN Number | Autogen | Yes | Generated **after posting** |
| 2 | GRN Date | Date | Yes | Today's Date |
| 3 | PO Number | Lookup | Yes | From PO Master |
| 4 | Supplier Code | AutoFetch | Yes | From PO |
| 5 | Supplier Name | AutoFetch | Yes | From PO |
| 6 | Vehicle Number | Text | Yes | — |
| 7 | Warehouse | Dropdown | Yes | 1.Wadki, 2.Main, 3.Neelo, 4.Gurgaon, 5.Bangalore, 6.Client Site |
| 8 | Client/Site Name | Text | Conditional | Visible only if Warehouse = Client Site |
| 9 | Invoice Number | Text | Yes | — |
| 10 | Invoice Date | Date | Yes | — |

**Line items (subform) — with checkbox for partial GRN:**
| # | Field | Type | Mandatory | Notes |
|---|-------|------|-----------|-------|
| 1 | ✅ Checkbox | Checkbox | No | For item selection (partial GRN) |
| 2 | Item Code | AutoFetch | Yes | From PO |
| 3 | Item Name | AutoFetch | Yes | From PO |
| 4 | Ordered Qty | AutoFetch | Yes | From PO |
| 5 | Received Qty | Number | Yes | — |
| 6 | QC Status | Dropdown | No | Pending / Pass / Fail |
| 7 | Packing Quality | Dropdown | No | Good / Damaged / Partial |

**Transport subform** (visible if PO Scope of Transport = Own):
| # | Field | Type | Mandatory | Notes |
|---|-------|------|-----------|-------|
| 1 | Transporter Name | Text | Yes | — |
| 2 | Transportation Charges | Currency | Yes | — |
| 3 | Local Transport | Text | Yes | — |
| 4 | Loading/Unloading Charges | Currency | Yes | — |

**Automation rules:**
- GRN Number generated **only after posting** (not on save)
- Quantity added to stock only after posting
- Timestamp logged at posting time
- Checkbox allows partial GRN against one PO
- If Warehouse = Client Site, show textbox
- Transport subform visibility conditional on PO transport scope

**Reports:** PO vs GRN Pending, Open PO Register, Transport Reports

### 4.5 QC/QA (Quality Control)
**Department**: QC

| # | Field | Type | Mandatory | Notes |
|---|-------|------|-----------|-------|
| 1 | QC Number | Autogen | Yes | — |
| 2 | Date | Date | Yes | Today's Date |
| 3 | GRN Number | Lookup | Yes | From GRN |
| 4 | Supplier Name | AutoFetch | Yes | From GRN |

**Line items:**
| # | Field | Type | Mandatory | Notes |
|---|-------|------|-----------|-------|
| 1 | Item No | AutoFetch | Yes | From GRN |
| 2 | Item Name | AutoFetch | Yes | From GRN |
| 3 | Inspection Date | Date | No | — |
| 4 | Viscosity Result | Text | No | — |
| 5 | Density Result | Text | No | — |
| 6 | Color Result | Text | No | — |
| 7 | Moisture Result | Text | No | — |
| 8 | Accepted Qty | Number | Yes | — |
| 9 | Rejected Qty | Number | Yes | — |
| 10 | Packaging Quality | Dropdown | No | Good / Damaged |
| 11 | QC Status | Dropdown | Yes | Pass / Fail / Hold |

| 12 | Remarks | Multi-line | Yes | — |

**Automation rule:** QC items auto-fetched from GRN items

---

## 5. Phase 3 — Inventory / Stores Module

### 5.1 Material Requisition (MR)
**Department**: Production & R&D  
**Role**: MR is the **complete project implementation cost baseline** — four cost components (Material, Application, Transportation, Tools & Tackles) summing to Total MR Cost, which Costing approves. SO is the revenue baseline (System/FG scope). **Project baseline = SO + MR.** MR is NOT just RM allocation.

**MR Status Workflow (Critical Gate):**
```
Draft → Production Verified → Costing Approved → Released
  │         │                       │                │
  │    Production checks MR     Costing approves    ⛔ Gate
  │    qty vs SO system req     TOTAL project cost  passed →
  │    (via BOM × SO qty)                            MIS can proceed
  ▼         ▼                       ▼                ▼
Initial   Verified by             Approved by     Released —
            Production              Costing        downstream
                                                    actions allowed
```

**Header:**
| # | Field | Type | Mandatory | Notes |
|---|-------|------|-----------|-------|
| 1 | MR Number | Autogen | Yes | — |
| 2 | MR Date | Date | Yes | Today's Date |
| 3 | Requisition Type | Dropdown | Yes | Options TBD (e.g., Production / R&D) |
| 4 | Batch Number | Text | No | — |
| 5 | Department | AutoFetch | Yes | As per user login |
| 6 | Requested By | Text | Yes | Employee Name |
| 7 | Priority | Dropdown | Yes | Low / Medium / High / Urgent |
| 8 | **MR Status** | **Dropdown** | **Yes** | **Draft / Production Verified / Costing Approved / Released** |

**Line items:**
| # | Field | Type | Mandatory | Notes |
|---|-------|------|-----------|-------|
| 1 | Sr No | Number | Yes | Auto |
| 2 | Item Code | Lookup | Yes | From Purchase Item Muster |
| 3 | Item Name | AutoFetch | Yes | — |
| 4 | Category | AutoFetch | Yes | From Item Muster |
| 5 | UOM | AutoFetch | Yes | From Item Muster |
| 6 | Available Stock | AutoFetch | Yes | From inventory (real-time) |
| 7 | Required Qty | Number | Yes | — |
| 8 | Remarks | Multi-line | No | — |

**MR = Complete Project Implementation Cost Baseline (four cost components):**

MR is NOT just RM allocation. It carries four cost components that sum to the **Total MR Cost** — the project implementation cost baseline that **Costing approves**:

1. **Material Cost** — from the per-project Material Allocation subform below (Σ Assigned Qty × Rate)
2. **Application Cost** — labour/execution cost to apply material on site (Activity, UOM, Qty/Area, Rate, Amount)
3. **Transportation Cost** — transport of material to site (From, To, Vehicle/Trips, Rate, Amount)
4. **Tools & Tackles** — tools/equipment needed (Item, Qty, Rate, Amount)

**Total MR Cost = Material Cost + Application Cost + Transportation Cost + Tools & Tackles.**

**Material Allocation subform (feeds Material Cost):**
Each MR line allocates RM to the Project. This subform is the **Material Cost component** of the cost baseline — every consumption entry (BMR/RM Consumption or Site Manager) resolves here by `Project ID + Item Code`.

| # | Field | Type | Mandatory | Notes |
|---|-------|------|-----------|-------|
| 1 | Item Code | Lookup | * | From Purchase Item Muster (RM) — auto-populated from MR line items |
| 2 | Item Name | AutoFetch | * | — |
| 3 | UOM | AutoFetch | * | From Item Muster |
| 4 | Assigned Qty | Number | * | Allocation baseline for this Project. Defaults from Required Qty |
| 5 | Rate | Currency | * | Per-unit RM rate |
| 6 | Material Cost | Formula | * | = Assigned Qty × Rate |
| 7 | Allocation Ratio % | Formula | * | = `Assigned Qty ÷ Σ All Assigned Qty × 100` — share of total project RM |
| 8 | 80% Threshold Alert Flag | Checkbox | | Default ON — fires alert when consumption reaches 80% of Assigned Qty |
| 9 | Consumed Qty | Number (auto) | | Running total; incremented by FG production (BMR/RM Consumption) + Site Manager entries |
| 10 | Consumption % | Formula | | = `Consumed Qty ÷ Assigned Qty × 100` |
| 11 | Alert Triggered | Checkbox (readonly) | | Auto-set TRUE once Consumption % ≥ 80% |

**Application Cost subform (labour/execution on site):**
| # | Field | Type | Mandatory | Notes |
|---|-------|------|-----------|-------|
| 1 | Activity | Text | | e.g., surface prep, laying, finishing |
| 2 | UOM | Dropdown | | — |
| 3 | Qty / Area | Number | | — |
| 4 | Rate | Currency | | Per unit |
| 5 | Amount | Formula | | = Qty/Area × Rate |

**Transportation Cost subform (material to site):**
| # | Field | Type | Mandatory | Notes |
|---|-------|------|-----------|-------|
| 1 | From | Text/Lookup | | Source (warehouse) |
| 2 | To | Text/Lookup | | Destination (site) |
| 3 | Vehicle / Trips | Text / Number | | — |
| 4 | Rate | Currency | | Per trip |
| 5 | Amount | Formula | | = Trips × Rate |

**Tools & Tackles subform (equipment needed):**
| # | Field | Type | Mandatory | Notes |
|---|-------|------|-----------|-------|
| 1 | Item | Text/Lookup | | From Item Muster |
| 2 | Qty | Number | | — |
| 3 | Rate | Currency | | Per unit |
| 4 | Amount | Formula | | = Qty × Rate |

**Automation rules:**
- Item lookup with autofetch of name, category, UOM, available stock
- Priority dropdown for urgency classification
- **MR Status workflow:** Draft (on create) → Production Verified (after Production checks qty vs SO system req via BOM) → Costing Approved (after Costing approves the TOTAL project cost — all four components) → Released (MR actionable)
- **Without Released MR, there is no MIS, no Production, no Logistics, no project execution**
- **Every consumption entry** (BMR/RM Consumption or Site Manager) increments `Consumed Qty` on the matching MR Allocation line matched by `Project ID + Item Code` — never a generic pool
- Site Manager entries made against SO System/FG are expanded into RMs at BOM ratios before incrementing Consumed Qty
- **80% Alert:** When `Consumption % ≥ 80%` and `80% Threshold Alert Flag` is ON → pop-up + dashboard banner + email to Project Manager

### 5.2 Material Issue Slip (MIS)
**Department**: Stores

| # | Field | Type | Mandatory | Notes |
|---|-------|------|-----------|-------|
| 1 | MR No | Lookup | Yes | From MR |
| 2 | MIS Number | Autogen | Yes | Auto-generated against MR |
| 3 | Date | Date | Yes | Today's Date |
| 4 | Batch Number | Text | No | — |

**Line items (auto-fetched from MR):**
| # | Field | Type | Mandatory | Notes |
|---|-------|------|-----------|-------|
| 1 | Item No | AutoFetch | Yes | From MR |
| 2 | Item Name | AutoFetch | Yes | From MR |
| 3 | Category | AutoFetch | Yes | From MR |
| 4 | Required Qty | AutoFetch | Yes | From MR |
| 5 | Issued Qty | Number | Yes | — |
| 6 | Balance Qty | Formula | No | Required - Issued (if shortage) |

| 7 | Issued By | Text | Yes | Supervisor Name |
| 8 | Handover To | Text | Yes | Supervisor Name |
| 9 | Remark | Multi-line | No | — |

**Automation rules:**
- Items auto-fetched from MR
- Balance Qty automatically calculated
- Stock reduced in inventory upon MIS posting

### 5.3 Material Return, Material Handover, Vehicle & Transport
Additional store forms listed in Screens.csv but without field-level detail in CSVs. Implement as:

#### Material Return Screen
- Return from production/stores
- Reference to MIS
- Returned Qty, Reason, Condition

#### Material Handover
- Inter-store transfer
- From Store, To Store
- Items with quantities
- Handover notes

#### Vehicle & Transport
- Vehicle registration
- Trip details
- Delivery challans
- Cost tracking

### 5.4 Finish Goods Handover Master (FGHM)
**Department**: Production

| # | Field | Type | Mandatory | Notes |
|---|-------|------|-----------|-------|
| 1 | FGH No | Autogen | Yes | — |
| 2 | Project ID | Lookup | * | From Project Master — links FG handover back to project RM consumption |
| 3 | Handover Date | Date | Yes | Today's Date |
| 4 | Client/Site Name | Lookup | Yes | From Customer/Site Master |
| 5 | Batch No | Text | Yes | Can be multiple batch numbers |

**Line items:**
| # | Field | Type | Mandatory | Notes |
|---|-------|------|-----------|-------|
| 1 | Sr No | Number | Yes | Auto |
| 2 | FG Product Code | Lookup | Yes | From Purchase Item Muster (FG items) |
| 3 | FG Product Name | AutoFetch | Yes | — |
| 4 | FG QTY | Number | Yes | — |
| 5 | UOM | AutoFetch | Yes | — |
| 6 | QC Status | Dropdown | Yes | Pass / Fail / Hold |

| 7 | Handed Over By | Text | Yes | Employee Name |
| 8 | Received By | Text | Yes | Employee Name |
| 9 | Remark | Multi-line | Yes | — |

**Automation:** After submission → Pop-up notification to Store/Logistics

### 5.5 FGHM Inline Acceptance

FGAN is eliminated. Acceptance is now inline within FGHM — damaged qty, accepted qty captured directly in FGHM line items. FG Stock updated on FGHM submission.

---

## 6. Phase 4 — Production Module

### 6.1 Production Planning
**Department**: Production

| # | Field | Type | Mandatory | Notes |
|---|-------|------|-----------|-------|
| 1 | Planning No | Text | Yes | MR Sheet No reference |
| 2 | Planning Date | Date | Yes | — |
| 3 | Planning Period | Dropdown | Yes | Week / Month |
| 4 | Plant | Dropdown | Yes | — |
| 5 | Planner Name | User lookup | Yes | — |
| 6 | Status | Dropdown | Yes | Draft / Approved / Released |
| 7 | Remarks | Multi-line | No | — |
| 8 | Total SO/WO Qty | AutoFetch | Yes | From MR Sheet |
| 9 | FG Stock Available | AutoFetch | Yes | From current FG stock |
| 10 | Net Production Requirement | Formula | Yes | SO/WO Qty - Available FG Stock |

### 6.2 Production Order

Fields needed (from Screens.csv):
- Production Order No (autogen)
- MR/Planning reference
- System Code
- Planned Qty
- Start Date, End Date
- Status (Planned / In Progress / Completed / On Hold)

### 6.3 Batch Manufacturing Record (BMR)

| # | Field | Notes |
|---|-------|-------|
| 1 | BMR No | Autogen |
| 2 | Production Order Ref | Lookup |
| 3 | Batch No | Text |
| 4 | Date | Date |
| 5 | System Code | Lookup |
| 6 | Raw Materials | Subform (Item Code, Qty, Batch No, Consumption) |
| 7 | Process Parameters | Subform (Step, Time, Temp, Operator) |
| 8 | Yield / Output | Number |
| 9 | QC Test Results | Subform |
| 10 | Status | Dropdown |

### 6.4 RM Consumption Entry
- Reference to BMR
- Item-wise consumption tracking
- Actual vs Standard comparison

### 6.5 Packing Entry
- FG product packing
- Packing material consumption
- Packed quantity, batch numbers
- Label/printing details

### 6.6 Rework Register
- Rework reason
- BMR reference
- Rework quantity
- Material consumed for rework
- QC revalidation status

---

## 7. Phase 5 — Project Management Module

### 7.1 Create Project

| # | Field | Type | Mandatory | Notes |
|---|-------|------|-----------|-------|
| 1 | Project ID | Autogen | Yes | — |
| 2 | Project Name | Text | Yes | — |
| 3 | Address | Multi-line | Yes | — |
| 4 | Project Manager | User lookup | Yes | — |
| 5 | Execution Base | Dropdown | Yes | 1.Area Basis, 2.Day Basis |
| 6 | Start Date | Date | Yes | — |
| 7 | End Date | Date | Yes | — |
| 8 | Project Cost | Currency | Yes | — |

**Systems subform:**
| # | Field | Type | Notes |
|---|-------|------|-------|
| 1 | System Code | Lookup | From System Master |
| 2 | Area | Number | — |
| 3 | UOM | Dropdown | — |
| 4 | Description | Text | — |

| 9 | Adjustments | Currency | No | Cost adjustment |

### 7.2 Task Budget

Single table with Category dropdown — no separate sections or conditional visibility rules.

**Budget columns:**
| # | Field | Type | Notes |
|---|-------|------|-------|
| 1 | Category | Dropdown | Transport / Execution / Manpower / Tools / Overhead |
| 2 | Description | Text | Subtask or work item name |
| 3 | Qty / Area | Number | Area for Execution, count for others |
| 4 | Rate | Currency | Per unit |
| 5 | Amount | Formula | Qty × Rate |
| 6 | Manpower | Number | Head count (if applicable) |

**Actual columns (added for P&amp;L):**
| # | Field | Type | Notes |
|---|-------|------|-------|
| 7 | Actual Qty | Number | Actual quantity consumed / work done |
| 8 | Actual Rate | Currency | Actual per-unit rate paid |
| 9 | Actual Amount | Formula | Actual Qty × Actual Rate |

- Execution Base = Day Basis → Show Manpower tasks
- Transportation, Tools, Additional Expenses always shown
- Actual columns feed Project P&amp;L cost calculation

### 7.3 Project Reports
- Project Report (overall)
- Monthly Report
- Annual Report
- Sitewise Costing Report
- Manpower Report
- Machinery Report
- Tools Report
- Issues Report
- Project Margin Report
- Material Consumption vs Work Completion
- Manpower vs Work Completion
- Transportation Report
- Loading/Unloading Report
- Consumable Report
- Task Report

---

## 8. Phase 6 — Sales Module

### 8.1 Sales/Work Order Master (SO)

**Dual mode** — controlled by a `Sales Type` header dropdown:
- **Supply+Apply**: Subform A — System Lines (sells a SYSTEM) → auto-creates Project (Stream B root).
- **Supply Only**: Subform B — FG Lines (sells FG directly) → NO Project (direct stock sale).

#### Fields

| # | Field | Type | Mandatory | Notes |
|---|-------|------|-----------|-------|
| 1 | Sales Type | Dropdown | * | Supply+Apply / Supply Only — controlling field; determines subform shown & Project creation |
| 2 | Date | Date | Yes | Today's Date |
| 3 | Employee Name | Text | Yes | — |
| 4 | Customer Code | Lookup | No | From Customer Master |
| 5 | Client Org Name | Text | Yes | — |
| 6 | Contact Person | Text | Yes | — |
| 7 | Contact No | Phone | Yes | — |
| 8 | Alt Contact No | Phone | Yes | — |
| 9 | Email | Email | Yes | — |
| 10 | GST No | Text | Yes | — |
| 11 | PAN | Text | Yes | — |
| 12 | Regd Address | Multi-line | Yes | — |
| 13 | Sales/Work Order No | Autogen | Yes | — |
| 14 | Sales/Work Order Date | Date | Yes | — |
| 15 | Site Name | Text | Yes | — |
| 16 | Site Address | Multi-line | Yes | — |
| 17 | Site Manager/Incharge | Text | No | — |
| 18 | Contact No (Site) | Phone | No | — |
| 19 | Project Type | Dropdown | Yes | 1.Industrial, 2.Commercial |
| 20 | Total Work Order Amount | Formula | | Sum of all line Amounts (auto-calculated) |
| 21 | Payment Terms | Text | | — |
| 22 | Transportation Scope | Dropdown | Yes | — |
| 23 | Transportation Amount | Currency | | — |
| 24 | Lead Time | Number (Days) | | — |
| 25 | PO/BOQ Attachment | File upload (Multiple) | | — |
| 26 | Warranty | Text | | — |
| 27 | Is proper System Required | Checkbox | | — |
| 28 | Remark | Multi-line | | — |
| 29 | Commission | Checkbox | | If checked → Based On (Dropdown: 1.Percentage, 2.Fix Amount) + Amount |

**Subform A — System Lines** (visible when Sales Type = Supply+Apply):
| # | Field | Type | Notes |
|---|-------|------|-------|
| 1 | System Code | Lookup | From System Master (autofetch) |
| 2 | System Name | AutoFetch | — |
| 3 | Thickness | Text | — |
| 4 | Area | Number | — |
| 5 | UOM | Dropdown | Conditional |
| 6 | Rate | Currency | — |
| 7 | Amount | Formula | Area × Rate |

**Subform B — FG Lines** (visible when Sales Type = Supply Only):
| # | Field | Type | Notes |
|---|-------|------|-------|
| 1 | FG Code | Lookup | From Purchase Item Muster (FG items) |
| 2 | FG Name | AutoFetch | — |
| 3 | Qty | Number | — |
| 4 | UOM | AutoFetch | — |
| 5 | Rate | Currency | — |
| 6 | Amount | Formula | Qty × Rate |

#### Automation
- **Sales Type controlling dropdown**: Selecting "Supply+Apply" shows Subform A (System Lines); "Supply Only" shows Subform B (FG Lines) — conditional visibility
- **Subform A fields** (Supply+Apply): System Code, System Name, Thickness, Area, UOM, Rate, Amount (Area × Rate formula)
- **Subform B fields** (Supply Only): FG Code, FG Name, Qty, UOM, Rate, Amount
- **Auto-create Project**: On SO Acceptance (Supply+Apply mode only) → create Project record with Project ID, systems subtab, SO reference
- **Autofetch**: Customer Code → Customer Name, GST, PAN, Address; System Code → System Name; FG Code → FG Name, UOM
- **Amount formula**: Area × Rate (System Lines) or Qty × Rate (FG Lines)
- **Total Work Order Amount**: Sum of all line Amounts
- **Commission logic**: If Commission checkbox ON → show conditional dropdown (Percentage / Fixed Amount) + Amount field
- **Warranty, Transport, Lead Time**: Captured as text/number fields per line

---

## 9. Phase 7 — Service Team Module

### 9.1 Service Entry
**Department**: Service Team

| # | Field | Type | Mandatory | Notes |
|---|-------|------|-----------|-------|
| 1 | Service No | Autogen | Yes | — |
| 2 | Project ID | Lookup | Yes | From Project Master |
| 3 | Area Allocation | Text | Yes | Site area assigned |
| 4 | Work Execution | Multi-line | Yes | Work performed details |
| 5 | Start Date | Date | Yes | — |
| 6 | End Date | Date | Yes | — |
| 7 | Status | Dropdown | Yes | In Progress / Completed / Invoiced |

**Automation**: Service Invoice auto-generated on completion.

### 9.2 Service Invoice
- Auto-generated from completed service work orders
- Links back to Project for P&L calculation

---

## 10. Phase 8 — Costing Module

### 10.1 Costing Approval
**Department**: Project Manager / Coordinator

| # | Field | Type | Mandatory | Notes |
|---|-------|------|-----------|-------|
| 1 | Costing No | Autogen | Yes | — |
| 2 | Project ID | Lookup | Yes | From Project Master |
| 3 | Estimated Cost | Currency | Yes | Budgeted cost |
| 4 | Approved Cost | Currency | No | After approval |
| 5 | Status | Dropdown | Yes | Draft / Pending Approval / Approved / Rejected |

### 10.2 Cost Reports
- Variance analysis: Estimated vs Actual costs
- Budget vs Actual comparison
- Filterable by Project

---

## 11. Phase 9 — Logistics Module

### 11.1 Delivery Challan (DC)
**Department**: Logistics

| # | Field | Type | Mandatory | Notes |
|---|-------|------|-----------|-------|
| 1 | DC No | Autogen | Yes | — |
| 2 | Project ID | Lookup | Yes | From Project Master |
| 3 | Vehicle No | Text | Yes | — |
| 4 | Driver Name | Text | Yes | — |
| 5 | Driver Contact | Phone | Yes | — |
| 6 | Dispatch Date | Date | Yes | — |
| 7 | Delivery Status | Dropdown | Yes | In Transit / Delivered / Partial |

**Line items:**
- Item Code, Item Name, Qty, UOM

### 11.2 Logistics Reports
- Dispatch tracking
- Delivery performance
- Transport cost analysis
- Vehicle utilization

### 11.3 Material Handover (Inter-Store)
- From Store, To Store
- Items with quantities
- Transfer notes

---

## 12. Phase 10 — Departmental Dashboards & Reports

### 9.1 Purchase Dept Dashboard

| Widget | For Entry | For Search | For Changes | Reports |
|--------|-----------|------------|-------------|---------|
| Total Purchase This Month | Purchase Item Master | Purchase Item Master | Purchase Item Master | Purchase Item Master |
| Open PO's | Supplier Master | Supplier Master | Supplier Master | Supplier Master |
| Pending PR Approvals | PO | PR | GRN | PR |
| Overdue Deliveries | PO Amendment | PO | Rate Comparison | PO |
| Transport Overview | GRN | GRN | — | PO Amendment |
| — | Rate Comparison | Payment Overdue | — | GRN |
| — | — | Rate Comparison | — | Open PO Register |
| — | — | Transport Data | — | PO vs GRN Pending |
| — | — | — | — | Vendor Performance |
| — | — | — | — | Purchase by Item Group |
| — | — | — | — | Price Comparison Report |
| — | — | — | — | Transportation Reports |

**Notification widgets:**
- Pending PR Approval
- PO Awaiting Release
- Pending GRN's
- Overdue Delivery Follow-up
- Overdue Supplier Payment
- Rate Comparison Data Missing

### 9.2 Store Dept Dashboard

| Widget | For Entry | For Search | For Changes | Reports |
|--------|-----------|------------|-------------|---------|
| Inventory Dashboard | Purchase Item Muster | Purchase Item Muster | Purchase Item Muster | Purchase Item Muster |
| Dispatch Planning | Supplier Master | Supplier Master | Supplier Master | Supplier Master |
| — | PO | PO | PO | PO |
| — | PO Amendment | PO Amendment | Rate Comparison | PO Amendment |
| — | GRN | GRN | GRN | GRN |
| — | Rate Comparison | Rate Comparison | Material Issue Screen | Rate Comparison |
| — | Material Issue Screen | Material Issue Screen | Material Return Screen | Material Issue Screen |
| — | Material Return Screen | Material Return Screen | Material Handover | Material Return Screen |
| — | Store Master | Store Master | FG Receiving | Store Master |
| — | Material Handover | Material Handover | Vehicle & Transport | Material Handover |
| — | FG Receiving | FG Receiving | — | FG Receiving |
| — | Vehicle & Transport | Vehicle & Transport | — | Vehicle & Transport |

**Notification widgets:**
- MR Sheet from Costing
- Pending Material Req.
- Pending FG Receiving

### 9.3 Production Dept Dashboard

| Widget | For Entry | For Search | For Changes | Reports |
|--------|-----------|------------|-------------|---------|
| Today's Production | Production Planning | Production Planning | Production Planning | Daily Production Report |
| Open Production Orders | Production Order | Production Order | Production Order | Batch Manufacturing Report |
| Planned Batches | BOM Formulation | BOM Formulation | BOM Formulation | Production Order Status Report |
| Material Consumption | Batch Manufacturing Record | Batch Manufacturing Record | Batch Manufacturing Record | Material Consumption Report |
| RM Stock | Material Requisition | Material Requisition | Material Requisition | BOM vs Actual Consumption Report |
| Completed Batches | RM Consumption Entry | RM Consumption Entry | RM Consumption Entry | Production Loss Report |
| Production Efficiency | Packing Entry | Packing Entry | Packing Entry | FG Handover Report |
| Pending Order | FG Handover Note | FG Handover Note | FG Handover Note | Packing Report |
| Pending FG Handover | Rework Register | Rework Register | Rework Register | Machine Utilization Report |

### 9.4 Project Management Dashboard

| Widget | Reports |
|--------|---------|
| Open Projects | Project Report |
| Active PO's | Monthly Report |
| Running Status | Annual Report |
| Project P&amp;L | Sitewise Costing Report |
| Issues | Manpower Report |
| Execution Target vs Achievement | Machinery Report |
| Manpower Cost Monthly | Tools Report |
| Transportation Monthly | Issues Report |
| Loading/Unloading Charges | Project P&amp;L Report |
| | Material Consumption vs Work Completion |
| | Manpower vs Work Completion |
| | Transportation Report |
| | Loading/Unloading Report |
| | Consumable Report |
| | Task Report |

### 9.5 Project P&amp;L Report (New)

Computed at Project level — no data entry required. All figures derived from transactional forms.

| Line | Component | Data Source | Formula |
|------|-----------|-------------|---------|
| Revenue | Work Order Amount | SO System subtable | Σ (Area × Rate) per system line |
| Revenue | Transportation billed | SO header | Transportation Amount field |
| Cost | Raw Materials | PO × GRN | Σ (GRN Received Qty × PO Rate) for RM items |
| Cost | Packing Materials | PO × GRN | Σ (GRN Received Qty × PO Rate) for packing items |
| Cost | Execution (labour) | Task Budget Actuals | SUM Actual Amount (Category=Execution) |
| Cost | Manpower | Task Budget Actuals | SUM Actual Amount (Category=Manpower) |
| Cost | Transport | Task Budget Actuals + GRN Transport | SUM Actual Amount (Category=Transport) + Σ GRN Transport Charges |
| Cost | Tools | Task Budget Actuals | SUM Actual Amount (Category=Tools) |
| Cost | Overhead | Task Budget Actuals | SUM Actual Amount (Category=Overhead) |
| Cost | Loading/Unloading | GRN Transport subform | Σ Loading/Unloading Charges |
| Cost | RM Consumption (actual) | RM Consumption Entry | Σ (Actual Qty × Item Rate from PIM) |
| Cost | Packing Material (actual) | Packing Entry subform | Σ packing item costs |
| Cost | Rework | Rework Register Material subform | Σ rework material costs |
| **Summary** | **Total Revenue** | — | SO Work Order + SO Transportation |
| | **Total Cost** | — | Material + Execution + Manpower + Logistics + Production |
| | **Gross Margin** | — | Total Revenue − Total Cost |
| | **Margin %** | — | (Gross Margin / Total Revenue) × 100 |

**Automation:**
- Auto-calculated on Project Close (snapshot stored)
- Real-time view from Project dashboard anytime
- Data completeness check before calculation
- Margin threshold alert if < 15%
- Exportable as PDF with company logo and signatures

---

## 13. Phase 11 — Automation & Business Rules

### 13.1 Sequential Procurement Flow
```
PR (Created by Production/R&D)
  → Approval (as per Approval Matrix)
    → Rate Comparison (Purchase dept)
      → PO (Purchase dept)
        → GRN (Store dept on goods arrival)
          → QC/QA (QC dept)
            → Stock Updated (after GRN posting)
```

### 13.2 Material Issue Flow (MR-Gated)
```
MR (Created by Production/R&D) 
  → MR Status = Draft
    → Production Verifies (checks MR qty vs SO system requirements via BOM)
      → MR Status = Production Verified
        → Costing Approves (validates material budget)
          → MR Status = Costing Approved → Released
            → ⛔ Gate passed: MIS can now proceed
              → MIS (Store dept issues material)
                → Stock Updated
```
**Critical rule:** Without a **Released MR**, there is no MIS, no Production, no Logistics, no project execution.

### 13.3 FG Flow (Post-MR Release)
```
[MR Released] → MIS (Stock issued to Production)
  → Production Planning → BMR → Packing
    → FGHM (Production hands over FG, inline acceptance)
      → Notification to Store/Logistics
        → FG Stock Updated
          → Logistics (DC → Outward)
            → Project Site Execution (Service Team)
```

### 13.4 Notification Triggers

| Trigger Event | Notification To | Type |
|---------------|-----------------|------|
| PR Submitted | Purchase dept (Pending Approval) | In-app |
| PR Approved | Production/R&D user | In-app |
| Rate Comparison Data Missing | Purchase dept | In-app alert |
| PO Ready for Release | Purchase dept | In-app |
| GRN Overdue | Purchase + Store dept | In-app |
| **MR Submitted (Draft → Pending Verification)** | **Production dept** | **In-app** |
| **MR Production Verified (→ Pending Costing Approval)** | **Costing dept** | **In-app** |
| **MR Released** | **Store + Production + Logistics** | **In-app + Email** |
| FGHM Submitted | Store & Logistics dept | Pop-up |

### 13.5 Autofetch Rules Summary

| Source Field | Target Form | Target Field |
|-------------|-------------|--------------|
| Item Code | PR, PO, MR, MIS, GRN, FGHM, BOM, QC | Item Name, UOM, Category, HSN, GST%, Lead Time |
| Supplier Code | PO, GRN, Rate Comparison | Supplier Name, GSTIN, Address, Contact |
| PR No | Rate Comparison, PO | Items, Product Details |
| PO No | GRN | Supplier, Items, Ordered Qty |
| GRN No | QC | Supplier, Items |
| MR No | MIS | Items, Required Qty |
| System Code | Sales Order, BOM, Project | System Name |
| User Login | PR, MR | Department |

### 13.6 Numbering Series

| Document | Series |
|----------|--------|
| PR | Auto (PR-YYYY-XXXX) |
| PO (Non-Coding) | RM-YYYY-XXXX |
| PO (Coding) | RMWAD-YYYY-XXXX |
| GRN | Auto (GRN-YYYY-XXXX) |
| MR | Auto (MR-YYYY-XXXX) |
| MIS | Auto against MR |
| FGH | Auto (FGH-YYYY-XXXX) |
| QC | Auto (QC-YYYY-XXXX) |

### 13.7 Stock Management Rules
- **GRN posting**: Qty added to stock only after posting; posting timestamp logged in backend
- **MIS posting**: Qty deducted from stock
- **FGHM inline acceptance**: FG qty added to stock on FGHM submission
- **Material Return**: Qty added back to stock
- **Min/Max stock**: Alert when stock level crosses thresholds (from Item Muster)

### 13.8 Consumption → Project-Assigned RM Rules (New)
- **Resolution rule**: Every consumption entry — whether from **FG production (BMR / RM Consumption)** or a **Site Manager consumption entry** — resolves to the **project-assigned RM** recorded in the MR Material Allocation (matched by `Project ID + Item Code`)
- **No generic pool deduction**: Project-tagged consumption never deducts from a generic stock pool
- **Site Manager expansion rule**: A Site Manager entry made against the SO System/FG is expanded into its constituent RMs at BOM ratios (via System Composition → BOM), then each RM's `Consumed Qty` on the matching MR Allocation line is incremented by `entry_qty × ratio`
- **FG Handover linkage**: FGHM submission updates FG stock AND the Project ID field links the handover back to the project's RM consumption tracking

### 13.9 80% Consumption Alert (New)
- **Trigger condition**: When any allocated RM reaches **80% of its Assigned Qty** (i.e., `Consumption % ≥ 80%`) AND the `80% Threshold Alert Flag` is ON
- **Three notification channels**:
  - **Pop-up** to user saving the consumption entry that triggered the threshold
  - **Dashboard banner** on Project dashboard showing which RM(s) have breached 80%
  - **Email** to Project Manager + Coordinator with RM details, current Consumption %, and remaining buffer
- **Escalation at 100%**: When `Consumption % ≥ 100%`, the label changes to **"Allocation Exhausted"** and a second alert fires to Project Manager + Purchase dept for re-stock planning
- **Reporting**: Project Material Allocation & 80% Utilization Report shows per-RM Assigned vs Consumed vs Alert status

### 13.10 P&amp;L Calculation Rules (New)
- **On Project Close**: P&amp;L auto-calculated from all linked forms; snapshot stored
- **Real-time view**: Live P&amp;L accessible from Project dashboard at any time
- **Data completeness check**: Before calculation, verify all GRNs posted, all Task Budget Actuals filled, all BMRs closed
- **Margin threshold alert**: If Gross Margin < 15%, notify Account & Finance + Project Manager
- **P&amp;L snapshot**: On project close, frozen P&amp;L record created (no further changes)
- **Export**: P&amp;L report exportable as PDF with company logo, project details, signatures
- **Project margin calculation**: Total Revenue − (Material Cost + Execution + Manpower + Transport + Tools + Overhead + Production Cost)

---

## 14. Phase 12 — User Roles & Permissions

### Role Definitions

| Role | Access Scope |
|------|-------------|
| Admin | Full access — all forms, reports, settings, user management |
| Purchase - Entry | Create/Edit: PR, PO, Rate Comparison, GRN. View: Reports |
| Purchase - Review | View only: all purchase forms + reports |
| Purchase - Approve | Approve: PR, PO within limits (Approval Matrix) |
| Store - Entry | Create/Edit: GRN, MIS, Material Return, FG Receiving, Vehicle & Transport |
| Store - Review | View: Inventory stock, GRN, PO, Reports |
| Production - Entry | Create/Edit: MR (Draft), BMR, Production Planning, RM Consumption, Packing, FGH |
| Production - Verify MR | Verify MR: checks MR qty vs SO system req (via BOM). Sets MR Status = Production Verified |
| Production - Review | View: BOM, Stock, Production Reports |
| Costing - Approve MR | Approve MR: validates material budget. Sets MR Status = Costing Approved → Released |
| Sales - Entry | Create/Edit: Sales/Work Order, Customer Master |
| Sales - Review | View: SO reports, project status |
| QC - Entry | Create/Edit: QC/QA forms |
| QC - Review | View: GRN, Item Muster, BOM |
| Project Manager | Create/Edit: Projects, Tasks. View: Stock, PO status |
| Account & Finance | View: PO, GRN, Payment terms, Supplier reports |
| Project Coordinator | Create/Edit: MR, view Production and Project status |

### Permission by Form

| Form | Create/Edit | View Only | No Access |
|------|-------------|-----------|-----------|
| Purchase Item Muster | Admin, Purchase-Entry | All depts | — |
| Supplier Master | Admin, Purchase-Entry | Purchase, Finance | Others |
| Customer Master | Admin, Sales-Entry | Sales, Projects, Finance | Others |
| System Composition | Admin, Production-Entry | Production, QC, Costing | Others |
| BOM Formulation | Admin, Production-Entry | Production, QC, Costing | Others |
| PR | Production, R&D | Purchase (review) | Others |
| Rate Comparison | Purchase-Entry | Purchase (review) | Others |
| PO | Purchase-Entry | Purchase, Finance, Store | Others |
| GRN | Purchase-Entry, Store-Entry | Purchase, Store | Others |
| QC/QA | QC-Entry | Purchase, Production | Others |
| MR (Create Draft) | Production, R&D | Store | Others |
| MR (Verify) | Production - Verify MR | Production, Store | Others |
| MR (Costing Approve) | Costing - Approve MR | Production, Store, Finance | Others |
| MIS | Store-Entry | Store, Production | Others |
| FGHM | Production-Entry, Store-Entry | Store, Logistics, Production | Others |
| Project | Project Manager, Coordinator | All (view) | — |
| Tasks | Project Manager | All (view) | — |
| Sales/Work Order | Sales-Entry | Sales, Projects, Finance | Others |
| Production Planning | Production-Entry | Production, Store | Others |

---

## 15. Implementation Phases — Suggested Timeline

### Phase 1: Foundation (Week 1-2)
- Setup Zoho Creator account and workspace
- Create Master Data forms: Item Muster, System Master, Supplier Master, Customer Master
- Create Store Master (with Bin Location as inline subform)
- Create User Access and Approval Matrix
- Configure lookup relationships

### Phase 2: Procurement (Week 3-4)
- Build PR form with item autofetch logic
- Build Rate Comparison with supplier comparison
- Build PO with dual numbering series (RM/RMWAD)
- Build GRN with partial GRN checkbox and transport subform
- Build QC/QA form linked to GRN
- Configure PR→PO→GRN workflow automation

### Phase 3: Inventory & Stores (Week 5-6)
- Build MR with stock availability lookup
- Add **MR Status field**: Draft / Production Verified / Costing Approved / Released
- Add **Production Verify** action: checks MR quantities against SO system requirements (via BOM)
- Add **Costing Approve** action: validates material budget against project allocation
- Add **MR Release** gate: only Released MR triggers MIS eligibility
- Build MIS linked to MR with balance tracking (only creatable after MR Released)
- Build notifications: MR Submitted, MR Verified, MR Released
- Build FGHM with pop-up notification and inline acceptance
- Build Material Return, Material Handover, Vehicle & Transport

### Phase 4: Production (Week 7)
- Build Production Planning form
- Build BMR, RM Consumption, Packing Entry, Rework Register
- Link to Production Order flow

### Phase 5: Costing (Week 7-8)
- Build Costing Approval form with Project lookup
- Configure approval workflow for cost estimation
- Build cost variance reports
- Link to Project P&L calculation

### Phase 6: Project Management (Week 8-9)
- Build Project form with execution base (Area/Day)
- Build 5 task categories with conditional visibility
- Link SO to Projects
- Build all project reports

### Phase 7: Sales (Week 9-10)
- Build SO Master with conditional `Sales Type`: Subform A (System Lines, Supply+Apply → auto-creates Project) / Subform B (FG Lines, Supply Only → NO Project)
- System Lines subtable with thickness, area, UOM, rate; FG Lines subtable with code, qty, UOM, rate
- Commission, warranty, transport fields (System Lines)
- Link SO to Projects (Supply+Apply only)

### Phase 8: Service Team (Week 10)
- Build Service Entry form with Area/Work tracking
- Build Service Invoice auto-generation
- Link to Project for cost tracking
- Configure service workflow (allocation→execution→invoicing)

### Phase 9: Dashboards & Reports (Week 10-11)
- Create Purchase Dept dashboard with all widgets
- Create Store Dept dashboard
- Create Production Dept dashboard
- Create Project Management dashboard
- Build all 30+ reports per department

### Phase 10: Logistics (Week 11)
- Build Delivery Challan (DC) form
- Configure vehicle/dispatch tracking
- Build logistics reports (dispatch, delivery, transport cost)
- Link to Project for delivery tracking

### Phase 11: Automation & Integration Testing (Week 11-12)
- Test all autofetch relationships
- Test notifications and pop-ups
- Test approval workflows
- Test stock update on GRN/MIS/FGHM
- Test partial GRN scenario
- Test dual PO numbering
- Test project costing calculations
- UAT with departmental users
- Bug fixes and refinements
- Go-live

---

## 16. Key Development Notes

### Lookup Configuration Tips
- Always enable "Allow New Entry" on lookup fields that reference Supplier/Customer master
- Use formula fields for GST calculation (CGST = Total GST / 2, SGST = Total GST / 2)
- Auto-fetch: use "On User Input" → "Lookup" → auto-populate related fields
- For bidirectional autofetch (Item Code ↔ Item Name), use two separate lookup rules

### Conditional Visibility
- GRN: Transport subform visible only when PO Scope of Transport = "Own"
- GRN: Client Site textbox visible only when Warehouse = "Client Site"
- Project: Application tasks visible only when Execution Base = "Area Basis"
- Project: Manpower tasks visible only when Execution Base = "Day Basis"
- SO: Commission amount visible only when Commission checkbox checked

### Partial GRN Implementation
- Use checkbox column in GRN items subform
- When creating GRN against PO, show all PO items with checkbox
- Only checked items are received; remaining stay open in PO
- GRN posting only adds checked items to stock

### Printable PO
- Design a separate printable template/layout
- Include all T&C as static text
- Show header with company logo
- Show total amount in words formula

### Reporting Hints
- Use Zoho Creator Report Designer for calculations
- Summary reports for Purchase: by item group, supplier, date range
- Cross-filter reports for Project costing (task costs × actuals)
- Use pivot tables for Project Margin and Sitewise Costing
