# Chemsol — Zoho Creator Project

## Domain

Flooring/construction materials company (Epoxy, PU, Demarcation systems). System manages end-to-end project procurement, inventory, production, and project management.

## Project-Centric Architecture

**Project is the root entity.** All downstream forms carry a Project ID lookup:

- SO (Supply+Apply) → auto-creates Project
- Project → PR → PO → GRN → QC (all carry Project ID)
- Project → MR → MIS (carry Project ID)
- Project → Production Planning → BMR → Packing (carry Project ID)
- Project → FGHM → FGAN (carry Project ID)
- Project ID flows downstream via lookup: PR → Rate Comparison → PO → GRN. MR → MIS. FGHM → FGAN.

Nothing exists outside a project context. Master Data (Item Muster, Suppliers, Customers) is global.

## Data source

`Creator Forms Screen.xlsx` (18 sheets exported as CSV in `files/`) — sole source of truth for form structure, fields, automation rules. Read ALL CSVs before building forms.

## Form inventory

### Master Data (Global)
- **Purchase Item Muster** — RM, Packaging Material, Tools/Consumable, Maintenance/Utility, Capital/Assets, Administration. Fields: code, name, UOM (Nos/Kg/Ltr/Mtr/Kit), HSN, GST%, min/max stock, preferred supplier, lead time, status.
- **Supplier Master** — code (autogen), name, type, GSTIN, PAN, contact, bank details, payment terms, credit days.
- **System Master** — flooring system definitions (e.g., EP01 for 1mm epoxy).
- **BOM Master** — material consumption per system/product.
- **Customer/Site Master** — client org, contact, GST, PAN, addresses.

### Project Hub (Root) + Sales
- **Sales Order Master** — Supply+Apply mode (auto-creates Project). System-code subtable with thickness, area, UOM, rate, amount. Commission, warranty, transport scope.
- **Project** — Project ID, name, SO ref, address, manager, execution base (Area/Day), start/end date, cost. Systems subform.
- **Task Budget** — Single table with Category dropdown (Transport / Execution / Manpower / Tools / Overhead), Description, Qty/Area, Rate, Amount, Manpower.

### Procurement (PR→PO→GRN→QC) — Tagged to Project
1. **PR** (Purchase Requisition) — PR# autogen, Project ID lookup, dept auto from login, items with autofill code/name/UOM/lead time.
2. **Rate Comparison** — PR ref, 5 supplier comparisons (dropdown, price, credit), finalised supplier/rate, PO ref.
3. **PO** (Purchase Order) — RM type (Coding/Non-Coding → different PO series: RM vs RMWAD), Project ID (autofetch from PR), supplier autofetch, items table with HSN, qty, rate, GST split (CGST/SGST/IGST), delivery/payment terms, transport scope.
4. **GRN** (Goods Receipt Note) — PO ref, Project ID (autofetch), warehouse dropdown (Wadki/Main/Neelo/Gurgaon/Bangalore/Client Site), item checkbox for partial GRN, ordered vs received qty, QC status, packing quality, transport subform.
5. **QC/QA** — GRN ref, inspection results (viscosity, density, color, moisture), accepted/rejected qty, packaging quality.

### Inventory/Stores — Tagged to Project
- **MR** (Material Requisition) — Project ID lookup, priority dropdown, batch no, items with autofetch of available stock.
- **MIS** (Material Issue Slip) — linked to MR, items with required/issued/balance qty, issued by/handover to.
- **FGHM** (FG Handover) — Project ID lookup, client/site, batch no, FG products with qty/QC, handed over/received by.
- **FGAN** (FG Acceptance) — open from notification, acceptance qty, damaged qty, approval.
- **Material Return, Material Handover, Vehicle & Transport** — additional store forms, tagged to project.

### Production — Tagged to Project
- **Production Planning** — Project ID lookup, MR Sheet ref, week/month period, SO/WO qty autofetch, FG stock, net requirement.
- **Batch Manufacturing Record**, **RM Consumption Entry**, **Packing Entry**, **Rework Register** — all carry Project ID.

### Departmental Groups
- **Purchase Dept** — dashboards: total purchase, open POs, pending approvals, overdue deliveries, transport. Filterable by project.
- **Store Dept** — inventory dashboard, dispatch planning, FG receiving. Filterable by project.
- **Production Dept** — today's production, open orders, material consumption, efficiency, pending handover. Filterable by project.

## System Code Conventions

| Prefix | Meaning |
|--------|---------|
| EP | Epoxy Flooring (EP01=1mm, EP02=2mm...) |
| PU | PU Flooring |
| DEM | Demarcation Line |
| NUM | Numbering |
| ARR | Arrow Marking |
| ANTI | Anti Static Flooring |
| ESD | ESD Flooring |
| FIL | Filling |
| COV | Coving |

## PO Numbering

- **Coding materials**: RM prefix (Purchase dept only)
- **Non-coding materials**: RMWAD prefix
- Different series per category

## Automation Requirements

- **PR→Rate Comparison→PO→GRN**: Sequential procurement flow with approvals at each stage. All tagged to Project.
- **MR→MIS**: Material issue linked to requisition with balance tracking. Tagged to Project.
- **Production→FGHM→FGAN**: FG handover then acceptance with QC data. Tagged to Project.
- **GRN posting**: Quantity added to stock only after posting; timestamp logged.
- **Rate Comparison**: Missing data notification to Purchase dept.
- **Notifications**: Pop-up triggers (e.g., FGHM submission → Store/Logistics notified).
- **SO → Project**: Auto-create Project on SO acceptance (Supply+Apply mode).

## Key Conventions

- All `*`-marked fields are mandatory.
- Autofetch patterns: Item Code⇄Item Name, Supplier details on code selection, UOM from item, Project ID→Project Name/Manager.
- Departments: Purchase, Sales, Store & Logistics, Account & Finance, Admin, Project Coordinator, Project Manager 1/2/3.
- Warehouse options: Wadki, Main, Neelo, Gurgaon, Bangalore, Client Site.
- Approval Matrix: separate form defining PR/PO limits and approvers per dept.

## Reports (not an exhaustive list)

- Open PO Register, PO vs GRN Pending, Vendor Performance, Purchase by Item Group/Project, Price Comparison, Transport Reports
- Daily Production Report, BOM vs Actual Consumption, Machine Utilization
- Project Margin, Sitewise Costing, Manpower vs Work Completion, Task Report
- All reports filterable by Project ID
