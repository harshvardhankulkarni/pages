# Project Budget Tracking & Inventory Management — Internal Implementation Plan

**ITOTCloud Systems Pvt. Ltd. — Zoho Creator Delivery Team**

---

## Overview

This repo contains the **internal implementation plan** for our Project Budget Tracking & Inventory Management system. This is the single source of truth for the ITOTCloud delivery team: module specs, Deluge workflow logic, lookup maps, build order, and deployment checklists.

**Status:** Design complete — ready for Phase 1A console implementation.

**Platform:** Zoho Creator (low-code)
**Logic layer:** Deluge scripts, form workflows, reports
**Integration target (Phase 2):** Zoho Projects, Zoho Analytics

## The 18-Module Architecture

Subforms are **embedded** inside the parent form — they are NOT separate forms. Users enter subform data while filling the main form.

| # | Module | Form Name | Key Purpose |
|---|--------|-----------|-------------|
| 1 | Project Master | `Projects` | Central project registry, auto-numbered codes |
| 2 | Vendor Management | `Vendors` (embedded subforms: `Vendor_Contacts`, `Vendor_Documents`) | Vendor master with contacts and documents |
| 3 | Account Management | `Accounts` (embedded subforms: `Account_Contacts`, `Account_Documents`) | Customer master with contacts and documents |
| 4 | Warehouses | `Warehouses` | Multi-warehouse stock locations |
| 5 | Inventory Master | `Inventory_Items` (embedded subform: `Item_Warehouse_Stock`) | SKU catalog, HSN/SAC, per-warehouse stock |
| 6 | Budget Planning | `Budget_Plans` (embedded subform: `Budget_Components`) | Per-project budget plans |
| 7 | Budget Components | `Budget_Components` | Dynamic cost breakdown per project |
| 8 | Expense Management | `Expenses` | Actual spend against budget components |
| 9 | Budget Approval | `Budget_Approvals` | Overrun approval workflow |
| 10 | Inventory Transactions | `Inventory_Transactions` | Stock In/Out/Adjustment/Return |
| 11 | Transfer Orders | `Transfer_Orders` (embedded subform: `TO_Line_Items`) | Inter-warehouse stock transfer |
| 12 | Purchase Requisition | `Purchase_Requisitions` (embedded subform: `PR_Line_Items`) | Multi-stage approval PRs |
| 13 | Purchase Orders | `Purchase_Orders` (embedded subform: `PO_Line_Items`) | Full PO lifecycle, line-level discount/tax |
| 14 | Goods Receipt | `Goods_Receipts` (embedded subform: `GRN_Line_Items`) | Accepted/rejected qty, auto Stock In |
| 15 | Reports & Dashboards | Reports + Dashboard widgets | KPIs, Budget vs Actual, stock alerts |
| 16 | Invoicing | `Invoices` (embedded subform: `Invoice_Line_Items`) | Revenue tracking per project |
| 17 | Delivery Challan | `Delivery_Challans` (embedded subform: `DC_Line_Items`) | Goods dispatch tracking |
| 18 | BOM | `BOM` (embedded subform: `BOM_Line_Items`) | Bill of Materials for manufacturing |

## Build Phases

| Phase | Modules | Build Order | Est. Effort |
|-------|---------|-------------|-------------|
| 1A | Vendors → Accounts → Projects → Warehouses → Inventory_Items | Foundation first | Start here |
| 1B | Budget Planning → Budget Components → Inventory Transactions | Budget + stock engine | After 1A |
| 1C | Expense Management → Purchase Requisition | Spend + requests | After 1B |
| 1D | Budget Approval → Purchase Orders → Goods Receipt → Transfer Orders | Procurement cycle | After 1C |
| 1E | BOM → Delivery Challan → Invoicing | Revenue & manufacturing | After 1D |
| 1F | Reports & Dashboards (all modules incl. Project P&L) | Intelligence | After 1E |

## Key Deluge Automations (25 total)

Subforms are embedded — Deluge accesses them via `input.<subform_name>` during On Submit workflows. There is no standalone CRUD on subform records.

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
| 9 | GRN → Stock In for accepted qty | GRN Status = Open | §C.13 |
| 10 | No auto-close based on GRN — must be closed manually by user | — | §C.13 |
| 11 | PO Open → email vendor | PO Status = Open | §C.12 |
| 12 | PR Approval Stage → notify next approver | PR stage change | §C.11 |
| 13 | Daily Cron — alerts, KPI refresh, overdue invoices | Scheduled (midnight) | §C.14 |
| 14 | Invoice Sent → update project Total Invoiced | Invoice Submit | §C.15 |
| 15 | Invoice Paid → update Amount Paid, Balance Due | Invoice Submit | §C.15 |
| 16 | DC Shipped → auto-create Stock Out | DC Status = Shipped | §C.16 |
| 17 | BOM Submit → calculate component + mfg costs | BOM Submit | §C.17 |
| 18 | PR Approved → auto-create PO (Draft) | PR final approval | §C.11 |
| 19 | Stock Reservation → increment Reserved_Qty | Reservation transaction | §C.9 |
| 20 | Invoice → Auto-create Delivery Challan | Custom button on Invoice | §C.15 |
| 21 | Project Completed → auto-final Invoice | Project status change | §C.1 |
| 22 | Transaction Validation — prevent negative stock | Inventory Transaction submit | §C.9 |
| 23 | PO Cancelled — validate no linked GRN | PO Status = Cancelled | §C.12 |
| 24 | Project Completion — validate no open items | Project Status = Completed | §C.1 |
| 25 | Flag POs aged >30 days for manual close review | Scheduled workflow | §C.14 |

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
5. **Phase 2 planning** → don't break Phase 1 form designs
6. **Update this repo** when design decisions change during implementation

## Key Documents

| Document | Purpose |
|----------|---------|
| `IMPLEMENTATION_PLAN.md` | Complete field-level specs for all 18 modules, Deluge workflows, lookup map, risks |
| `AGENTS.md` | Compact AI assistant guide — module list, automation points, roles |
| `index.html` | Interactive HTML blueprint with sidebar nav, KPI bar, module cards, lookup map, build phases, role matrix, and tab+stepper implementation guide |
| `README.md` | This file — team onboarding and navigation |
| `build-viewer.html` | Markdown viewer for `build/` phase guides — loads via `?phase=1A` through `1F` |
| `build/PHASE_1A_BUILD.md` – `1F_BUILD.md` | Phase-wise console build guides with Deluge scripts, field configs, validation rules, and verification checklists (2,101 lines total) |
| `user-guide.html` | End-user guide — 17 modules in data entry order, relationship diagrams, flow charts, report descriptions |
| `handoff-spec.html` | Developer handoff spec for engineering team — component specs, design tokens, interaction states |

---

**ITOTCloud Systems Pvt. Ltd.** — Aston Plaza, Ambegaon BK, Pune — 411046
**Contact:** Implementation Lead — Zoho Creator Delivery Team
**Confidential — © 2026 — Internal Use Only**
