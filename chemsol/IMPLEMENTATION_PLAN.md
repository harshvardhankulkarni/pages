# Chemsol — Zoho Creator Workflow Blueprint: Implementation Plan

## Core Process Flow
```
SO (Sales Order) → Costing Sheet (Costing team: detailed cost breakdown)
  → Production Plan (auto-derived from Costing Sheet + stock check)
    → Auto-PR (if stock insufficient) → PO → GRN → QC [parallel procurement]
    → MR (Material Requisition: 4 cost components auto-filled from Costing Sheet)
      → Production Verified (cross-check: SO system × BOM vs MR Assigned Qty)
        → Costing Approved (TOTAL project cost confirmed)
          → MR Released [⛔ CRITICAL GATE]
            → Auto-MIS + Auto-Production Job created on release
              → MIS (Store issues RM to Production)
                → Production (BMR → RM Consumption → Packing)
                  → FGHM (FG Handover with inline acceptance → FG Stock +)
                    → Site Consumption (hourly/daily task tracking per area)
                      → Project Close → P&L auto-calculated

← Side: Procurement (PR → PO → GRN → QC) triggered by Production Plan shortage
← Side: Material Return (unused RM back to Store)
← Side: Real-time Project Inventory Report (Received − Consumed = Remaining)
```

## 1. Overview

**Client**: Chemsol — Flooring/construction materials company (Epoxy, PU, Demarcation)
**Platform**: Zoho Creator
**Core Modules**: 18+ modules across 7 phases
**Departments**: Sales, Costing, Purchase, Store, Production, QC, Project Manager
**Warehouses**: Wadki, Main, Neelo, Gurgaon, Bangalore, Client Site

### System Code Prefixes
|| Code | Meaning | Example ||
||------|---------|---------||
|| EP | Epoxy Flooring | EP01 (1mm), EP02 (2mm) ||
|| PU | PU Flooring | PU01 (1mm) ||
|| DEM | Demarcation Line | — ||
|| ANTI | Anti Static | — ||
|| ESD | ESD Flooring | — ||
|| FIL | Filling | — ||
|| COV | Coving | — ||

---
## 2. Phase 1 — Master Data (Foundation)
Build first — all transactional forms depend on these.

### 2.1 Purchase Item Muster
**Purpose**: Central item repository — RM, FG, Packaging, Tools, Consumable
|| # | Field | Type | Req | Notes ||
||---|-------|------|-----|-------||
|| 1 | Category | Dropdown | * | 1.RM, 2.Packaging, 3.Tools & Consumable, 4.FG, 5.Maintenance, 6.Capital ||
|| 2 | Item Code | Autogen | * | Auto based on category ||
|| 3 | Item Name | Text | * | — ||
|| 4 | UOM | Dropdown | * | Nos / Kg / Ltr / Mtr / Kit ||
|| 5 | HSN Code | Text | * | For GST ||
|| 6 | GST % | Number | | — ||
|| 7 | Min Stock | Number | * | Reorder threshold ||
|| 8 | Max Stock | Number | | — ||
|| 9 | Standard Rate | Currency | | Hidden from non-Purchase/Store ||
|| 10 | Preferred Supplier | Multi-lookup | | From Supplier Master ||
|| 11 | Lead Time | Number (Days) | | — ||
|| 12 | Status | Dropdown | * | Active / Inactive ||

**AutoFetch target**: PR, PO, MR, MIS, GRN, FGHM, BOM, QC

### 2.2 System Master
**Purpose**: Flooring system definitions
|| # | Field | Type | Req ||
||---|-------|------|-----||
|| 1 | System Code | Text (autogen) | * ||
|| 2 | System Name | Text | * ||
|| 3 | Description | Multi-line | ||
|| 4 | Status | Active / Inactive | * ||

### 2.3 System Composition (System → FG Mapping)
**Purpose**: Defines which FGs make up each System (e.g., EP01 = FG-001 + FG-002)
**Header:**
|| # | Field | Type | Req ||
||---|-------|------|-----||
|| 1 | Comp No | Autogen (SC-YYYY-XXXX) | * ||
|| 2 | System Code | Lookup (System Master) | * ||
|| 3 | System Name | AutoFetch (from System Code) | * ||
|| 4 | Revision No | Text | ||
|| 5 | Date | Date (Today) | * ||
|| 6 | Status | Draft / Approved / Released | * ||

**Line Items (N FGs per System):**
|| # | Field | Type | Req ||
||---|-------|------|-----||
|| 1 | FG Product Code | Lookup (Item Muster - FG) | * ||
|| 2 | FG Name | AutoFetch (from FG Product Code) | * ||
|| 3 | Qty per System Unit | Number | * ||
|| 4 | UOM | AutoFetch (from Item Muster via FG Code) | * ||
||* Code) | * ||
|| 5 | Rate per FG Unit | Currency | ||

### 2.4 BOM / FG Formulation (FG → RM Mapping)
**Purpose**: Defines which RMs make up each FG with ratios
**Header:**
|| # | Field | Type | Req ||
||---|-------|------|-----||
|| 1 | BOM No | Autogen | * ||
|| 2 | FG Code | Lookup (Item Muster - FG) | * ||
|| 3 | FG Name | AutoFetch (from FG Code) | * ||
|| 4 | Date | Date (Today) | * ||
|| 5 | Status | Draft / Approved / Released | * ||

**Line Items (N RMs per FG):**
|| # | Field | Type | Req ||
||---|-------|------|-----||
|| 1 | RM Item Code | Lookup (Item Muster - RM) | * ||
|| 2 | RM Name | AutoFetch (from RM Item Code) | * ||
|| 3 | UOM | AutoFetch (from Item Muster via RM Code) | * ||
|| 4 | Qty per FG Unit | Number | * ||
|| 5 | Waste % | Number | ||
|| 6 | Total Qty | Formula | * ||

### 2.5 Supplier Master
**Purpose**: Vendor database
|| # | Field | Type | Req ||
||---|-------|------|-----||
|| 1 | Supplier Code | Autogen | * ||
|| 2 | Supplier Name | Text | * ||
|| 3 | GSTIN | Text | * ||
|| 4 | PAN No | Text | * ||
|| 5 | Contact Person | Text | * ||
|| 6 | Mobile No | Phone | * ||
|| 7 | Email | Email | * ||
|| 8 | Address | Multi-line | * ||
|| 9 | Bank Name / Account No / IFSC | Text | * ||
|| 10 | Payment Terms | Text | * ||
|| 11 | Credit Days | Number | * ||
|| 12 | Status | Active / Inactive | * ||

### 2.6 Store Master
**Purpose**: Warehouse definitions
|| # | Field | Type | Req ||
||---|-------|------|-----||
|| 1 | Store Code | Autogen | * ||
|| 2 | Store Name | Text | * ||
|| 3 | Store Type | Dropdown | * | RM Store / FG Store / QC Store / Site Store ||
|| 4 | Location | Text | * ||
|| 5 | Status | Active / Inactive | * ||

**Bin Location** (inline subform): Rack No, Shelf No, Bin No, Status

### 2.7 User Access & Approval Matrix
**Purpose**: Define roles, departments, approval limits
**User Access:**
|| Field | Type | Req ||
||-------|------|-----||
|| User Name | User lookup | * ||
|| Department | Dropdown | * | Purchase / Sales / Store / Production / QC / Project Manager / Account & Finance ||
|| Role | Entry / Review / Approve / Admin | * ||
|| Status | Active / Inactive | * ||

