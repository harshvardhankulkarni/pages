# Requirements — Chemsol Zoho Creator Application

**70 v1 requirements** across 8 departments + cross-cutting automation.

---

## Admin (Phase 1)

| ID | Title | Description | Status |
|----|-------|-------------|--------|
| ADM-01 | Item Master | Create Item Master form for RM, PM, FG, consumables with Category dropdown, auto-generated codes, auto-fetch, HSN, GST, Min/Max Stock, Preferred Supplier lookup, Lead Time. | pending |
| ADM-02 | System Master | Create System Master with system codes (EP, PU, DEM, NUM, ARR, ANTI, ESD, FIL, COV), name, thickness, description, UOM. | pending |
| ADM-03 | BOM Master | Create BOM Master linking System to Items with quantity and UOM per unit. Single-level BOM. | pending |
| ADM-04 | Supplier Master | Create Supplier Master with auto-generated codes, GSTIN, PAN, contact info, bank details, Payment Terms, Credit Days. | pending |
| ADM-05 | Customer Master | Create Customer Master with auto-generated codes, GST, PAN, registered/billing/shipping addresses. | pending |
| ADM-06 | Store Master | Create Store Master with store code, name, type (RM/FG/QC/Site), location. | pending |
| ADM-07 | Bin Location Master | Create Bin Location Master with Store lookup, rack/shelf/bin 3-level hierarchy. | pending |
| ADM-08 | User Access & Approval Matrix | Create User Access form with user lookup, department, role, PR Approval Limit, PO Approval Limit. Admin-only. | pending |

## Sales (Phase 2)

| ID | Title | Description |
|----|-------|-------------|
| SAL-01 | SO/WO Dual Mode | Sales/Work Order with Supply+Apply and Supply-only modes selected at creation |
| SAL-02 | Supply+Apply form | WO mode fields: system code, area, UOM, site info, project type, warranty |
| SAL-03 | Supply-only form | SO mode fields: FG items with quantity, rate, auto-calculated totals |
| SAL-04 | Customer auto-fetch | Customer details auto-fill from Customer Master on code entry |
| SAL-05 | Line-item calculations | Auto-calculated amounts, totals, GST |
| SAL-06 | Commission entry | Commission field — Percentage or Fixed |
| SAL-07 | File attachments | PO/BOQ document upload per order |
| SAL-08 | Payment terms | Payment terms dropdown as per defined options |
| SAL-09 | Transportation scope | Transport within PO scope flag, line items |

## Purchase (Phase 3)

| ID | Title | Description |
|----|-------|-------------|
| PUR-01 | PR auto-number | Auto-generated PR number with departmental sequence |
| PUR-02 | PR item lines | Item entry subform with auto-fetch from Item Master |
| PUR-03 | Department filter | Department dropdown on PR, restricts visibility |
| PUR-04 | PR approval | Approval workflow on PR submission |
| PUR-05 | Rate Comparison form | Multi-supplier quote collection against PR |
| PUR-06 | Supplier quote entry | 1-5 supplier quotes per line item with rate, delivery |
| PUR-07 | Rate finalisation | Finalise supplier and rate from comparison |
| PUR-08 | PO auto-number | Dual series: RMWAD (coding) / RM (non-coding) |
| PUR-09 | PO from Rate Comp | Auto-populate PO from finalised Rate Comparison |
| PUR-10 | GST calculation | CGST/SGST/IGST auto-calculated on line items |
| PUR-11 | PO printable format | PO with T&C, signature fields, print layout |
| PUR-12 | PO Amendment | Change order before GRN, approval escalation at ₹2L |
| PUR-13 | GRN auto-number | Auto-generated GRN number |
| PUR-14 | Partial GRN | Checkbox selection for partial receipt per line item |
| PUR-15 | Stock update on post | Stock updated only when GRN is posted (not saved) |
| PUR-16 | Transport subform | Conditional transport details field (visible if transport in PO scope) |
| PUR-17 | Warehouse selection | Store selection dropdown (Client Site shows text field) |
| PUR-18 | QC status on GRN | QC status set to "Pending" on GRN creation |

## Quality Control (Phase 4)

