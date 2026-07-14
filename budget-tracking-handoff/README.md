# Project Budget Tracking & Inventory Management — Internal Implementation Plan

**ITOTCloud Systems Pvt. Ltd. — Zoho Creator Delivery Team**

---

## Overview

This repo contains the **internal implementation plan** for our Project Budget Tracking & Inventory Management system. This is the single source of truth for the ITOTCloud delivery team: module specs, Deluge workflow logic, lookup maps, build order, and deployment checklists.

**Status:** Design complete — ready for Phase 1A console implementation. 27 modules, 58+ automations.

**Platform:** Zoho Creator (low-code)
**Logic layer:** Deluge scripts, form workflows, reports
**Integration target (Phase 2):** Zoho Projects, Zoho Analytics

## The 27-Module Architecture

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
| 13 | Purchase Orders | `Purchase_Orders` (embedded subform: `PO_Line_Items`) | Full PO lifecycle, line-level discount/tax, per-line receipt tracking |
| 14 | Goods Receipt | `Goods_Receipts` (embedded subform: `GRN_Line_Items`) | Accepted/rejected qty, credit tracking, auto Stock In |
| 15 | **Supplier Credit Notes** | `Supplier_Credit_Notes` (embedded subform: `SCN_Line_Items`) | **Finance-initiated credit/debit notes against suppliers for defective/rejected items** |
| 16 | Reports & Dashboards | Reports + Dashboard widgets | KPIs, Budget vs Actual, stock alerts |
| 17 | Invoicing | `Invoices` (embedded subform: `Invoice_Line_Items`) | Revenue tracking per project |
| 18 | Delivery Challan | `Delivery_Challans` (embedded subform: `DC_Line_Items`) | Goods dispatch tracking |
| 19 | BOM | `BOM` (embedded subform: `BOM_Line_Items`) | Bill of Materials for manufacturing |
| 20 | Vendor Bills (AP) | `Vendor_Bills` (embedded subform: `Bill_Line_Items`) | Record vendor invoices against POs, 3-way match, AP aging |
| 21 | Payments | `Payments` | Unified AP vendor payments and AR customer receipts |
| 22 | Currency Exchange Rates | `Currency_Rates` | FX rate management for multi-currency support |
| 23 | Accounting Periods | `Accounting_Periods` | Month-end close, period locking, GRNI accrual |
| 24 | Audit Log | `Audit_Log` | Immutable audit trail for all P0 financial forms |
| 25 | Customer Credit Notes | `Customer_Credit_Notes` (embedded subform: `CCN_Line_Items`) | Customer returns/credit — reduces Invoice Balance Due |
| 26 | Manufacturing Orders | `Manufacturing_Orders` (embedded subform: `MO_Components`) | Production lifecycle — reserve, issue, receive finished goods |
| 27 | Sales Orders | `Sales_Orders` (embedded subform: `SO_Line_Items`) | Customer order management — invoice/DC creation buttons |

## Build Phases

| Phase | Modules | Build Order | Est. Effort |
|-------|---------|-------------|-------------|
| 1A | Vendors → Accounts → Projects → Warehouses → Inventory_Items | Foundation first | Start here |
| 1B | Budget Planning → Budget Components → Inventory Transactions | Budget + stock engine | After 1A |
| 1C | Expense Management → Purchase Requisition | Spend + requests | After 1B |
| 1D | Budget Approval → Purchase Orders (enhanced) → Goods Receipt (enhanced) → **Supplier Credit Notes** → Transfer Orders | Procurement + supplier credits | After 1C |
| 1E | BOM → Delivery Challan → Invoicing | Revenue & manufacturing | After 1D |
| 1F | Reports & Dashboards (all modules incl. Project P&L) | Intelligence | After 1E |
| 1G | Vendor Bills → Payments | AP/AR sub-ledger | After 1F |
| 1H | FX Rates → Accounting Periods → Tax/GST | Cross-cutting financial | After 1G |
| 1I | Audit Log → Expense Allocations → Budget Revisions | Governance & controls | After 1H |
| 1J | PO/Bill/Payment approval + Committed Budget + SoD | Approval workflows & controls | After 1I |
| 1K | Customer Credit Notes → Manufacturing Orders → Sales Orders | Gaps closure | After 1J |

