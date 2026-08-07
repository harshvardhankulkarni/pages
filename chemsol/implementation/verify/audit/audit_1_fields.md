# Audit 1 — Forms & Fields

**Repo:** Chemsol — Zoho Creator ERP · **Scope:** forms & fields only (no automation, no reports, no roles)
**Date:** 2026-08-06 · **Auditor:** Hermes subagent (audit_1_fields)

## Source-of-truth priority (higher wins on conflict)

1. **CSVs** — `chemsol/files/*.csv` (18 sheets from `Creator Forms Screen.xlsx`; actual form field lists)
2. **forms.html** — `chemsol/forms.html` (1754 lines; revised field definitions; Deluge API names live here via `automation.html` + `implementation/deluge/*`)
3. **IMPLEMENTATION_PLAN.md** — `chemsol/IMPLEMENTATION_PLAN.md` (1065 lines; field tables with types)
4. (Context only, never overrides 1–3: `chemsol/AGENTS.md` 196 lines — form inventory; `chemsol/files/Screens.csv` — screen list; `automation.html` + `implementation/deluge/` — Deluge field API names)

**CSV notes:** `Sheet4.csv` is empty (1 blank line — no fields, do not invent). `Project.csv` is a Project-Management **dashboard mockup** (open projects, margins, report list — lines 2–19), NOT a form; real Project form fields come from `Sheet2.csv` ("Create Project" + "Tasks") and forms.html §2B. `Integrations.csv` holds system-code prefixes + departments + module-integration notes, not form fields. `Screens.csv` lists screens/forms by department (Admin/Purchase/Store/Production) — confirms existence of Store Master (Bin Location subform), User Access, Approval Matrix, Material Handover, Production Order, BMR, RM Consumption Entry, Packing Entry, FG Handover Note, Rework Register, FG Receiving, Material Issue/Return screens.

**Field type vocabulary used (Zoho Creator, first-time-builder friendly):** Single Line · Multi Line · Number · Decimal · Currency · Date · Date-Time · Dropdown · Checkbox · Lookup · AutoFetch · Formula · Subform · File Upload · User · Auto Number.
(Mapping from source wording: Text→Single Line, Multi-line→Multi Line, Phone/Email→Single Line with format note, Autogen→Auto Number, Timestamp→Date-Time, Multi-lookup→Lookup (multi-select), Selectbox→Dropdown.)

**API names:** Taken from `automation.html` and `implementation/deluge/*.deluge` where they exist (e.g. `Assigned_Qty`, `80%_Alert_Flag`). Where no Deluge name exists, the display label is used and a snake_case API name is proposed (marked *proposed*).

---

## 1. Form inventory

| # | Form | Module / Phase | Stream | Source sheet (CSV) | Purpose |
|---|------|---------------|--------|--------------------|---------|
| 1 | Purchase Item Muster | Master Data | Global | Purchase_Item_Muster.csv | Central item repository: RM, FG, Packaging, Tools, Maintenance, Capital — 6 categories |
| 2 | Supplier Master | Master Data | Global | Supplier_Master.csv | Vendor master (like Zoho Books vendor) |
| 3 | System Master | Master Data | Global | — (Screens.csv confirms) | Flooring system definitions (EP01 = 1mm epoxy) |
| 4 | System Composition | Master Data | Global | — | System→FG mapping (which FGs make a system) |
| 5 | BOM / FG Formulation | Master Data | Global | — | FG→RM mapping with ratios (kg-per-kg, 4dp precision) |
| 6 | Customer/Site Master | Master Data | Global | — (SO CSV carries the client block) | Client org + site addresses (SO/Project/FGHM lookups) |
| 7 | Store Master (+ Bin Location subform) | Master Data | Global | — (Screens.csv confirms) | Warehouses: RM/FG/QC/Site store; Rack/Shelf/Bin mapping |
| 8 | User Access & Approval Matrix | Master Data | Global | — (Screens.csv confirms) | Roles, departments, approval limits, approvers |
| 9 | Sales Order Master (Subform A System Lines / Subform B FG Lines) | Sales & Project | B (dual-mode: Supply Only = direct FG sale, no Project) | Sales_Order_Master.csv | Conditional SO — Supply+Apply drives Costing→Project; Supply Only sells FG direct |
| 10 | Project (+ Systems subform + Task Budget subform) | Sales & Project | B (root entity) | Sheet2.csv (Create Project + Tasks) | Stream B root — auto-created on Costing Approved |
| 11 | Costing Sheet (Sections A–E) | Costing gate | B | — | 5-section cost baseline auto-expanded from SO × System Composition × BOM |
| 12 | Production Plan | Costing gate | B | Production_Report.csv (legacy "Production Planning Master") | Stock check + auto-PR for shortages; auto-created on Costing Approved |
| 13 | Material Requisition (MR) — Material Allocation subform + Application/Transport/Tools cost subforms | Costing gate | B | MR.csv (LEGACY — superseded) | Critical approval gate; auto-derived from Costing Sheet; per-project RM allocation baseline |
| 14 | Purchase Requisition (PR) | Procurement | A (optional Project ID) | PR.csv | Internal requisition; auto-created from Production Plan shortage |
| 15 | Rate Comparison | Procurement | Excluded (standalone reference) | Rate_Comparison.csv | 5-supplier quote comparison — removed from core loop (forms.html:852, IMPL §11) |
| 16 | Purchase Order (PO) | Procurement | A (optional Project ID) | PO.csv | Official order; dual numbering RM/RMWAD; GST split footer |
| 17 | Goods Receipt Note (GRN) — Transport subform | Procurement | A (Project ID autofetched) | GRN.csv | Goods receipt vs PO; partial via checkbox; stock + only after posting |
| 18 | QC / QA | Procurement | A | QC_QA.csv | Inspection results vs GRN (viscosity, density, color, moisture) |
| 19 | Material Issue Slip (MIS) | Production | B | MIS.csv | Store issues RM to production; only for Released MRs |
| 20 | Production Job | Production | B | — (Screens.csv: "Production Order") | Execution-level FG batch planning from Released MR |
| 21 | Batch Manufacturing Record (BMR) | Production | B | — (Screens.csv confirms) | Actual batch production — RM consumed, FG produced |
| 22 | RM Consumption Entry | Production | B | — (Screens.csv confirms) | BOM variance check (Actual vs Standard) — does NOT increment allocation |
| 23 | Packing Entry | Production | B | — (Screens.csv confirms) | FG packing; deducts packaging material from inventory only |
| 24 | FG Handover Master (FGHM) — inline acceptance | Production | B | FGHM.csv | FG handover to store/site; inline acceptance (no separate FGAN) |
| 25 | FG Consumption Entry | Production / Site | B | — | FG used at project site; FG stock −; creates Project FG Consumption record |
| 26 | Project FG Consumption Tracking | Inventory | B | — | AUTO-created tracking records (not a manual form) |
| 27 | RM Inventory — Stock Ledger | Inventory | Global (per-project aware) | — | RM stock ledger: Opening/GRN/MIS/Returns/Closing |
| 28 | FG Inventory — Stock Ledger | Inventory | Global (per-project aware) | — | FG stock ledger: Opening/FGHM/Dispatched/Returns/Closing |
| 29 | Site Consumption Entry (SCE) | Inventory / Site | B | — | Hourly/daily task-level RM consumption per work area; resolves to MR Allocation |
| 30 | Material Return Entry (MRT) | Inventory / Site | B | — | Unused RM back to Store; credits project allocation |
| 31 | Stock Movement Transaction Log | Inventory | Global | — | Auto audit trail of every stock movement (RM + FG) |

**Referenced but NOT spec'd (no field table exists anywhere — do not build without a spec):** Material Handover (Screens.csv:43–45, AGENTS.md:13 — Coding/Non-Coding RM split; no fields defined), FG Receiving (Screens.csv:44–47), Rework Register (Screens.csv:58), Vehicle & Transport (Screens.csv:45–47 — **excluded** per IMPL §11).
**Legacy / superseded:** FGAN (FG Acceptance Note) — FGAN.csv has a full spec but is superseded by FGHM inline acceptance (see §3 row 28). Production Order (Screens.csv:51) — superseded by Production Job (forms.html 5B, IMPL §6.2).

---

## 2. Per-form field tables

> **488 fields** across 31 core forms (counted from the tables below; +10 legacy FGAN fields in §2.32).

### 2.1 Purchase Item Muster — 12 fields (forms.html:169–180 · IMPL §2.1 · Purchase_Item_Muster.csv)

| # | Field API Name | Display Label | Creator Field Type | Required? | Autofetch source / Lookup target | Formula / Dropdown options | Notes (who updates it) |
|---|----------------|---------------|--------------------|-----------|----------------------------------|----------------------------|------------------------|
| 1 | Category | Category of Purchase Item | Dropdown | ✔ | — | 1.RM, 2.Packaging, 3.Tools & Consumable, 4.FG, 5.Maintenance, 6.Capital | forms.html:169 & IMPL:51 — CSV:5 had "6.Administation" instead of FG (see §3 row 1) |
| 2 | Item_Code | Purchase Item Code | Auto Number | ✔ | — | auto per category | forms.html:170 "Autogen" |
| 3 | Item_Name | Purchase Item Name | Single Line | ✔ | — | — | — |
| 4 | UOM | UOM | Dropdown | ✔ | — | 1.Nos, 2.Kg, 3.Ltr, 4.Mtr, 5.Kit | CSV:11 |
| 5 | HSN_Code | HSN Code | Single Line | ✔ | — | — | for GST |
| 6 | GST_Percent | GST % | Number | — | — | — | — |
| 7 | Min_Stock | Min Stock | Number | ✔ | — | — | reorder threshold |
| 8 | Max_Stock | Max Stock | Number | — | — | — | — |
| 9 | Standard_Rate | Standard Rate | Currency | — | — | — | hidden from non-Purchase/Admin/Store |
| 10 | Preferred_Supplier | Preferred Supplier | Lookup (multi-select) | — | Supplier Master | — | CSV:23 "Multiselection" |
| 11 | Lead_Time | Lead Time | Number (Days) | — | — | — | — |
| 12 | Status | Status | Dropdown | ✔ | — | Active / Inactive | CSV:27 |

**AutoFetch target:** PR, PO, MR, MIS, GRN, FGHM, BOM, QC — Item Code ⇄ Item Name bidirectional (forms.html:184).

### 2.2 Supplier Master — 16 fields (Supplier_Master.csv · forms.html:296–308 has 12 · IMPL §2.5 has 12)

| # | Field API Name | Display Label | Creator Field Type | Required? | Autofetch source / Lookup target | Formula / Dropdown options | Notes |
|---|----------------|---------------|--------------------|-----------|----------------------------------|----------------------------|-------|
| 1 | Supplier_Code | Supplier Code | Auto Number | ✔ | — | — | autogen on new registration (CSV:4) |
| 2 | Supplier_Name | Supplier Name | Single Line | ✔ | — | — | — |
| 3 | Supplier_Type | Supplier Type | Single Line | — | — | — | CSV:8 only — forms.html/IMPL omit (see §3 row 2) |
| 4 | GSTIN | GSTIN | Single Line | ✔ | — | — | — |
| 5 | PAN_No | PAN No | Single Line | ✔ | — | — | — |
| 6 | Contact_Person | Contact Person | Single Line | ✔ | — | — | — |
| 7 | Mobile_No | Mobile No | Single Line (phone) | ✔ | — | — | CSV:16 "Alternate" |
| 8 | Email_ID | Email ID | Single Line (email) | ✔ | — | — | — |
| 9 | Address | Address | Multi Line | ✔ | — | — | — |
| 10 | Pincode | Pincode | Single Line | — | — | — | CSV:22 only — forms.html/IMPL omit (see §3 row 3) |
| 11 | Bank_Name | Bank Name | Single Line | ✔ | — | — | CSV:24 (forms.html/IMPL merge 11–13 into one row) |
| 12 | Account_No | Account No | Single Line | ✔ | — | — | CSV:26 |
| 13 | IFSC_Code | IFSC Code | Single Line | ✔ | — | — | CSV:28 |
| 14 | Payment_Terms | Payment Terms | Single Line | ✔ | — | — | CSV:30 |
| 15 | Credit_Days | Credit Days | Number | ✔ | — | — | CSV:32 |
| 16 | Status | Status | Dropdown | ✔ | — | Active / Inactive | CSV:34 |

**AutoFetch target:** PO, GRN (Supplier Name/GSTIN/Address/Contact/Payment Terms).

### 2.3 System Master — 4 fields (forms.html:199–203 · IMPL §2.2)

