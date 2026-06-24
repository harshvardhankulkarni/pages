# Requirements: Chemsol — Zoho Creator Application

**Defined:** 2026-06-24
**Core Value:** Chemsol's entire business operations run through a single, accurate Zoho Creator system replacing manual tracking.

## v1 Requirements

### Admin — Master Data

- [ ] **ADM-01**: User can create, edit, search, and view Items (RM/PM/FG) with Category, Code, Name, UOM, HSN, Min/Max Stock, Standard Rate, Preferred Supplier, Lead Time
- [ ] **ADM-02**: Item Code and Item Name auto-fetch each other; UOM auto-fetches from Item Master
- [ ] **ADM-03**: User can create, edit, and view Flooring Systems with System Code (EP/PU/DEM/ANTI/etc.), Name, Thickness, UOM
- [ ] **ADM-04**: User can create BOM Master mapping material consumption per system
- [ ] **ADM-05**: User can manage Suppliers with auto-generated code, GSTIN, PAN, Bank details, Payment Terms, Credit Days
- [ ] **ADM-06**: User can manage Customers with auto-generated code, Contact, GST, PAN, Billing/Shipping Addresses
- [ ] **ADM-07**: User can define Stores (RM/FG/QC/Site) and Bin Locations (Rack/Shelf/Bin)
- [ ] **ADM-08**: Admin can configure User Access roles and Approval Matrix (PR/PO limits by role)

### Sales — Order Management

- [ ] **SAL-01**: User can create Sales Order (Supply mode) with FG line items, Rate, Amount, Billing/Shipping
- [ ] **SAL-02**: User can create Work Order (Supply+Apply mode) with System Code, Area, UOM, Rate, Amount, Site info, Project Type, Warranty, Commission
- [ ] **SAL-03**: SO/WO form switches fields based on mode selection (Supply+Apply vs Supply-only)
- [ ] **SAL-04**: Customer details auto-fetch from Customer Master on Code selection
- [ ] **SAL-05**: System details auto-fetch from System Master on Code selection
- [ ] **SAL-06**: Line item Amount auto-calculates (Area × Rate for WO, Qty × Rate for SO)
- [ ] **SAL-07**: Total Work Order/Sales Order Amount auto-calculated from line items
- [ ] **SAL-08**: User can set Payment Terms, Transportation Scope + Amount, Lead Time, attach PO/BOQ files (multiple)
- [ ] **SAL-09**: Commission can be set as Percentage or Fix Amount

### Purchase — Procurement

- [ ] **PUR-01**: User can create PR with auto-number, auto-fetch for Item Code/Name/UOM/Lead Time, Department from login
- [ ] **PUR-02**: PR requires approval before proceeding to Rate Comparison
- [ ] **PUR-03**: User can create Rate Comparison against an approved PR, quote from 1-5 suppliers, finalise supplier and rate
- [ ] **PUR-04**: User can create PO with auto-number (RM for Non-coding, RMWAD for Coding materials)
- [ ] **PUR-05**: PO auto-fetches Supplier details, Item details, HSN, UOM, GST%
- [ ] **PUR-06**: PO line items auto-calculate Basic Amount, GST Amount, Total Amount
- [ ] **PUR-07**: PO footer shows CGST/SGST/IGST breakdown and Total in words
- [ ] **PUR-08**: PO can be printed with standard T&C
- [ ] **PUR-09**: PO requires approval (Manager ≤ ₹2L, Director > ₹2L)
- [ ] **PUR-10**: PO Amendment allows changes before GRN
- [ ] **PUR-11**: User can create GRN against PO with partial receipt via checkbox selection
- [ ] **PUR-12**: GRN auto-fetches Supplier and line items from PO
- [ ] **PUR-13**: GRN supports warehouse selection (Wadki, Main, Neelo, Gurgaon, Bangalore, Client Site)
- [ ] **PUR-14**: Client Site warehouse shows additional textbox for site name
- [ ] **PUR-15**: GRN Transport subform visible only when PO scope = Own
- [ ] **PUR-16**: GRN updates stock only on Post (not Save)
- [ ] **PUR-17**: GRN Number generated after posting
- [ ] **PUR-18**: GRN sets QC status to "Pending" for all items

### Quality Control

- [ ] **QC-01**: User can create QC record against GRN with auto-number and date
- [ ] **QC-02**: QC auto-fetches Supplier and line items from GRN
- [ ] **QC-03**: User can enter Viscosity, Density, Color, Moisture results per item
- [ ] **QC-04**: User can set QC Status (Pass/Fail/Pending) with Accepted/Rejected quantities
- [ ] **QC-05**: QC pass makes stock fully available; QC fail quarantines/rejects stock
- [ ] **QC-06**: Partial acceptance supported (Accepted Qty < Received Qty)

### Store — Inventory

- [ ] **STO-01**: User can create MR with auto-number, Requisition Type, Priority, Department from login
- [ ] **STO-02**: MR auto-fetches Item Name, Category, UOM, Available Stock on Item Code entry
- [ ] **STO-03**: MR shows shortage flag when Required Qty > Available Stock
- [ ] **STO-04**: User can create MIS against MR with auto-number
- [ ] **STO-05**: MIS posting reduces stock by issued quantity
- [ ] **STO-06**: User can process Material Return (stock add-back)
- [ ] **STO-07**: User can process Material Handover between stores/sites
- [ ] **STO-08**: User can create FG Receiving from production (stock add to FG store)
- [ ] **STO-09**: User can record Vehicle & Transport details

