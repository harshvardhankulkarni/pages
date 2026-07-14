# Chemsol — Zoho Creator Project

## Domain

Flooring/construction materials company (Epoxy, PU, Demarcation systems). System manages end-to-end project procurement, inventory, production, and project management.

## Two-Stream Architecture

The system has two independent streams:

### Stream A: Pre-Project / Stock Procurement (No Project ID)
- **PR → PO → GRN → QC → Material Handover** — materials bought for stock
- **Material Handover** (Purchase → Store, Coding/Non-Coding RM split)
- **Inventory** sits in Store (RM + FG)
- These forms do NOT carry a Project ID. They are independent stock procurement.

### Stream B: Project-Triggered (Project ID is root)
- **SO (Supply+Apply)** → auto-creates **Project**. The SO **System Lines** subform (EP01…) defines the **System → FG → RM composition** (via System Composition + BOM) that drives backend consumption. **SO (Supply Only)** → sells **FG directly** (FG Lines subform); **NO Project** created — direct stock sale, no consumption tracking.
          - **Project → MR → MIS** (project consumes materials from Store inventory). **The MR carries a per-project Material Allocation subform** — each RM line records its **Assigned Qty** (allocation baseline), **Allocation Ratio %** (share of total project RM allocation, always sums to 100%), and an **80% Threshold Alert Flag**. Applies to **Supply+Apply** projects only (SO auto-creates the Project); Supply Only FG sales skip MR allocation and the 80% alert entirely.
- **Project → Production Planning → BMR → Packing → FGHM** (consume RM → produce FG with inline acceptance).
- **Project → Costing Approval** (material cost valuation gate).
- **Project → Service Team** (Area Measurement → Material Custody → Work Start → Final Invoice).
- **Project → Finance** (Customer Invoice / AR / Supplier CN / GL).
- **Project → Logistics** (Delivery Challan → Outward Invoice).

**Consumption Tracking (KEY):** The **Project is the anchor** for material consumption.
- FG production (BMR / RM Consumption) and **Site Manager consumption entries** both resolve to the **project-assigned RM** recorded in the MR Material Allocation (matched by `Project ID + Item Code`). They do **NOT** deduct from a generic stock pool.
- The SO System composition (FG → RM via BOM) is the template: a Site Manager entry made against the System/FG is expanded into RMs at BOM ratios, then increments `Consumed Qty` on the matching MR Allocation line.
- **80% Alert:** when any allocated RM reaches **80% of its Assigned Qty** (and the flag is ON), the system fires a pop-up + dashboard banner + email to the Project Manager.

Project ID flows downstream via: MR → MIS. Production Planning → BMR → Packing → FGHM. Service → Finance → Logistics.

Master Data (Item Muster, Suppliers, Customers, Store Master) is global — used by both streams.

## Data source

`Creator Forms Screen.xlsx` (18 sheets exported as CSV in `files/`) — sole source of truth for form structure, fields, automation rules. Read ALL CSVs before building forms.

## Form inventory

### Master Data (Global)
- **Purchase Item Muster** — RM, Packaging Material, Tools/Consumable, Maintenance/Utility, Capital/Assets, Administration. Fields: code, name, UOM (Nos/Kg/Ltr/Mtr/Kit), HSN, GST%, min/max stock, preferred supplier, lead time, status.
- **Supplier Master** — code (autogen), name, type, GSTIN, PAN, contact, bank details, payment terms, credit days.
- **System Master** — flooring system definitions (e.g., EP01 for 1mm epoxy).
- **System Composition** — which FGs make up each system (System→FG mapping).
- **BOM / FG Formulation** — which RMs make up each FG (FG→RM mapping with ratios).
- **Customer/Site Master** — client org, contact, GST, PAN, addresses.

### Project Hub (Root) + Sales
- **Sales Order Master** — Conditional **Sales Type** (Supply Only / Supply+Apply) controls which subform shows: **Subform A — System Lines** (Supply+Apply: System Code, Name, Thickness, Area, UOM, Rate, Amount, Commission%, Warranty, Transport Scope → auto-creates Project) OR **Subform B — FG Lines** (Supply Only: FG Code, Name, Qty, UOM, Rate, Amount → NO Project, direct FG sale). Only Supply+Apply triggers Project creation + MR Material Allocation + 80% alert.
- **Project** — Project ID, name, SO ref, address, manager, execution base (Area/Day), start/end date, cost. Systems subform.
- **Task Budget** — Single table with Category dropdown (Transport / Execution / Manpower / Tools / Overhead), Description, Qty/Area, Rate, Amount, Manpower. Plus Actual Qty, Actual Rate, Actual Amount columns for P&amp;L.

### Procurement (PR→PO→GRN→QC) — Stream A (No Project ID)
1. **PR** (Purchase Requisition) — PR# autogen, Project ID lookup, dept auto from login, items with autofill code/name/UOM/lead time.
2. **Rate Comparison** — PR ref, 5 supplier comparisons (dropdown, price, credit), finalised supplier/rate, PO ref.
3. **PO** (Purchase Order) — RM type (Coding/Non-Coding → different PO series: RM vs RMWAD), Project ID (autofetch from PR), supplier autofetch, items table with HSN, qty, rate, GST split (CGST/SGST/IGST), delivery/payment terms, transport scope.
4. **GRN** (Goods Receipt Note) — PO ref, Project ID (autofetch), warehouse dropdown (Wadki/Main/Neelo/Gurgaon/Bangalore/Client Site), item checkbox for partial GRN, ordered vs received qty, QC status, packing quality, transport subform.
5. **QC/QA** — GRN ref, inspection results (viscosity, density, color, moisture), accepted/rejected qty, packaging quality.

