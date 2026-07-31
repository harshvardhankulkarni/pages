# Chemsol — Zoho Creator ERP

## Domain

Flooring/construction materials company (Epoxy, PU, Demarcation systems). System manages end-to-end project costing, procurement, production, inventory, and site operations.

## Two-Stream Architecture

The system has two independent streams:

### Stream A: Pre-Project / Stock Procurement (No Project ID)
- **PR → PO → GRN → QC → Material Handover** — materials bought for stock
- **Material Handover** (Purchase → Store, Coding/Non-Coding RM split)
- **Inventory** sits in Store (RM + FG)
- These forms do NOT carry a Project ID. They are independent stock procurement.

### Stream B: Project-Triggered (Project ID is root)
- **SO (Supply+Apply)** → **Costing Sheet** — standalone module where Costing team creates detailed cost breakdown (5 sections: Material auto-expanded from SO×BOM, Application, Transportation, Tools, Overhead). **SO (Supply Only)** → direct FG sale, NO Project.
- **Costing Sheet Approved** → auto-creates **Project** + auto-creates **Production Plan** (Draft)
- **Production Plan Released** → checks Available Stock = physical − other allocations → auto-PR for shortage items
- **Production Plan + Costing Sheet** → **MR auto-derived** (4 cost components pre-filled from Costing Sheet, zero manual re-entry)
- **MR → Production Verified → Costing Approved → Released** (critical approval gate)
- **MR Released** → auto-MIS → Store issues RM to Production
- **Production** (BMR → RM Consumption → Packing → FGHM)
- **Site Consumption Entry** (hourly/daily task tracking per project area — replaces full Service Team module)
- **Material Return** (unused RM back to Store, credits project allocation)
- **Project Close → P&L** (real-time computed view, not just at close)

**Consumption Tracking (KEY):** The **Project is the anchor** for material consumption.
- The **MR is the consumption baseline** — records Assigned Qty per RM with ratio % and 80% alert flag.
- BMR/RM Consumption and **Site Consumption entries** resolve to MR Allocation (matched by `Project ID + Item Code`). They do **NOT** deduct from a generic stock pool.
- **SO↔BOM↔MR cross-validation**: Σ(MR Assigned Qty) must match Σ(SO Area × BOM Qty) within 5%. >5% flags, >10% blocks.
- **80% Alert**: real-time — when any allocated RM hits 80% of Assigned Qty (flag ON) → pop-up + dashboard + email to PM.
- **100% Alert**: "Allocation Exhausted" → PM + Purchase notified.

Project ID flows via: Costing Sheet → Production Plan → MR → MIS → Production (BMR → FGHM) → Site Consumption → Material Return → Close.

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

### Costing (NEW standalone module — precedes MR)
- **Costing Sheet** — Standalone detailed costing form created by Costing team AFTER SO. 5 sections: **(A) Material Cost** (auto-expanded from SO System Lines × System Composition × BOM — all RMs pre-populated), **(B) Application Cost** (labour/execution), **(C) Transportation Cost**, **(D) Tools & Tackles**, **(E) Overhead & Miscellaneous**. Total Costing Amount = sum of all 5. On Costing Approved → auto-create Project + auto-create Production Plan.
- **Production Plan** — Reviews Costing Sheet, checks existing RM stock (net of other project allocations). If stock insufficient, auto-PR on Plan Release.

### Project Hub (Root) + Sales
- **Sales Order Master** — Conditional **Sales Type** (Supply Only / Supply+Apply) controls which subform shows: **Subform A — System Lines** (Supply+Apply: System Code, Name, Thickness, Area, UOM, Rate, Amount → drives Costing Sheet) OR **Subform B — FG Lines** (Supply Only: FG Code, Name, Qty, UOM, Rate, Amount → NO Project). Supply+Apply creates Costing Sheet, which then auto-creates Project on approval.
- **Project** — Project ID, name, SO ref, address, manager, execution base (Area/Day), start/end date, cost. Systems subform.
- **Task Budget** — Category dropdown (Transport / Execution / Manpower / Tools / Overhead), Description, Qty/Area, Rate, Amount. Actual columns feed P&amp;L.