### Production

- [ ] **PROD-01**: User can create Production Plan with Planning No, Date, Period, SO/WO Qty vs FG Stock
- [ ] **PROD-02**: User can create Production Order against a plan/system
- [ ] **PROD-03**: User can create Batch Manufacturing Record with BOM-based RM/PM consumption auto-fetch
- [ ] **PROD-04**: User can record actual RM consumption vs planned
- [ ] **PROD-05**: User can create Packing Entry for FG output

### Project Management

- [ ] **PRJ-01**: User can create Project with auto-generated ID, Name, Address, Manager, Execution Base (Area/Day), Dates, Cost
- [ ] **PRJ-02**: Project supports Systems subform (System, Area, UOM)
- [ ] **PRJ-03**: User can manage 5 task buckets: Transportation (Dispatch sub-tasks), Application/Execution, Manpower, Tools, Additional Expenses
- [ ] **PRJ-04**: Application task uses Area/Cost/MP when Execution Base = Area Basis
- [ ] **PRJ-05**: Manpower uses Budget + Count when Execution Base = Day Basis
- [ ] **PRJ-06**: Project Dashboard shows Open Projects, Active POs, Margins, Issues, Execution vs Target, Monthly Manpower/Transport costs
- [ ] **PRJ-07**: User can manage Machinery & Equipment and Labour sub-modules per project

### Reports

- [ ] **RPT-01**: Purchase reports — Open PO Register, PO vs GRN Pending, Vendor Performance, Purchase by Item Group, Price Comparison, Transportation
- [ ] **RPT-02**: Store reports — Material Issue/Return, FG Receiving, Vehicle & Transport
- [ ] **RPT-03**: Production reports — Daily Production, BMR, Order Status, Material Consumption, BOM vs Actual, Production Loss, FG Handover
- [ ] **RPT-04**: Project reports — Margins, Execution vs Achieve

### Security & Access

- [ ] **SEC-01**: Role-based form-level permissions (C/R/U/D) per the User Roles & Permissions Matrix
- [ ] **SEC-02**: Field-level restrictions (Rate hidden from non-Purchase, Project Cost hidden from non-Admin/PM)
- [ ] **SEC-03**: Record-level access rules (PR by department, PO by purchase, Project by PM)
- [ ] **SEC-04**: Approval limit enforcement (PR: ₹50K, PO: ₹2L)

### Automation & Workflows

- [ ] **AUT-01**: Auto-numbering on all documents (PR, PO-RM, PO-RMWAD, GRN, MR, MIS, QC, SO, WO)
- [ ] **AUT-02**: Auto-fetch workflows (Item, Supplier, Customer, System lookups)
- [ ] **AUT-03**: Calculation workflows (Amount, GST, Totals in PO and SO/WO)
- [ ] **AUT-04**: Stock update workflows (GRN → Stock In, MIS → Stock Out, FG Receiving → Stock In)
- [ ] **AUT-05**: Approval workflows (PR, Rate Comparison, PO, MR) with limit escalation
- [ ] **AUT-06**: GRN posting workflow (number generation, stock update, QC trigger)

## v2 Requirements

Deferred to future release.

### Integrations

- **INT-01**: Zoho Books sync for accounting/invoicing
- **INT-02**: Zoho CRM sync for lead-to-order pipeline
- **INT-03**: SMS/Email notifications on approval/rejection

### Advanced Features

- **ADV-01**: Stock reorder auto-alert when stock < Min Stock
- **ADV-02**: Barcode generation for Item Master
- **ADV-03**: Automated PO generation from MR (for non-stock items)
- **ADV-04**: Mobile-optimised project site photo upload

## Out of Scope

| Feature | Reason |
|---------|--------|
| Payroll processing | Not part of Creator app scope |
| Fixed asset management | Not in Chemsol's requirements |
| HR/employee lifecycle management | Handled externally |
| Online payment gateway | B2B business — invoices/POs only |
| Multi-currency support | India-only operations |
| Barcode/RFID scanning | Not in requirements |
| Real-time external ERP integration | No external ERP to integrate with |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| ADM-01 through ADM-08 | Phase 1 | Pending |
| SAL-01 through SAL-09 | Phase 2 | Pending |
| PUR-01 through PUR-18 | Phase 3 | Pending |
| QC-01 through QC-06 | Phase 4 | Pending |
| STO-01 through STO-09 | Phase 5 | Pending |
| PROD-01 through PROD-05 | Phase 6 | Pending |
| PRJ-01 through PRJ-07 | Phase 7 | Pending |
| RPT-01 through RPT-04 | Phase 8 | Pending |
| SEC-01 through SEC-04 | Phase 8 | Pending |
| AUT-01 through AUT-06 | Throughout | Pending |

**Coverage:**
- v1 requirements: 70 total
- Mapped to phases: 70
- Unmapped: 0 ✓

---
*Requirements defined: 2026-06-24*
*Last updated: 2026-06-24 after initial definition*