| # | Field API Name | Display Label | Creator Field Type | Required? | Lookup target | Dropdown options | Notes |
|---|----------------|---------------|--------------------|-----------|---------------|------------------|-------|
| 1 | System_Code | System Code | Single Line (auto-formatted) | ✔ | — | — | prefix+number: EP01, PU02, DEM01 (forms.html:194) |
| 2 | System_Name | System Name | Single Line | ✔ | — | — | e.g. "1mm Epoxy Flooring" |
| 3 | Description | Description | Multi Line | — | — | — | — |
| 4 | Status | Status | Dropdown | ✔ | — | Active / Inactive | — |

**AutoFetch target:** System Composition, SO Subform A, Project Systems subform, Costing Sheet.

### 2.4 System Composition — 6 header + 5 line fields (forms.html:222–241 · IMPL §2.3)

**Header:**

| # | Field API Name | Display Label | Creator Field Type | Required? | Lookup target | Dropdown options | Notes |
|---|----------------|---------------|--------------------|-----------|---------------|------------------|-------|
| 1 | Comp_No | Comp No | Auto Number | ✔ | — | — | SC-YYYY-XXXX |
| 2 | System_Code | System Code | Lookup | ✔ | System Master | — | — |
| 3 | System_Name | System Name | AutoFetch | ✔ | from System Code | — | — |
| 4 | Revision_No | Revision No | Single Line | — | — | — | — |
| 5 | Date | Date | Date | ✔ | — | — | Today's date |
| 6 | Status | Status | Dropdown | ✔ | — | Draft / Approved / Released | — |

**Line Items (N FGs per System):**

| # | Field API Name | Display Label | Creator Field Type | Required? | Autofetch source / Lookup target | Notes |
|---|----------------|---------------|--------------------|-----------|----------------------------------|-------|
| 1 | FG_Product_Code | FG Product Code | Lookup | ✔ | Item Muster — FG | — |
| 2 | FG_Product_Name | FG Product Name | AutoFetch | ✔ | from FG Product Code | — |
| 3 | Qty_per_System_Unit | Qty per System Unit | Number | ✔ | — | how much FG per 1 unit of System |
| 4 | UOM | UOM | AutoFetch | ✔ | Item Muster via FG Code | — |
| 5 | Rate_per_FG_Unit | Rate per FG Unit | Currency | — | — | for costing |

### 2.5 BOM / FG Formulation — 5 header + 6 line fields (forms.html:259–278 · IMPL §2.4)

**Header:**

| # | Field API Name | Display Label | Creator Field Type | Required? | Lookup target | Dropdown options | Notes |
|---|----------------|---------------|--------------------|-----------|---------------|------------------|-------|
| 1 | BOM_No | BOM No | Auto Number | ✔ | — | — | BOM-YYYY-XXXX |
| 2 | FG_Code | FG Code | Lookup | ✔ | Item Muster — FG | — | — |
| 3 | FG_Name | FG Name | AutoFetch | ✔ | from FG Code | — | — |
| 4 | Date | Date | Date | ✔ | — | — | Today's date |
| 5 | Status | Status | Dropdown | ✔ | — | Draft / Approved / Released | — |

**Line Items (N RMs per FG):**

| # | Field API Name | Display Label | Creator Field Type | Required? | Autofetch source / Lookup target | Formula / options | Notes |
|---|----------------|---------------|--------------------|-----------|----------------------------------|-------------------|-------|
| 1 | RM_Item_Code | RM Item Code | Lookup | ✔ | Item Muster — RM | — | — |
| 2 | RM_Name | RM Name | AutoFetch | ✔ | from RM Item Code | — | — |
| 3 | UOM | UOM | AutoFetch | ✔ | Item Muster via RM Code | — | — |
| 4 | Qty_per_FG_Unit | Qty per FG Unit | Decimal | ✔ | — | — | **4dp precision (0.3333, not 0.33)** — AGENTS.md pitfall C28 |
| 5 | Waste_Percent | Waste % | Decimal | — | — | — | — |
| 6 | Total_Qty | Total Qty | Formula | ✔ | — | Qty per FG Unit + Waste% | forms.html:277 |

### 2.6 Customer/Site Master — 12 fields (forms.html:325–336 · no CSV — client block from Sales_Order_Master.csv)

| # | Field API Name | Display Label | Creator Field Type | Required? | Dropdown options | Notes |
|---|----------------|---------------|--------------------|-----------|------------------|-------|
| 1 | Customer_Code | Customer Code | Auto Number | ✔ | — | CUST-YYYY-XXXX |
| 2 | Client_Org_Name | Client Org Name | Single Line | ✔ | — | company/org name |
| 3 | Contact_Person | Contact Person | Single Line | ✔ | — | primary contact |
| 4 | Mobile_No | Mobile No | Single Line (phone) | ✔ | — | — |
| 5 | Email | Email | Single Line (email) | ✔ | — | — |
| 6 | GSTIN | GSTIN | Single Line | ✔ | — | for invoicing |
| 7 | PAN_No | PAN No | Single Line | ✔ | — | — |
| 8 | Regd_Address | Regd Address | Multi Line | ✔ | — | registered office |
| 9 | Site_Name | Site Name | Single Line | ✔ | — | project site name |
| 10 | Site_Address | Site Address | Multi Line | ✔ | — | delivery/work site |
| 11 | Site_Manager | Site Manager / Contact | Single Line | — | — | on-site supervisor |
| 12 | Status | Status | Dropdown | ✔ | Active / Inactive | — |

**AutoFetch target:** SO (forms.html:320).

### 2.7 Store Master — 5 header + 4 Bin Location subform fields (forms.html:354–370 · IMPL §2.6)

**Header:**

| # | Field API Name | Display Label | Creator Field Type | Required? | Dropdown options | Notes |
|---|----------------|---------------|--------------------|-----------|------------------|-------|
| 1 | Store_Code | Store Code | Auto Number | ✔ | — | — |
| 2 | Store_Name | Store Name | Single Line | ✔ | — | — |
| 3 | Store_Type | Store Type | Dropdown | ✔ | RM Store / FG Store / QC Store / Site Store | — |
| 4 | Location | Location | Single Line | ✔ | — | — |
| 5 | Status | Status | Dropdown | ✔ | Active / Inactive | — |

**Bin Location (inline subform):**

| # | Field API Name | Display Label | Creator Field Type | Required? | Notes |
|---|----------------|---------------|--------------------|-----------|-------|
| 1 | Rack_No | Rack No | Single Line | ✔ | — |
| 2 | Shelf_No | Shelf No | Single Line | ✔ | — |
| 3 | Bin_No | Bin No | Single Line | ✔ | — |
| 4 | Status | Status | Dropdown | ✔ | Active / Inactive |

### 2.8 User Access & Approval Matrix — 4 + 5 fields (IMPL §2.7 only · Screens.csv:12–13 · **absent from forms.html** — see §3 row 31)

**User Access:**

| # | Field API Name | Display Label | Creator Field Type | Required? | Dropdown options |
|---|----------------|---------------|--------------------|-----------|------------------|
| 1 | User_Name | User Name | User | ✔ | — |
| 2 | Department | Department | Dropdown | ✔ | Purchase / Sales / Store / Production / QC / Project Manager / Account & Finance |
| 3 | Role | Role | Dropdown | ✔ | Entry / Review / Approve / Admin |
| 4 | Status | Status | Dropdown | ✔ | Active / Inactive |

**Approval Matrix:**

| # | Field API Name | Display Label | Creator Field Type | Required? | Dropdown options |
|---|----------------|---------------|--------------------|-----------|------------------|
| 1 | Department | Department | Dropdown | ✔ | — |
| 2 | Document_Type | Document Type | Dropdown | ✔ | PR / PO / MR |
| 3 | Min_Amount | Min Amount | Currency | ✔ | — |
| 4 | Max_Amount | Max Amount | Currency | ✔ | — |
| 5 | Approver_1_2_3 | Approver 1 / 2 / 3 | User | ✔ | — |

### 2.9 Sales Order (SO) — 28 header + 7 Subform A + 6 Subform B fields (Sales_Order_Master.csv · forms.html:402–455 · IMPL §3.1)

**Header:**

| # | Field API Name | Display Label | Creator Field Type | Required? | Autofetch source / Lookup target | Dropdown options | Notes |
|---|----------------|---------------|--------------------|-----------|----------------------------------|------------------|-------|
| 1 | Sales_Type | Sales Type | Dropdown | ✔ | — | Supply+Apply (creates Project) / Supply Only (direct FG sale) | controls subform visibility (forms.html:402). CSV:4–5 had typos "Suppy+Apply / Suppy (Material Sales)" |
| 2 | SO_No | SO No | Auto Number | ✔ | — | — | SO-YYYY-XXXX |
| 3 | SO_Date | SO Date | Date | ✔ | — | — | Today's date |
| 4 | Employee_Name | Employee Name | Single Line | ✔ | — | — | CSV:11 |
| 5 | Customer_Code | Customer Code | Lookup | — | Customer/Site Master → AutoFetch Org Name, GST, Contact | — | CSV:13 |
| 6 | Client_Org_Name | Client Org Name | Single Line | ✔ | — | — | CSV:14 |
| 7 | Contact_Person | Contact Person | Single Line | ✔ | — | — | CSV:15 |
| 8 | Contact_No | Contact No. | Single Line (phone) | ✔ | — | — | CSV:16 |
| 9 | Alt_Contact_No | Alt Contact No. | Single Line (phone) | ✔ | — | — | CSV:17 only — absent from forms.html (see §3 row 6) |
| 10 | Email | Email | Single Line (email) | ✔ | — | — | CSV:18 |
| 11 | GST_No | GST No. | Single Line | ✔ | — | — | CSV:19 |
| 12 | PAN | Pan | Single Line | ✔ | — | — | CSV:20 |
| 13 | Regd_Address | Regd Address | Multi Line | ✔ | — | — | CSV:21 |
| 14 | Site_Name | Site Name | Single Line | ✔ | — | — | CSV:26 |
| 15 | Site_Address | Site Address | Multi Line | ✔ | — | — | CSV:27 |
| 16 | Site_Manager | Site Manager / Incharge | Single Line | — | — | — | CSV:28 (forms.html:410 Text/Phone) |
| 17 | Project_Type | Project Type | Dropdown | — | — | 1.Industrial, 2.Commercial | CSV:30 |
| 18 | Total_Amount | Total Amount | Formula | ✔ | — | Sum of active subform line amounts | forms.html:412 |
| 19 | Payment_Terms | Payment Terms | Single Line | — | — | — | CSV:41 |
| 20 | Transportation_Scope | Transportation Scope | Dropdown | — | — | Supplier / Own | CSV:43, forms.html:414 |
| 21 | Transportation_Amount | Transportation Amount | Currency | — | — | — | forms.html:414 |
| 22 | Lead_Time | Lead Time | Number (Days) | — | — | — | CSV:47 |
| 23 | PO_BOQ_Attachment | PO/BOQ Attachment | File Upload | — | — | — | CSV:39 "(Multiple)" |
| 24 | Warranty | Warranty | Single Line | — | — | — | CSV:42 ("Warrenty") |
| 25 | Commission | Commission | Checkbox | — | — | → then dropdown "Based On": 1.Percentage, 2.Fix Amount + Amount | CSV:49–50; applies to Supply+Apply only |
| 26 | Is_Proper_System_Require | Is proper System Require | Checkbox | — | — | — | CSV:45 only — absent from forms.html (see §3 row 7) |
| 27 | Remark | Remark | Multi Line | — | — | — | CSV:38 (Supply Only side) |
| 28 | Status | Status | Dropdown | ✔ | — | Draft / Accepted / Completed / Cancelled | forms.html:419 only (see §3 row 8) |

**Subform A — System Lines (visible when Sales Type = Supply+Apply):**

| # | Field API Name | Display Label | Creator Field Type | Required? | Autofetch source / Lookup target | Formula / options | Notes |
|---|----------------|---------------|--------------------|-----------|----------------------------------|-------------------|-------|
| 1 | System_Code | System Code | Lookup | ✔ | System Master → AutoFetch Name | — | — |
| 2 | System_Name | System Name | AutoFetch | ✔ | from System Code | — | CSV:32 "Systems Name" |
| 3 | Thickness | Thickness | Single Line | — | — | e.g. 1mm, 2mm | — |
| 4 | Area | Area | Number | ✔ | — | sqm | CSV:32 |
| 5 | UOM | UOM | Dropdown | ✔ | — | SqM / Mtr / Nos (conditional) | CSV:33 |
| 6 | Rate | Rate | Currency | ✔ | — | per-unit system rate | — |
| 7 | Amount | Amount | Formula | ✔ | — | Area × Rate | — |