### Procurement (PR→Rate Comparison→PO→GRN→QC→Material Handover) — Stream A (No Project ID)
1. **PR** (Purchase Requisition) — PR# autogen, department auto from login, items with autofill code/name/UOM/lead time. **No Project ID.**
2. **Rate Comparison** — PR ref, 5 supplier comparisons (dropdown, price, credit), finalised supplier/rate, PO ref.
3. **PO** (Purchase Order) — RM type (Coding/Non-Coding → different PO series: RM vs RMWAD), PR reference, supplier autofetch, items table with HSN, qty, rate, GST split (CGST/SGST/IGST), delivery/payment terms, transport scope. **No Project ID.**
4. **GRN** (Goods Receipt Note) — PO ref, warehouse dropdown (Wadki/Main/Neelo/Gurgaon/Bangalore/Client Site), item checkbox for partial GRN, ordered vs received qty, QC status, packing quality, transport subform. **No Project ID.**
5. **QC/QA** — GRN ref, inspection results (viscosity, density, color, moisture), accepted/rejected qty, packaging quality.
6. **Material Handover** — Coding/Non-Coding RM split from Purchase → Store (with Bin Location subform in Store Master).

### Costing (NEW) — Standalone, before MR
- **Costing Sheet** — 5 cost sections auto-expanded from SO (via BOM). On Approval → auto-creates Project + Production Plan.
- **Production Plan** — Stock check + auto-PR trigger for shortages. Available Stock = physical − other allocations.

### Inventory/Stores — Tagged to Project (Stream B)
- **MR** (Material Requisition) — **Auto-derived** from Costing Sheet + Production Plan. All 4 cost components pre-filled. Project cost baseline with **Material Allocation subform** (Assigned Qty per RM, Allocation Ratio %, 80% Alert Flag). Consumer resolution by `Project ID + Item Code`.
- **Consumption resolution** — BMR/RM Consumption and **Site Consumption Entry** resolve to **MR Allocation** (`Project ID + Item Code`), never a generic pool. `Consumed Qty` tracked per allocated line.
- **MIS** (Material Issue Slip) — linked to MR (only Released MRs shown). Auto-created on MR Release.
- **FGHM** (FG Handover) — Inline acceptance. On accept → marks MR Allocation Fully Consumed + increments FG stock.
- **Site Consumption Entry [NEW]** — Hourly/daily task-level tracking per project work area. All entries resolve to MR Allocation for project inventory deduction.
- **Material Return Entry [NEW]** — Return unused RM from site/production to Store. Credits Consumed Qty on MR Allocation. Restores available stock.
- **Store** — RM/FG inventory with per-project tracking. Bin Location subform.

### Production — Tagged to Project
- **Production Planning** (revised) — Now auto-created from Costing Sheet approval. Stock check against other project allocations. Auto-PR for shortages.
- **Batch Manufacturing Record**, **RM Consumption Entry**, **Packing Entry**, **Rework Register** — all carry Project ID. Each consumption entry increments `Consumed Qty` on MR Allocation.

### Site Operations — Tagged to Project [NEW]
- **Site Consumption Entry** — Hourly/daily per area. Line items: RM Item Code, Qty Consumed, System/FG Reference (for BOM expansion), Consumption Type (Actual/Wastage/Rework). All entries deduct from project's MR Allocation.
- **Material Return Entry** — Return excess/damaged RM to Store. Credits project allocation.

### Costing — Tagged to Project (Revised)
- **Costing Sheet** [NEW standalone module] — Created by Costing team, auto-expanded from SO. 5 cost sections. On Approval → Project + Production Plan auto-created.
- **Cost Reports** — Variance analysis: Costing Sheet vs Actual consumption costs. Real-time Project P&amp;L.

### Excluded from core loop (moved to separate scope):
- Full Service Team module (replaced by lightweight Site Consumption Entry)
- Service Invoice, Finance (Supplier CN, Customer Invoice/AR), Logistics (DC, Outward), Vehicle & Transport, Rate Comparison

### Departmental Groups
- **Purchase Dept** — dashboards: total purchase, open POs, pending approvals, auto-PR tracking from Production Plan shortages. Stream A: no Project ID. Stream B: filterable by Project ID.
- **Store Dept** — inventory dashboard, MIS dispatch, FGHM receiving, Material Return processing. Per-project inventory filters.
- **Production Dept** — today's production, open orders, material consumption, efficiency, pending handover. Filterable by Project ID.
- **Costing Dept** — Costing Sheet status, approval dashboard, Costing vs Actual variance, Project P&amp;L.
- **Site Supervisor** — Site Consumption Entry, hourly/daily consumption tracking per area. Filterable by Project ID.

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