**Approval Matrix:**
|| Field | Type | Req ||
||-------|------|-----||
|| Department | Dropdown | * ||
|| Document Type | PR / PO / MR | * ||
|| Min Amount / Max Amount | Currency | * ||
|| Approver 1 / 2 / 3 | User lookup | * ||

---
## 3. Phase 2 — Sales & Project

### 3.1 Sales Order (SO)
**Purpose**: Create customer orders. On acceptance (Supply+Apply), auto-creates Costing Sheet (Draft); Project is auto-created on Costing Approved (single creation point — C2).
**Department**: Sales

**Header:**
|| # | Field | Type | Req ||
||---|-------|------|-----||
|| 1 | Sales Type | Dropdown | * | Supply+Apply (creates Project) / Supply Only (direct FG sale) ||
|| 2 | SO No | Autogen | * ||
|| 3 | SO Date | Date (Today) | * ||
|| 4 | Employee Name | Text | * ||
|| 5 | Customer Code | Lookup (Customer/Site Master) → AutoFetch: Org Name, GST, Contact | ||
|| 6 | Client Org / Contact / GST / PAN | Text | * ||
|| 7 | Regd Address | Multi-line | * ||
|| 8 | Site Name / Address | Text / Multi-line | * ||
|| 9 | Site Manager / Contact | Text / Phone | ||
|| 10 | Project Type | Dropdown | | Industrial / Commercial ||
|| 11 | Total Amount | Formula | * ||
|| 12 | Payment Terms | Text | ||
|| 13 | Transportation Scope / Amount | Dropdown / Currency | ||
|| 14 | Lead Time | Number (Days) | ||
|| 15 | PO/BOQ Attachment | File upload | ||
|| 16 | Warranty | Text | ||
|| 17 | Commission | Checkbox → % or Fix Amount | ||

**Subform A — System Lines** (when Sales Type = Supply+Apply):
|| # | Field | Type ||
||---|-------|------||
|| 1 | System Code | Lookup (System Master) → AutoFetch Name ||
|| 2 | Thickness | Text ||
|| 3 | Area | Number ||
|| 4 | UOM | Dropdown ||
|| 5 | Rate | Currency ||
|| 6 | Amount | Formula = Area × Rate ||

**Subform B — FG Lines** (when Sales Type = Supply Only):
|| # | Field | Type ||
||---|-------|------||
|| 1 | FG Code | Lookup (Item Muster - FG) → AutoFetch: Name, UOM ||
|| 2 | Qty | Number ||
|| 3 | UOM | AutoFetch (from FG Code via Item Muster) ||
|| 4 | Rate | Currency ||
|| 5 | Amount | Formula = Qty × Rate ||

**Automation:**
- Sales Type controls subform visibility (show/hide rule)
- Supply+Apply on acceptance → auto-create Costing Sheet (Draft); Project auto-created on Costing Approved (C2)
- Supply Only → NO Project, direct FG dispatch only
- System lines define System→FG→RM composition that drives backend consumption

### 3.2 Project
**Purpose**: Root entity — every downstream form links here. Auto-created from SO.
**Department**: Project Manager / Coordinator

|| # | Field | Type | Req ||
||---|-------|------|-----||
|| 1 | Project ID | Autogen | * ||
|| 2 | SO Reference | Lookup (Sales Order Master) → AutoFetch: SO No, Customer, Amount | * ||
|| 3 | Project Name | Text | * ||
|| 4 | Address | Multi-line | * ||
|| 5 | Project Manager | User lookup | * ||
|| 6 | Execution Base | Dropdown | * | Area Basis / Day Basis ||
|| 7 | Start Date / End Date | Date | * ||
|| 8 | Project Cost | Currency | * ||
|| 9 | Status | Dropdown | * | Planned / In Progress / Completed / On Hold ||

**Systems Subform:**
|| # | Field | Type ||
||---|-------|------|---||
|| 1 | System Code | Lookup (System Master) ||
|| 2 | Area | Number ||
|| 3 | UOM | Dropdown ||
|| 4 | Description | Text ||
||---|

---
## 4. Phase 3 — Costing Sheet, Production Plan & MR

### 4.1 Costing Sheet [NEW — Costing Team module]

**Purpose**: Standalone detailed costing form created by the Costing team AFTER SO is accepted. Costing Sheet is the complete project cost breakdown — more granular than SO. MR will later be **auto-derived** from the approved Costing Sheet.

**Department**: Costing Team

**How it fits**:
```
SO (System/FG scope + area) → Costing Sheet (detailed per-cost line)
  → Production Plan (check existing stock, trigger procurement if needed)
    → MR auto-created from Costing Sheet (4 cost components pre-filled)
```

**Header:**
| # | Field | Type | Req | Notes |
|---|-------|------|-----|-------|
| 1 | Costing No | Autogen (CST-YYYY-XXXX) | * | — |
| 2 | Costing Date | Date (Today) | * | — |
| 3 | SO Reference | Lookup (Sales Order — Supply+Apply only) | * | Auto-fetches Customer, System Lines, Area |
| 4 | Project ID | Auto-created on Costing approval | * | Project auto-created when Costing is approved |
| 5 | Costing Status | Draft / Under Review / Approved / Rejected | * | Controls downstream flow |
| 6 | Prepared By | User lookup | * | Costing team member |
| 7 | Reviewed By | User lookup | | Costing manager |
| 8 | Revision No | Text | | For revised costings |
| 9 | Total Costing Amount | Formula (sum of all sections) | * | Auto-calculated |

**Section A — Material Cost (auto-expanded from SO System Lines × BOM):**
| # | Field | Type | Notes |
|---|-------|------|-------|
| 1 | System Code | Auto-fetch from SO | |
| 2 | FG Code | Auto-fetch from System Composition × BOM | All FGs in the system |
| 3 | RM Item Code | Auto-fetch from BOM | All RMs per FG |
| 4 | RM Name | Auto-fetch | |
| 5 | UOM | Auto-fetch | |
| 6 | BOM Qty per FG Unit | Auto-fetch | |
| 7 | SO Area/Qty | Auto-fetch from SO | |
| 8 | Total RM Required | Formula = BOM Qty × SO Area × (1 + Waste%) | |
| 9 | Rate per Unit | Lookup (Item Muster — Standard Rate) | Costing can override |
| 10 | Material Cost | Formula = Total RM Required × Rate | |

**Section B — Application Cost (labour/execution on site):**
| # | Field | Type |
|---|-------|------|
| 1 | Activity | Text (e.g., Surface Preparation, Primer Application, Top Coat) |
| 2 | UOM | Dropdown (SqM / Day / Hour) |
| 3 | Qty / Area | Number |
| 4 | Rate | Currency |
| 5 | Amount | Formula = Qty × Rate |

**Section C — Transportation Cost:**
| # | Field | Type |
|---|-------|------|
| 1 | From (Warehouse) | Lookup (Store Master) |
| 2 | To (Site) | Text |
| 3 | Mode of Transport | Dropdown (Own / Third Party) |
| 4 | Estimated Trips | Number |
| 5 | Rate per Trip | Currency |
| 6 | Amount | Formula = Trips × Rate |
| 7 | Logistics Notes | Multi-line |