**Subform B — FG Lines (visible when Sales Type = Supply Only):**

| # | Field API Name | Display Label | Creator Field Type | Required? | Autofetch source / Lookup target | Formula | Notes |
|---|----------------|---------------|--------------------|-----------|----------------------------------|---------|-------|
| 1 | FG_Code | FG Code | Lookup | ✔ | Item Muster — FG → AutoFetch Name, UOM | — | — |
| 2 | FG_Name | FG Name | AutoFetch | ✔ | from FG Code | — | — |
| 3 | Qty | Qty | Number | ✔ | — | — | FG quantity sold |
| 4 | UOM | UOM | AutoFetch | ✔ | Item Muster via FG Code | — | — |
| 5 | Rate | Rate | Currency | ✔ | — | — | FG unit rate |
| 6 | Amount | Amount | Formula | ✔ | — | Qty × Rate | — |

### 2.10 Project — 15 header + 4 Systems + 7 Task Budget fields (forms.html:474–515 · IMPL §3.2 · Sheet2.csv)

**Header:**

| # | Field API Name | Display Label | Creator Field Type | Required? | Autofetch source / Lookup target | Dropdown options | Notes |
|---|----------------|---------------|--------------------|-----------|----------------------------------|------------------|-------|
| 1 | Project_ID | Project ID | Auto Number | ✔ | — | — | PRJ-YYYY-XXXX |
| 2 | SO_Reference | SO Reference | Lookup | ✔ | Sales Order Master → AutoFetch SO No, Customer, Amount | — | auto-filled from Costing Sheet approval (single creation point C2) |
| 3 | Project_Name | Project Name | Single Line | ✔ | — | — | — |
| 4 | Address | Address | Multi Line | ✔ | — | — | — |
| 5 | Project_Manager | Project Manager | User | ✔ | — | — | — |
| 6 | Execution_Base | Execution Base | Dropdown | ✔ | — | 1.Area Basis, 2.Day Basis | Sheet2.csv:8 "Areabasis/Day Basis" |
| 7 | Start_Date | Start Date | Date | ✔ | — | — | — |
| 8 | End_Date | End Date | Date | ✔ | — | — | — |
| 9 | Project_Cost | Project Cost | Currency | ✔ | — | — | — |
| 10 | Status | Status | Dropdown | ✔ | — | Planned / In Progress / Completed / On Hold | — |
| 11 | Total_Revenue | Total Revenue | AutoFetch | ✔ | SO Total Amount — set at Project creation | — | G2 |
| 12 | Total_Actual_Cost | Total Actual Cost | AutoFetch | ✔ | MR Total MR Cost — set on MR Released | — | G2 |
| 13 | PnL | P&L | Formula | ✔ | — | = Total Revenue − Total Actual Cost | G2 |
| 14 | Description | Description | Multi Line | — | — | — | Sheet2.csv:13 only |
| 15 | Adjustments | Adjustments | Single Line | — | — | — | Sheet2.csv:14 only |

**Systems Subform:**

| # | Field API Name | Display Label | Creator Field Type | Required? | Lookup target | Dropdown options |
|---|----------------|---------------|--------------------|-----------|---------------|------------------|
| 1 | System_Code | System Code | Lookup | — | System Master | — |
| 2 | Area | Area | Number | — | — | — |
| 3 | UOM | UOM | Dropdown | — | — | SqM / Mtr / Nos |
| 4 | Description | Description | Single Line | — | — | — |

**Task Budget Subform (G2 — Budget + Actuals per Category):**

| # | Field API Name | Display Label | Creator Field Type | Required? | Dropdown options | Formula | Notes |
|---|----------------|---------------|--------------------|-----------|------------------|---------|-------|
| 1 | Category | Category | Dropdown | — | Transport / Execution / Manpower / Tools / Overhead | — | Sheet2.csv legacy had "Application" + "Additional Expenses" (see §3 row 11) |
| 2 | Description | Description | Single Line | — | — | — | — |
| 3 | Budget_Qty | Budget Qty | Number | — | — | — | planned qty/area |
| 4 | Rate | Rate | Currency | — | — | — | — |
| 5 | Budget_Amount | Budget Amount | Formula | — | — | Budget Qty × Rate | — |
| 6 | Actual_Qty | Actual Qty | Number | — | — | — | updated from actuals |
| 7 | Actual_Amount | Actual Amount | Formula | — | — | Actual Qty × Rate | feeds P&L |

### 2.11 Costing Sheet — 6 header + 10 Section A + 5 Section B + 7 Section C + 4 Section D + 2 Section E + 1 Total (forms.html:564–655 · IMPL §4.1)

**Header:**

| # | Field API Name | Display Label | Creator Field Type | Required? | Autofetch source / Lookup target | Dropdown options | Notes |
|---|----------------|---------------|--------------------|-----------|----------------------------------|------------------|-------|
| 1 | Costing_Number | Costing Number | Auto Number | ✔ | — | — | CST-YYYY-XXXX |
| 2 | Costing_Date | Costing Date | Date | ✔ | — | — | Today's date |
| 3 | SO_Reference | SO Reference | Lookup | ✔ | SO Master (Supply+Apply only) | — | autofetch System Lines, Area, Customer |
| 4 | Project_Name | Project Name | AutoFetch | ✔ | from SO | — | forms.html:567 |
| 5 | Customer | Customer | AutoFetch | ✔ | from SO | — | forms.html:568 |
| 6 | Costing_Status | Costing Status | Dropdown | ✔ | — | Draft / Under Review / Approved / Rejected | controls downstream flow |
| — | Prepared_By | Prepared By | User | ✔ | — | — | IMPL:267 only — **absent from forms.html** (see §3 row 12) |
| — | Reviewed_By | Reviewed By | User | — | — | — | IMPL:268 only |
| — | Revision_No | Revision No | Single Line | — | — | — | IMPL:269 only; incremented on Rejected-with-revision |
| — | Total_Costing_Amount | Total Costing Amount | Formula | ✔ | — | = Section A + B + C + D + E totals | IMPL:270; forms.html:655 presents it as the section-level formula (G3) |

**Section A — Material Cost (auto-expanded from SO × System Composition × BOM):**

| # | Field API Name | Display Label | Creator Field Type | Required? | Autofetch source | Formula | Notes |
|---|----------------|---------------|--------------------|-----------|------------------|---------|-------|
| 1 | System_Code | System Code | AutoFetch | ✔ | SO | — | — |
| 2 | FG_Code | FG Code | AutoFetch | ✔ | System Composition | — | all FGs in the system |
| 3 | RM_Item_Code | RM Item Code | AutoFetch | ✔ | BOM | — | all RMs per FG (API `RM_Code`) |
| 4 | RM_Item_Name | RM Item Name | AutoFetch | ✔ | BOM / Item Muster | — | API `RM_Name` |
| 5 | UOM | UOM | AutoFetch | ✔ | Item Muster | — | — |
| 6 | BOM_Ratio | BOM Ratio | AutoFetch | ✔ | BOM | — | 4dp (0.3333) |
| 7 | Area | Area (sqm) | AutoFetch | ✔ | SO | — | API `Area` |
| 8 | Required_Qty | Required Qty | Formula | ✔ | — | = BOM Ratio × Area (round 1dp) | forms.html:589. **IMPL:282 uses × (1+Waste%) — CONFLICT, see §3 row 13** |
| 9 | Rate | Rate | Currency | ✔ | (default Item Muster Standard Rate) | — | editable (forms.html:590); IMPL:283 "Costing can override" |
| 10 | Material_Cost | Material Cost | Formula | ✔ | — | = Required Qty × Rate | — |

**Section B — Application Cost:**

| # | Field API Name | Display Label | Creator Field Type | Required? | Dropdown options | Formula |
|---|----------------|---------------|--------------------|-----------|------------------|---------|
| 1 | Activity | Activity | Single Line | ✔ | e.g. Surface Preparation, Primer, Top Coat | — |
| 2 | UOM | UOM | Dropdown | ✔ | SqM / Day / Hour | — |
| 3 | Qty_Area | Qty / Area | Number | ✔ | — | — |
| 4 | Rate | Rate | Currency | ✔ | — | — |
| 5 | Amount | Amount | Formula | ✔ | — | Qty × Rate |

**Section C — Transportation Cost:**

| # | Field API Name | Display Label | Creator Field Type | Required? | Lookup target | Dropdown options | Formula |
|---|----------------|---------------|--------------------|-----------|---------------|------------------|---------|
| 1 | From_Warehouse | From (Warehouse) | Lookup | ✔ | Store Master | — | — |
| 2 | To_Site | To (Site) | Single Line | ✔ | — | — | — |
| 3 | Mode_of_Transport | Mode of Transport | Dropdown | ✔ | — | Own / Third Party | — |
| 4 | Estimated_Trips | Estimated Trips | Number | ✔ | — | — | — |
| 5 | Rate_per_Trip | Rate per Trip | Currency | ✔ | — | — | — |
| 6 | Amount | Amount | Formula | ✔ | — | — | Trips × Rate |
| 7 | Logistics_Notes | Logistics Notes | Multi Line | — | — | — | — |

**Section D — Tools & Tackles:**

| # | Field API Name | Display Label | Creator Field Type | Required? | Lookup target | Formula |
|---|----------------|---------------|--------------------|-----------|---------------|---------|
| 1 | Item_Tool | Item / Tool | Lookup | ✔ | Item Muster — Tools & Consumable | — |
| 2 | Qty | Qty | Number | ✔ | — | — |
| 3 | Rate | Rate | Currency | ✔ | — | — |
| 4 | Amount | Amount | Formula | ✔ | — | Qty × Rate |

**Section E — Overhead & Miscellaneous:**

| # | Field API Name | Display Label | Creator Field Type | Required? | Notes |
|---|----------------|---------------|--------------------|-----------|-------|
| 1 | Description | Description | Single Line | ✔ | — |
| 2 | Amount | Amount | Currency | ✔ | — |
| — | Remarks | Remarks | Multi Line | — | IMPL:319 only — absent from forms.html (see §3 row 14) |

**Total Costing Amount** (Formula, G3) = Section A Total + B Total + C Total + D Total + E Total (forms.html:655).

### 2.12 Production Plan — 8 header + 7 line fields (forms.html:676–699 · IMPL §4.2 · Production_Report.csv legacy)

**Header:**

| # | Field API Name | Display Label | Creator Field Type | Required? | Autofetch source / Lookup target | Dropdown options | Notes |
|---|----------------|---------------|--------------------|-----------|----------------------------------|------------------|-------|
| 1 | Plan_Number | Plan Number | Auto Number | ✔ | — | — | PLAN-YYYY-XXXX (CSV legacy: "Planning No (MR Sheet No.)") |
| 2 | Plan_Date | Plan Date | Date | ✔ | — | — | Today's date |
| 3 | Costing_Sheet_No | Costing Sheet No | Lookup | ✔ | Costing Sheet (Approved) | — | autofetch material lines (API `Costing_Sheet_Ref`) |
| 4 | Project_ID | Project ID | AutoFetch | ✔ | from Costing Sheet | — | — |
| 5 | Planning_Period | Planning Period | Dropdown | ✔ | — | Week / Month | — |
| 6 | Plant | Plant | Dropdown | — | — | Wadki / Main / Neelo / Gurgaon / Bangalore | — |
| 7 | Planner_Name | Planner Name | User | ✔ | — | — | — |
| 8 | Plan_Status | Plan Status | Dropdown | ✔ | — | **Draft / Released** (forms.html:683) | CSV:9 had Draft/Approved/Released; IMPL:343 had Draft/Reviewed/Released — CONFLICT, see §3 row 15 |

**Line Items (auto-fetched from Costing Sheet §A):**

| # | Field API Name | Display Label | Creator Field Type | Required? | Autofetch source | Formula | Dropdown options | Notes |
|---|----------------|---------------|--------------------|-----------|------------------|---------|------------------|-------|
| 1 | RM_Item_Code | RM Item Code | AutoFetch | ✔ | Costing Sheet | — | — | — |
| 2 | RM_Name | RM Name | AutoFetch | ✔ | Costing Sheet | — | — | — |
| 3 | Total_Required | Total Required | AutoFetch | ✔ | Costing Sheet §A | — | — | — |
| 4 | Available_Stock | Available Stock | AutoFetch | ✔ | RM Inventory (net of other project allocations) | — | — | = Physical Stock − Σ(Assigned Qty from unreleased MRs) |
| 5 | Shortage | Shortage | Formula | ✔ | — | = Total Required − Available Stock (if > 0) | — | — |
| 6 | Source | Source | Dropdown | ✔ | — | — | Stock / Purchase / Both | — |
| 7 | Procurement_Triggered | Procurement Triggered | Checkbox (auto) | — | — | — | — | set when Shortage > 0; Plan Release → auto-PR |

