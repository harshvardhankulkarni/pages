# Chemsol — Zoho Creator Project

## Domain

Flooring/construction materials company (Epoxy, PU, Demarcation systems). System manages end-to-end project procurement, inventory, production, and project management.

## Data source

`Creator Forms Screen.xlsx` (18 sheets exported as CSV in `files/`) — sole source of truth for form structure, fields, automation rules. Read ALL CSVs before building forms.

## Form inventory

### Master Data
- **Purchase Item Muster** — RM, Packaging Material, Tools/Consumable, Maintenance/Utility, Capital/Assets, Administration. Fields: code, name, UOM (Nos/Kg/Ltr/Mtr/Kit), HSN, GST%, min/max stock, preferred supplier, lead time, status.
- **Supplier Master** — code (autogen), name, type, GSTIN, PAN, contact, bank details, payment terms, credit days.
- **System Master** — flooring system definitions (e.g., EP01 for 1mm epoxy).
- **BOM Master** — material consumption per system/product.
- **Sales Order Master** — dual-mode: Supply+Apply / Supply Only. System-code subtable with thickness, area, UOM, rate, amount. Commission, warranty, transport scope fields.
- **Customer/Site Master** — client org, contact, GST, PAN, addresses.

### Procurement (PR→PO→GRN→QC)
1. **PR** (Purchase Requisition) — PR# autogen, dept auto from login, items with autofill code/name/UOM/lead time.
2. **Rate Comparison** — PR ref, 5 supplier comparisons (dropdown, price, credit), finalised supplier/rate, PO ref.
3. **PO** (Purchase Order) — RM type (Coding/Non-Coding → different PO series: RM vs RMWAD), supplier autofetch, items table with HSN, qty, rate, GST split (CGST/SGST/IGST), delivery/payment terms, transport scope.
4. **GRN** (Goods Receipt Note) — PO ref, warehouse dropdown (Wadki/Main/Neelo/Gurgaon/Bangalore/Client Site), item checkbox for partial GRN, ordered vs received qty, QC status, packing quality, transport subform.
5. **QC/QA** — GRN ref, inspection results (viscosity, density, color, moisture), accepted/rejected qty, packaging quality.

### Inventory/Stores
- **MR** (Material Requisition) — for Production/R&D, priority dropdown, batch no, items with autofetch of available stock.
- **MIS** (Material Issue Slip) — linked to MR, items with required/issued/balance qty, issued by/handover to.
- **FGHM** (FG Handover) — client/site, batch no, FG products with qty/QC, handed over/received by.
- **FGAN** (FG Acceptance) — open from notification, acceptance qty, damaged qty, approval.
- **Material Return, Material Handover, Vehicle & Transport** — additional store forms per Screens sheet.

### Production
- **Production Planning** — MR Sheet ref, week/month period, SO/WO qty autofetch, FG stock, net requirement.
- **Batch Manufacturing Record**, **RM Consumption Entry**, **Packing Entry**, **Rework Register**.

### Project Management
- **Project** — Project ID, name, address, manager, execution base (Area/Day basis), start/end date, cost.
- **Tasks** — 5 categories: Transportation (Intracity/Intercity, Loading/Unloading → multiple dispatches with from/to/charges), Application/Execution (grinding, primer, screed, top coat, markings — per sub-area with cost/MP), Manpower (budget + count), Tools budget, Additional Expenses/Overhead.

### Departmental Groups
- **Purchase Dept** — dashboards: total purchase, open POs, pending approvals, overdue deliveries, transport.
- **Store Dept** — inventory dashboard, dispatch planning, FG receiving.
- **Production Dept** — today's production, open orders, material consumption, efficiency, pending handover.

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

- **PR→Rate Comparison→PO→GRN**: Sequential procurement flow with approvals at each stage.
- **MR→MIS**: Material issue linked to requisition with balance tracking.
- **Production→FGHM→FGAN**: FG handover then acceptance with QC data.
- **GRN posting**: Quantity added to stock only after posting; timestamp logged.
- **Rate Comparison**: Missing data notification to Purchase dept.
- **Notifications**: Pop-up triggers (e.g., FGHM submission → Store/Logistics notified).

## Key Conventions

- All `*`-marked fields are mandatory.
- Autofetch patterns: Item Code⇄Item Name, Supplier details on code selection, UOM from item.
- Departments: Purchase, Sales, Store & Logistics, Account & Finance, Admin, Project Coordinator, Project Manager 1/2/3.
- Warehouse options: Wadki, Main, Neelo, Gurgaon, Bangalore, Client Site.
- Approval Matrix: separate form defining PR/PO limits and approvers per dept.

## Reports (not an exhaustive list)

- Open PO Register, PO vs GRN Pending, Vendor Performance, Purchase by Item Group, Price Comparison, Transport Reports
- Daily Production Report, BOM vs Actual Consumption, Machine Utilization
- Project Margin, Sitewise Costing, Manpower vs Work Completion, Task Report