**Section D — Tools & Tackles:**
| # | Field | Type |
|---|-------|------|
| 1 | Item | Lookup (Item Muster — Tools & Consumable) |
| 2 | Qty | Number |
| 3 | Rate | Currency |
| 4 | Amount | Formula = Qty × Rate |

**Section E — Overhead & Miscellaneous:**
| # | Field | Type |
|---|-------|------|
| 1 | Description | Text |
| 2 | Amount | Currency |
| 3 | Remarks | Multi-line |

**Automation:**
- On SO Reference selection → auto-expand SO System Lines → expand each System via System Composition to get all FGs → expand each FG via BOM to get all RMs → pre-populate Section A Material Cost lines
- Total Costing Amount = Σ(Material) + Σ(Application) + Σ(Transportation) + Σ(Tools) + Σ(Overhead)
- **On Costing Approved**: auto-create Project (if not already created) + auto-create Production Plan (Draft) with all material requirements
- On Costing Rejected with revision → increment Revision No, reset status to Draft
- SLA: Costing must be completed within 24 hours of SO acceptance. Escalation to management at 48 hours.

### 4.2 Production Plan [REVISED — triggers procurement]

**Purpose**: Production team reviews Costing Sheet, checks existing RM stock, generates production plan. If stock insufficient, auto-creates PR.

**Department**: Production

| # | Field | Type | Req | Notes |
|---|-------|------|-----|-------|
| 1 | Plan No | Autogen (PLAN-YYYY-XXXX) | * | |
| 2 | Plan Date | Date (Today) | * | |
| 3 | Costing Ref | Lookup (Costing Sheet — Approved) | * | Auto-fetches all material lines |
| 4 | Project ID | Auto-fetch from Costing | * | |
| 5 | Planning Period | Week / Month | * | |
| 6 | Plant | Dropdown | | |
| 7 | Planner Name | User lookup | * | |
| 8 | Status | Draft / Reviewed / Released | * | |

**Line Items:**
| # | Field | Type | Notes |
|---|-------|------|-------|
| 1 | RM Item Code | Auto-fetch from Costing | |
| 2 | RM Name | Auto-fetch | |
| 3 | Total Required | Auto-fetch from Costing Sheet Section A | |
| 4 | Available Stock | Auto-fetch from RM Inventory (net of other project allocations) | |
| 5 | Shortage | Formula = Total Required − Available Stock (if negative) | |
| 6 | Source | Dropdown | Stock / Purchase / Both |
| 7 | Procurement Triggered | Checkbox (auto) | Set when Shortage > 0 |

**Automation:**
- On Plan Release → for each line where Shortage > 0 → auto-create PR (project-tagged) with item + shortage qty → notify Purchase dept
- Available Stock = physical stock − Σ(Assigned Qty from all other unreleased MRs). Prevents double-allocation.
- Production Plan must be Released before MR can be created

### 4.3 MR — Material Requisition [CRITICAL GATE] [REVISED]
**Purpose**: MR is auto-derived from approved Costing Sheet and Released Production Plan. Carries the **complete project implementation cost baseline** — four cost components (Material + Application + Transportation + Tools & Tackles) auto-filled from Costing Sheet. Costing approves the TOTAL.
**Department**: Production / R&D

**MR Status Workflow (The Critical Approval Gate):**
```
Draft → Pending Production Verification → Production Verified → Costing Approved → Released
  │           │                      │              │
  │      Production checks       Costing           ⛔ Gate
  │      MR qty vs SO system     approves TOTAL    passed →
      req (via BOM × SO qty)  project cost      MIS can proceed
```

**Header:**
|| # | Field | Type | Req | Notes ||
||---|-------|------|-----|-------||
|| 1 | MR Number | Autogen (MR-YYYY-XXXX) | * | — ||
|| 2 | MR Date | Date (Today) | * | — ||
|| 3 | Project ID | Lookup (Project Master) | * | Links MR to Project ||
|| 4 | Requisition Type | Dropdown | * | Production / R&D ||
|| 5 | Batch Number | Text | | — ||
|| 6 | Department | AutoFetch from login | * | — ||
|| 7 | Requested By | Text (Employee Name) | * | — ||
|| 8 | Priority | Low / Medium / High / Urgent | * | — ||
|| 9 | **MR Status** | **Draft / Pending Production Verification / Production Verified / Costing Approved / Released** | * | **CRITICAL — controls downstream flow** ||

**Line Items (N items):**
|| # | Field | Type ||
||---|-------|------|---||
|| 1 | Item Code | Lookup (Item Muster - RM only via filter) ||
|| 2 | Item Name | AutoFetch (from Item Code) ||
|| 3 | Category | AutoFetch (from Item Code) ||
|| 4 | UOM | AutoFetch (from Item Code) ||
|| 5 | Available Stock | AutoFetch from RM Inventory (real-time via stock summary) ||
|| 6 | Required Qty | Number ||
|| 7 | Remarks | Multi-line ||

**MR = Complete Project Implementation Cost Baseline:**
MR carries **four cost components** that sum to **Total MR Cost** — the project implementation cost baseline that **Costing approves**:

1. **Material Cost** — from Material Allocation subform (Σ Assigned Qty × Rate)
2. **Application Cost** — labour/execution on site
3. **Transportation Cost** — material transport to site
4. **Tools & Tackles** — equipment needed

**Total MR Cost = Material + Application + Transportation + Tools & Tackles**

**Material Allocation Subform** (feeds Material Cost — per-project RM allocation):
|| # | Field | Type | Notes ||
||---|-------|------|-------||
|| 1 | Item Code | Lookup (Item Muster - RM) | Auto-populated from MR line items ||
|| 2 | Item Name | AutoFetch (from Item Code) | — ||
|| 3 | UOM | AutoFetch (from Item Code) | — ||
|| 4 | Assigned Qty | Number | Allocation baseline, defaults from Required Qty ||
|| 5 | Rate | Currency | Per-unit RM rate ||
|| 6 | Material Cost | Formula | = Assigned Qty × Rate ||
|| 7 | Allocation Ratio % | Formula | = Assigned Qty ÷ Σ Assigned Qty × 100 ||
|| 8 | 80% Threshold Alert Flag | Checkbox | Default ON ||
|| 9 | Consumed Qty | Number (auto) | Incremented by BMR/RM Consumption entries ||
|| 10 | Consumption % | Formula | = Consumed Qty ÷ Assigned Qty × 100 ||
|| 11 | Alert Triggered | Checkbox (readonly) | Auto-set at Consumption % ≥ 80% ||
|| 12 | Issued Qty | Number (auto) | **G4** — Incremented by MIS-Post Deluge per matching Project+Item ||
|| 13 | Returned Qty | Number (auto) | **C1** — Incremented by Material Return Deluge per matching Project+Item ||
|| 14 | Remaining | Formula | **C1** — = Assigned Qty − Consumed Qty + Returned Qty ||
|| 15 | Fully Consumed | Checkbox (auto) | **C1** — Set when Consumed Qty ≥ Assigned Qty (100%); checked by FGHM acceptance Deluge ||
|| 16 | Variance % | Number (readonly) | **C19** — SO↔BOM↔MR cross-validation result (set when diff > 5%) ||
|| 17 | Variance Flag | Checkbox (readonly) | **C19** — Auto-set when variance > 5% (flag, allow); > 10% hard-blocks submit ||