**Legacy CSV-only fields (Production_Report.csv:4–14 — superseded):** Remarks, Total SO/WO Qty (autofetch per MR Sheet), FG Stock Available (autofetch per FG Stock), Net Production Requirement — FG-level planning replaced by RM-level lines above (see §3 row 16).

### 2.13 Material Requisition (MR) — 11 header + 7 lines + 17 Material Allocation + 5+5+4 cost subform + 1 total = 50 fields (forms.html:727–833 · IMPL §4.3 · MR.csv LEGACY)

> ⚠ **BLOCKER (§3 row 17):** MR.csv is the LEGACY manual MR (no Project ID, no Material Allocation, no cost components). Build the forms.html/IMPL revised MR (auto-derived, project-centric).

**Header:**

| # | Field API Name | Display Label | Creator Field Type | Required? | Autofetch source / Lookup target | Dropdown options | Notes |
|---|----------------|---------------|--------------------|-----------|----------------------------------|------------------|-------|
| 1 | MR_Number | MR Number | Auto Number | ✔ | — | — | MR-YYYY-XXXX |
| 2 | MR_Date | MR Date | Date | ✔ | — | — | Today's date |
| 3 | Project_ID | Project ID | Lookup | ✔ | Project Master | — | Stream B root link |
| 4 | Requisition_Type | Requisition Type | Dropdown | ✔ | — | Production / R&D | — |
| 5 | Batch_Number | Batch Number | Single Line | — | — | — | — |
| 6 | Department | Department | AutoFetch | ✔ | login user | — | — |
| 7 | Requested_By | Requested By | Single Line | ✔ | login user | — | Employee name |
| 8 | Priority | Priority | Dropdown | ✔ | — | Low / Medium / High / Urgent | — |
| 9 | MR_Status | MR Status | Dropdown | ✔ | — | Draft / Pending Production Verification / Production Verified / Costing Approved / Released | CRITICAL gate (5-state) |
| 10 | Last_Status_Change | Last Status Change | Date-Time (auto) | — | — | — | C32 — stamped on every Blueprint transition |
| 11 | SLA_Reminder_Sent | SLA Reminder Sent | Checkbox (auto) | — | — | — | C32 — 2 hr Draft reminder fires once |

**Line Items (N items):**

| # | Field API Name | Display Label | Creator Field Type | Required? | Autofetch source / Lookup target | Notes |
|---|----------------|---------------|--------------------|-----------|----------------------------------|-------|
| 1 | Item_Code | Item Code | Lookup | ✔ | Item Muster — RM only (filter) | — |
| 2 | Item_Name | Item Name | AutoFetch | ✔ | from Item Code | — |
| 3 | Category | Category | AutoFetch | ✔ | Item Muster | — |
| 4 | UOM | UOM | AutoFetch | ✔ | Item Muster | — |
| 5 | Available_Stock | Available Stock | AutoFetch | ✔ | RM Inventory (real-time) | — |
| 6 | Required_Qty | Required Qty | Number | ✔ | — | API `Required_Qty` |
| 7 | Remarks | Remarks | Multi Line | — | — | — |

**Material Allocation Subform** (per-project RM allocation — consumption budget baseline; API names from automation.html:693–702, 1284–1494):

| # | Field API Name | Display Label | Creator Field Type | Required? | Autofetch source / Lookup target | Formula | Notes |
|---|----------------|---------------|--------------------|-----------|----------------------------------|---------|-------|
| 1 | Item_Code | Item Code | Lookup | ✔ | Item Muster — RM | — | auto-populated from MR lines |
| 2 | Item_Name | Item Name | AutoFetch | ✔ | from Item Code | — | — |
| 3 | UOM | UOM | AutoFetch | ✔ | Item Muster | — | — |
| 4 | Assigned_Qty | Assigned Qty | Number | ✔ | — | — | allocation baseline; defaults from Required Qty (mrDerive: `"Assigned_Qty": line.Required_Qty`) |
| 5 | Rate | Rate | Currency | ✔ | Item Muster Standard Rate | — | per-unit RM rate |
| 6 | Material_Cost | Material Cost | Formula | ✔ | — | = Assigned Qty × Rate | — |
| 7 | Allocation_Ratio_Percent | Allocation Ratio % | Formula | ✔ | — | = Assigned Qty ÷ Σ Assigned Qty × 100 | — |
| 8 | 80%_Alert_Flag | 80% Threshold Alert Flag | Checkbox | ✔ | — | — | default ON (automation.html:697) |
| 9 | Consumed_Qty | Consumed Qty | Number (auto) | — | — | — | incremented by BMR / SCE Deluge per Project+Item |
| 10 | Consumption_Percentage | Consumption % | Formula | — | — | = Consumed Qty ÷ Assigned Qty × 100 | API `Consumption_Percentage` (automation.html:1494) |
| 11 | Alert_Triggered | Alert Triggered | Checkbox (readonly) | — | — | — | auto-set at Consumption % ≥ 80% |
| 12 | Issued_Qty | Issued Qty | Number (auto) | — | — | — | G4 — incremented by MIS-Post Deluge per Project+Item |
| 13 | Returned_Qty | Returned Qty | Number (auto) | — | — | — | C1 — incremented by Material Return Deluge per Project+Item |
| 14 | Remaining | Remaining | Formula | — | — | = Assigned Qty − Consumed Qty + Returned Qty | C1 — live project inventory balance |
| 15 | Fully_Consumed | Fully Consumed | Checkbox (auto) | — | — | — | C1/C29 — set only when ALL allocation lines ≥ 100% (FGHM acceptance Deluge checks) |
| 16 | Variance_Percentage | Variance % | Decimal (readonly) | — | — | — | C19 — SO↔BOM↔MR cross-validation result (set when diff > 5%) |
| 17 | Variance_Flag | Variance Flag | Checkbox (readonly) | — | — | — | C19 — auto-set when variance > 5% (flag/allow); > 10% hard-blocks submit |

**Application Cost subform (labour/execution):** Activity (Single Line, ✔) · UOM (Dropdown, ✔, SqM/Day/Hour) · Qty/Area (Number, ✔) · Rate (Currency, ✔) · Amount (Formula, ✔, Qty × Rate) — API `Application_Component`.

**Transportation Cost subform:** From (Single Line — warehouse, ✔) · To (Single Line — site, ✔) · Vehicle/Trips (Single Line/Number, ✔) · Rate (Currency, ✔) · Amount (Formula, ✔, Trips × Rate) — API `Transport_Component`.

**Tools & Tackles subform:** Item/Tool (Single Line/Lookup — Item Muster Tools & Consumable, ✔) · Qty (Number, ✔) · Rate (Currency, ✔) · Amount (Formula, ✔, Qty × Rate) — API `Tools_Component`.

**Total_MR_Cost** (Formula, G4) = Material Cost (Σ Allocation Assigned Qty × Rate) + Application + Transportation + Tools & Tackles (forms.html:833). Auto-set on Project.Total Actual Cost when MR is Released. API names (mrDerive.deluge): `MR_Number`, `MR_Status`, `Project_ID`, `Requisition_Type`, `Priority`, `Material_Allocation`, `Material_Component`, `Application_Component`, `Transport_Component`, `Tools_Component`, `Total_MR_Cost`, `Costing_Sheet_Ref`, `Production_Plan_Ref`.

### 2.14 Purchase Requisition (PR) — 7 header + 6 line fields (forms.html:869–889 · IMPL §5.1 · PR.csv)

**Header:**

| # | Field API Name | Display Label | Creator Field Type | Required? | Autofetch source / Lookup target | Dropdown options | Notes |
|---|----------------|---------------|--------------------|-----------|----------------------------------|------------------|-------|
| 1 | PR_Number | PR Number | Auto Number | ✔ | — | — | PR-YYYY-XXXX |
| 2 | PR_Date | PR Date | Date | ✔ | — | — | Today's date |
| 3 | Project_ID | Project ID | Lookup | — | Project Master | — | optional — project-linked procurement only (stock PR has no Project ID) |
| 4 | Reference | Reference | Single Line | — | — | — | manual reference |
| 5 | Department | Department | AutoFetch | ✔ | login user | — | CSV:10 "(Production / R & D)" |
| 6 | Approved_By | Approved By | Single Line | — | — | — | PR.csv:12 only — absent from forms.html (see §3 row 37) |
| 7 | Status | Status | Dropdown | ✔ | — | Draft / Pending Approval / Approved / Rejected | forms.html:874 |

**Line Items:**

| # | Field API Name | Display Label | Creator Field Type | Required? | Autofetch source / Lookup target | Notes |
|---|----------------|---------------|--------------------|-----------|----------------------------------|-------|
| 1 | Item_Code | Item Code | Lookup | ✔ | Item Muster | bidirectional autofill with Name |
| 2 | Item_Name | Item Name | AutoFetch | ✔ | from Item Code | — |
| 3 | Qty | Qty | Number | ✔ | — | — |
| 4 | Item_Description | Item Description | Multi Line | — | — | PR.csv:14 only — absent from forms.html |
| 5 | UOM | UOM | AutoFetch | ✔ | Item Muster via Item Code | — |
| 6 | Lead_Time | Lead Time | AutoFetch | — | Item Muster via Item Code | days |

API names (planReleaseAutoPR.deluge): `PR_Number`, `PR_Line_Items`, `Department`, `Status`, `Project_ID`.

### 2.15 Rate Comparison — 14 fields (Rate_Comparison.csv · **EXCLUDED from core loop**)

> forms.html:852 "Rate Comparison removed — simplified procurement flow"; IMPL §11 "Rate Comparison (simplified — standalone reference only)". Build as standalone reference form only if the client wants the CSV sheet preserved.

| # | Field API Name | Display Label | Creator Field Type | Required? | Dropdown options | Notes |
|---|----------------|---------------|--------------------|-----------|------------------|-------|
| 1 | Date | Date | Date | ✔ | — | Today's date |
| 2 | PR_Reference_No | PR Reference No. | Lookup | ✔ | PR Master | — |
| 3 | Product_No | Product No. | Lookup | ✔ | Item Muster | — |
| 4 | Product_Name | Product Name | AutoFetch | ✔ | from Product No. | — |
| 5–9 | Supplier_1..5 | Supplier 1..5 | Dropdown | — | — | 5 supplier comparisons |
| 10 | Price_1..5 | Price (per supplier) | Currency | — | — | paired with each supplier |
| 11 | Credit_1..5 | Credit (per supplier) | Single Line | — | — | paired with each supplier |
| 12 | Finalised_Supplier | Finalised Supplier | Single Line | ✔ | — | — |
| 13 | Final_Rate | Final Rate | Currency | ✔ | — | — |
| 14 | PO_No | PO No. | Single Line | ✔ | — | — |
| 15 | PO_Release_Date | PO Release Date | Date | ✔ | — | — |
| 16 | Remark | Remark | Multi Line | — | — | — |

### 2.16 Purchase Order (PO) — 10 header + 14 line + 10 footer fields (PO.csv · forms.html:907–953 · IMPL §5.2)

**Header:**

| # | Field API Name | Display Label | Creator Field Type | Required? | Autofetch source / Lookup target | Dropdown options | Notes |
|---|----------------|---------------|--------------------|-----------|----------------------------------|------------------|-------|
| 1 | RM_Type | RM Type | Dropdown | ✔ | — | 1.Coding, 2.Non Coding | drives numbering series |
| 2 | PO_Number | PO Number | Auto Number | ✔ | — | — | **Dual series:** RMWAD-YYYY-XXXX (Coding) / RM-YYYY-XXXX (Non-Coding) — poSeriesPrefix.deluge |
| 3 | PO_Date | PO Date | Date | ✔ | — | — | Today's date |
| 4 | Supplier_Code | Supplier Code | Lookup | ✔ | Supplier Master | — | AutoFetch Name, GSTIN, Address |
| 5 | Supplier_Name | Supplier Name | AutoFetch | ✔ | from Supplier Code | — | PO.csv:12 |
| 6 | Project_ID | Project ID | Lookup | — | Project Master | — | project-tagged procurement |
| 7 | PR_Reference | PR Reference | Lookup | — | PR Master | — | AutoFetch items, qty |
| 8 | Bill_To | Bill to | Dropdown | ✔ | — | Wadki / Main / Neelo / Gurgaon / Bangalore / Client Site | PO.csv:16 |
| 9 | Ship_To | Ship to | Dropdown | ✔ | — | same list | PO.csv:16 |
| 10 | Status | Status | Dropdown | ✔ | — | Draft / Sent / Partially Received / Fully Received / Cancelled | G5 — forms.html:914 |

