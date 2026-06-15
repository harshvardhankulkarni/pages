# Project Budget Tracking & Inventory Management — Internal Implementation Plan

**ITOTCloud Systems Pvt. Ltd. — Zoho Creator Delivery Team**

---

## Overview

This repo contains the **internal implementation plan** for our Project Budget Tracking & Inventory Management system. This is the single source of truth for the ITOTCloud delivery team: module specs, Deluge workflow logic, lookup maps, build order, and deployment checklists.

**Status:** Design complete — ready for Phase 1A console implementation.

**Platform:** Zoho Creator (low-code)
**Logic layer:** Deluge scripts, form workflows, reports
**Integration target (Phase 2):** Zoho Inventory, Zoho Books, Zoho Projects, Zoho Analytics

## The 17-Module Architecture

| # | Module | Form Name | Key Purpose |
|---|--------|-----------|-------------|
| 1 | Project Master | `Projects` | Central project registry, auto-numbered codes |
| 2 | Vendor Management | `Vendors` + `Vendor_Contacts` + `Vendor_Documents` | Zoho Inventory-aligned vendor master |
| 3 | Warehouses | `Warehouses` | Multi-warehouse stock locations |
| 4 | Inventory Master | `Inventory_Items` + `Item_Warehouse_Stock` | SKU catalog, HSN/SAC, per-warehouse stock |
| 5 | Budget Planning | `Budget_Plans` | Per-project budget plans |
| 6 | Budget Components | `Budget_Components` | Dynamic cost breakdown per project |
| 7 | Expense Management | `Expenses` | Actual spend against budget components |
| 8 | Budget Approval | `Budget_Approvals` | Overrun approval workflow |
| 9 | Inventory Transactions | `Inventory_Transactions` | Stock In/Out/Adjustment/Return |
| 10 | Transfer Orders | `Transfer_Orders` + `TO_Line_Items` | Inter-warehouse stock transfer |
| 11 | Purchase Requisition | `Purchase_Requisitions` + `PR_Line_Items` | Multi-stage approval PRs |
| 12 | Purchase Orders | `Purchase_Orders` + `PO_Line_Items` | Full PO lifecycle, line-level discount/tax |
| 13 | Goods Receipt | `Goods_Receipts` + `GRN_Line_Items` | Accepted/rejected qty, auto Stock In |
| 14 | Reports & Dashboards | Reports + Dashboard widgets | KPIs, Budget vs Actual, stock alerts |
| 15 | Invoicing | `Invoices` + `Invoice_Line_Items` | Revenue tracking, Zoho Books compatible |
| 16 | Delivery Challan | `Delivery_Challans` + `DC_Line_Items` | Goods dispatch tracking |
| 17 | BOM | `BOM` + `BOM_Line_Items` | Bill of Materials for manufacturing |

## Build Phases

| Phase | Modules | Build Order | Est. Effort |
|-------|---------|-------------|-------------|
| 1A | Vendor Management → Project Master → Warehouses → Inventory Master | Foundation first | Start here |
| 1B | Budget Planning → Budget Components → Inventory Transactions | Budget + stock engine | After 1A |
| 1C | Expense Management → Purchase Requisition | Spend + requests | After 1B |
| 1D | Budget Approval → Purchase Orders → Goods Receipt → Transfer Orders | Procurement cycle | After 1C |
| 1E | BOM → Delivery Challan → Invoicing | Revenue & manufacturing | After 1D |
| 1F | Reports & Dashboards (all modules incl. Project P&L) | Intelligence | After 1E |

## Key Deluge Automations (25 total)

| # | Automation | Trigger | File ref |
|---|------------|---------|----------|
| 1 | Generate Project Code | Project Create | `IMPLEMENTATION_PLAN.md` §C.1 |
| 2 | Budget Validation — sum of components ≤ total | Budget Plan Submit | §C.5 |
| 3 | Expense Budget Check — auto-approve or overrun | Expense Submit | §C.7 |
| 4 | Overrun Approval — create Budget_Approval + notify | Expense Overrun | §C.8 |
| 5 | Approval Status Change — update Expense + notify | Budget_Approval status | §C.8 |
| 6 | Stock Sync — update Item_Warehouse_Stock + roll up | Inventory Transaction | §C.9 |
| 7 | Stock Out → Auto-create Expense record | Stock Out + Project set | §C.9 (highest value) |
| 8 | Transfer Complete → paired Stock Out/In | TO Status = Completed | §C.10 |
| 9 | GRN → Stock In for accepted qty + PO update | GRN Status = Open | §C.13 |
| 10 | All items received → auto-close PO | GRN completion check | §C.13 |
| 11 | PO Open → email vendor | PO Status = Open | §C.12 |
| 12 | PR Approval Stage → notify next approver | PR stage change | §C.11 |
| 13 | Daily Cron — alerts, KPI refresh, overdue invoices | Scheduled (midnight) | §C.14 |
| 14 | Invoice Sent → update project Total Invoiced | Invoice Submit | §C.15 |
| 15 | Invoice Paid → update Amount Paid, Balance Due | Invoice Submit | §C.15 |
| 16 | DC Shipped → auto-create Stock Out | DC Status = Shipped | §C.16 |
| 17 | BOM Submit → calculate component + mfg costs | BOM Submit | §C.17 |
| 18 | PR Approved → auto-create PO (Draft) | PR final approval | §C.11 |
| 19 | Invoice → Create DC (custom button) | Invoice Sent + stock items | §C.15 |
| 20 | Stock Reservation → increment Reserved_Qty | Reservation transaction | §C.9 |
| 21 | Project Completed → auto-final Invoice | Project status change | §C.1 |

## Team Access

- **Zoho Creator Console:** [creator.zoho.com](https://creator.zoho.com) — ITOTCloud org
- **Design Docs:** Open `/budget-tracking-handoff/` in this repo's GitHub Pages
- **Full Spec:** `IMPLEMENTATION_PLAN.md` — field-level, workflow, lookup map
- **AI Agent Context:** `AGENTS.md` — optimized for AI coding assistants

## How to Use This Repo

1. **Before building a module** → read its section in `IMPLEMENTATION_PLAN.md` for field specs
2. **When writing Deluge** → follow the pseudo-code in each module's workflow section
3. **When linking forms** → reference the lookup map in `IMPLEMENTATION_PLAN.md` §D
4. **When testing** → follow the build order, seed "Main Warehouse" first
5. **Phase 2 planning** → don't break Phase 1 form designs — the data model is already Zoho Inventory compatible
6. **Update this repo** when design decisions change during implementation

## Key Documents

| Document | Purpose |
|----------|---------|
| `IMPLEMENTATION_PLAN.md` | Complete field-level specs for all 17 modules, Deluge workflows, lookup map, risks |
| `AGENTS.md` | Compact AI assistant guide — module list, automation points, roles |
| `index.html` | Interactive HTML implementation plan with expandable module cards |
| `README.md` | This file — team onboarding and navigation |

---

**ITOTCloud Systems Pvt. Ltd.** — Aston Plaza, Ambegaon BK, Pune — 411046
**Contact:** Implementation Lead — Zoho Creator Delivery Team
**Confidential — © 2026 — Internal Use Only**