**Application Cost Subform** (labour/execution):
|| # | Field | Type ||
||---|-------|------|---||
|| 1 | Activity | Text (e.g., surface prep, laying) ||
|| 2 | UOM | Dropdown ||
|| 3 | Qty / Area | Number ||
|| 4 | Rate | Currency ||
|| 5 | Amount | Formula = Qty × Rate ||

**Transportation Cost Subform** (material to site):
|| # | Field | Type ||
||---|-------|------|---||
|| 1 | From | Text (warehouse) ||
|| 2 | To | Text (site) ||
|| 3 | Vehicle / Trips | Text / Number ||
|| 4 | Rate | Currency ||
|| 5 | Amount | Formula = Trips × Rate ||

**Tools & Tackles Subform:**
|| # | Field | Type ||
||---|-------|------|---||
|| 1 | Item | Text / Lookup (Item Muster - Tools & Consumable) ||
|| 2 | Qty | Number ||
|| 3 | Rate | Currency ||
|| 4 | Amount | Formula = Qty × Rate ||

**Automation Rules:**
- MR is **auto-created** from approved Costing Sheet + Released Production Plan. All 4 cost components pre-filled. Not manually entered.
- MR Status workflow: Draft (auto-created) → Pending Production Verification → Production Verified → Costing Approved → Released
- **SO↔BOM↔MR cross-validation**: On MR creation, validate that Σ(MR Allocation Assigned Qty) = Σ(SO Area × BOM Qty per Unit × (1+Waste%)). If mismatch > 5%, flag for review. Hard block if > 10%.
- **Without Released MR, there is no MIS, no Production, no project execution**
- Consumption entries increment Consumed Qty on matching MR Allocation (matched by Project ID + Item Code)
- **80% Alert**: When Consumption % ≥ 80% and Alert Flag is ON → pop-up + dashboard banner + email to Project Manager
- **100% Alert**: "Allocation Exhausted" → email to Project Manager + Purchase dept
- **Tight SLAs**: MR stuck in Draft > 2 hours → reminder to Production. In Production Verified > 2 hours → escalation to Costing lead. In Costing Approved > 1 hour → auto-release if all checks passed.

---
## 5. Phase 4 — Procurement (As Needed)
Procurement runs when production needs materials not in stock.

### 5.1 PR — Purchase Requisition
**Department**: Production
**Linked to**: Project (when procurement is for a project)

**Header:**
|| # | Field | Type | Req ||
||---|-------|------|-----||
|| 1 | PR Number | Autogen | * ||
|| 2 | PR Date | Date (Today) | * ||
|| 3 | Project ID | Lookup (Project Master) | | Optional — for project-linked procurement only; stock procurement has no Project ID ||
|| 4 | Reference | Text | ||
|| 5 | Department | AutoFetch from login user | * ||
|| 6 | Status | Draft / Pending Approval / Approved / Rejected | * ||

**Line Items:**
|| # | Field | Type ||
||---|-------|------|---||
|| 1 | Item Code | Lookup (Item Muster) ↔ bidirectional autofill: Name ||
|| 2 | Item Name | AutoFetch (from Item Code) ||
|| 3 | Qty | Number ||
|| 4 | UOM | AutoFetch (from Item Code via Item Muster) ||
|| 5 | Lead Time | AutoFetch (from Item Muster via Item Code) ||

**Automation:** Status = Draft → Pending Approval (on submit) → Approved. Notification to Purchase dept.

### 5.2 PO — Purchase Order
**Department**: Purchase
**Purpose**: Official order to supplier with GST split

**Header:**
|| # | Field | Type | Req ||
||---|-------|------|-----||
|| 1 | RM Type | Coding / Non Coding | * ||
|| 2 | PO Number | Autogen (RM-YYYY-XXXX / RMWAD-YYYY-XXXX) | * ||
|| 3 | PO Date | Date (Today) | * ||
|| 4 | Supplier Code | Lookup (Supplier Master) → AutoFetch Name, GSTIN, Address | * ||
|| 5 | Project ID | Lookup (Project Master) | * ||
|| 6 | PR Reference | Lookup (PR Master) → AutoFetch: Items, Qty | ||
|| 7 | Bill To / Ship To | Dropdown | * ||

**Line Items:**
|| # | Field | Type ||
||---|-------|------|---||
|| 1 | Item Code | Lookup (Item Muster) → AutoFetch: Name, HSN, GST%, UOM ||
|| 2 | Item Name / HSN | AutoFetch (from Item Code) ||
|| 3 | Quantity / Rate | Number / Currency ||
|| 4 | Basic Amount | Formula = Qty × Rate ||
|| 5 | GST % | AutoFetch from Item Muster ||
|| 6 | GST Amount | Formula = Basic × GST% ||
|| 7 | Total Amount | Formula = Basic + GST ||

**Footer (Auto-calculated):**
|| Field | Formula ||
||-------|---------||
|| Basic Total | SUM of line Basic Amounts ||
|| CGST / SGST | Each = GST/2 (intra-state) ||
|| IGST | Full GST (inter-state) ||
|| Total Amount (Words) | Auto-convert ||
|| Delivery Date / Payment Terms | Mandatory ||
|| Scope of Transport | Supplier / Own ||

**Printable PO** with T&C, company logo, total in words.

### 5.3 GRN — Goods Receipt Note
**Department**: Store / Purchase

**Header:**
|| # | Field | Type | Req ||
||---|-------|------|-----||
|| 1 | GRN Number | Autogen (after posting) | * ||
|| 2 | GRN Date | Date (Today) | * ||
|| 3 | PO Number | Lookup (PO Master) → AutoFetch: Supplier Name, Items, Ordered Qty, Project ID | * ||
|| 4 | Project ID | AutoFetch from PO | * ||
|| 5 | Vehicle Number | Text | * ||
|| 6 | Warehouse | Dropdown | * | Wadki / Main / Neelo / Gurgaon / Bangalore / Client Site ||
|| 7 | Invoice Number / Date | Text / Date | * ||

**Line Items (Checkbox for partial GRN):**
|| # | Field | Type | Source ||
||---|-------|------|--------||
|| 1 | ✅ Checkbox | Checkbox (select items for partial GRN) | ||
|| 2 | Item Code / Name | AutoFetch (from PO via PO Number) | PO Master ||
|| 3 | Ordered Qty | AutoFetch (from PO via PO Number) | PO Master ||
|| 4 | Received Qty | Number | ||
|| 5 | QC Status | Pending / Pass / Fail | ||
|| 6 | Packing Quality | Good / Damaged / Partial | ||

**Transport Subform** (visible when PO Scope = Own): Transporter, Charges, Local Transport, Loading/Unloading

**Stock Rule:** Qty added to stock **only after posting**. Timestamp logged. Partial GRN via checkbox.

### 5.4 QC / QA
**Department**: QC

|| # | Field | Type | Req ||
||---|-------|------|-----||
|| 1 | QC Number | Autogen | * ||
|| 2 | Date | Date (Today) | * ||
|| 3 | GRN Number | Lookup (GRN Master) → AutoFetch: Item No, Name, Received Qty | * ||
|| 4 | Item No / Name | AutoFetch from GRN | * ||
|| 5 | Inspection Date | Date | ||
|| 6 | Viscosity / Density / Color / Moisture | Text (result) | ||
|| 7 | Accepted Qty / Rejected Qty | Number | * ||
|| 8 | QC Status | Pass / Fail / Hold | * ||
|| 9 | Remarks | Multi-line | * ||