**Line Items:**

| # | Field API Name | Display Label | Creator Field Type | Required? | Autofetch source / Lookup target | Formula | Notes |
|---|----------------|---------------|--------------------|-----------|----------------------------------|---------|-------|
| 1 | Item_Code | Item Code | Lookup | ✔ | Item Muster | — | AutoFetch Name, HSN, GST%, UOM |
| 2 | Item_Name | Item Name | AutoFetch | ✔ | from Item Code | — | — |
| 3 | HSN_Code | HSN Code | AutoFetch | ✔ | Item Muster | — | CSV:18 typo "HNS" (see §3 row 21) |
| 4 | Item_Description | Item Description | Single Line | — | — | — | CSV:19 "Require sub textbox for item description" |
| 5 | Quantity | Quantity | Number | ✔ | — | — | ordered qty |
| 6 | UOM | UOM | AutoFetch | ✔ | Item Muster | — | CSV:18 column — forms.html omits (see §3 row 23) |
| 7 | Rate | Rate | Currency | ✔ | — | — | — |
| 8 | Basic_Amount | Basic Amount | Formula | ✔ | — | Qty × Rate | — |
| 9 | GST_Percent | GST % | AutoFetch | ✔ | Item Muster | — | — |
| 10 | GST_Amount | GST Amount | Formula | ✔ | — | Basic × GST% | — |
| 11 | Total_Amount | Total Amount | Formula | ✔ | — | Basic + GST | — |
| 12 | Received_Qty | Received Qty | Number (auto) | — | — | — | G5 — incremented on GRN posting |
| 13 | Balance_Qty | Balance Qty | Formula | — | — | Quantity − Received Qty | G5 |
| 14 | Receipt_Status | Receipt Status | Formula (text) | — | — | Not Started / Partial / Complete | G5 |

**Footer (GST Split):**

| # | Field API Name | Display Label | Creator Field Type | Required? | Formula | Notes |
|---|----------------|---------------|--------------------|-----------|---------|-------|
| 1 | Basic_Total | Basic Total | Formula | — | Σ line Basic Amounts | poGstSplit.deluge |
| 2 | CGST_Total | CGST (Intra-state) | Formula | — | Σ GST/2 per line | — |
| 3 | SGST_Total | SGST (Intra-state) | Formula | — | Σ GST/2 per line | — |
| 4 | IGST_Total | IGST (Inter-state) | Formula | — | Σ full GST per line | — |
| 5 | Total_Amount_Words | Total Amount (Words) | Formula | — | auto-convert | — |
| 6 | Delivery_Date | Delivery Date | Date | ✔ | — | — |
| 7 | Payment_Terms | Payment Terms | Single Line | ✔ | — | — |
| 8 | Scope_of_Transport | Scope of Transport | Dropdown | — | Supplier / Own | — |
| 9 | Mode_of_Transport | Mode of Transport | Dropdown | — | — | PO.csv:28 only — absent from forms.html (see §3 row 22) |
| 10 | Delivery_Days | Delivery Days | Number (auto) | — | GRN Date − Delivery Date | G5 |

### 2.17 Goods Receipt Note (GRN) — 11 header + 7 line + 4 Transport subform fields (GRN.csv · forms.html:971–1004 · IMPL §5.3)

**Header:**

| # | Field API Name | Display Label | Creator Field Type | Required? | Autofetch source / Lookup target | Dropdown options | Notes |
|---|----------------|---------------|--------------------|-----------|----------------------------------|------------------|-------|
| 1 | GRN_Number | GRN Number | Auto Number | ✔ | — | — | GRN-YYYY-XXXX — generated **after posting** |
| 2 | GRN_Date | GRN Date | Date | ✔ | — | — | Today's date |
| 3 | PO_Number | PO Number | Lookup | ✔ | PO Master | — | AutoFetch Supplier, Items, Ordered Qty, Project ID |
| 4 | Supplier_Code | Supplier Code | AutoFetch | ✔ | from PO | — | GRN.csv:8 (forms.html omits — see §3 row 24) |
| 5 | Supplier_Name | Supplier Name | AutoFetch | ✔ | from PO Number | — | GRN.csv:10 |
| 6 | Project_ID | Project ID | AutoFetch | ✔ | from PO | — | forms.html:974 |
| 7 | Vehicle_Number | Vehicle Number | Single Line | ✔ | — | — | — |
| 8 | Warehouse | Warehouse | Dropdown | ✔ | — | 1.Wadki w/h, 2.Main w/h 1, 3.Neelo w/h 2, 4.Gurgaon, 5.Bangalore, 6.Client Site | GRN.csv:14 |
| 9 | Client_Site_Name | Client/Site Name | Single Line | — | — | — | conditional — visible only when Warehouse = Client Site (GRN.csv:15) |
| 10 | Invoice_Number | Invoice Number | Single Line | ✔ | — | — | — |
| 11 | Invoice_Date | Invoice Date | Date | ✔ | — | — | — |

**Line Items (checkbox for partial GRN):**

| # | Field API Name | Display Label | Creator Field Type | Required? | Autofetch source | Dropdown options | Notes |
|---|----------------|---------------|--------------------|-----------|------------------|------------------|-------|
| 1 | Select | ✅ Checkbox | Checkbox | — | — | — | select items for partial GRN (API `Partial_GRN`) |
| 2 | Item_Code | Item Code | AutoFetch | ✔ | PO via PO Number | — | — |
| 3 | Item_Name | Item Name | AutoFetch | ✔ | PO via PO Number | — | — |
| 4 | Ordered_Qty | Ordered Qty | AutoFetch | ✔ | PO via PO Number | — | — |
| 5 | Received_Qty | Received Qty | Number | ✔ | — | — | — |
| 6 | QC_Status | QC Status | Dropdown | — | — | Pending / Pass / Fail | — |
| 7 | Packing_Quality | Packing Quality | Dropdown | — | — | Good / Damaged / Partial | — |

**Transport Subform (visible when PO Scope = Own; GRN.csv:24 "if in PO transportation is in our scope"):**

| # | Field API Name | Display Label | Creator Field Type | Required? | Notes |
|---|----------------|---------------|--------------------|-----------|-------|
| 1 | Transporter_Name | Transporter Name | Single Line | ✔ | — |
| 2 | Transportation_Charges | Transportation Charges | Currency | ✔ | — |
| 3 | Local_Transport | Local Transport | Single Line | — | — |
| 4 | Loading_Unloading | Loading/Unloading Charges | Currency | — | — |

**Stock rule:** qty added to stock only after posting; timestamp logged; GRN number generated after posting (GRN.csv:32–35).

### 2.18 QC / QA — 6 header + 8 inspection fields (QC_QA.csv · forms.html:1023–1043 · IMPL §5.4)

**Header:**

| # | Field API Name | Display Label | Creator Field Type | Required? | Autofetch source / Lookup target | Notes |
|---|----------------|---------------|--------------------|-----------|----------------------------------|-------|
| 1 | QC_Number | QC Number | Auto Number | ✔ | — | QC-YYYY-XXXX |
| 2 | Date | Date | Date | ✔ | — | Today's date |
| 3 | GRN_Number | GRN Number | Lookup | ✔ | GRN Master | AutoFetch Item No, Name, Received Qty |
| 4 | Supplier_Name | Supplier Name | AutoFetch | ✔ | from GRN Number | QC_QA.csv:10 — forms.html omits (see §3 row 26) |
| 5 | Item_No | Item No. | AutoFetch | ✔ | GRN | per-GRN line |
| 6 | Item_Name | Item Name | AutoFetch | ✔ | GRN | — |

**Inspection Results (per item):**

| # | Field API Name | Display Label | Creator Field Type | Required? | Dropdown options | Notes |
|---|----------------|---------------|--------------------|-----------|------------------|-------|
| 1 | Inspection_Date | Inspection Date | Date | — | — | — |
| 2 | Viscosity_Result | Viscosity Result | Single Line | — | — | — |
| 3 | Density_Result | Density Result | Single Line | — | — | — |
| 4 | Color_Result | Color Result | Single Line | — | — | — |
| 5 | Moisture_Result | Moisture Result | Single Line | — | — | — |
| 6 | Accepted_Qty | Accepted Qty | Number | ✔ | — | — |
| 7 | Rejected_Qty | Rejected Qty | Number | ✔ | — | — |
| 8 | Packaging_Quality | Packaging Quality | Dropdown | — | Good / Damaged | QC_QA.csv:12 — forms.html omits (see §3 row 26) |
| 9 | QC_Status | QC Status | Dropdown | ✔ | Pass / Fail / Hold | — |
| 10 | Remarks | Remarks | Multi Line | ✔ | — | header-level (QC_QA.csv:18) |

### 2.19 Material Issue Slip (MIS) — 5 header + 6 line + 3 footer fields (MIS.csv · forms.html:1071–1092 · IMPL §6.1)

**Header:**

| # | Field API Name | Display Label | Creator Field Type | Required? | Autofetch source / Lookup target | Dropdown options | Notes |
|---|----------------|---------------|--------------------|-----------|----------------------------------|------------------|-------|
| 1 | MR_Ref | Material Req. (MR No.) | Lookup | ✔ | MR — only Released MRs shown | — | API `MR_Ref` |
| 2 | MIS_Number | MIS Number | Auto Number | ✔ | — | — | auto-generated against MR |
| 3 | Date | Date | Date | ✔ | — | — | Today's date |
| 4 | Batch_Number | Batch Number | Single Line | — | — | — | — |
| 5 | Status | Status | Dropdown | ✔ | — | Draft (auto on MR Release) / Posted (by "Post MIS" button) | C17 — forms.html:1075; MIS.csv lacks it (see §3 row 20) |

**Line Items (auto-fetched from MR):**

| # | Field API Name | Display Label | Creator Field Type | Required? | Autofetch source | Formula | Notes |
|---|----------------|---------------|--------------------|-----------|------------------|---------|-------|
| 1 | Item_Code | Item Code | AutoFetch | ✔ | MR line items | — | API `Item_Code` |
| 2 | Item_Name | Item Name | AutoFetch | ✔ | MR line items | — | — |
| 3 | Category | Category | AutoFetch | ✔ | MR line items | — | — |
| 4 | Required_Qty | Required Qty | AutoFetch | ✔ | MR line items | — | — |
| 5 | Issued_Qty | Issued Qty | Number | ✔ | — | — | — |
| 6 | Balance_Qty | Balance Qty | Formula | — | — | Required − Issued | "If Qty Shortage" (MIS.csv:12) |

**Footer:** Issued By (Single Line, ✔ — Supervisor name) · Handover To (Single Line, ✔ — Supervisor name) · Remark (Multi Line).

API names (postMIS.deluge): `MIS_Number`, `MIS_Line_Items`, `MR_Ref`, `Status`, `Posted_Time`.

### 2.20 Production Job — 10 fields (forms.html:1108–1117 · IMPL §6.2)

| # | Field API Name | Display Label | Creator Field Type | Required? | Autofetch source / Lookup target | Dropdown options | Notes |
|---|----------------|---------------|--------------------|-----------|----------------------------------|------------------|-------|
| 1 | Job_Number | Job Number | Auto Number | ✔ | — | — | JOB-YYYY-XXXX |
| 2 | Job_Date | Job Date | Date | ✔ | — | — | — |
| 3 | Project_ID | Project ID | Lookup | ✔ | Project Master | — | AutoFetch Project Name, Manager |
| 4 | MR_Sheet_No | MR Sheet No | Lookup | ✔ | MR — Released only | — | AutoFetch Items, Qty |
| 5 | FG_Code | FG Code | Lookup | ✔ | Item Muster — FG | — | FG to produce |
| 6 | Planned_FG_Qty | Planned FG Qty | Number | ✔ | — | — | planned batch qty |
| 7 | Planning_Period | Planning Period | Dropdown | ✔ | — | Week / Day | — |
| 8 | Plant | Plant | Dropdown | — | — | Wadki / Main / Neelo / Gurgaon / Bangalore | — |
| 9 | Planner_Name | Planner Name | User | ✔ | — | — | — |
| 10 | Status | Status | Dropdown | ✔ | — | Draft / Scheduled / In Progress / Completed | — |

### 2.21 Batch Manufacturing Record (BMR) — 6 header + 8 line fields (forms.html:1136–1158 · IMPL §6.3)

**Header:**

