# Chemsol — Zoho Creator ERP
## BRD · PRD · RFP (Consolidated)

| Document | Version | Date |
|----------|---------|------|
| BRD + PRD + RFP | 1.0 | 03-Jul-2026 |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Business Requirements (BRD)](#2-business-requirements-brd)
3. [Product Requirements (PRD) — Form Specifications](#3-product-requirements-prd--form-specifications)
   - 3.1 Master Data (Global)
   - 3.2 Sales
   - 3.3 Project Management (Root Entity)
   - 3.4 Procurement
   - 3.5 Inventory / Stores
   - 3.6 Production
   - 3.7 Project P&L (Computed View)
4. [RFP — Technical Specifications](#4-rfp--technical-specifications)
5. [Appendices](#5-appendices)

---

## 1. Executive Summary

**Company:** Chemsol — Flooring & Construction Materials  
**Platform:** Zoho Creator (India .in instance)  
**Architecture:** Two-Stream — Stream A (Pre-Project): Procurement for stock, no Project ID. Stream B (Project-Centric): SO (Supply+Apply)→Project triggers downstream forms with Project ID; SO (Supply Only) is a direct FG sale with no Project.  
**Users:** Purchase, Sales, Store & Logistics, Account & Finance, Admin, Project Coordinator, Project Managers (3)  
**Modules:** 7 groups — Master Data, Sales, Project Management, Procurement, Inventory, Production, P&L  
**Forms:** 18 forms + 2 computed reports  
**Implementation:** Zoho Creator GenAI Builder (Build applications faster with GenAI)

### Subform Convention (Critical for GenAI Builder)

Zoho Creator GenAI requires explicit demarcation of form structure. Every form with N-line-items **MUST** be structured as:

```
FORM: [Form Name]
  ├── HEADER — Single-value fields (one per form)
  ├── SUBFORM: [Name] — Repeating table with N rows (line items)
  │   └── Fields: col1, col2, col3...
  └── FOOTER — Summary/totals/terms (single-value after subform)
```

**This document follows this convention exactly.** Feed each form section directly into Zoho Creator GenAI.

---

## 2. Business Requirements (BRD)

### 2.1 Business Context

Chemsol manufactures and applies industrial flooring systems (Epoxy, PU, Demarcation, Anti-Static, Coving) across client sites. Each engagement is a **Project** — from sales acceptance through procurement, production, site execution, and handover.

### 2.2 Pain Points (Current State)

| Problem | Impact |
|---------|--------|
| Paper-based / spreadsheet tracking across 18+ forms | Data loss, no audit trail |
| No project-level cost visibility | Cannot calculate project profitability |
| Manual procurement tracking | Delays, no PO vs GRN reconciliation |
| No real-time inventory visibility | Stockouts / overstocking |
| No standardized QC process | Quality issues not tracked |

### 2.3 Business Objectives

| Objective | KPI |
|-----------|-----|
| Digitize all 18+ paper forms | 100% forms online |
| Project-level P&L per project | Margin % visible on project close |
| Procurement cycle tracking | PR→PO→GRN cycle time reduced |
| Real-time inventory | Stock accuracy ≥ 95% |
| QC tracking | All GRN items QC-checked |

### 2.4 Stakeholders

| Role | Department | Access |
|------|------------|--------|
| Purchase - Entry | Purchase | Create/Edit: PR, PO, Rate Comparison, GRN |
| Purchase - Approve | Purchase | Approve PR, PO within limits |
| Purchase - Review | Purchase | View-only all purchase forms |
| Store - Entry | Store & Logistics | Create/Edit: GRN, MIS, Material Return, FG Receiving |
| Production - Entry | Production | Create/Edit: MR, BMR, Production Planning, Packing |
| Sales - Entry | Sales | Create/Edit: SO, Customer Master |
| Project Manager | Projects | Create/Edit: Projects, Tasks, view all project data |
| Project Coordinator | Projects | Create/Edit: MR, view production & project status |
| QC - Entry | QC | Create/Edit: QC/QA forms |
| Account & Finance | Finance | View-only: PO, GRN, Reports |
| Admin | Admin | Full access, user management, approval matrix |

---

## 3. Product Requirements (PRD) — Form Specifications

### Convention: Unified Field Table

Every form uses a **single field table** with a **Section** column. The Section column tells Zoho Creator GenAI where each field belongs:
- **Header** — single-value field at top of form (one per form record)
- **Subform** — this field IS the subform (type: Subform, N rows). Its child columns are listed underneath with `—` prefix and `Subform Column` section.
- **Footer** — single-value field placed after all subforms (summary/totals/terms)

---

### 3.1 Master Data (Global)

---

#### FORM: Purchase Item Muster

**Purpose:** Central item catalog (RM, Packaging, Consumables, etc.)  
**Subforms:** None

| # | Field Name | Field Type | Section | Req | Notes / Options |
|---|---|---|---|---|---|
| 1 | Category of Purchase Item | Dropdown | Header | * | 1.RM, 2.Packaging Material, 3.Tools & Consumable, 4.Maintenance & Utility, 5.Capital & Assets, 6.Administration |
| 2 | Purchase Item Code | Text (Autogen) | Header | * | Auto-generated per category |
| 3 | Purchase Item Name | Text | Header | * | — |
| 4 | UOM | Dropdown | Header | * | Nos / Kg / Ltr / Mtr / Kit |
| 5 | HSN Code | Text | Header | * | For GST invoicing |
| 6 | GST % | Number | Header | * | — |
| 7 | Min Stock | Number | Header | | Alert threshold |
| 8 | Max Stock | Number | Header | | Alert threshold |
| 9 | Standard Rate | Currency | Header | | Default purchase rate |
| 10 | Preferred Supplier | Multi-select Lookup | Header | | From Supplier Master |
| 11 | Lead Time | Number (Days) | Header | | — |
| 12 | Status | Dropdown | Header | * | Active / Inactive |

**Automation:** Item Code auto-generated. Preferred Supplier multi-select from Supplier Master. Min/Max stock alerts.

---

#### FORM: Supplier Master

**Purpose:** Vendor/supplier directory  
**Subforms:** None

| # | Field Name | Field Type | Section | Req | Notes / Options |
|---|---|---|---|---|---|
| 1 | Supplier Code | Text (Autogen) | Header | * | Auto on new registration |
| 2 | Supplier Name | Text | Header | * | — |
| 3 | Supplier Type | Dropdown | Header | * | — |
| 4 | GSTIN | Text | Header | * | 15-digit GSTIN |
| 5 | PAN No. | Text | Header | * | — |
| 6 | Contact Person | Text | Header | * | — |
| 7 | Mobile No. | Phone | Header | * | — |
| 8 | Alternate Mobile No. | Phone | Header | | — |
| 9 | Email ID | Email | Header | * | — |
| 10 | Address | Multi-line | Header | * | — |
| 11 | Pincode | Text | Header | * | — |
| 12 | Bank Name | Text | Header | * | — |
| 13 | Account No. | Text | Header | * | — |
| 14 | IFSC Code | Text | Header | * | — |
| 15 | Payment Terms | Text | Header | * | — |
| 16 | Credit Days | Number | Header | | — |
| 17 | Status | Dropdown | Header | * | Active / Inactive |

---

#### FORM: System Master

**Purpose:** Flooring system definitions (EP01 = 1mm Epoxy)  
**Subforms:** None

| # | Field Name | Field Type | Section | Req | Notes / Options |
|---|---|---|---|---|---|
| 1 | System Code | Text (Autogen) | Header | * | Prefix+Number (EP01, PU02) |
| 2 | System Name | Text | Header | * | Description |
| 3 | Category | Dropdown | Header | * | EP / PU / DEM / NUM / ARR / ANTI / ESD / FIL / COV |
| 4 | Thickness | Text | Header | | e.g., 1mm, 2mm |
| 5 | UOM | Dropdown | Header | * | SqM / Mtr / Nos |
| 6 | Description | Multi-line | Header | | — |
| 7 | Status | Dropdown | Header | * | Active / Inactive |

---

#### FORM: System Composition (1C — System → FG Mapping)

**Purpose:** Which FGs make up each system (e.g., EP01 = Floorchem 300 Matt [R] + Floorchem 300 Matt [H])  
**Subforms:** System → FG Line Items (N rows)

| # | Field Name | Field Type | Section | Req | Notes / Options |
|---|---|---|---|---|---|---|
| 1 | Composition ID | Text (Autogen) | Header | * | — |
| 2 | System Code | Lookup | Header | * | From System Master |
| 3 | System Name | AutoFetch | Header | * | — |
| 4 | Revision No | Text | Header | | Version control |
| 5 | **System → FG Line Items** | **Subform (N rows)** | **Subform** | * | FG composition per system |
|   | — Sr No | Auto | Subform Column | * | Sequence |
|   | — FG Product Code | Lookup | Subform Column | * | From Item Muster (FG type) |
|   | — FG Product Name | AutoFetch | Subform Column | * | — |
|   | — Qty per System Unit | Number | Subform Column | * | E.g., 0.75 Kg per unit area |
|   | — UOM | AutoFetch | Subform Column | * | From Item Muster |
|   | — Rate | Currency | Subform Column | * | FG unit rate |

**Automation:** FG Code ↔ FG Name cross-fill. UOM auto-fetch from Item Muster. AutoFetch target: SO pricing, Production Planning.

---

#### FORM: BOM / FG Formulation (1D — FG → RM Mapping)

**Purpose:** Which RMs make up each FG with ratios (e.g., Floorchem 300 Matt [R] = RK Resin 32% + BA 27.3% + Talc 20% + ...)  
**Subforms:** FG → RM Line Items (N rows)

| # | Field Name | Field Type | Section | Req | Notes / Options |
|---|---|---|---|---|---|---|
| 1 | BOM No | Text (Autogen) | Header | * | — |
| 2 | FG Product Code | Lookup | Header | * | From Item Muster (FG type) |
| 3 | FG Product Name | AutoFetch | Header | * | — |
| 4 | Revision No | Text | Header | | Version control |
| 5 | Date | Date | Header | * | Today's Date |
| 6 | Status | Dropdown | Header | * | Draft / Approved / Released |
| 7 | **FG → RM Line Items** | **Subform (N rows)** | **Subform** | * | RM formulation per FG |
|   | — Sr No | Auto | Subform Column | * | Sequence |
|   | — RM Item Code | Lookup | Subform Column | * | From Item Muster (RM type) |
|   | — RM Item Name | AutoFetch | Subform Column | * | — |
|   | — Qty per 100 Kg FG | Number | Subform Column | * | E.g., RK Resin 32 Kg, BA 27.33 Kg |
|   | — Ratio % | Formula | Subform Column | * | Auto-calculated (Qty / Total × 100) |
|   | — UOM | AutoFetch | Subform Column | * | From Item Muster |
|   | — Waste % | Number | Subform Column | | Standard waste factor |

**Automation:** RM Code ↔ RM Name cross-fill. UOM auto-fetch from Item Muster. Formula: Ratio % = Qty / Σ Qty × 100. AutoFetch target: BMR, MR calculation, Costing.

---

#### FORM: Customer / Site Master

**Purpose:** Client organization directory with site addresses  
**Subforms:** None

| # | Field Name | Field Type | Section | Req | Notes / Options |
|---|---|---|---|---|---|
| 1 | Customer Code | Text (Autogen) | Header | * | — |
| 2 | Client Org Name | Text | Header | * | — |
| 3 | Contact Person | Text | Header | * | — |
| 4 | Contact No | Phone | Header | * | — |
| 5 | Alt Contact No | Phone | Header | | — |
| 6 | Email | Email | Header | * | — |
| 7 | GST No | Text | Header | * | — |
| 8 | PAN | Text | Header | * | — |
| 9 | Regd Address | Multi-line | Header | * | — |
| 10 | Site Name | Text | Header | * | — |
| 11 | Site Address | Multi-line | Header | * | — |
| 12 | Site Manager/Incharge | Text | Header | | — |
| 13 | Site Contact No | Phone | Header | | — |

---

### 3.2 Sales

---

#### FORM: Sales / Work Order Master (SO)

**Purpose:** Customer order intake with **conditional line-item subform** driven by a `Sales Type` controlling field.  
**Mode:** Dual — (A) **Supply+Apply** sells a **SYSTEM** (auto-creates Project, Stream B root); (B) **Supply Only** sells **FG directly** (NO Project, direct stock sale).  
**Controlling Field:** `Sales Type` (Header dropdown) toggles subform visibility + downstream automation.  
**Subforms:** Subform A — System Lines (N rows, Supply+Apply), Subform B — FG Lines (N rows, Supply Only), Commission (1 row, conditional)

| # | Field Name | Field Type | Section | Req | Notes / Options |
|---|---|---|---|---|---|
| 1 | Date | Date | Header | * | Today's Date |
| 2 | Employee Name | Text | Header | * | Sales person |
| 3 | Customer Code | Lookup | Header | | From Customer Master |
| 4 | Client Org Name | Text | Header | * | — |
| 5 | Contact Person | Text | Header | * | — |
| 6 | Contact No | Phone | Header | * | — |
| 7 | Alt Contact No | Phone | Header | | — |
| 8 | Email | Email | Header | * | — |
| 9 | GST No | Text | Header | * | — |
| 10 | PAN | Text | Header | * | — |
| 11 | Regd Address | Multi-line | Header | * | — |
| 12 | Sales/Work Order No | Text (Autogen) | Header | * | — |
| 13 | Sales/Work Order Date | Date | Header | * | — |
| 14 | Site Name | Text | Header | * | — |
| 15 | Site Address | Multi-line | Header | * | — |
| 16 | Site Manager/Incharge | Text | Header | | — |
| 17 | Contact No (Site) | Phone | Header | | — |
| 18 | Project Type | Dropdown | Header | | 1.Industrial, 2.Commercial — **conditional: shown/required only when Sales Type = Supply+Apply** |
| 19 | **Sales Type (CONTROLLING FIELD)** | Dropdown | Header | * | 1. Supply+Apply (sell SYSTEM → auto-creates Project) · 2. Supply Only (sell FG directly → NO Project). Drives subform visibility + automation. |
| 20 | **Subform A — System Lines** | **Subform (N rows)** | **Subform** | | **Visible when Sales Type = Supply+Apply.** System/Product line items |
|   | — System Code | Lookup | Subform Column | * | From System Master |
|   | — System Name | AutoFetch | Subform Column | * | — |
|   | — Thickness | Text | Subform Column | | e.g., 1mm, 2mm |
|   | — Area | Number | Subform Column | * | Area in SqM |
|   | — UOM | Dropdown | Subform Column | | SqM / Mtr / Nos (area UOM) |
|   | — Rate | Currency | Subform Column | * | Per-unit system rate |
|   | — Amount | Formula | Subform Column | * | Area × Rate |
|   | — Commission % | Number | Subform Column | | Per-line commission % |
|   | — Warranty | Text | Subform Column | | Per-line warranty (copies to Project) |
|   | — Transport Scope | Dropdown | Subform Column | | Per-line transport scope |
| 21 | **Subform B — FG Lines** | **Subform (N rows)** | **Subform** | | **Visible when Sales Type = Supply Only.** Direct FG sale — NO Project |
|   | — FG Code | Lookup | Subform Column | * | From FG Handover / Item Muster (FG type) |
|   | — FG Name | AutoFetch | Subform Column | * | — |
|   | — Qty | Number | Subform Column | * | FG quantity sold |
|   | — UOM | AutoFetch | Subform Column | * | From Item Muster |
|   | — Rate | Currency | Subform Column | * | FG unit rate |
|   | — Amount | Formula | Subform Column | * | Qty × Rate |
| 22 | **Commission** | **Subform (1 row, conditional)** | **Subform** | | Visible if Commission checkbox checked (Supply+Apply) |
|   | — Commission | Checkbox | Subform Column | | Show/hide toggle for this subform |
|   | — Based On | Dropdown | Subform Column | * | Percentage / Fix Amount |
|   | — Commission Amount | Currency | Subform Column | * | — |
|   | — Commission Paid To | Text | Subform Column | | — |
| 23 | Total Work Order Amount | Formula | Footer | * | Sum of **active** subform line Amounts (System or FG) |
| 24 | Payment Terms | Text | Footer | * | — |
| 25 | Transportation Scope | Dropdown | Footer | | — |
| 26 | Transportation Amount | Currency | Footer | | — |
| 27 | Lead Time | Number (Days) | Footer | | — |
| 28 | PO/BOQ Attachment | File upload | Footer | | Multiple files |
| 29 | Warranty | Text | Footer | | — |
| 30 | Is Proper System Required | Checkbox | Footer | | — |

**Controlling-Field Logic (Zoho Creator):** One SO form with **two subforms**. A show/hide rule on `Sales Type` displays Subform A (Supply+Apply) or Subform B (Supply Only); the inactive subform is hidden and its validation skipped. At least one line is required in the active subform.

**Automation per Sales Type:**
- **Supply+Apply:** Subform A shown → validate ≥1 system line → on acceptance **auto-creates Project** (Stream B root); Systems subform copied from SO System Lines → downstream MR/MIS/Production/Service/Finance/Logistics carry Project ID → **MR Material Allocation + 80% alert active**. System composition (System→FG→RM via BOM) drives backend consumption.
- **Supply Only:** Subform B shown → validate ≥1 FG line → **NO Project created** → routes to FG dispatch / customer invoice only (Stream A-adjacent stock sale). **No MR allocation, no 80% alert, no project consumption tracking.**

---

### 3.3 Project Management (Root Entity)

---

#### FORM: Create Project

**Purpose:** Central hub record. Auto-created from SO acceptance.  
**Subforms:** Systems (N rows), Task Budget (N rows)

| # | Field Name | Field Type | Section | Req | Notes / Options |
|---|---|---|---|---|---|
| 1 | Project ID | Text (Autogen) | Header | * | — |
| 2 | Project Name | Text | Header | * | — |
| 3 | SO Reference | Lookup | Header | | Auto-filled from SO |
| 4 | Address | Multi-line | Header | * | — |
| 5 | Project Manager | User lookup | Header | * | — |
| 6 | Execution Base | Dropdown | Header | * | 1.Area Basis, 2.Day Basis |
| 7 | Start Date | Date | Header | * | — |
| 8 | End Date | Date | Header | * | — |
| 9 | Project Cost | Currency | Header | * | — |
| 10 | Adjustments | Currency | Header | | Cost adjustment |
| 11 | **Systems** | **Subform (N rows)** | **Subform** | | Systems/areas within this project |
|   | — System Code | Lookup | Subform Column | * | From System Master |
|   | — Description | Text | Subform Column | | — |
|   | — Area | Number | Subform Column | | — |
|   | — UOM | Dropdown | Subform Column | | — |
| 12 | **Task Budget** | **Subform (N rows)** | **Subform** | * | Budget + Actuals for 5 categories |
|   | — Category | Dropdown | Subform Column | * | Transport / Execution / Manpower / Tools / Overhead |
|   | — Description | Text | Subform Column | * | Subtask name or work item |
|   | — Qty / Area | Number | Subform Column | | Area for Execution, count for others |
|   | — Rate | Currency | Subform Column | | Per unit rate (budgeted) |
|   | — Amount | Formula | Subform Column | | Qty × Rate (budgeted) |
|   | — Manpower | Number | Subform Column | | Head count (if applicable) |
|   | — Actual Qty | Number | Subform Column | | Actual quantity consumed / work done |
|   | — Actual Rate | Currency | Subform Column | | Actual per-unit rate paid |
|   | — Actual Amount | Formula | Subform Column | | Actual Qty × Actual Rate |

**Automation:** Auto-create from SO acceptance. Systems autofetch from SO line items. Task categories fixed. If Execution Base = Day Basis → highlight Manpower tasks. Actual Amounts feed Project P&L.

---

### 3.4 Procurement

---

#### FORM: Purchase Requisition (PR)

**Purpose:** Internal request to purchase materials. Dept: Production & R&D  
**Subforms:** Line Items (N rows)

| # | Field Name | Field Type | Section | Req | Notes / Options |
|---|---|---|---|---|---|
| 1 | PR Number | Text (Autogen) | Header | * | PR-YYYY-XXXX |
| 2 | PR Date | Date | Header | * | Today's Date |
| 3 | Reference | Text | Header | | Manual reference |
| 4 | RM Type | Dropdown | Header | * | Coding / Non-Coding |
| 5 | Department | AutoFetch | Header | * | As per user login |
| 6 | Approved By | User lookup | Header | | Filled after approval |
| 7 | Status | Dropdown | Header | * | Draft / Pending Approval / Approved / Rejected |
| 8 | **Line Items** | **Subform (N rows)** | **Subform** | * | Items to purchase |
|   | — Sr | Number | Subform Column | * | Auto |
|   | — Item Code | Lookup | Subform Column | * | From Purchase Item Muster |
|   | — Item Name | AutoFetch | Subform Column | * | Autofill on Item Code |
|   | — Qty | Number | Subform Column | * | — |
|   | — Item Description | Multi-line | Subform Column | | — |
|   | — UOM | AutoFetch | Subform Column | * | From Item Muster |
|   | — Lead Time | AutoFetch | Subform Column | | Days, from Item Muster |

**Automation:** Item Code ↔ Item Name bidirectional autofill. UOM autofill. Lead Time autofill. Status workflow. Notification to Purchase dept on approval.

---

#### FORM: Rate Comparison

**Purpose:** Compare up to 5 suppliers per PR item. Finalize supplier + rate.  
**Subforms:** Supplier Comparison (5 fixed rows)

| # | Field Name | Field Type | Section | Req | Notes / Options |
|---|---|---|---|---|---|
| 1 | Date | Date | Header | * | Today's Date |
| 2 | PR Reference No | Lookup | Header | * | From PR Master |
| 3 | Product No | AutoFetch | Header | * | From PR items |
| 4 | Product Name | AutoFetch | Header | * | From PR items |
| 5 | **Supplier Comparison** | **Subform (5 rows)** | **Subform** | * | Fixed 5-row comparison grid |
|   | — Supplier 1 | Lookup | Subform Column | | From Supplier Master + Price + Credit |
|   | — Supplier 2 | Lookup | Subform Column | | From Supplier Master + Price + Credit |
|   | — Supplier 3 | Lookup | Subform Column | | From Supplier Master + Price + Credit |
|   | — Supplier 4 | Lookup | Subform Column | | From Supplier Master + Price + Credit |
|   | — Supplier 5 | Lookup | Subform Column | | From Supplier Master + Price + Credit |
| 6 | Finalised Supplier | Lookup | Footer | * | Selected from above 5 |
| 7 | Final Rate | Currency | Footer | * | — |
| 8 | PO No | Text | Footer | | Linked after PO creation |
| 9 | PO Release Date | Date | Footer | | — |
| 10 | Remark | Multi-line | Footer | | — |

**Automation:** Supplier dropdown → lookup from Supplier Master. Notification "Rate Comparison Data Missing" to Purchase dept if data incomplete.

---

#### FORM: Purchase Order (PO)

**Purpose:** Legal PO sent to supplier. Dual series: RM (Non-Coding) / RMWAD (Coding)  
**Subforms:** Line Items (N rows, with GST split)

| # | Field Name | Field Type | Section | Req | Notes / Options |
|---|---|---|---|---|---|
| 1 | RM Type | Dropdown | Header | * | 1.Coding, 2.Non Coding |
| 2 | PO Number | Text (Autogen) | Header | * | RMWAD-YYYY-XXXX / RM-YYYY-XXXX |
| 3 | PO Date | Date | Header | * | Today's Date |
| 4 | Supplier Code | Lookup | Header | * | From Supplier Master |
| 5 | Supplier Name | AutoFetch | Header | * | Autofill from Supplier Code |
| 6 | PR Reference | Lookup | Header | | From PR |
| 7 | Bill To | Dropdown | Header | * | Address list |
| 8 | Ship To | Dropdown | Header | * | Address list |
| 9 | **Line Items** | **Subform (N rows)** | **Subform** | * | PO items with GST split |
|   | — Sr No | Number | Subform Column | * | Auto |
|   | — Item Code | Lookup | Subform Column | * | From Purchase Item Muster |
|   | — Item Name | AutoFetch | Subform Column | * | — |
|   | — HSN | AutoFetch | Subform Column | * | From Item Muster |
|   | — Quantity | Number | Subform Column | * | — |
|   | — UOM | AutoFetch | Subform Column | * | From Item Muster |
|   | — Rate | Currency | Subform Column | * | From Rate Comparison or manual |
|   | — Basic Amount | Formula | Subform Column | * | Qty × Rate |
|   | — GST % | AutoFetch | Subform Column | * | From Item Muster |
|   | — GST Amount | Formula | Subform Column | * | Basic × GST% |
|   | — Total Amount | Formula | Subform Column | * | Basic + GST |
| 10 | Basic Total | Formula | Footer | * | Sum of line Basic Amount |
| 11 | CGST | Formula | Footer | * | Sum of GST/2 (intra-state) |
| 12 | SGST | Formula | Footer | * | Sum of GST/2 (intra-state) |
| 13 | IGST | Formula | Footer | * | Sum of GST (inter-state) |
| 14 | Total Amount (Words) | Formula | Footer | * | Amount in words |
| 15 | Delivery Date | Date | Footer | * | — |
| 16 | Payment Terms | Text | Footer | * | — |
| 17 | Scope of Transport | Dropdown | Footer | | Supplier / Own |
| 18 | Mode of Transport | Dropdown | Footer | | — |

**Automation:** Dual numbering based on RM Type. GST split at line level. Printable PO with e-way bill, COA, batch nos, quality clause, T&C.

---

#### FORM: Goods Receipt Note (GRN)

**Purpose:** Record goods received against PO. Partial receipt via checkbox.  
**Subforms:** Line Items (N rows, with checkbox), Transport (1 row, conditional)

| # | Field Name | Field Type | Section | Req | Notes / Options |
|---|---|---|---|---|---|
| 1 | GRN Number | Text (Autogen) | Header | * | Generated **after posting** |
| 2 | GRN Date | Date | Header | * | Today's Date |
| 3 | PO Number | Lookup | Header | * | From PO Master |
| 4 | Supplier Code | AutoFetch | Header | * | From PO |
| 5 | Supplier Name | AutoFetch | Header | * | From PO |
| 6 | Vehicle Number | Text | Header | * | — |
| 7 | Warehouse | Dropdown | Header | * | 1.Wadki, 2.Main, 3.Neelo, 4.Gurgaon, 5.Bangalore, 6.Client Site |
| 8 | Client/Site Name | Text | Header | Cnd | Visible if Warehouse = Client Site |
| 9 | Invoice Number | Text | Header | * | — |
| 10 | Invoice Date | Date | Header | * | — |
| 11 | **Line Items** | **Subform (N rows)** | **Subform** | * | GRN items with partial receipt |
|   | — Checkbox | Checkbox | Subform Column | | Select items for partial GRN |
|   | — Item Code | AutoFetch | Subform Column | * | From PO |
|   | — Item Name | AutoFetch | Subform Column | * | From PO |
|   | — Ordered Qty | AutoFetch | Subform Column | * | From PO |
|   | — Received Qty | Number | Subform Column | * | — |
|   | — QC Status | Dropdown | Subform Column | | Pending / Pass / Fail |
|   | — Packing Quality | Dropdown | Subform Column | | Good / Damaged / Partial |
| 12 | **Transport** | **Subform (1 row, conditional)** | **Subform** | | Visible if PO Scope = Own |
|   | — Transporter Name | Text | Subform Column | * | — |
|   | — Transportation Charges | Currency | Subform Column | * | — |
|   | — Local Transport | Text | Subform Column | * | — |
|   | — Loading/Unloading Charges | Currency | Subform Column | * | — |

**Automation:** GRN Number generated **after posting** (not on create). Qty added to stock only after posting — timestamp logged. Checkbox selects items for partial GRN.

---

#### FORM: QC / QA

**Purpose:** Incoming material quality inspection.  
**Subforms:** Inspection Line Items (N rows, auto-fetched from GRN)

| # | Field Name | Field Type | Section | Req | Notes / Options |
|---|---|---|---|---|---|
| 1 | QC Number | Text (Autogen) | Header | * | QC-YYYY-XXXX |
| 2 | Date | Date | Header | * | Today's Date |
| 3 | GRN Number | Lookup | Header | * | From GRN |
| 4 | Supplier Name | AutoFetch | Header | * | From GRN |
| 5 | **Inspection Line Items** | **Subform (N rows)** | **Subform** | * | QC inspection per item |
|   | — Item No | AutoFetch | Subform Column | * | From GRN |
|   | — Item Name | AutoFetch | Subform Column | * | From GRN |
|   | — Inspection Date | Date | Subform Column | | — |
|   | — Viscosity Result | Text | Subform Column | | — |
|   | — Density Result | Text | Subform Column | | — |
|   | — Color Result | Text | Subform Column | | — |
|   | — Moisture Result | Text | Subform Column | | — |
|   | — Accepted Qty | Number | Subform Column | * | — |
|   | — Rejected Qty | Number | Subform Column | * | — |
|   | — Packaging Quality | Dropdown | Subform Column | | Good / Damaged |
|   | — QC Status | Dropdown | Subform Column | * | Pass / Fail / Hold |
|   | — Remarks | Multi-line | Subform Column | * | — |

---

### 3.5 Inventory / Stores

---

#### FORM: Material Requisition (MR)

**Purpose:** Request materials from store. Dept: Production & R&D. **MR is the project implementation cost baseline** — carries four cost components (Material, Application, Transportation, Tools & Tackles) summing to the Total MR Cost that Costing approves (alongside SO as revenue baseline). MR is NOT just RM allocation.  
**Subforms:** Line Items (N rows), Material Allocation (N rows, feeds Material Cost), Application Cost (N rows), Transportation Cost (N rows), Tools & Tackles (N rows). All four cost components sum to the Total MR Cost.  
**Status Workflow:** Draft → Pending Production Verification → Production Verified → Costing Approved → Released

| # | Field Name | Field Type | Section | Req | Notes / Options |
|---|---|---|---|---|---|
| 1 | MR Number | Text (Autogen) | Header | * | MR-YYYY-XXXX |
| 2 | MR Date | Date | Header | * | Today's Date |
| 3 | Requisition Type | Dropdown | Header | * | Production / R&D |
| 4 | Batch Number | Text | Header | | — |
| 5 | Project ID | Lookup | Header | * | From Project Master (Stream B root) — anchors the MR (project implementation cost baseline with 4 cost components) |
| 6 | Department | AutoFetch | Header | * | As per user login |
| 7 | Requested By | Text | Header | * | Employee Name |
| 8 | Priority | Dropdown | Header | * | Normal / Urgent / Emergency |
| 9 | **MR Status** | **Dropdown** | **Header** | * | **Draft / Pending Production Verification / Production Verified / Costing Approved / Released** — governs downstream execution |
| 10 | **Line Items** | **Subform (N rows)** | **Subform** | * | Materials requested (RM only) |
|   | — Sr No | Number | Subform Column | * | Auto |
|   | — Item Code | Lookup | Subform Column | * | From Purchase Item Muster |
|   | — Item Name | AutoFetch | Subform Column | | — |
|   | — Category | AutoFetch | Subform Column | | From Item Muster |
|   | — UOM | AutoFetch | Subform Column | * | From Item Muster |
|   | — Available Stock | AutoFetch | Subform Column | | From current stock |
|   | — Required Qty | Number | Subform Column | * | — |
|   | — Remarks | Multi-line | Subform Column | | — |
| 11 | **Material Allocation** | **Subform (N rows)** | **Subform** | * | **Material Cost component** — one line per allocated RM (Σ Assigned Qty × Rate = Material Cost) |
|   | — Item Code | Lookup | Subform Column | * | From Purchase Item Muster (RM) |
|   | — Item Name | AutoFetch | Subform Column | * | — |
|   | — UOM | AutoFetch | Subform Column | * | From Item Muster |
|   | — Assigned Qty | Number | Subform Column | * | Allocation baseline for this Project (e.g., X=10, Y=20, Z=30). Defaults from Required Qty |
|   | — Rate | Currency | Subform Column | * | Per-unit RM rate |
|   | — Material Cost | Formula | Subform Column | * | = Assigned Qty × Rate |
|   | — Allocation Ratio % | Formula | Subform Column | * | = Assigned Qty ÷ Σ Assigned Qty × 100 |
|   | — 80% Threshold Alert Flag | Checkbox | Subform Column | | Default ON — alert when consumption ≥ 80% of Assigned Qty |
|   | — Consumed Qty | Number (auto) | Subform Column | | Running total; incremented by FG production + Site entries |
|   | — Consumption % | Formula | Subform Column | | = Consumed Qty ÷ Assigned Qty × 100 |
|   | — Alert Triggered | Checkbox (readonly) | Subform Column | | Auto-set TRUE once Consumption % ≥ 80% |
| 12 | **Application Cost** | **Subform (N rows)** | **Subform** | | **Labour/execution cost to apply material on site** |
|   | — Activity | Text | Subform Column | | e.g., surface prep, laying, finishing |
|   | — UOM | Dropdown | Subform Column | | — |
|   | — Qty / Area | Number | Subform Column | | — |
|   | — Rate | Currency | Subform Column | | Per unit |
|   | — Amount | Formula | Subform Column | | = Qty/Area × Rate |
| 13 | **Transportation Cost** | **Subform (N rows)** | **Subform** | | **Transport of material to site** |
|   | — From | Text/Lookup | Subform Column | | Source (warehouse) |
|   | — To | Text/Lookup | Subform Column | | Destination (site) |
|   | — Vehicle / Trips | Text / Number | Subform Column | | — |
|   | — Rate | Currency | Subform Column | | Per trip |
|   | — Amount | Formula | Subform Column | | = Trips × Rate |
| 14 | **Tools & Tackles** | **Subform (N rows)** | **Subform** | | **Tools/equipment needed for the project** |
|   | — Item | Text/Lookup | Subform Column | | From Item Muster |
|   | — Qty | Number | Subform Column | | — |
|   | — Rate | Currency | Subform Column | | Per unit |
|   | — Amount | Formula | Subform Column | | = Qty × Rate |
| 15 | **Total MR Cost** | Formula | Footer | * | **Material Cost + Application Cost + Transportation Cost + Tools & Tackles** — the project implementation cost baseline that Costing approves |

**Automation:** Item Code → autofetch Name, Category, UOM, Available Stock. Project ID lookup from Project Master. **Material Allocation** establishes the per-project RM budget; `Assigned Qty` defaults from `Required Qty`.  
**MR Status Workflow:**  
- **Draft** → initial state on creation  
- **Production Verified** → Production checks MR quantities against SO system requirements (via BOM — verifies item qty matches expected RM from BOM × SO system qty)  
- **Costing Approved** → Costing approves the TOTAL project cost — all four MR cost components (Material + Application + Transportation + Tools & Tackles)  
- **Released** → MR is actionable. **Without Released status, no MIS, no Production, no Logistics, no project execution.**  
**Consumption resolution (backend):** FG production (BMR / RM Consumption) and Site Manager entries expand the SO System→FG→RM via BOM and increment `Consumed Qty` on the matching MR Allocation line (`Project ID + Item Code`) — never a generic pool. **80% Alert:** when Consumption % ≥ 80% (flag ON) → pop-up + dashboard banner + email to Project Manager.

---

#### FORM: Material Issue Slip (MIS)

**Purpose:** Store issues materials against MR. Tracks issued vs balance.  
**Subforms:** Line Items (N rows, auto-fetched from MR)

| # | Field Name | Field Type | Section | Req | Notes / Options |
|---|---|---|---|---|---|
| 1 | MR No | Lookup | Header | * | From MR |
| 2 | MIS Number | Text (Autogen) | Header | * | Auto against MR |
| 3 | Date | Date | Header | * | Today's Date |
| 4 | Batch Number | Text | Header | | — |
| 5 | **Line Items** | **Subform (N rows)** | **Subform** | * | Items issued from store |
|   | — Item No | AutoFetch | Subform Column | * | From MR |
|   | — Item Name | AutoFetch | Subform Column | * | From MR |
|   | — Category | AutoFetch | Subform Column | * | From MR |
|   | — Required Qty | AutoFetch | Subform Column | * | From MR |
|   | — Issued Qty | Number | Subform Column | * | — |
|   | — Balance Qty | Formula | Subform Column | | Required − Issued |
| 6 | Issued By | Text | Footer | * | Supervisor Name |
| 7 | Handover To | Text | Footer | * | Supervisor Name |
| 8 | Remark | Multi-line | Footer | | If Any |

**Automation:** Items auto-fetched from MR. Balance Qty calculated. Stock deducted on posting.

---

#### FORM: Finish Goods Handover Note (FGHM)

**Purpose:** Production hands over FG to store.  
**Subforms:** FG Items (N rows)

| # | Field Name | Field Type | Section | Req | Notes / Options |
|---|---|---|---|---|---|
| 1 | FGH No | Text (Autogen) | Header | * | FGH-YYYY-XXXX |
| 2 | Handover Date | Date | Header | * | Today's Date |
| 3 | Client / Site Name | Text | Header | | — |
| 4 | Batch No | Text | Header | | Multiple batch numbers |
| 5 | **FG Items** | **Subform (N rows)** | **Subform** | * | FG products handed over |
|   | — Sr No | Number | Subform Column | * | Auto |
|   | — FG Product Code | Lookup | Subform Column | * | — |
|   | — FG Product Name | AutoFetch | Subform Column | * | — |
|   | — FG QTY | Number | Subform Column | * | — |
|   | — UOM | AutoFetch | Subform Column | * | — |
|   | — QC Status | Dropdown | Subform Column | * | Pass / Fail |
| 6 | Handed Over By | Text | Footer | * | Employee Name |
| 7 | Received By | Text | Footer | * | Employee Name |
| 8 | Remark | Multi-line | Footer | | — |

**Automation:** Pop-up notification to Store & Logistics on submit. Project ID lookup.

---

#### NOTE: FG Acceptance merged into FGHM

FGAN is eliminated. Acceptance is now inline within FGHM — damaged qty, accepted qty captured directly in FGHM line items. FG Stock updated on FGHM submission.

---

### 3.6 Production

---

#### FORM: Production Planning

**Purpose:** Plan production from SO demand. Net req = SO − FG Stock.  
**Subforms:** None

| # | Field Name | Field Type | Section | Req | Notes / Options |
|---|---|---|---|---|---|
| 1 | Planning No | Text | Header | * | MR Sheet No reference |
| 2 | Planning Date | Date | Header | * | — |
| 3 | Planning Period | Dropdown | Header | * | Week / Month |
| 4 | Plant | Dropdown | Header | * | — |
| 5 | Planner Name | User lookup | Header | * | — |
| 6 | Status | Dropdown | Header | * | Draft / Approved / Released |
| 7 | Remarks | Multi-line | Header | | — |
| 8 | Total SO/WO Qty | AutoFetch | Footer | * | From MR Sheet |
| 9 | FG Stock Available | AutoFetch | Footer | * | From current FG stock |
| 10 | Net Production Requirement | Formula | Footer | * | SO/WO Qty − Available FG Stock |

**Automation:** SO/WO Qty autofetch from MR Sheet. FG Stock autofetch from inventory.

---

#### FORM: Production Order

**Purpose:** Release production order per system.  
**Subforms:** None

| # | Field Name | Field Type | Section | Req | Notes / Options |
|---|---|---|---|---|---|
| 1 | Production Order No | Text (Autogen) | Header | * | — |
| 2 | MR/Planning Reference | Lookup | Header | * | From Production Planning / MR |
| 3 | System Code | Lookup | Header | * | From System Master |
| 4 | Planned Qty | Number | Header | * | — |
| 5 | Start Date | Date | Header | * | — |
| 6 | End Date | Date | Header | * | — |
| 7 | Status | Dropdown | Header | * | Planned / In Progress / Completed / On Hold |

---

#### FORM: Batch Manufacturing Record (BMR)

**Purpose:** Detailed batch record — RM, process parameters, QC results.  
**Subforms:** Raw Materials (N rows), Process Parameters (N rows), QC Test Results (N rows)

| # | Field Name | Field Type | Section | Req | Notes / Options |
|---|---|---|---|---|---|
| 1 | BMR No | Text (Autogen) | Header | * | — |
| 2 | Production Order Ref | Lookup | Header | * | — |
| 3 | Batch No | Text | Header | * | — |
| 4 | Date | Date | Header | * | — |
| 5 | System Code | Lookup | Header | * | From System Master |
| 6 | Yield / Output | Number | Header | * | — |
| 7 | Status | Dropdown | Header | * | — |
| 8 | **Raw Materials** | **Subform (N rows)** | **Subform** | * | RM consumed in batch |
|   | — Item Code | Lookup | Subform Column | * | From Purchase Item Muster |
|   | — Qty | Number | Subform Column | * | — |
|   | — Batch No | Text | Subform Column | | — |
|   | — Consumption | Number | Subform Column | | — |
| 9 | **Process Parameters** | **Subform (N rows)** | **Subform** | | Manufacturing steps |
|   | — Step | Text | Subform Column | | — |
|   | — Time | Text | Subform Column | | — |
|   | — Temperature | Text | Subform Column | | — |
|   | — Operator | Text | Subform Column | | — |
| 10 | **QC Test Results** | **Subform (N rows)** | **Subform** | | Inline QC tests |
|   | — Parameter | Text | Subform Column | | — |
|   | — Specification | Text | Subform Column | | — |
|   | — Result | Text | Subform Column | | — |
|   | — Status | Dropdown | Subform Column | | Pass / Fail |

---

#### FORM: RM Consumption Entry

**Purpose:** Track actual vs standard RM consumption.  
**Subforms:** Consumption Items (N rows)

| # | Field Name | Field Type | Section | Req | Notes / Options |
|---|---|---|---|---|---|
| 1 | BMR Reference | Lookup | Header | * | From BMR |
| 2 | **Consumption Items** | **Subform (N rows)** | **Subform** | | Actual vs standard per item |
|   | — Item Code | AutoFetch | Subform Column | | From BMR raw materials |
|   | — Standard Qty | AutoFetch | Subform Column | | From BOM |
|   | — Actual Qty | Number | Subform Column | | — |
|   | — Variance | Formula | Subform Column | | Actual − Standard |
|   | — Reason (if variance) | Text | Subform Column | | — |

---

#### FORM: Packing Entry

**Purpose:** FG product packing with material consumption.  
**Subforms:** Packing Materials (N rows)

| # | Field Name | Field Type | Section | Req | Notes / Options |
|---|---|---|---|---|---|
| 1 | BMR Reference | Lookup | Header | | — |
| 2 | FG Product Code | Lookup | Header | | — |
| 3 | Packed Qty | Number | Header | | — |
| 4 | Batch Numbers | Text | Header | | — |
| 5 | **Packing Materials** | **Subform (N rows)** | **Subform** | | Packing items consumed |
|   | — Item Code | Lookup | Subform Column | | — |
|   | — Qty | Number | Subform Column | | — |
| 6 | Label/Printing Details | Text | Footer | | — |

---

#### FORM: Rework Register

**Purpose:** Track rework on failed batches with QC revalidation.  
**Subforms:** Material Consumed (N rows)

| # | Field Name | Field Type | Section | Req | Notes / Options |
|---|---|---|---|---|---|
| 1 | BMR Reference | Lookup | Header | | — |
| 2 | Rework Reason | Multi-line | Header | | — |
| 3 | Rework Qty | Number | Header | | — |
| 4 | **Material Consumed** | **Subform (N rows)** | **Subform** | | Rework materials |
|   | — Item Code | Lookup | Subform Column | | — |
|   | — Qty | Number | Subform Column | | — |
| 5 | QC Revalidation | Dropdown | Footer | | Pass / Fail |

---

### 3.7 Project P&L Statement (Computed View)

**Purpose:** Project-level P&L. Auto-computed — no data entry. All figures from transactional forms.

| # | Line | Component | Data Source | Formula |
|---|------|-----------|-------------|---------|
| 1 | Revenue | Work Order Amount | SO System subtable | Σ (Area × Rate) per system line |
| 2 | Revenue | Transportation billed | SO header | Transportation Amount field |
| 3 | Cost | Raw Materials | PO × GRN | Σ (GRN Received Qty × PO Rate) for RM items |
| 4 | Cost | Packing Materials | PO × GRN | Σ (GRN Received Qty × PO Rate) for packing items |
| 5 | Cost | Execution (labour) | Task Budget Actuals | SUM Actual Amount (Category=Execution) |
| 6 | Cost | Manpower | Task Budget Actuals | SUM Actual Amount (Category=Manpower) |
| 7 | Cost | Transport | Task Budget + GRN Transport | SUM Actual Amount (Category=Transport) + Σ GRN Transport Charges |
| 8 | Cost | Tools | Task Budget Actuals | SUM Actual Amount (Category=Tools) |
| 9 | Cost | Overhead | Task Budget Actuals | SUM Actual Amount (Category=Overhead) |
| 10 | Cost | Loading/Unloading | GRN Transport subform | Σ Loading/Unloading Charges |
| 11 | Cost | RM Consumption (actual) | RM Consumption Entry | Σ (Actual Qty × Item Rate from PIM) |
| 12 | Cost | Packing Material (actual) | Packing Entry subform | Σ packing item costs |
| 13 | Cost | Rework | Rework Register Material subform | Σ rework material costs |
| 14 | Summary | **Total Revenue** | — | SO Work Order + SO Transportation |
| 15 | Summary | **Total Cost** | — | Material + Execution + Manpower + Logistics + Production |
| 16 | Summary | **Gross Margin** | — | Total Revenue − Total Cost |
| 17 | Summary | **Margin %** | — | (Gross Margin / Total Revenue) × 100 |

**Automation:** Auto-calculated on Project Close (snapshot stored). Real-time view from Project dashboard. Data completeness check before calculation. Margin threshold alert if < 15%. Exportable as PDF.

---

## 4. RFP — Technical Specifications

### 4.1 Platform Requirements

| Requirement | Specification |
|-------------|---------------|
| Platform | Zoho Creator (India .in instance) |
| Build Method | GenAI Builder (Build applications faster with GenAI) |
| Deployment | Cloud (Zoho-managed) |
| Mobile | Zoho Creator Mobile App (iOS + Android) |
| Backup | Zoho Creator auto-backup |
| Security | Role-based access control (see Section 2.4) |

### 4.2 Integration Requirements

| Integration | Purpose |
|-------------|---------|
| Zoho Books (optional) | Financial accounting, GST invoicing |
| Zoho Projects (optional) | Project task management |
| Zoho Mail | Email notifications |
| Zoho Sign | Digital signatures on PO / P&L |

### 4.3 Form Implementation Rules

#### Rule 1: Every form is one Zoho Creator Form

Each form defined in Section 3 maps to exactly **one Zoho Creator Form** with:

```
Form: [Name]
  ├── Fields (Section: HEADER)
  │   └── Single-value fields (text, date, dropdown, lookup, etc.)
  ├── Subform: [Name] (Section: SUBFORM)
  │   └── Multi-row table with N entries
  │       └── Fields as defined
  └── Fields (Section: FOOTER)
      └── Summary/calculated fields
```

#### Rule 2: N-line item forms use Zoho Creator Subforms

Forms with **SUBFORM** must be implemented as Zoho Creator **Subforms** (not separate forms linked by lookup). This ensures:

- Line items are stored as child records of the parent form
- N rows can be added dynamically (not fixed count)
- Autofetch works across parent → child

Forms requiring subforms:

| Form | Subform Name | Max Rows |
|------|-------------|----------|
| Purchase Item Muster | (none) | — |
| Supplier Master | (none) | — |
| System Master | (none) | — |
| System Composition | FG Line Items | N |
| BOM / FG Formulation | RM Line Items | N |
| Customer/Site Master | (none) | — |
| Sales/Work Order Master | Subform A — System Lines (Supply+Apply) | N |
| Sales/Work Order Master | Subform B — FG Lines (Supply Only) | N |
| Sales/Work Order Master | Commission (conditional, Supply+Apply) | 1 |
| Create Project | Systems | N |
| Create Project | Task Budget | N |
| Purchase Requisition (PR) | Line Items | N |
| Rate Comparison | Supplier Comparison | 5 (fixed) |
| Purchase Order (PO) | Line Items | N |
| Goods Receipt Note (GRN) | Line Items | N |
| Goods Receipt Note (GRN) | Transport (conditional) | 1 |
| QC / QA | Inspection Line Items | N |
| Material Requisition (MR) | MR Status (Draft/Prod Verified/Costing Approved/Released) | 1 (header) |
| Material Requisition (MR) | Line Items | N |
| Material Requisition (MR) | Material Allocation (Material Cost), Application Cost, Transportation Cost, Tools & Tackles (4 cost components → Total MR Cost) | N each |
| Material Issue Slip (MIS) | Line Items | N |
| Finish Goods Handover (FGHM) | FG Items (inline acceptance) | N |
| Production Planning | (none) | — |
| Production Order | (none) | — |
| Batch Manufacturing Record (BMR) | Raw Materials | N |
| Batch Manufacturing Record (BMR) | Process Parameters | N |
| Batch Manufacturing Record (BMR) | QC Test Results | N |
| RM Consumption Entry | Consumption Items | N |
| Packing Entry | Packing Materials | N |
| Rework Register | Material Consumed | N |

#### Rule 3: Footer fields are part of the main form, not subform

Footer fields (totals, formulas, terms) sit on the **main form**, below the subform. They are:

- **Formula fields** — auto-calculated from subform totals (e.g., PO Total = SUM of line item Totals)
- **Single-value fields** — delivery date, payment terms, remarks (not repeating)

#### Rule 4: Two-Stream Architecture — Project ID only in Stream B

```
=== STREAM A (Pre-Project — no Project ID) ===
Purchase Dept → PR → Rate Comparison → PO → GRN → QC → Material Handover → Store

=== STREAM B (Project-Centric — Project ID on all forms) ===
SO (Supply+Apply → creates Project; Supply Only → NO Project, FG sale only) → Project (root, Supply+Apply only)
                ├── MR [Cost Baseline] (Draft → Pending Production Verification → Production Verified → Costing Approved → Released)
                │       └── ⛔ Without Released MR → no further steps
                ├── After MR Released: MIS (Project ID autofetched)
                ├── Production Planning → Order → BMR → Packing → FGHM (inline acceptance)
                ├── Costing Approval (valuation gate)
                ├── Service Team (Area→Work→Invoice)
                ├── Finance (AP/AR / GL)
                ├── Logistics (DC→Outward→Close)
                └── Task Budget (part of Project form)
```

The Project ID is passed from parent to child in Stream B only:
- **MR**: User selects Project ID → MR is the **project implementation cost baseline** (four cost components: Material + Application + Transportation + Tools & Tackles → Total MR Cost) that Costing approves. MR Status: **Draft → Production Verified → Costing Approved (TOTAL cost) → Released**.
- **MIS**: Only creatable after MR is **Released** — stock issued against the Released MR
- **Production**: User selects Project ID → flows through all production forms
- **FGHM**: Project ID lookup with inline acceptance
- **Stream A procurement forms (PR/PO/GRN/QC)**: No Project ID — these are pre-project stock purchases
- **Critical rule**: Without a **Released MR**, there is no MIS, no Production, no Logistics, no project execution

### 4.4 Numbering Series

| Document | Format | Generated |
|----------|--------|-----------|
| PR | PR-YYYY-XXXX | On create |
| PO (Non-Coding) | RM-YYYY-XXXX | On create |
| PO (Coding) | RMWAD-YYYY-XXXX | On create |
| GRN | GRN-YYYY-XXXX | **After posting** |
| MR | MR-YYYY-XXXX | On create |
| MIS | Auto against MR | On create |
| FGH | FGH-YYYY-XXXX | On create |
| QC | QC-YYYY-XXXX | On create |
| SO | SO-YYYY-XXXX | On create |
| Project | PRJ-YYYY-XXXX | On create |
| System Composition | SC-YYYY-XXXX | On create |
| BOM / FG Formulation | BOM-YYYY-XXXX | On create |
| Production Planning | PLAN-YYYY-XXXX | On create |
| BMR | BMR-YYYY-XXXX | On create |
| Customer / Site Master | CUST-YYYY-XXXX | On create |

### 4.5 Notification Triggers

| Event | Notifies | Type |
|-------|----------|------|
| PR Submitted | Purchase (pending approval) | In-app |
| PR Approved | Production/R&D user | In-app |
| Rate Comparison Data Missing | Purchase dept | Alert |
| PO Ready | Purchase dept | In-app |
| GRN Overdue | Purchase + Store | In-app |
| **MR Submitted (Draft → Pending Verification)** | **Production dept** | **In-app** |
| **MR Production Verified (→ Pending Costing Approval)** | **Costing dept** | **In-app** |
| **MR Released** | **Store + Production + Logistics** | **In-app + Email** |
| FGHM Submitted | Store & Logistics | Pop-up |
| Project Close | Account & Finance + Project Manager | In-app + Email |
| P&L Margin below threshold (< 15%) | Account & Finance + Project Manager | Alert |
| Task Budget Actuals pending | Project Coordinator | Alert |
| **Material 80% Allocation Consumed** | **Project Manager + Coordinator (pop-up + dashboard banner + Email)** | **Alert** |

### 4.6 Key Automation Rules

| Rule | Description |
|------|-------------|
| SO → Project | Supply+Apply acceptance auto-creates Project record |
| **Project Baseline** | **SO = revenue side (System/FG scope). MR = complete project implementation cost baseline (Material + Application + Transportation + Tools & Tackles) that Costing approves. Both anchor the project.** |
| **MR Status Workflow** | **Draft → Production Verified (Production checks qty vs SO) → Costing Approved (Costing approves TOTAL project cost — all 4 components) → Released. Without Released MR, no downstream steps.** |
| PR → PO | PR approval triggers PO readiness |
| Partial GRN | Checkbox per line item; only checked items received |
| GRN Posting | Stock added only after posting; timestamp logged |
| MIS Posting | Stock deducted on issue (only after MR Released) |
| FGHM Inline Acceptance | FG stock added on FGHM submission with inline acceptance |
| P&L Auto-calculation | On Project Close — revenue minus all costs |
| Material Return | Qty added back to stock |
| Min/Max Alert | Alert when stock crosses threshold from Item Muster |
| MR = Project Cost Baseline | MR carries four cost components — Material (per-project RM allocation: Assigned Qty, Rate, Allocation Ratio, 80% Alert Flag), Application, Transportation, Tools & Tackles — summing to Total MR Cost, the project implementation cost baseline that Costing approves |
| Consumption → Project-Assigned RM | BMR/RM Consumption and Site Manager entries increment `Consumed Qty` on the matching MR Allocation line (`Project ID + Item Code`), never a generic pool |
| 80% Consumption Alert | When any allocated RM hits 80% of Assigned Qty (flag ON) → pop-up + dashboard banner + email to Project Manager |

### 4.7 AutoFetch Rules

| Source Field | Target Forms | Auto-fetched Fields |
|-------------|-------------|---------------------|
| Item Code | PR, PO, MR, MIS, GRN, FGHM, BOM, QC | Name, UOM, Category, HSN, GST%, Lead Time |
| Supplier Code | PO, GRN, Rate Comparison | Name, GSTIN, Address, Contact |
| PR No | Rate Comparison, PO | Items, Product Details |
| PO No | GRN | Supplier, Items, Ordered Qty |
| MR No | MIS | Items, Required Qty, Project |
| Project ID | MR, MIS, Production, FGHM, Service, Finance, Logistics (Stream B only) | Project Name, Manager |
| System Code | SO, BOM, Project | System Name |

---

## 5. Appendices

### 5.1 System Code Reference

| Prefix | Meaning | Example |
|--------|---------|---------|
| EP | Epoxy Flooring | EP01 (1mm), EP02 (2mm) |
| PU | PU Flooring | PU01 (1mm) |
| DEM | Demarcation Line | — |
| NUM | Numbering | — |
| ARR | Arrow Marking | — |
| ANTI | Anti Static Flooring | — |
| ESD | ESD Flooring | — |
| FIL | Filling | — |
| COV | Coving | — |

### 5.2 Warehouse List

1. Wadki w/h
2. Main w/h 1
3. Neelo w/h 2
4. Gurgaon
5. Bangalore
6. Client Site (conditional: shows textbox for site name)

### 5.3 UOM List

- Nos
- Kg
- Ltr
- Mtr
- Kit

### 5.4 Department List

- Purchase
- Sales
- Store & Logistics
- Account & Finance
- Admin
- Project Coordinator
- Project Manager 1 / 2 / 3

### 5.5 Form-Flow Sequence Diagram

```
[Master Data] ──→ [Sales: SO]
                      │ Sales Type (controlling field)
            ┌─────────┴───────────────┐
            ▼ (Supply+Apply)          ▼ (Supply Only)
       [Project] ──→ … (Stream B)   [FG Dispatch / Invoice]  (no Project · Stream A-adjacent)
            │
            ▼
   [PR]──→[RC]──→ [PO]──→[GRN]──→[QC]    Procurement (Stream A)
        
   ╔══════════════════════════════════════════╗
   ║  PROJECT BASELINE = SO + MR             ║
   ║  SO = Revenue (System/FG scope)         ║
   ║  MR = Cost (RM allocation)              ║
   ╚══════════════════════════════════════════╝
              
        ▼
   [MR (Cost Baseline)]──→ MR Workflow:
        │  Draft → Pending Production Verification → Production Verified → Costing Approved → Released
        │  ⛔ Without Released MR → STOP
        ▼
   [MIS] (Stock issued)    Inventory / Stores
        ▼
   [Production Planning]──→[Production Order]──→[BMR]──→[RM Consumption]
        │                                              │
        │                                              ▼
        │                                         [Packing]
        │                                              │
        │                                              ▼
        │                                         [FGHM (inline acceptance)]
        │                                              │
        │                                              ▼
        │                                    [Logistics: DC → Outward]
        │                                              │
        │                                              ▼
        │                                    [Project Site Execution]
        │                                    (Service Team: Area→Custody→Work→Invoice)
```

---

*End of Document — Chemsol Zoho Creator ERP | BRD · PRD · RFP v1.0*