---
## 6. Phase 5 — Inventory & Production

### 6.1 MIS — Material Issue Slip
**Department**: Store
**Purpose**: Issue RM from Store to Production. Procedes only after MR Released.

|| # | Field | Type | Req |
---|-------|------|-----|  MR No | No | Look MR No | Lookup (MR — only Released MRs shown) | * |
| MIS Number | Autogen (against MR) | * |
| Date | Date (Today) | * |
| Batch Number | Text | |
| Status | Dropdown — Draft (auto on MR Release) / Posted (set by "Post MIS" button) | * | **C17** — required by MIS Deluge (input.Status = "Posted") |

**Line Items** (auto-fetched from MR):
|| Item Code / Name | AutoFetch (from MR line items via MR No) | MR |
| Category | AutoFetch (from MR line items) | MR |
| Required Qty | AutoFetch (from MR line items) | MR |
| Issued Qty | Number | |
| Balance Qty | Formula = Required − Issued | |
| Issued By / Handover To | Text (Supervisor Name) | |

**Automation:** Stock deducted from inventory on MIS posting. Only creatable after MR Released.

### 6.2 Production Job [REVISED — execution-level planning]
**Department**: Production
**Purpose**: Plan FG batch execution after MR Released. This is execution planning (which FG batch to produce when), distinct from Procurement Planning (Phase 3B) which handles stock checks.

|| # | Field | Type | Req ||
||---|-------|------|-----||
|| 1 | Job No | Autogen (JOB-YYYY-XXXX) | * ||
|| 2 | Job Date | Date | * ||
|| 3 | Project ID | Lookup (Project Master) → AutoFetch: Project Name, Manager | * ||
|| 4 | MR Sheet No | Lookup (MR — only Released MRs) → AutoFetch: Items, Qty | * ||
|| 5 | FG Code | Lookup (Item Muster - FG) | * |
|| 6 | Planned FG Qty | Number | * |
|| 7 | Planning Period | Week / Day | * ||
|| 8 | Plant | Dropdown | |
|| 9 | Planner Name | User lookup | * ||
|| 10 | Status | Draft / Scheduled / In Progress / Completed | * ||

### 6.3 BMR — Batch Manufacturing Record
**Department**: Production
**Purpose**: Record actual batch production — consume RM to produce FG

|| # | Field | Type | Req ||
||---|-------|------|-----||
|| 1 | BMR No | Autogen | * ||
|| 2 | Production Job Ref | Lookup (Production Job) → AutoFetch: Project ID, FG Code, Planned Qty | * ||
|| 3 | Project ID | AutoFetch (from Production Order Ref) | * ||
|| 4 | Batch No | Text | * ||
|| 5 | Date | Date | * ||
|| 6 | FG Code | Lookup (Item Muster - FG) → AutoFetch: FG Name, BOM RM list | * ||

**Line Items (RM consumed to produce FG):**
|| RM Item Code | Lookup (Item Muster - RM) → AutoFetch: Name, UOM | Item Muster ||
| RM Item Name | AutoFetch (from RM Item Code) | Item Muster ||
| Batch No (RM) | Text | ||
| Qty Consumed | Number | ||
| UOM | AutoFetch (from RM Item Code via Item Muster) | Item Muster ||
| Yield / FG Output | Number | ||

### 6.4 RM Consumption Entry
|| # | Field | Type | Source ||
||---|-------|------|--------||
|| 1 | Reference to BMR | Lookup (BMR Master) → AutoFetch: FG Code, Batch No, RM Items | BMR ||
|| 2 | Item-wise RM | Lookup (Item Muster - RM, filtered by BMR items) | Item Muster ||
|| 3 | Actual Qty | Number | ||
|| 4 | Standard Qty | AutoFetch (from BOM via FG Code) | BOM / FG Formulation ||
|| 5 | Variance | Formula = Actual − Standard | ||

### 6.5 Packing Entry
|| # | Field | Type | Source ||
||---|-------|------|--------||
|| 1 | BMR Reference | Lookup (BMR Master) → AutoFetch: FG Code, Batch No | BMR ||
|| 2 | FG Product | Lookup (Item Muster - FG) → AutoFetch: FG Name, UOM | Item Muster ||
|| 3 | Packed Qty | Number | ||
|| 4 | Packing Material Consumed | Lookup (Item Muster - Packaging) + Qty | Item Muster ||
|| 5 | Batch No | AutoFetch (from BMR Reference) | BMR ||

### 6.6 FGHM — FG Handover Master
**Department**: Production
**Purpose**: Handover FG to store/site with inline acceptance

|| # | Field | Type | Req ||
||---|-------|------|-----||
|| 1 | FGH No | Autogen | * ||
|| 2 | Project ID | Lookup (Project Master) | * ||
|| 3 | Handover Date | Date (Today) | * ||
|| 4 | Batch No | Text | * ||
||---|

**Line Items:**
|| FG Product Code | Lookup (Item Muster - FG) → AutoFetch: Name, UOM | Item Muster ||
| FG Product Name | AutoFetch (from FG Product Code) | Item Muster ||
| FG Qty | Number | ||
| UOM | AutoFetch (from FG Product Code via Item Muster) | Item Muster ||
| QC Status | Pass / Fail / Hold ||
| Damaged Qty / Accepted Qty | Number (inline acceptance) ||
| Handed Over By / Received By | Text ||
| Remark | Multi-line ||

**Automation:** On FGHM submission → Notification to Store. FG Stock updated. On FGHM acceptance → mark corresponding MR Allocation lines with `Fully Consumed = Yes` if sum of consumption entries ≥ Assigned Qty for all RM lines in that batch.

### 6.7 Site Consumption Entry [NEW — Hourly/Daily Task Tracking]

**Purpose**: Track actual material consumption at the project site — hourly or daily per work area. This is **how project inventory is tracked against allocations**. Every entry decrements the project's allocated RM.

**Department**: Project Manager / Site Supervisor

| # | Field | Type | Req | Notes |
|---|-------|------|-----|-------|
| 1 | Consumption No | Autogen (SCE-YYYY-XXXX) | * | |
| 2 | Project ID | Lookup (Project Master) | * | |
| 3 | Work Area | Text | * | e.g., "Zone A — Ground Floor", "Section 2 — Wall" |
| 4 | Date | Date | * | |
| 5 | Time Slot | Dropdown | | Morning / Afternoon / Full Day / Night |
| 6 | Supervisor | User lookup | * | |
| 7 | Remarks | Multi-line | | |

**Line Items (materials consumed):**
| # | Field | Type | Source |
|---|-------|------|--------|
| 1 | RM Item Code | Lookup (Item Muster — RM) → AutoFetch: Name, UOM | Item Muster |
| 2 | Qty Consumed | Number | |
| 3 | UOM | AutoFetch (from RM Item Code) | Item Muster |
| 4 | System / FG Reference | Lookup (Project Systems subform) | Optional — for BOM expansion |
| 5 | Consumption Type | Dropdown | Actual / Wastage / Rework |