### Inventory/Stores — Tagged to Project
- **MR** (Material Requisition) — Project ID lookup, priority dropdown, batch no, RM line items (autofetch available stock), AND a **Material Allocation subform** (Assigned Qty per RM, Allocation Ratio %, 80% Alert Flag) that is the per-project consumption budget.
- **Consumption resolution** — FG production and Site Manager entries deduct from the **project-assigned RM** (MR Allocation), not a generic pool; `Consumed Qty` is tracked per allocated line and compared to `Assigned Qty` for the 80% alert.
- **MIS** (Material Issue Slip) — linked to MR, items with required/issued/balance qty, issued by/handover to.
- **FGHM** (FG Handover) — Project ID lookup, client/site, batch no, FG products with qty/QC, handed over/received by. Inline acceptance on handover.
- **Material Return, Material Handover, Vehicle & Transport** — additional store forms, tagged to project.

### Production — Tagged to Project
- **Production Planning** — Project ID lookup, MR Sheet ref, week/month period, SO/WO qty autofetch, FG stock, net requirement.
- **Batch Manufacturing Record**, **RM Consumption Entry**, **Packing Entry**, **Rework Register** — all carry Project ID.

### Service Team — Tagged to Project
- **Service Entry** — Area allocation, work execution tracking, service invoice generation.
- **Service Invoice** — Auto-generated from completed service work orders.

### Costing — Tagged to Project
- **Costing Approval** — Project cost estimation, approval workflow, budget allocation.
- **Cost Reports** — Variance analysis, cost vs budget comparison.

### Logistics — Tagged to Project
- **Delivery Challan (DC)** — Outward dispatch, vehicle tracking, delivery confirmation.
- **Logistics Reports** — Dispatch tracking, delivery performance, transport cost analysis.

### Departmental Groups
- **Purchase Dept** — dashboards: total purchase, open POs, pending approvals, overdue deliveries, transport. Filterable by project.
- **Store Dept** — inventory dashboard, dispatch planning, FG receiving. Filterable by project.
- **Production Dept** — today's production, open orders, material consumption, efficiency, pending handover. Filterable by project.
- **Service Team** — service work allocation, completion tracking, invoicing. Filterable by project.
- **Logistics** — dispatch planning, delivery challans, transport tracking. Filterable by project.

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

- **Coding materials**: RMWAD prefix
- **Non-coding materials**: RM prefix
- Different series per category

## Automation Requirements

- **PR→Rate Comparison→PO→GRN**: Sequential procurement flow with approvals at each stage. Stream A — no Project ID.
- **MR→MIS**: Material issue linked to requisition with balance tracking. Tagged to Project.
- **Production→FGHM**: FG handover with inline acceptance and QC data. Tagged to Project.
- **GRN posting**: Quantity added to stock only after posting; timestamp logged.
- **Rate Comparison**: Missing data notification to Purchase dept.
- **Notifications**: Pop-up triggers (e.g., FGHM submission → Store/Logistics notified).
- **SO → Project**: Auto-create Project on SO acceptance (Supply+Apply mode).
- **P&amp;L Calculation**: Project-level P&amp;L auto-computed on Project Close. Revenue from SO minus costs from Materials (PO×GRN), Execution/Manpower/Transport/Tools/Overhead (Task Budget Actuals), Production (BMR RM Consumption + Packing).
- **MR Material Allocation**: Each MR records per-project RM allocation (Assigned Qty, Allocation Ratio, 80% Alert Flag). Establishes the consumption budget baseline.
- **Consumption → Project-Assigned RM**: BMR/RM Consumption and Site Manager entries increment `Consumed Qty` on the matching MR Allocation line (`Project ID + Item Code`), never a generic pool.
- **80% Consumption Alert**: When any allocated RM hits 80% of Assigned Qty (flag ON), fire pop-up + dashboard banner + email to Project Manager.

## Key Conventions

- All `*`-marked fields are mandatory.
- Autofetch patterns: Item Code⇄Item Name, Supplier details on code selection, UOM from item, Project ID→Project Name/Manager.
- Departments: Purchase, Sales, Store & Logistics, Account & Finance, Admin, Project Coordinator, Project Manager 1/2/3.
- Warehouse options: Wadki, Main, Neelo, Gurgaon, Bangalore, Client Site.
- Approval Matrix: separate form defining PR/PO limits and approvers per dept.

## Reports (not an exhaustive list)

- Open PO Register, PO vs GRN Pending, Vendor Performance, Purchase by Item Group/Project, Price Comparison, Transport Reports
- Daily Production Report, BOM vs Actual Consumption, Machine Utilization
- Project Material Allocation & 80% Utilization Report (per-RM Assigned vs Consumed vs Alert status)
- Project Margin, Sitewise Costing, Manpower vs Work Completion, Task Report
- Project P&amp;L Report (Revenue − Total Cost = Gross Margin, computed view)
- All reports filterable by Project ID