## Key Deluge Automations (58+ total)

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
| 26 | SCN Issued — update PO credits, auto Return to Vendor | SCN Status = Issued | §C.15 |
| 27 | SCN Settled — clear PO credit flag | SCN Status = Settled | §C.15 |
| 28 | PO Receipt Status per line item — recalculate from GRN | GRN Submit (Open) | §C.13 |
| 29 | Bill Received — record vendor bill, notify finance | Bill Status = "Received" | §C.20 |
| 30 | Bill Matched — 3-way match validation (PO × GRN × Bill), calculate PPV | Bill Status = "Matched" | §C.20 |
| 31 | Bill Approved — finalize PPV, update AP metrics | Bill Status = "Approved" | §C.20 |
| 32 | Bill Cancelled — validate no linked Payments or SCNs | Bill Status = "Cancelled" | §C.20 |
| 33 | Payment Completed (AP) — update Bill Amount_Paid + Balance_Due + Status | Payment Submit | §C.21 |
| 34 | Payment Completed (AR) — update Invoice Amount_Paid + Balance_Due + Status | Payment Submit | §C.21 |
| 35 | Payment Reversed — reverse Amount_Paid update on linked document | Payment Reversed | §C.21 |
| 36 | Weighted Average Cost — recalc Average_Cost on Stock In | Inventory Transaction (Stock In) | §C.5 |
| 37 | FX Rate Lookup — auto-populate rate from Currency_Rates | Bill/Invoice/Payment Create | §H.1 |
| 38 | FX Gain/Loss — calculate difference on Payment | Payment Submit | §H.1 |
| 39 | Period Lock — reject posting to closed periods | All financial forms | §H.2 |
| 40 | Audit Log Status Change — log every status change | All P0 forms submit | §I.1 |
| 41 | Audit Log Financial Edit — log field-level changes | All P0 forms submit | §I.1 |
| 42 | Expense Allocation — validate sum = expense, update multiple components | Expense Submit | §I.2 |
| 43 | Budget Revision — auto-create on budget amount change | Budget Approval Submit | §I.3 |
| 44 | GRNI Accrual — identify unbilled GRN lines | Scheduled (month-end) | §H.2 |
| 45 | Period Close Validation — verify no late transactions | Period Status = Closed | §H.2 |
| 46 | PO Budget Check — validate budget before Open | PO Status = Pending Approval | §C.12 |
| 47 | PO Budget Commit — increment Committed_Amount on Open | PO Status = Open | §C.12 |
| 48 | PO Budget Release — decrement Committed_Amount on Cancel | PO Status = Cancelled | §C.12 |
| 49 | Bill Pending Approval — route to Finance Manager after match | Bill Status = Matched | §C.20 |
| 50 | Payment Approval Routing — threshold-based auto-approve | Payment Status = Pending Approval | §C.21 |
| 51 | PR Budget Check — validate available budget before PO creation | PR final approval | §C.11 |
| 52 | CCN Issued — reduce Invoice Balance Due, create return inventory | CCN Status = Issued | §K.1 |
| 53 | CCN Cancelled — reverse Invoice adjustments | CCN Status = Cancelled | §K.1 |
| 54 | MO Released — reserve component stock | MO Status = Released | §K.2 |
| 55 | MO Completed — issue components, receive finished goods | MO Status = Completed | §K.2 |
| 56 | MO Cancelled — release reserved stock | MO Status = Cancelled | §K.2 |
| 57 | SO → Create Invoice — custom button for uninvoiced items | Button click | §K.3 |
| 58 | SO → Create DC — custom button for undelivered items | Button click | §K.3 |

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
| `IMPLEMENTATION_PLAN.md` | Complete field-level specs for all 27 modules, Deluge workflows, lookup map, risks |
| `AGENTS.md` | Compact AI assistant guide — module list, automation points, roles |
| `index.html` | Interactive HTML blueprint with sidebar nav, KPI bar, module cards, lookup map, build phases, role matrix, and tab+stepper implementation guide |
| `README.md` | This file — team onboarding and navigation |
| `build-viewer.html` | Markdown viewer for `build/` phase guides — loads via `?phase=1A` through `1F` |
| `build/PHASE_1A_BUILD.md` – `1K_BUILD.md` | Phase-wise console build guides with Deluge scripts, field configs, validation rules, and verification checklists |
| `user-guide.html` | End-user guide — 24 modules in data entry order, relationship diagrams, flow charts, report descriptions |
| `handoff-spec.html` | Developer handoff spec for engineering team — component specs, design tokens, interaction states |
| `TESTING_GUIDE.md` | Phase-by-phase testing scenarios with sample data, expected results, edge cases, and full end-to-end integration test |

---

**ITOTCloud Systems Pvt. Ltd.** — Aston Plaza, Ambegaon BK, Pune — 411046
**Contact:** Implementation Lead — Zoho Creator Delivery Team
**Confidential — © 2026 — Internal Use Only**