| # | Field API Name | Display Label | Creator Field Type | Required? | Autofetch source / Lookup target | Notes |
|---|----------------|---------------|--------------------|-----------|----------------------------------|-------|
| 1 | BMR_Number | BMR No | Auto Number | ✔ | — | BMR-YYYY-XXXX |
| 2 | Production_Job_Ref | Production Job Ref | Lookup | ✔ | Production Job | AutoFetch Project ID, FG Code, Planned Qty |
| 3 | Project_ID | Project ID | AutoFetch | ✔ | from Production Job Ref | — |
| 4 | Batch_No | Batch No | Single Line | ✔ | — | — |
| 5 | Date | Date | Date | ✔ | — | Today's date |
| 6 | FG_Code | FG Code | Lookup | ✔ | Item Muster — FG | AutoFetch FG Name, BOM RM list |

**Line Items (RM consumed to produce FG):**

| # | Field API Name | Display Label | Creator Field Type | Required? | Autofetch source / Lookup target | Formula | Notes |
|---|----------------|---------------|--------------------|-----------|----------------------------------|---------|-------|
| 1 | RM_Item_Code | RM Item Code | Lookup | ✔ | Item Muster — RM | — | AutoFetch Name, UOM |
| 2 | RM_Item_Name | RM Item Name | AutoFetch | ✔ | from RM Item Code | — | — |
| 3 | Batch_No_RM | Batch No (RM) | Single Line | — | — | — | — |
| 4 | Qty_Consumed | Qty Consumed | Number | ✔ | — | — | **increments MR Allocation Consumed_Qty** (bmrSubmit.deluge) |
| 5 | UOM | UOM | AutoFetch | ✔ | Item Muster via RM Code | — | — |
| 6 | Yield_FG_Output | Yield / FG Output | Number | — | — | — | — |
| 7 | Rate | Rate | AutoFetch | ✔ | MR Allocation Rate | — | G8 — forms.html:1156 (IMPL §6.3 omits Rate/Amount) |
| 8 | Amount | Amount | Formula | ✔ | — | Qty Consumed × Rate | G8 |

### 2.22 RM Consumption Entry — 5 fields (forms.html:1175–1179 · IMPL §6.4)

> **Variance check ONLY** — does NOT increment Consumed Qty (avoids double count with BMR; AGENTS.md:86).

| # | Field API Name | Display Label | Creator Field Type | Required? | Autofetch source / Lookup target | Formula | Notes |
|---|----------------|---------------|--------------------|-----------|----------------------------------|---------|-------|
| 1 | BMR_Reference | Reference to BMR | Lookup | ✔ | BMR Master | — | AutoFetch FG Code, Batch No, RM Items |
| 2 | Item_wise_RM | Item-wise RM | Lookup | ✔ | Item Muster — RM (filtered by BMR items) | — | — |
| 3 | Actual_Qty | Actual Qty | Number | ✔ | — | — | — |
| 4 | Standard_Qty | Standard Qty | AutoFetch | ✔ | BOM via FG Code | — | — |
| 5 | Variance | Variance | Formula | — | — | Actual − Standard | — |

### 2.23 Packing Entry — 5 fields (forms.html:1197–1201 · IMPL §6.5)

| # | Field API Name | Display Label | Creator Field Type | Required? | Autofetch source / Lookup target | Notes |
|---|----------------|---------------|--------------------|-----------|----------------------------------|-------|
| 1 | BMR_Reference | BMR Reference | Lookup | ✔ | BMR Master | AutoFetch FG Code, Batch No |
| 2 | FG_Product | FG Product | Lookup | ✔ | Item Muster — FG | AutoFetch FG Name, UOM |
| 3 | Packed_Qty | Packed Qty | Number | ✔ | — | — |
| 4 | Packing_Material_Consumed | Packing Material Consumed | Lookup + Number | — | Item Muster — Packaging | Item Code + Qty |
| 5 | Batch_No | Batch No | AutoFetch | ✔ | from BMR Reference | — |

**Automation:** deducts packaging material from inventory only (packingDeduct.deluge). API: `Packing_Number`, `Packing_Line_Items`.

### 2.24 FG Handover Master (FGHM) — 5 header + 10 line fields (FGHM.csv · forms.html:1219–1241 · IMPL §6.6)

**Header:**

| # | Field API Name | Display Label | Creator Field Type | Required? | Autofetch source / Lookup target | Dropdown options | Notes |
|---|----------------|---------------|--------------------|-----------|----------------------------------|------------------|-------|
| 1 | FGHM_Number | FGH No | Auto Number | ✔ | — | — | FGH-YYYY-XXXX |
| 2 | Project_ID | Project ID | Lookup | ✔ | Project Master | — | forms.html:1220 — CSV had Client/Site Name instead (see §3 row 27) |
| 3 | Handover_Date | Handover Date | Date | ✔ | — | — | Today's date |
| 4 | Batch_No | Batch No | Single Line | ✔ | — | — | CSV:10 "some times multiple batch numbers" |
| 5 | Status | Status | Dropdown | ✔ | — | Pending Acceptance / Accepted | G6 — forms.html:1223 |

**Line Items:**

| # | Field API Name | Display Label | Creator Field Type | Required? | Autofetch source / Lookup target | Formula | Dropdown options | Notes |
|---|----------------|---------------|--------------------|-----------|----------------------------------|---------|------------------|-------|
| 1 | FG_Product_Code | FG Product Code | Lookup | ✔ | Item Muster — FG | — | — | AutoFetch Name, UOM |
| 2 | FG_Product_Name | FG Product Name | AutoFetch | ✔ | from FG Product Code | — | — | — |
| 3 | FG_Qty | FG Qty | Number | ✔ | — | — | — | handover qty |
| 4 | UOM | UOM | AutoFetch | ✔ | Item Muster via FG Code | — | — | — |
| 5 | QC_Status | QC Status | Dropdown | ✔ | — | — | Pass / Fail / Hold | — |
| 6 | Damaged_Qty | Damaged Qty | Number | — | — | — | — | inline acceptance (replaces FGAN) |
| 7 | Accepted_Qty | Accepted Qty | Formula | ✔ | — | FG Qty − Damaged Qty | — | inline acceptance |
| 8 | Handed_Over_By | Handed Over By | Single Line | ✔ | — | — | — | employee name |
| 9 | Received_By | Received By | Single Line | ✔ | — | — | — | employee name |
| 10 | Remark | Remark | Multi Line | — | — | — | — | — |

**Automation:** FGHM submission → pop-up notification to Store/Logistic (FGHM.csv:25); FG stock + on inline acceptance; FGHM accept marks MR Allocation Fully Consumed (C1/C29). API: `FGHM_Number`, `FGHM_Line_Items`.

### 2.25 FG Consumption Entry — 5 header + 6 line fields (forms.html:1266–1285 · site/fgConsumption.deluge)

**Header:**

| # | Field API Name | Display Label | Creator Field Type | Required? | Autofetch source / Lookup target | Notes |
|---|----------------|---------------|--------------------|-----------|----------------------------------|-------|
| 1 | Project_ID | Project ID | Lookup | ✔ | Project Master | filters FGHM to this project |
| 2 | FGHM_Reference | FGHM Reference | Lookup | ✔ | FGHM — filtered by Project | AutoFetch FG items, Qty, Batch No |
| 3 | Task_Date | Task Date | Date | ✔ | — | date of site usage |
| 4 | Site_Location | Site Location | Single Line | ✔ | — | area/location on site |
| 5 | Supervisor | Supervisor | Single Line | ✔ | — | site supervisor name |

**Usage Line Items:**

| # | Field API Name | Display Label | Creator Field Type | Required? | Autofetch source / Lookup target | Notes |
|---|----------------|---------------|--------------------|-----------|----------------------------------|-------|
| 1 | FG_Product_Code | FG Product Code | Lookup | ✔ | Item Muster — FG | AutoFetch Name, UOM; filtered by FGHM reference |
| 2 | FG_Product_Name | FG Product Name | AutoFetch | ✔ | Item Muster | — |
| 3 | UOM | UOM | AutoFetch | ✔ | Item Muster | — |
| 4 | Used_Qty | Used Qty | Number | ✔ | — | qty consumed at site |
| 5 | Site_Area | Site Area | Single Line | — | — | where applied on site |
| 6 | Remark | Remark | Multi Line | — | — | — |

**Automation:** deduct Used Qty from FG Inventory; create Project_FG_Consumption record; log Stock Movement "FG_CONSUMPTION — OUT" (forms.html:1290). API (fgConsumption.deluge): `FGC_Number`, `Used_Qty`, `FGC_Ref`, `Site_Location`.

### 2.26 Project FG Consumption Tracking — 9 fields (forms.html:1424–1432 · AUTO-CREATED, not a manual form)

| # | Field API Name | Display Label | Creator Field Type | Required? | Source | Notes |
|---|----------------|---------------|--------------------|-----------|--------|-------|
| 1 | Project_ID | Project ID | Lookup | — | Auto | from FG Consumption Entry |
| 2 | FG_Product_Code | FG Product Code | Lookup | — | Auto | from FG Consumption Entry |
| 3 | FG_Product_Name | FG Product Name | AutoFetch | — | Auto | — |
| 4 | UOM | UOM | AutoFetch | — | Auto | — |
| 5 | Used_Qty | Used Qty | Number | — | Auto | from FG Consumption Entry |
| 6 | Consumption_Date | Consumption Date | Date | — | Auto | Today's date |
| 7 | Site_Location | Site Location | Single Line | — | Auto | from FG Consumption Entry |
| 8 | Supervisor | Supervisor | Single Line | — | Auto | from FG Consumption Entry |
| 9 | Reference_FGHM | Reference FGHM | Single Line | — | Auto | FGHM reference number |

### 2.27 RM Inventory — Stock Ledger — 13 fields (forms.html:1317–1329)

| # | Field API Name | Display Label | Creator Field Type | Required? | Autofetch source / Lookup target | Formula | Notes |
|---|----------------|---------------|--------------------|-----------|----------------------------------|---------|-------|
| 1 | Item_Code | Item Code | Lookup | ✔ | Item Muster — RM | — | unique RM code |
| 2 | Item_Name | Item Name | AutoFetch | ✔ | Item Muster | — | — |
| 3 | Category | Category | AutoFetch | ✔ | Item Muster | — | — |
| 4 | UOM | UOM | AutoFetch | ✔ | Item Muster | — | — |
| 5 | Standard_Rate | Standard Rate | AutoFetch | ✔ | Purchase Item Muster | — | G7 — latest purchase rate |
| 6 | Opening_Stock | Opening Stock | Number | ✔ | — | — | carried forward |
| 7 | GRN_Received | GRN Received | Number (auto) | ✔ | — | — | Σ GRN quantities posted |
| 8 | MIS_Issued | MIS Issued | Number (auto) | ✔ | — | — | Σ MIS quantities posted |
| 9 | Returns | Returns | Number | — | — | — | material returned to store |
| 10 | Closing_Stock | Closing Stock | Formula | ✔ | — | Opening + GRN − MIS + Returns | API `Current_Stock` (stockMoveRM.deluge) |
| 11 | Min_Stock | Min Stock | AutoFetch | ✔ | Purchase Item Muster | — | — |
| 12 | Max_Stock | Max Stock | AutoFetch | — | Purchase Item Muster | — | — |
| 13 | Reorder_Status | Reorder Status | Formula | ✔ | — | OK / Below Min / Above Max | — |

### 2.28 FG Inventory — Stock Ledger — 11 fields (forms.html:1373–1383)

| # | Field API Name | Display Label | Creator Field Type | Required? | Autofetch source / Lookup target | Formula | Notes |
|---|----------------|---------------|--------------------|-----------|----------------------------------|---------|-------|
| 1 | Item_Code | Item Code | Lookup | ✔ | Item Muster — FG | — | unique FG code |
| 2 | Item_Name | Item Name | AutoFetch | ✔ | Item Muster | — | — |
| 3 | UOM | UOM | AutoFetch | ✔ | Item Muster | — | — |
| 4 | Standard_Rate | Standard Rate | AutoFetch | ✔ | Purchase Item Muster | — | G7 |
| 5 | Opening_Stock | Opening Stock | Number | ✔ | — | — | — |
| 6 | FGHM_Accepted | FGHM Accepted | Number (auto) | ✔ | — | — | Σ FGHM accepted qty |
| 7 | Dispatched | Dispatched | Number (auto) | ✔ | — | — | Σ dispatch (SO Supply Only / DC) |
| 8 | Returns | Returns | Number | — | — | — | customer returns |
| 9 | Closing_Stock | Closing Stock | Formula | ✔ | — | Opening + FGHM − Dispatched + Returns | — |
| 10 | Min_Stock | Min Stock | AutoFetch | ✔ | Purchase Item Muster | — | — |
| 11 | Status | Status | Formula | ✔ | — | In Stock / Low Stock / Out of Stock | — |

