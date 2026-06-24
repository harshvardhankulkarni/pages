# Roadmap: Chemsol — Zoho Creator Application

**8 phases** | **70 v1 requirements**

---

## Phase 1: Master Data & Admin

**Goal:** Build all foundational master data forms (Item, System, BOM, Supplier, Customer, Store, Bin Location, User Access) that every downstream transactional module depends on.

**Dependencies:** None (greenfield).

**Success Criteria:**
1. Admin can create, edit, search, and view Items (RM/PM/FG) with full field set including auto-fetch between Item Code and Item Name
2. User can create Flooring Systems with system codes (EP/PU/DEM/ANTI/ESD/etc.) and map material consumption via BOM
3. Supplier and Customer masters are operational with auto-generated codes, GSTIN, PAN, and bank details
4. Stores and Bin Locations are defined; Admin can configure user roles and approval limits
5. All master data lookups return correct values in dependent forms during testing

**Requirements:** ADM-01, ADM-02, ADM-03, ADM-04, ADM-05, ADM-06, ADM-07, ADM-08

**Automation (bundled):** AUT-01 (Item/Supplier/Customer auto-numbering), AUT-02 (Item/Supplier/Customer auto-fetch lookups)

---

## Phase 2: Sales Order / Work Order

**Goal:** Build the core revenue transaction form with dual-mode (Supply+Apply / Supply-only), auto-fetch from masters, line-item calculations, and file attachments.

**Dependencies:** Phase 1 (Item Master, System Master, Customer Master).

**Success Criteria:**
1. User can create a Sales Order (Supply mode) with FG line items, quantity, rate, and auto-calculated totals
2. User can create a Work Order (Supply+Apply mode) with System Code, Area, UOM, site info, project type, warranty
3. Form fields dynamically switch based on Supply+Apply vs Supply-only mode selection
4. Customer details, System details, and line-item amounts auto-fetch and auto-calculate on code entry
5. User can attach PO/BOQ files, set payment terms, transportation scope, and commission (Percentage or Fixed)

**Requirements:** SAL-01, SAL-02, SAL-03, SAL-04, SAL-05, SAL-06, SAL-07, SAL-08, SAL-09

**Automation (bundled):** AUT-01 (SO/WO auto-numbering), AUT-02 (Customer/System auto-fetch), AUT-03 (line-item and total calculations)

---

## Phase 3: Procurement — PR → Rate Comparison → PO → GRN

**Goal:** Build the complete sequential procurement workflow from Purchase Requisition through Rate Comparison, Purchase Order, PO Amendment, and Goods Receipt Note with partial receipt and stock update on posting.

**Dependencies:** Phase 1 (Item Master, Supplier Master, Store Master).

**Success Criteria:**
1. User can create a PR with auto-number, auto-fetch item details, departmental filtering, and submit for approval
2. User can create a Rate Comparison against approved PR, collect quotes from 1-5 suppliers, finalise supplier and rate
3. User can generate PO with dual auto-number series (RM / RMWAD), auto-calculated GST (CGST/SGST/IGST), printable format with T&C
4. PO Amendment workflow allows changes before GRN; approval escalation works at ₹2L threshold
5. User can create GRN with partial receipt via checkbox, warehouse selection (Client Site shows site name textbox), transport subform conditional on PO scope, stock updates only on Post, with QC status set to "Pending"

**Requirements:** PUR-01, PUR-02, PUR-03, PUR-04, PUR-05, PUR-06, PUR-07, PUR-08, PUR-09, PUR-10, PUR-11, PUR-12, PUR-13, PUR-14, PUR-15, PUR-16, PUR-17, PUR-18

**Automation (bundled):** AUT-01 (PR/PO/GRN auto-numbering), AUT-02 (Item/Supplier auto-fetch), AUT-03 (GST calculations, amounts), AUT-04 (GRN stock update), AUT-05 (PR/PO approval workflows), AUT-06 (GRN posting workflow)

---

## Phase 4: Quality Control

**Goal:** Build QC/QA forms linked to GRN for batch-level testing of Viscosity, Density, Color, and Moisture, with Pass/Fail status determining stock availability.

**Dependencies:** Phase 3 (GRN — QC is created against GRN items).

**Success Criteria:**
1. User can create a QC record against a GRN with auto-number and date, auto-fetching Supplier and line items
2. User can enter Viscosity, Density, Color, and Moisture test results per item
3. QC Status (Pass/Fail/Pending) with Accepted/Rejected quantities correctly controls stock availability
4. Passing QC makes stock fully available; failing QC quarantines/rejects stock
5. Partial acceptance (Accepted Qty < Received Qty) is supported

**Requirements:** QC-01, QC-02, QC-03, QC-04, QC-05, QC-06

**Automation (bundled):** AUT-01 (QC auto-numbering), AUT-02 (GRN/Supplier auto-fetch), AUT-04 (stock status update based on QC result)

---

## Phase 5: Store & Inventory

**Goal:** Build Material Requisition (MR), Material Issue Slip (MIS), Material Return, Material Handover, FG Receiving, and Vehicle & Transport forms with stock impact on posting.