| ID | Title | Description |
|----|-------|-------------|
| QC-01 | QC form against GRN | QC record created referencing a GRN with auto-number |
| QC-02 | Supplier auto-fetch | Supplier details auto-fill from GRN |
| QC-03 | Test result entry | Viscosity, Density, Color, Moisture test results per batch |
| QC-04 | Pass/Fail status | QC Status: Pass/Fail/Pending with Accepted/Rejected quantities |
| QC-05 | Stock control | Pass → stock available; Fail → quarantined/rejected |
| QC-06 | Partial acceptance | Accepted Qty < Received Qty supported |

## Store & Inventory (Phase 5)

| ID | Title | Description |
|----|-------|-------------|
| STO-01 | MR auto-number | Auto-generated Material Requisition number |
| STO-02 | MR with stock display | MR items show available stock, shortage flag |
| STO-03 | MIS creation | Material Issue Slip against MR with stock deduction on posting |
| STO-04 | Material Return | Return to store with stock add-back on posting |
| STO-05 | Material Handover | Inter-store/site material transfer with tracking |
| STO-06 | FG Receiving | Finished goods receipt from production, stock addition |
| STO-07 | Vehicle & Transport | Vehicle entry, transport details, gate pass tracking |
| STO-08 | MR approval | Approval workflow on MR submission |
| STO-09 | MR auto-fetch | Item details auto-fetch from Item Master on code entry |

## Production (Phase 6)

| ID | Title | Description |
|----|-------|-------------|
| PROD-01 | Production Planning | Plan referencing SO/WO with FG stock visibility |
| PROD-02 | Production Order | Order against plan/system with dates |
| PROD-03 | BMR with BOM fetch | Batch Manufacturing Record auto-fetches RM/PM from BOM |
| PROD-04 | RM Consumption | Actual consumption entry against planned BOM |
| PROD-05 | Packing Entry | FG packing/output recording |

## Project Management (Phase 7)

| ID | Title | Description |
|----|-------|-------------|
| PRJ-01 | Create Project | Project creation with auto-ID, manager, execution mode, dates |
| PRJ-02 | Systems subform | Flooring systems assigned to project |
| PRJ-03 | Task buckets | Transport, Application, Manpower, Tools, Additional Expenses |
| PRJ-04 | Area/Day modes | Execution mode determines task fields (Area vs Day basis) |
| PRJ-05 | Project Dashboard | Open projects, POs, margins, issues, execution vs target, costs |
| PRJ-06 | Machinery & Equipment | Equipment management sub-module per project |
| PRJ-07 | Labour management | Labour tracking per project |

## Reports & Security (Phase 8)

| ID | Title | Description |
|----|-------|-------------|
| RPT-01 | Purchase reports | Open PO Register, PO vs GRN Pending, Vendor Performance, Price Comparison, Transportation |
| RPT-02 | Store reports | Material Issue/Return Register, FG Receiving, Vehicle & Transport |
| RPT-03 | Production reports | Daily Production, BMR, Material Consumption |
| RPT-04 | Project reports | Margin reports, Execution vs Achieve, Monthly Manpower/Transport Costs |
| SEC-01 | Form-level permissions | C/R/U/D per role per form per USER-ROLES matrix |
| SEC-02 | Field-level security | Restricted fields (Bank details, Standard Rate) per role |
| SEC-03 | Record-level access | Department-scoped visibility for transactional forms |
| SEC-04 | Approval limits | PR ₹50K, PO ₹2L escalation thresholds enforced |

## Cross-Cutting Automation

| ID | Title | Phases |
|----|-------|--------|
| AUT-01 | Auto-numbering | All — sequential codes per form format |
| AUT-02 | Auto-fetch lookups | All — code→name, item→UOM, etc. |
| AUT-03 | Calculations | 2,3,6,7 — GST, totals, margin, planned vs actual |
| AUT-04 | Stock updates | 3,4,5 — GRN add, MIS deduct, Return add-back |
| AUT-05 | Approval workflows | 3,5,8 — PR, MR, PO approvals |
| AUT-06 | GRN posting workflow | 3 — stock update only on Post action |