### 2.29 Site Consumption Entry (SCE) — 7 header + 7 line fields (forms.html:1463–1484 · IMPL §6.7)

**Header:**

| # | Field API Name | Display Label | Creator Field Type | Required? | Autofetch source / Lookup target | Dropdown options | Notes |
|---|----------------|---------------|--------------------|-----------|----------------------------------|------------------|-------|
| 1 | SCE_Number | Consumption No | Auto Number | ✔ | — | — | SCE-YYYY-XXXX |
| 2 | Project_ID | Project ID | Lookup | ✔ | Project Master | — | — |
| 3 | Work_Area | Work Area | Single Line | ✔ | — | — | zone/area on site |
| 4 | Date | Date | Date | ✔ | — | — | — |
| 5 | Time_Slot | Time Slot | Dropdown | ✔ | — | Morning / Afternoon / Full Day / Night | forms.html:1467 |
| 6 | Supervisor | Supervisor | Single Line | ✔ | — | — | forms.html:1468 (IMPL:692 says User lookup — see §3 row 41) |
| 7 | Remarks | Remarks | Multi Line | — | — | — | — |

**Line Items (RM only):**

| # | Field API Name | Display Label | Creator Field Type | Required? | Autofetch source / Lookup target | Formula | Dropdown options | Notes |
|---|----------------|---------------|--------------------|-----------|----------------------------------|---------|------------------|-------|
| 1 | RM_Item_Code | RM Item Code | Lookup | ✔ | Item Muster — RM | — | — | resolves by Project ID + Item Code |
| 2 | Qty_Consumed | Qty Consumed | Number | ✔ | — | — | — | — |
| 3 | UOM | UOM | AutoFetch | ✔ | Item Muster | — | — | — |
| 4 | System_FG_Reference | System/FG Reference | Single Line | — | — | — | — | for BOM expansion (IMPL:701 says Lookup — Project Systems subform) |
| 5 | Consumption_Type | Consumption Type | Dropdown | ✔ | — | — | Actual / Wastage / Rework | — |
| 6 | Rate | Rate | AutoFetch | ✔ | MR Allocation Rate | — | — | G8 |
| 7 | Amount | Amount | Formula | ✔ | — | Qty Consumed × Rate | — | G8 |

**Automation:** submit → increment Consumed Qty on MR Allocation (Project + Item); over-consumption (>100%) BLOCKED — "Allocation Exhausted — return material first" (C5); no matching allocation → alert + block; ≥80% → real-time alert (sceSubmit.deluge).

### 2.30 Material Return Entry (MRT) — 6 header + 5 line fields (forms.html:1503–1521 · IMPL §6.8)

**Header:**

| # | Field API Name | Display Label | Creator Field Type | Required? | Autofetch source / Lookup target | Dropdown options | Notes |
|---|----------------|---------------|--------------------|-----------|----------------------------------|------------------|-------|
| 1 | Return_No | Return No | Auto Number | ✔ | — | — | MRT-YYYY-XXXX |
| 2 | Project_ID | Project ID | Lookup | ✔ | Project Master | — | — |
| 3 | Return_Date | Return Date | Date | ✔ | — | — | — |
| 4 | Returned_By | Returned By | User | ✔ | — | — | — |
| 5 | Received_By | Received By | User | ✔ | — | — | Store |
| 6 | Reason | Reason | Dropdown | ✔ | — | Excess Issued / Unused / Damaged / Wrong Item | — |

**Line Items:**

| # | Field API Name | Display Label | Creator Field Type | Required? | Autofetch source / Lookup target | Dropdown options | Notes |
|---|----------------|---------------|--------------------|-----------|----------------------------------|------------------|-------|
| 1 | RM_Item_Code | RM Item Code | Lookup | ✔ | Item Muster — RM | — | — |
| 2 | RM_Item_Name | RM Item Name | AutoFetch | ✔ | from RM Item Code | — | — |
| 3 | UOM | UOM | AutoFetch | ✔ | Item Muster | — | — |
| 4 | Return_Qty | Return Qty | Number | ✔ | — | — | — |
| 5 | Condition | Condition | Dropdown | ✔ | — | Good / Damaged / Expired | — |

**Automation:** submit → decrement Consumed Qty on MR Allocation; Good/Unused → RM stock +; Damaged/Expired → damaged stock count only (materialReturn.deluge: decrements `Consumed_Qty`, increments `Returned_Qty`, recomputes `Consumption_Percentage`).

### 2.31 Stock Movement Transaction Log — 8 fields (forms.html:1541–1547 · AUTO-populated audit trail)

| # | Field API Name | Display Label | Creator Field Type | Required? | Notes |
|---|----------------|---------------|--------------------|-----------|-------|
| 1 | DateTime | Date / Time | Date-Time | — | auto-logged on transaction posting |
| 2 | Form_Ref | Form Ref | Single Line | — | GRN-2026-001 / MIS-2026-015 / FGH-2026-008 / FGC-2026-003 / DC-2026-003 |
| 3 | Item_Code | Item Code | Single Line | — | auto from source form |
| 4 | Item_Name | Item Name | Single Line | — | auto from source form |
| 5 | Type | Type | Dropdown | — | RM / FG |
| 6 | In_Out | In / Out | Dropdown | — | In / Out |
| 7 | Qty | Qty | Number | — | transaction qty |
| 8 | Running_Balance | Running Balance | Formula | — | previous balance ± Qty |

**Writers:** stockMoveRM.deluge / stockMoveFG.deluge shared functions — fields `doc_ref`, `doc_type`, `item_code`, `qty`, `store`, `Form_Type` (RM_IN/RM_OUT/FG_IN/FG_OUT).

### 2.32 Legacy FGAN — FG Acceptance Note — 10 fields (FGAN.csv · **superseded — do NOT build**)

> forms.html:1214 "inline acceptance fields — no separate FGAN form". FGHM line items carry Damaged Qty + Accepted Qty instead (see §3 row 28).

| # | Field API Name (legacy) | Display Label | Creator Field Type | Required? | Notes |
|---|----------------|---------------|--------------------|-----------|-------|
| 1 | FGH_No | FGH No | Lookup | ✔ | autofetch if opened from notification |
| 2 | Acceptance_Date | Acceptance Date | Date | ✔ | Today's date |
| 3 | Product_No | Product No. | AutoFetch | ✔ | — |
| 4 | Product_Name | Product Name | AutoFetch | ✔ | — |
| 5 | Handovered_Qty | Handovered Quantity | AutoFetch | ✔ | — |
| 6 | Damaged_Rejected_Qty | Damaged or Packaging Rejected Quantity | Number | — | — |
| 7 | Accepted_Qty | Accepted Quantity | Number | — | — |
| 8 | Approved_By | Approved By | Single Line | ✔ | — |
| 9 | Remark | Remark | Multi Line | ✔ | — |
| 10 | (acceptance no) | Acceptance Number | Auto Number | — | generated after Approval (FGAN.csv:18) |

---

## 3. Discrepancy log (cross-source: CSV vs forms.html vs IMPLEMENTATION_PLAN.md)