**Automation:**
- On submit → increment `Consumed Qty` on matching MR Allocation line (`Project ID + Item Code`). If no matching allocation exists, alert and block.
- If `System / FG Reference` is provided → auto-expand into RMs at BOM ratios and consume from MR Allocation proportionally
- After increment → recalculate `Consumption %` on MR Allocation. If ≥ 80% and flag ON → fire 80% Alert
- **Project Inventory deduction**: Remaining = MR Allocation.Assigned Qty − Consumed Qty + Returned Qty (C1 — this is the live project inventory balance)

### 6.8 Material Return Entry [NEW]

**Purpose**: Return unused RM from project site / production back to Store. Credits the project's allocated inventory.

**Department**: Store / Production

| # | Field | Type | Req |
|---|-------|------|-----|
| 1 | Return No | Autogen (MRT-YYYY-XXXX) | * |
| 2 | Project ID | Lookup (Project Master) | * |
| 3 | Return Date | Date (Today) | * |
| 4 | Returned By | User lookup | * |
| 5 | Received By | User lookup (Store) | * |
| 6 | Reason | Dropdown | Excess Issued / Unused / Damaged / Wrong Item |

**Line Items:**
| # | Field | Type |
|---|-------|------|
| 1 | RM Item Code | Lookup (Item Muster — RM) |
| 2 | RM Name | AutoFetch |
| 3 | UOM | AutoFetch |
| 4 | Return Qty | Number |
| 5 | Condition | Good / Damaged / Expired |

**Automation:**
- On submit → decrement `Consumed Qty` on matching MR Allocation line by Return Qty
- If Return Reason = "Excess Issued" or "Unused" → add Return Qty back to Store RM inventory (RM Stock +)
- If Damaged/Expired → add to damaged stock (separate count), do not credit available stock

---
## 7. Phase 6 — Inventory Management [REVISED]

### 7.1 RM Inventory
- Stock increased on GRN posting
- Stock decreased on MIS posting
- Stock alerts at Min/Max thresholds
- Available Stock = physical stock − Σ(Assigned Qty from all unreleased MRs) — prevents double-allocation

### 7.2 FG Inventory
- Stock increased on FGHM inline acceptance
- Stock decreased on dispatch (Supply Only sales)
- FG stock tracked per Project ID for project-level reporting

### 7.3 Project Inventory Status [NEW Report]
Each project tracks:
- **Assigned Qty** (from MR Material Allocation)
- **Issued Qty** (from MIS — total issued to production)
- **Consumed Qty** (from BMR + RM Consumption + Site Consumption entries)
- **Returned Qty** (from Material Return)
- **Remaining** = Assigned Qty − Consumed Qty + Returned Qty
- **Consumption %** = Consumed Qty / Assigned Qty × 100
- **80% Alert status** per RM line
- This is the **single source of truth for project P&L inventory calculation**