## Automation Requirements [REVISED]

### Costing Sheet (NEW)
- SO System Lines → System Composition → BOM → auto-expand into Costing Sheet Section A (all RMs pre-populated with BOM quantities × SO area)
- Costing Sheet Approved → auto-create Project + Production Plan (Draft)
- Costing Sheet stuck >24 hr → escalation to admin

### Production Plan (REVISED)
- Available Stock = physical stock − Σ(Assigned Qty from all other unreleased MRs) — prevents double-allocation
- Production Plan Released → auto-PR for every line where Shortage > 0
- Production Plan must be Released before MR can be auto-created

### MR (Critical Gate — REVISED)
- MR is **auto-derived** from Costing Sheet + Production Plan. All 4 cost components pre-filled. No manual data entry.
- **SO↔BOM↔MR cross-validation**: Σ(Assigned Qty) vs Σ(SO Area × BOM Qty). >5% flag, >10% block.
- MR Status: Draft → Production Verified → Costing Approved → Released
- Tighter SLAs: 2 hr Draft → reminder, 2 hr Verified → escalation, 1 hr Approved → auto-release
- MR Released → auto-create MIS draft

### Consumption Tracking (REVISED)
- BMR/RM Consumption and **Site Consumption Entry** increment `Consumed Qty` on matching MR Allocation line (`Project ID + Item Code`), never a generic pool
- **80% Alert**: real-time — formula field triggers on any consumption entry. Pop-up + banner + email.
- **100% Alert**: "Allocation Exhausted" → PM + Purchase

### FGHM (REVISED)
- On FGHM acceptance → mark MR Allocation as Fully Consumed if all RM lines exhausted

### Site Consumption Entry (NEW)
- Hourly/daily task tracking per project work area
- Each entry resolves to MR Allocation → real-time project inventory deduction
- Supports BOM expansion via System/FG Reference

### Material Return (NEW)
- Unused RM returned to Store → decrements Consumed Qty on MR Allocation
- Good condition → restores available stock
- Damaged → separate damaged stock count

### Procurement
- **PR→PO→GRN** with approvals. Stream A: no Project ID. Stream B: project-tagged.
- **PR auto-created** from Production Plan shortage (not from MR — earlier in flow)
- **GRN posting**: Qty added to stock only after posting; timestamp logged. Partial GRN via checkbox.

### P&amp;L Calculation (REVISED)
- **Real-time computed view** (not only at Project Close)
- Revenue from SO. Costs from: Costing Sheet vs actual (Site Consumption + BMR + Procurement)
- Project Inventory Status: Assigned vs Consumed vs Returned vs Remaining per RM

### Notifications
- All events in §8.7 of IMPLEMENTATION_PLAN.md. Tighter SLAs: 2 hr per MR stage, 4 hr Costing review, real-time consumption alerts.

## Key Conventions

- All `*`-marked fields are mandatory.
- Autofetch patterns: Item Code⇄Item Name, Supplier details on code selection, UOM from item, Project ID→Project Name/Manager.
- Departments: Purchase, Sales, Store & Logistics, Account & Finance, Admin, Project Coordinator, Project Manager 1/2/3.
- Warehouse options: Wadki, Main, Neelo, Gurgaon, Bangalore, Client Site.
- Approval routing uses Zoho Creator's native approval features (Blueprint/Approval processes).

## Reports (revised)

- **Project Inventory Status Report [NEW]** — Per RM per project: Assigned Qty (from MR) vs Issued (MIS) vs Consumed (BMR + Site) vs Returned vs Remaining. Single source of truth for project P&amp;L.
- **Project P&amp;L real-time view [NEW]** — Costing Sheet Total − Material Consumption Costs − Procurement Costs. On-demand, not just at close.
- **Costing Sheet vs Actual Report [NEW]** — Planned (Costing Sheet) vs actual (Site Consumption + BMR) cost variance.
- **Site Consumption Report [NEW]** — Hourly/daily consumption by work area, project, RM item.
- **Material Return Report [NEW]** — Returns by project, reason, condition.
- Open PO Register, PO vs GRN Pending, Vendor Performance, Purchase by Item Group/Project
- Daily Production Report, BOM vs Actual Consumption
- MR Status tracking with drill-through
- Project Material Allocation & 80% Utilization Report
- All reports filterable by Project ID