| # | Form | Field / Aspect | Source A says | Source B says | Verdict (winner + why) | Severity |
|---|------|----------------|---------------|---------------|-------------------------|----------|
| 1 | Purchase Item Muster | Category options | **CSV** (Purchase_Item_Muster.csv:5): "1.RM, 2.Packaging Material, 3.Tools & Consumable, 4.Maintenance & Utility, 5.Capital & Assets, 6.Administation" — no FG | **forms.html:169 & IMPL:51**: "1.RM, 2.Packaging, 3.Tools & Consumable, 4.FG, 5.Maintenance, 6.Capital" — no Administration | forms.html/IMPL win: FG category is mandatory (FGHM/BOM/SO Subform B look up FG items from Item Muster). Drop "Administration". | FIX |
| 2 | Supplier Master | Supplier Type | **CSV:8** — field exists | forms.html:296–308 & IMPL:120–133 — absent | CSV wins (it's the actual sheet): keep field, optional. | INFO |
| 3 | Supplier Master | Pincode | **CSV:22** — field exists | forms.html/IMPL — absent | CSV wins: keep field, optional. | INFO |
| 4 | Supplier Master | Bank fields | **CSV:24–28** — 3 separate fields (Bank Name, Account No, IFSC Code) | forms.html:304 & IMPL:130 — merged single row "Bank Name / Account No / IFSC" | CSV wins: build 3 fields (Deluge + forms need distinct API names). | INFO |
| 5 | Sales Order | Sales Type options | **CSV:4–5** — "Suppy+Apply" / "Suppy (Material Sales)" (typos) | forms.html:402 — "Supply+Apply" / "Supply Only" | forms.html wins: fix typos; "Supply Only" is the canonical label used everywhere. | INFO |
| 6 | Sales Order | Alt Contact No. | **CSV:17** — mandatory field | forms.html:402–419 — absent | CSV wins: keep field. | INFO |
| 7 | Sales Order | Is proper System Require | **CSV:45** — Checkbox | forms.html — absent | CSV wins: keep (checkbox, optional). | INFO |
| 8 | Sales Order | Status | **CSV** — no status field | forms.html:419 — Dropdown Draft/Accepted/Completed/Cancelled | forms.html wins: SO needs a status for acceptance automation. | INFO |
| 9 | Project | Description / Adjustments | **Sheet2.csv:13–14** — fields exist | forms.html:474–485 — absent | Sheet2 wins: keep both (optional). | INFO |
| 10 | Project | Source of fields | **Project.csv:2–19** — dashboard mockup (Open Projects, Running Status, Margins, report list) — no form fields | forms.html §2B + Sheet2.csv define real fields | Project.csv is a dashboard screen, NOT a form; do not use it for fields. | INFO |
| 11 | Task Budget | Structure | **Sheet2.csv:16–75** — legacy: 5 categories (Transportation/Application/Manpower/Tools/Additional Expenses) each with subtasks (Grinding/Primer/Screed/Top Coat...), Dispatches (From/To/Transport Charges), Manpower Budget/Count | forms.html:501–516 — simplified G2: Category/Description/Budget Qty/Rate/Budget Amount/Actual Qty/Actual Amount | forms.html wins (G2 simplified w/ actuals for P&L); legacy subtask/dispatch detail is optional enrichment, not build scope. | INFO |
| 12 | Costing Sheet | Prepared By / Reviewed By / Revision No | **forms.html:564–569** — absent | **IMPL:267–269** — present (Prepared By ✔, Reviewed By, Revision No) | IMPL wins: forms.html is incomplete here; keep all three (Prepared By is needed for Costing dept). | FIX |
| 13 | Costing Sheet §A | Required Qty formula | **forms.html:589** — `Required_Qty = BOM Ratio × Area` | **IMPL:282** — `Total RM Required = BOM Qty × SO Area × (1 + Waste%)`; **AGENTS.md (Deluge conventions)** — `Required_Qty = round(Area × CompQty/sqm × Ratio, 1)` | **CONFLICT — must reconcile before build.** forms.html wins on priority but silently drops Waste%; recommend the IMPL formula (waste is captured in BOM Total Qty). Decide once, then fix BOM → Costing → MR chain consistently. | BLOCKER |
| 14 | Costing Sheet §E | Remarks | forms.html:648–649 — absent | **IMPL:319** — present (Multi Line) | INFO: optional; harmless to add. forms.html wins strictly, but keep Remarks for completeness. | INFO |
| 15 | Production Plan | Status options | **CSV** (Production_Report.csv:9): Draft / Approved / Released | **forms.html:683**: Draft / Released; **IMPL:343**: Draft / Reviewed / Released | forms.html wins (2-state, matches auto-creation flow); CSV & IMPL disagree with each other — treat "Approved"/"Reviewed" as legacy. | FIX |
| 16 | Production Plan | Line items level | **CSV** (Production_Report.csv:12–14): FG-level (Total SO/WO Qty, FG Stock Available, Net Production Requirement) | **forms.html:692–698**: RM-level (RM Item Code, Total Required, Available Stock, Shortage, Source, Procurement Triggered) | forms.html wins: RM-level matches Costing §A and the auto-PR trigger (per-item shortage). CSV is the legacy FG-level planning sheet. | FIX |
| 17 | MR | Form scope | **MR.csv:2–25** — legacy manual MR: no Project ID, no Material Allocation subform, no cost components; Requisition Type dropdown (options not listed), items only Item Code/Name/Category/UOM/Available Stock/Required Qty | **forms.html:727–833 & IMPL §4.3** — revised: Project ID root, 17-field Material Allocation, Application/Transport/Tools cost subforms, 5-state gate, auto-derived | **forms.html/IMPL win — do NOT build the legacy MR.** Building the CSV version breaks the entire consumption-tracking design (AGENTS.md:30–33). | BLOCKER |
| 18 | MR | Status workflow states | forms.html:714–719 — 5 states (Draft → Pending Production Verification → Production Verified → Costing Approved → Released) | forms.html:1672–1677 (§6G summary) — 4 states (Draft → Production Verified → Costing Approved → Released, missing Pending Production Verification) | 5-state wins: AGENTS.md:142 & IMPL §4.3 & forms.html §3C all confirm 5 states; the §6G diagram is an abbreviation. Internal forms.html inconsistency — fix the diagram. | INFO |
| 19 | MR Allocation | Field naming | forms.html:773 "80% Threshold Alert Flag" | automation.html:697 / deluge API `80%_Alert_Flag`; IMPL:418 "80% Threshold Alert Flag" | Consistent; use API name `80%_Alert_Flag` (label "80% Threshold Alert Flag"). | INFO |
| 20 | MIS | Status | **MIS.csv** — no status field | forms.html:1075 — Status Draft/Posted (**C17**); IMPL:587 same | forms.html/IMPL win: Status is required by postMIS.deluge (`input.Status == "Posted"`). | INFO |
| 21 | PO | HSN field name | **PO.csv:18** — "HNS" | forms.html:924–925 — HSN | HSN wins (obvious typo). | INFO |
| 22 | PO | Mode of Transport | **PO.csv:28** — field exists | forms.html:907–953 — absent (only Scope of Transport) | CSV wins: keep field (dropdown). | INFO |
| 23 | PO | UOM in line items | **PO.csv:18** — UOM column present | forms.html:923–935 — line table omits UOM | CSV wins: keep UOM line field (autofetched). | INFO |
| 24 | GRN | Supplier Code / Name | **GRN.csv:8–10** — explicit AutoFetch fields | forms.html:971–978 — absent (implied via PO lookup) | CSV wins: keep explicit Supplier Code + Supplier Name autofetch fields. | INFO |
| 25 | GRN | Client/Site Name conditional | **GRN.csv:15** — "If Select Client Site then textbox for Client/Site Name" | forms.html — absent | CSV wins: add conditional Single Line shown when Warehouse = Client Site. | INFO |
| 26 | QC/QA | Supplier Name + Packaging Quality | **QC_QA.csv:10,12** — Supplier Name (autofetch per GRN) + Packaging Quality fields | forms.html:1023–1043 — both absent | CSV wins: keep both (Packaging Quality dropdown Good/Damaged). | INFO |
| 27 | FGHM | Project ID vs Client/Site Name | **FGHM.csv:8** — Client/ Site Name | forms.html:1220 — Project ID (Lookup Project Master) | forms.html wins: Stream B requires Project anchor for FG stock per project. | FIX |
| 28 | FGHM / FGAN | Inline acceptance vs separate form | **FGAN.csv:1–18** — separate FG Acceptance Note form (FGH No lookup, Acceptance Date, Damaged/Rejected Qty, Approved By, acceptance number after approval) | **forms.html:1214** — "inline acceptance fields — no separate FGAN form"; FGHM line items 6–7 carry Damaged Qty + Accepted Qty | forms.html wins: build inline acceptance; do NOT build FGAN. | FIX |
| 29 | Rate Comparison | In/out of scope | **Rate_Comparison.csv:1–26** — full form spec | forms.html:852 — "Rate Comparison removed"; IMPL §11 — "standalone reference only" | CSV spec retained only as a standalone reference form (optional build); not part of core loop. | INFO |
| 30 | User Access & Approval Matrix | Presence in forms.html | IMPL §2.7 + Screens.csv:12–13 — full spec | **forms.html — absent entirely** | IMPL/Screens win: forms.html has a gap; build from IMPL §2.7 (User Access 4 fields + Approval Matrix 5 fields). | FIX |
| 31 | Numbering | Supplier series | forms.html:1724 — SUP-YYYY-XXXX | IMPL §8.5 — not listed | forms.html wins: add SUP-YYYY-XXXX series (Supplier Code autogen). | INFO |
| 32 | System prefixes | NUM / ARR | **Integrations.csv:8–9 + AGENTS.md:114–115** — NUM (Numbering), ARR (Arrow Marking) | IMPL:37–41 — only EP/PU/DEM/ANTI/ESD/FIL/COV | Integrations.csv/AGENTS.md win: add NUM + ARR prefixes. | INFO |
| 33 | PR / PO / GRN | Project ID on Stream A | **chemsol/AGENTS.md:15** — "These forms do NOT carry a Project ID" | forms.html:871 (PR optional), 912 (PO), 974 (GRN autofetch from PO); IMPL:478 (PR optional) | forms.html/IMPL win: Project ID is optional (stock procurement = blank; project-linked = filled). AGENTS.md statement is the legacy Stream A rule. | INFO |
| 34 | Production Plan | Planning No source | **Production_Report.csv:4** — "Planning No (MR Sheet No.)" | forms.html:676 — PLAN-YYYY-XXXX auto-created at Costing approval (before MR exists) | forms.html wins: plan precedes MR in the revised flow. | INFO |
| 35 | FG Consumption Entry | Numbering series | forms.html:1561 sample log — "FGC-2026-003" | forms.html numbering table (1700–1727) — FGC not listed; IMPL §8.5 — not listed | Add FGC-YYYY-XXXX (fgConsumption.deluge uses `FGC_Number`); the numbering reference table is incomplete. | INFO |
| 36 | BMR | Rate / Amount line fields | forms.html:1156–1157 — Rate (AutoFetch MR Allocation) + Amount (Formula) — **G8** | IMPL §6.3:630–635 — line items omit Rate/Amount | forms.html wins (G8 fields required for cost tracking). | INFO |
| 37 | PR | Approved By / Item Description | **PR.csv:12,14** — Approved By + Item Description (with notes) fields | forms.html:869–889 — absent | CSV wins: keep both (optional fields). | INFO |
| 38 | SCE | Supervisor type | forms.html:1468 — Single Line | IMPL:692 — User lookup | forms.html wins (higher priority); IMPL's User lookup is acceptable alternative. | INFO |
| 39 | GRN | Invoice fields | **GRN.csv:16** — Invoice Number + Invoice Date as separate columns | forms.html:977 — merged "Invoice Number / Date" (Text/Date) | Same content, different presentation; build as 2 fields (CSV style). | INFO |
| 40 | MR header | Department options | **MR.csv:10** — "Auto Fetch As per user Login" | forms.html:732 — AutoFetch from login | Consistent. No change. | INFO |
| 41 | MR.csv / MIS.csv | Header field "Batch Number" | CSV MR:10 & MIS:10 — Batch Number | forms.html — MR 731, MIS 1074 — Batch Number (Text) | Consistent. No change. | INFO |
| 42 | Sheet4.csv | Content | Empty (1 blank line, 2 bytes) | — | No fields to build; ignore. | INFO |
| 43 | Project.csv | Content | Dashboard mockup only (open projects, running status, margins, reports) | — | Not a form; ignore for fields. | INFO |

---

## 4. Numbering series per document form

Consolidated from **forms.html:1700–1727** + **IMPL §8.5:816–837** + deluge (`shared/numberSeries.deluge`, `poSeriesPrefix.deluge`). ✓ = in both; (F) = forms.html only; (I) = IMPL only.

| Document form | Format | Sources |
|---------------|--------|---------|
| Sales Order (SO) | SO-YYYY-XXXX | ✓ |
| Costing Sheet | CST-YYYY-XXXX | ✓ |
| Production Plan | PLAN-YYYY-XXXX | ✓ |
| Production Job | JOB-YYYY-XXXX | ✓ |
| PR | PR-YYYY-XXXX | ✓ |
| PO (Coding) | RMWAD-YYYY-XXXX | ✓ |
| PO (Non-Coding) | RM-YYYY-XXXX | ✓ |
| GRN | GRN-YYYY-XXXX | ✓ |
| MR | MR-YYYY-XXXX | ✓ |
| MIS | Auto against MR (MIS-YYYY-XXXX implied; deluge `MIS_Number`) | ✓ |
| FGHM | FGH-YYYY-XXXX | ✓ |
| QC | QC-YYYY-XXXX | ✓ |
| Project | PRJ-YYYY-XXXX | ✓ |
| System Composition | SC-YYYY-XXXX | ✓ |
| BOM / FG Formulation | BOM-YYYY-XXXX | ✓ |
| BMR | BMR-YYYY-XXXX | ✓ |
| Site Consumption Entry | SCE-YYYY-XXXX | ✓ |
| Material Return | MRT-YYYY-XXXX | ✓ |
| Customer / Site Master | CUST-YYYY-XXXX | ✓ |
| Supplier Master | SUP-YYYY-XXXX | (F) forms.html:1724 — missing from IMPL (see §3 row 31) |
| FG Consumption Entry | FGC-YYYY-XXXX | inferred from forms.html:1561 sample + `FGC_Number` deluge — missing from both series tables (see §3 row 35) |
| FGAN (legacy) | Acceptance number generated after approval | FGAN.csv:18 — superseded |

**Implementation note:** all prefixed series route through `shared/numberSeries.deluge` (No_Series counter form: Series_Prefix, Series_Year, Last_Number — automation.html F1). PO series prefix is chosen by RM Type via `poSeriesPrefix.deluge`.

---

## 5. Blueprint / status-state sets per form

| Form | Status field (API) | State set | Notes |
|------|--------------------|-----------|-------|
| MR | MR_Status | **Draft → Pending Production Verification → Production Verified → Costing Approved → Released** | CRITICAL GATE (5-state; AGENTS.md:142, forms.html:714–719). SLA: 2 hr Draft reminder, 2 hr Verified escalation, 1 hr Approved auto-release. Last Status Change + SLA Reminder Sent fields (C32). |
| Costing Sheet | Costing_Status | Draft → Under Review → Approved / Rejected | forms.html:554–557; Rejected-with-revision → increment Revision No, reset Draft (IMPL:325). |
| Production Plan | Plan_Status | Draft → Released | forms.html:683. (CSV: Draft/Approved/Released; IMPL: Draft/Reviewed/Released — see §3 row 15.) |
| SO | Status | Draft → Accepted → Completed / Cancelled | forms.html:419. |
| Project | Status | Planned → In Progress → Completed / On Hold | forms.html:482. |
| PR | Status | Draft → Pending Approval → Approved / Rejected | forms.html:874; submit auto-moves Draft → Pending Approval. |
| PO | Status | Draft / Sent / Partially Received / Fully Received / Cancelled | G5 — forms.html:914; Receipt_Status per line (Not Started/Partial/Complete). |
| GRN | (no header status) | Line QC Status: Pending / Pass / Fail; Packing Quality: Good / Damaged / Partial | Posting flag + Posted_Time logged in backend; GRN number generated after posting (GRN.csv:32–35). |
| QC/QA | QC_Status | Pass / Fail / Hold | per inspection line (forms.html:1042). |
| MIS | Status | Draft (auto on MR Release) → Posted (Post MIS button) | C17 — forms.html:1075. |
| Production Job | Status | Draft / Scheduled / In Progress / Completed | forms.html:1117. |
| FGHM | Status | Pending Acceptance → Accepted | G6 — forms.html:1223; inline acceptance updates FG stock. |
| System Composition / BOM | Status | Draft / Approved / Released | forms.html:227, 263. |
| Master forms (Item Muster, Supplier, System, Store, Customer) | Status | Active / Inactive | — |
| Purchase Item Muster | Status | Active / Inactive | CSV:27. |
| SCE / Material Return / FG Consumption / RM-FG Inventory | — | no workflow state | consumption/return entries are immediate-effect; alerts fire on submit. |

---

## Findings summary

- **Forms audited:** 31 core forms + 2 legacy (FGAN) / referenced (Material Handover, Production Order, Rework Register, FG Receiving, Vehicle & Transport) — **488 fields** enumerated across core forms (10 more in legacy FGAN).
- **Discrepancies logged:** 43 rows; **2 BLOCKER** (MR legacy-vs-revised scope; Costing §A Required Qty formula conflict), **8 FIX** (FGAN must not be built; Production Plan status set; PIM category list; Costing header Prepared By/Reviewed By/Revision No; FGHM Project ID; User Access & Approval Matrix missing from forms.html), rest INFO.
- **Biggest build risk:** three sources disagree on MR scope, Production Plan status, and the Costing §A math — reconcile before the beginner build guide is written.
- **CSV health:** Sheet4.csv empty; Project.csv is a dashboard (not a form); Project.csv/Sheet2.csv split the Project form fields; Rate_Comparison.csv is the only spec for an excluded form.