### 7.4 End-to-End Stock Flow (Revised)
```
Costing Sheet Approved → Production Plan Released
  → MR Created (auto, 4 cost pre-filled)
    → MR Released
      → MIS Created (items auto-fetched from MR)
        → MIS Posted (RM Stock −, Project Inventory +)
          → Production (BMR → RM Consumption → Packing)
            → FGHM Created
              → FGHM Inline Accepted (FG Stock +)
                → Site Consumption Entries (hourly/daily, decrement project inventory)
                  → Material Return (if excess, credit back)
                    → Project Close → P&L auto-calculated
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

### 8.4 Autofetch Rules (Complete Reference)
|| Source Lookup Field | Source Form | Target Forms | Fetched Fields ||
||---------------------|-------------|-------------|----------------||
|| Item Code | Purchase Item Muster | PR, PO, MR, GRN, BMR, FGHM, Costing Sheet, Site Consumption, Material Return | Item Name, UOM, Category, HSN, GST%, Lead Time, Standard Rate ||
|| Supplier Code | Supplier Master | PO, GRN | Supplier Name, GSTIN, Address, Contact, Payment Terms ||
|| SO Reference | Sales Order | Costing Sheet | Customer, System Lines, Area, Total Amount ||
|| Costing Sheet No | Costing Sheet | Production Plan, MR | All material lines, 4 cost components, Project ID ||
|| PO Number | PO Master | GRN | Supplier Name, Items List, Ordered Qty per Item, Project ID ||
|| MR Number | MR Master | MIS, Production Planning, Site Consumption | Items List, Required Qty per Item, Category, Project ID, Allocation lines ||
|| Project ID | Project Master | PR, PO, GRN, MR, MIS, Production Planning, FGHM, Costing Sheet, Site Consumption, Material Return | Project Name, Project Manager, SO Reference, Start/End Date |
|| System Code | System Master | SO (Subform A), Project, System Composition, Costing Sheet | System Name, Description |
|| FG Code / FG Product Code | Item Muster (FG) | BOM, SO (Subform B), FGHM, Costing Sheet | FG Name, UOM |
|| RM Item Code | Item Muster (RM) | BOM Line, MR Line, BMR Line, Costing Sheet, Site Consumption | RM Name, UOM |
|| BMR Reference | BMR Master | RM Consumption, Packing Entry | FG Code, Batch No, RM Items List |
|| GRN Number | GRN Master | QC | Item Name, Received Qty |
|| Production Job Ref | Production Job | BMR | Project ID, FG Code, Planned Qty ||

### 8.5 Numbering Series
|| Document | Format ||
||----------|--------||
|| Costing Sheet | CST-YYYY-XXXX ||
|| Production Plan (procurement) | PLAN-YYYY-XXXX ||
|| Production Job (execution) | JOB-YYYY-XXXX ||
|| PR | PR-YYYY-XXXX ||
|| PO (Coding) | RMWAD-YYYY-XXXX ||
|| PO (Non-Coding) | RM-YYYY-XXXX ||
|| GRN | GRN-YYYY-XXXX ||
|| MR | MR-YYYY-XXXX ||
|| MIS | Auto against MR ||
|| FGH | FGH-YYYY-XXXX ||
|| QC | QC-YYYY-XXXX ||
|| SO | SO-YYYY-XXXX ||
|| Project | PRJ-YYYY-XXXX ||
|| System Composition | SC-YYYY-XXXX ||
|| BOM / FG Formulation | BOM-YYYY-XXXX ||
|| BMR | BMR-YYYY-XXXX ||
|| Site Consumption Entry | SCE-YYYY-XXXX ||
|| Material Return | MRT-YYYY-XXXX ||
|| Customer | CUST-YYYY-XXXX ||

### 8.6 Stock Management Rules
- **GRN posting**: Qty added to stock only after posting; timestamp logged
- **MIS posting**: Qty deducted from stock
- **FGHM inline acceptance**: FG qty added to stock after inline acceptance
- **Material Return**: Qty added back to stock
- **Min/Max stock**: Alert when stock crosses thresholds

### 8.7 Notification Triggers [REVISED — tighter SLAs]
|| Event | Notifies | Type | SLA ||
||-------|----------|------|------||
|| Costing Sheet Submitted | Costing Manager (review) | In-app | 4 hr to review ||
|| Costing Sheet Approved | Production + Project Manager | In-app + Email | Immediate ||
|| Production Plan Released | Purchase (if shortage) + Store | In-app | Immediate ||
|| PR Submitted | Purchase (pending approval) | In-app | 2 hr to process ||
|| PR to PO auto-creation | Purchase dept | In-app | Immediate ||
|| PO Ready | Supplier (email) + Store | Email + In-app | On PO Open ||
|| GRN Overdue | Purchase + Store | In-app | Daily at 8 AM ||
|| MR Ready for Verification | Production dept | In-app | 2 hr SLA ||
|| MR Production Verified (→ Pending Costing Approval) | Costing dept | In-app | 2 hr SLA ||
|| MR Stuck (breached SLA) | Department Head + Admin | Push + Email | Immediate on breach ||
|| MR Released | Store + Production + Project Manager | In-app + Email | Immediate ||
|| MIS Created (auto) | Store | In-app | On MR Release ||
|| MIS Posted | Production | In-app | Immediate ||
|| FGHM Submitted | Store & Logistics | Pop-up | Immediate ||
|| Site Consumption >80% | Project Manager | Pop-up + Email | Real-time on entry ||
|| Site Consumption =100% | Project Manager + Purchase | Email + Push | Real-time on entry ||
|| Material Return Submitted | Store (receive) | In-app | Immediate ||
|| Project Inventory Low (<20% remaining) | Project Manager + Purchase | Email | Daily check ||
|| SO↔BOM↔MR quantity mismatch flagged | Production + Costing | In-app | On MR creation ||

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

### Week 4-6: Costing Sheet, Production Plan & MR [NEW ORDER]
- **Costing Sheet** form (5 sections: Material, Application, Transport, Tools, Overhead)
- Auto-expansion of SO → System Composition → BOM → pre-populated Costing Sheet lines
- Costing Sheet workflow: Draft → Under Review → Approved → Project auto-created
- **Production Plan** with stock check (Available Stock = physical − other allocations)
- Auto-PR trigger on Production Plan Release for shortage items
- **MR** auto-derived from Costing Sheet (4 cost components pre-filled)
- MR Status workflow: Draft → Production Verified → Costing Approved → Released
- SO↔BOM↔MR cross-validation (quantity mismatch >5% flags, >10% blocks)
- 80% Consumption Alert automation
- SLA enforcement: 2 hr per stage, auto-escalation

### Week 7-8: Procurement (As Needed)
- PR with Project tagging + auto-creation from Production Plan shortage
- PO with dual numbering (RM/RMWAD), GST split
- GRN with partial checkbox, transport subform
- QC/QA linked to GRN

### Week 8-10: Production, Inventory & Site Operations
- MIS linked to MR (auto-created on MR Release, only Released MRs selectable)
- BMR, RM Consumption, Packing — ALL increment Consumed Qty on MR Allocation
- FGHM with inline acceptance → marks MR lines as Fully Consumed
- **Site Consumption Entry** (hourly/daily task tracking per project area)
- **Material Return Entry** (unused RM back to Store, credits project allocation)
- RM + FG inventory with per-project tracking
- Stock update automations (GRN→RM+, MIS→RM−, Site Consumption→Project Inventory−, FGHM→FG+)
- FGHM marks MR Allocation as Fully Consumed

### Week 10-11: Reports & Dashboards [REVISED]
- Purchase Dept dashboard (open POs, pending GRN, vendor performance)
- Store Dept dashboard (RM + FG stock, min/max alerts, by project)
- Production Dept dashboard (daily production, open orders, efficiency)
- **Project Inventory Status Report** (Assigned vs Issued vs Consumed vs Remaining per RM per Project)
- **Project P&L real-time view** (Costing Sheet total − consumption costs − procurement costs)
- MR Status tracking report with drill-through
- 80%/100% Consumption Alert dashboard per project
- **Site Consumption Report** (hourly/daily consumption by area, project)
- **Material Return Report** (returns by project, reason, condition)
- **Costing Sheet vs Actual** variance report

### Week 11-12: UAT & Go-Live
- Test Costing Sheet → Production Plan → MR auto-derivation flow
- Test all autofetch relationships
- Test MR workflow gates (SO↔BOM↔MR validation, cannot proceed without Released)
- Test stock updates on GRN/MIS/FGHM/Site Consumption/Material Return
- Test 80%/100% consumption alerts with real-time triggers
- Test auto-PR generation on Production Plan Release
- Test partial GRN
- UAT with departmental users (Sales, Costing, Production, Purchase, Store, QC, Project Manager, Site Supervisor)
- Go-live

---
## 10. Roles & Permissions [REVISED]
|| Role | Forms | Key Actions ||
||------|-------|------------||
|| Admin | ALL | Full access — all forms, reports, settings, user management ||
|| Sales - Entry | SO, Customer Master | Create/Edit SO, manage customers |
|| Costing - Entry | Costing Sheet | Create/edit Costing Sheet from SO. View: reports |
|| Costing - Approve | Costing Sheet, MR | Approve Costing Sheet (→ Project auto-created). Approve MR (Costing Approved status) |
|| Production - Entry | MR, Production Plan, BMR, RM Consumption, Packing, FGHM, PR | Create MR Draft, Production Plan, BMR, consumption entries, packing, FGHM. Initiate PR when stock needed |
|| Production - Verify MR | MR | Verify MR — checks MR qty vs SO area × BOM. Sets MR Status = Production Verified |
|| Site Supervisor | Site Consumption Entry | Create hourly/daily consumption entries per project area |
|| Purchase - Entry | PR, PO, GRN | Create/Edit PR, PO, GRN. Process PR→PO |
|| Purchase - Approve | PR, PO | Approve PR and PO within approval limits |
|| Store - Entry | GRN, MIS, FGHM, Material Return | Create GRN (goods receipt), MIS (issue to production), receive FGHM, process material returns |
|| Store - Review | ALL read-only | View: Inventory stock, GRN, PO, MR status, consumption reports |
|| QC - Entry | QC/QA | Create/Edit QC inspection records against GRN |
|| Project Manager | Project, ALL read-only | Create/Edit Projects. View: Stock, PO status, MR status, Consumption dashboard, P&L reports |

---
## 11. Forms Not in Core Loop (Excluded)
The following are **excluded** from this implementation as they fall outside the core loop:
- Service Team full module (Area → Work → Invoice) — replaced by lightweight Site Consumption Entry
- Service Invoice
- Finance (Supplier Credit Note, Customer Invoice/AR)
- Logistics (Delivery Challan, Outward)
- Vehicle & Transport
- Rate Comparison (simplified — standalone reference only)

**Site Consumption Entry** IS in scope (see §6.7) — this replaces the full Service Team module. It provides hourly/daily task-level consumption tracking without the overhead of full service workflow.

## Implementation Plan Enhancements (Overcoming Lag Points)

### Goal
Accelerate the end‑to‑end flow by eliminating 15 identified bottlenecks across Costing → Production Plan → MR → Procurement → Production → Site Consumption.

### Phase‑by‑Phase Improvements

#### Phase 1 – Master Data Foundation (Weeks 1‑2)
- **Automate look‑up population**: Use Deluge `on Add → after` to auto‑populate HSN, GST%, UOM from Item Master.
- **Validate master data**: Add validation rules (mandatory fields, unique codes) and schedule a weekly data‑quality report.

#### Phase 2 – Sales & Project (Weeks 3‑4)
- **SO → Project automation**: Deluge `on Submit` creates Project record instantly and copies SO fields.
- **Dashboard**: Real‑time SO‑to‑Project conversion dashboard for sales managers.

#### Phase 3 – Costing Sheet, Production Plan & MR (Weeks 4‑6) [REVISED]
1. **Costing Sheet auto-expansion**: On SO Reference selection, Deluge expands SO System Lines → System Composition → BOM → pre-populates all Section A material lines. No manual RM re-entry.
2. **Costing Sheet → Project auto-creation**: On Costing Approved, auto-create Project (if not yet created). Escalate to admin if Costing stuck >24 hr.
3. **Production Plan auto-creation**: On Costing Approved, auto-create Production Plan (Draft) with all material lines carried forward.
4. **Stock check at plan time**: Available Stock = physical stock − Σ(Assigned Qty from all unreleased MRs). Prevents double-allocation across projects.
5. **Auto-PR on shortage**: On Production Plan Release → for every line where Shortage > 0 → auto-create project‑tagged PR. Notify Purchase with priority from plan.
6. **MR auto-derived from Costing Sheet**: All 4 cost components pre-filled. No manual re-entry. SO↔BOM↔MR cross-validation: if Σ(Assigned Qty) vs Σ(SO Area × BOM) differs >5% → flag; >10% → block.
7. **Tighter SLAs**: MR Draft >2 hr → reminder. Production Verified >2 hr → escalation to Costing lead. Costing Approved >1 hr → auto-release.
8. **MR Release cascade**: Auto-create MIS draft + notify Store + Production simultaneously.

#### Phase 4 – Procurement (As Needed) (Weeks 7‑8)
- **PR Auto‑Creation**: From Production Plan shortage (not from MR). Earlier in the flow.
- **PO Dual Numbering**: RM vs RMWAD driven by Item Master flag.
- **GRN Partial Posting**: Line‑item checkbox; on save, immediately update stock.
- **QC Integration**: Auto‑create QC record on GRN save.

#### Phase 5 – Production, Inventory & Site Operations (Weeks 8‑10) [EXPANDED]
- **MIS Posting Auto‑Stock Update**: Immediate RM stock deduction + timestamp.
- **BMR / RM Consumption Real‑Time Update**: Each entry increments `Consumed Qty` on MR Allocation (by Project ID + Item Code).
- **80% Consumption Alert**: Real-time formula. ≥80% + flag ON → pop‑up, banner, email. 100% → escalation to PM + Purchase.
- **FGHM Inline Acceptance**: Mobile-optimized. On save, FG stock + and mark MR Allocation Fully Consumed.
- **Site Consumption Entry [NEW]**: Hourly/daily task-level tracking per project area. All entries resolve to MR Allocation. Enables project inventory deduction in real time.
- **Material Return Entry [NEW]**: Return unused RM to Store. Credits Consumed Qty and restores available stock.

#### Phase 6 – Reports & Dashboards (Weeks 10‑11) [EXPANDED]
- **MR Status Dashboard**: Counts per status, drill-through to individual MR.
- **Stock Dashboard**: RM & FG stock levels, min/max alerts, per-project filter.
- **Project Inventory Status Report [NEW]**: Per RM per project: Assigned vs Issued vs Consumed vs Remaining. Single source of truth for project P&L.
- **Project P&L real-time view [NEW]**: Costing Sheet Total − Material Consumption Costs − Procurement Costs.
- **Consumption Dashboard**: Items nearing 80%/100% with direct link to MR Allocation.
- **Site Consumption Report [NEW]**: Hourly/daily consumption by work area, project, RM.
- **Costing vs Actual Report [NEW]**: Planned (Costing Sheet) vs actual (Site Consumption + BMR) cost variance.
- **Procurement Lag Report**: PR→PO→GRN cycle time per item.

#### Phase 7 – UAT & Go-Live (Weeks 11‑12) [EXPANDED]
- **End‑to‑End Test Scripts** covering:
  - Full flow: SO → Costing Sheet → Production Plan → MR → MIS → Production → FGHM → Site Consumption → Project P&L
  - Shortage flow: Costing Sheet → Production Plan → Auto-PR → PO → GRN → MR
  - Alert triggers: 80%, 100%, and SO↔BOM↔MR mismatch
  - Material Return: project inventory credit + stock restoration
  - Partial GRN and stock rollback
- **UAT** with all 8 roles: Sales, Costing, Production, Purchase, Store, QC, Project Manager, Site Supervisor
- **Go‑Live Checklist**: All workflows, notifications, alerts, dashboards, and SLA monitors validated

### Risk Mitigation Summary [REVISED]
| Lag Point | Mitigation |
|-----------|------------|
| Costing Sheet not created after SO | Auto-reminder to Costing team 4 hr after SO acceptance. Escalate at 24 hr |
| Costing Sheet stuck in review | SLA notifications: 4 hr → reminder, 8 hr → escalation to Costing Head |
| MR manual data entry | MR auto-derived from Costing Sheet + Production Plan. Zero manual re-entry |
| SO↔MR quantity mismatch | Cross-validation on MR creation: >5% flag, >10% block |
| Double-allocation of RM across projects | Available Stock = physical − Σ(other unreleased MR allocations) |
| MR stuck in Draft/Pending Verification | 2 hr SLA → automated reminder + escalation |
| Costing approval delay | 2 hr SLA → escalation to Costing lead. 1 hr auto-release after approval |
| No MIS until MR Released | Auto‑create MIS draft on MR Release |
| Procurement delay when stock low | Auto-PR on Production Plan Release (earlier in flow than MR Release) |
| GRN posting delay | Partial GRN checkbox; immediate stock update on save |
| No site-level consumption tracking | **Site Consumption Entry** — hourly/daily per area. Resolves to MR Allocation |
| Excess RM at site not returned | **Material Return Entry** — credits project allocation, restores store stock |
| Consumption alerts delayed | Real‑time alert on every Site Consumption/BMR entry |
| FG stock not linked to project | FG inventory tracked per Project ID |
| No project P&L visibility until close | **Real-time Project P&L computed view** — available on demand |
| Reporting lag | Event-driven dashboard refresh (1 min cache). Critical alerts fire instantly |

### Success Criteria [REVISED]
- **Costing Sheet → Approved** ≤ 24 hours from SO acceptance
- **Production Plan Released** ≤ 4 hours from Costing Sheet approval
- **MR → Released** ≤ 4 hours from submission (auto-derived, no manual entry)
- **SO↔BOM↔MR mismatch** detected on creation; zero mismatched MRs reach Release
- **MIS posting** ≤ 15 min of MR Release when stock available
- **Procurement cycle** (PR→PO→GRN) ≤ 24 hours for stock‑out items
- **80% consumption alert** fires within 1 min of threshold breach (real-time, not cron)
- **Site Consumption Entry** created daily per active project work area
- **Project Inventory Status** report reflects every consumption/return within 1 min
- **FG stock** reflects availability within 1 min of FGHM acceptance
- **Project P&L** available on-demand, updated in real time
- All dashboards refresh ≤ 5 min and show accurate counts
- All roles trained and UAT signed off before go-live

### Implementation Steps (High‑Level)
1. **Review & Update Deluge Scripts** – add validation, auto‑creation, and workflow steps as per phases.
2. **Build Dashboards & Reports** using Zoho Creator reporting tools.
3. **Configure Alerts & Notifications** (in‑app, email, banner).
4. **Create Test Data Sets** covering all streams and edge cases.
5. **Run UAT**, collect feedback, adjust scripts.
6. **Deploy to Production**, monitor SLA metrics, iterate.

---