**Dependencies:** Phase 1 (Item Master, Store Master), Phase 3 (stock exists after GRN).

**Success Criteria:**
1. User can create MR with auto-number, requisition type, priority, auto-fetch item details including available stock
2. MR shows shortage flag when Required Qty exceeds Available Stock
3. User can create MIS against MR with auto-number; posting reduces stock by issued quantity
4. User can process Material Return (stock add-back) and Material Handover between stores/sites
5. User can record FG Receiving from production and Vehicle & Transport details

**Requirements:** STO-01, STO-02, STO-03, STO-04, STO-05, STO-06, STO-07, STO-08, STO-09

**Automation (bundled):** AUT-01 (MR/MIS auto-numbering), AUT-02 (Item auto-fetch), AUT-04 (MIS stock deduction, Material Return stock add-back, FG Receiving stock addition), AUT-05 (MR approval workflow)

---

## Phase 6: Production

**Goal:** Build Production Planning, Production Order, Batch Manufacturing Record (BMR), RM Consumption, and Packing Entry forms to manage the full production lifecycle.

**Dependencies:** Phase 1 (Item Master, BOM Master), Phase 2 (SO/WO as production demand source), Phase 5 (FG Receiving links to packing).

**Success Criteria:**
1. User can create a Production Plan referencing SO/WO quantities with FG stock visibility
2. User can create a Production Order against a plan/system
3. BMR auto-fetches RM/PM consumption from BOM Master based on selected system
4. User can record actual RM consumption against planned and create Packing Entry for FG output

**Requirements:** PROD-01, PROD-02, PROD-03, PROD-04, PROD-05

**Automation (bundled):** AUT-02 (BOM auto-fetch in BMR), AUT-03 (planned vs actual consumption comparison)

---

## Phase 7: Project Management

**Goal:** Build the Project creation form with 5 task buckets (Transport, Application, Manpower, Tools, Additional Expenses), Area/Day execution modes, and the Project Dashboard with margin tracking and monthly cost aggregation.

**Dependencies:** Phase 1 (Customer Master, Item Master), Phase 2 (WO references), Phase 3 (PO references), Phase 5 (Material issues to projects).

**Success Criteria:**
1. User can create a Project with auto-generated ID, manager assignment, execution mode (Area/Day), dates, and cost
2. Project supports Systems subform and 5 task buckets with correct visibility based on execution mode
3. Application tasks use Area/Cost/Machine Power when Area Basis; Manpower uses Budget + Count when Day Basis
4. Project Dashboard displays Open Projects, Active POs, Margins, Issues, Execution vs Target, Monthly Manpower/Transport costs
5. User can manage Machinery & Equipment and Labour sub-modules per project

**Requirements:** PRJ-01, PRJ-02, PRJ-03, PRJ-04, PRJ-05, PRJ-06, PRJ-07

**Automation (bundled):** AUT-01 (Project auto-numbering), AUT-03 (cost calculations, margin computations)

---

## Phase 8: Reports, Dashboards & Permissions

**Goal:** Build department-wise reports, apply role-based security (form/field/record-level permissions), enforce approval limits, and perform end-to-end integration testing across all modules.

**Dependencies:** All prior phases (forms and data must exist before reports and permissions can be tested against them).

**Success Criteria:**
1. Purchase reports are operational: Open PO Register, PO vs GRN Pending, Vendor Performance, Price Comparison, Transportation
2. Store reports are operational: Material Issue/Return, FG Receiving, Vehicle & Transport
3. Production and Project reports are operational: Daily Production, BMR, Material Consumption, Margins, Execution vs Achieve
4. Role-based permissions enforce form-level C/R/U/D, field-level visibility, and record-level access per the permissions matrix
5. Approval limits (PR: ₹50K, PO: ₹2L) are enforced across all applicable workflows

**Requirements:** RPT-01, RPT-02, RPT-03, RPT-04, SEC-01, SEC-02, SEC-03, SEC-04

**Automation (bundled):** AUT-05 (approval limit enforcement)

---

## Requirements Traceability

| Phase | Requirements | Count |
|-------|-------------|-------|
| 1. Master Data & Admin | ADM-01 to ADM-08 | 8 |
| 2. Sales Order / Work Order | SAL-01 to SAL-09 | 9 |
| 3. Procurement (PR→PO→GRN) | PUR-01 to PUR-18 | 18 |
| 4. Quality Control | QC-01 to QC-06 | 6 |
| 5. Store & Inventory | STO-01 to STO-09 | 9 |
| 6. Production | PROD-01 to PROD-05 | 5 |
| 7. Project Management | PRJ-01 to PRJ-07 | 7 |
| 8. Reports, Dashboards & Permissions | RPT-01 to RPT-04, SEC-01 to SEC-04 | 8 |
| **Total** | | **70** |

**Cross-cutting (bundled into each phase):** AUT-01 to AUT-06 (auto-numbering, auto-fetch, calculations, stock updates, approvals, GRN posting)

---

*Generated: 2026-06-24*
