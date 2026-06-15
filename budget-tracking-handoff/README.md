# Project Budget Tracking & Inventory Management

**A Zoho Creator Implementation by ITOTCloud Systems Pvt. Ltd.**

---

## Overview

This repository contains the complete design artifacts for a **Project Budget Tracking & Inventory Management** system built on the **Zoho Creator** low-code platform. The system provides end-to-end project financial control, multi-warehouse inventory tracking, procurement lifecycle management, and executive reporting — all within a single Zoho Creator application.

The data model is designed to be **Zoho Inventory compatible**, making Phase 2 integration seamless if API sync is later required.

## Who We Are

**ITOTCloud Systems Pvt. Ltd.** is a **Zoho Premium Partner** and **Zoho Creator Partner** based in Pune, India. We specialize in delivering enterprise-grade Zoho solutions — CRM automation, custom Creator applications, Books integrations, Projects sync, and Deluge scripting. This repository is maintained by our internal implementation team for project delivery and knowledge continuity.

## The 14-Module Architecture

| # | Module | Purpose |
|---|--------|---------|
| 1 | **Project Master** | Central project registry with budgets, statuses, and PM assignment |
| 2 | **Vendor Management** | Multi-contact, multi-address vendor master with tax IDs, payment terms |
| 3 | **Warehouses** | Multi-warehouse stock tracking with default warehouse seeding |
| 4 | **Inventory Master — Items** | SKU-level item catalog (goods/services), HSN/SAC, price lists, stock aggregation |
| 5 | **Budget Planning** | Per-project budget plans with status workflow (Draft → Active → Revised → Closed) |
| 6 | **Budget Components** | Dynamic budget breakdown per project (Labor, Materials, etc.) with consumption tracking |
| 7 | **Expense Management** | Expense submission with auto-approval or overrun routing |
| 8 | **Budget Approval Workflow** | Overrun approval process with PM + Finance Manager notifications |
| 9 | **Inventory Transactions** | Stock In/Out/Adjustment/Return with per-warehouse tracking |
| 10 | **Transfer Orders** | Inter-warehouse stock movement with paired transaction generation |
| 11 | **Purchase Requisition** | Multi-line item requisitions with 3-stage approval (Dept → Finance → Procurement) |
| 12 | **Purchase Orders** | Full PO lifecycle with line-level discount/tax, billing/shipping addresses |
| 13 | **Goods Receipt** | Accepted/rejected quantity tracking, auto-inventory update, PO closure |
| 14 | **Reports & Dashboards** | Executive KPIs, Budget vs Actual, stock alerts, vendor spend, and more |

## Build Phases

```
Phase 1A:  Project Master → Vendor Management → Warehouses → Inventory Master
Phase 1B:  Budget Planning → Budget Components || Inventory Transactions
Phase 1C:  Expense Management → Purchase Requisition
Phase 1D:  Budget Approval || Purchase Orders → Goods Receipt || Transfer Orders
Phase 1E:  Reports & Dashboards (all modules)
```

## Key Deluge Automations

| # | Automation | Description |
|---|------------|-------------|
| 1 | **Budget Validation** | Sum of component budgets must not exceed approved project budget |
| 2 | **Auto-Inventory Deduction** | Stock Out on a project auto-creates Expense record and updates budget |
| 3 | **Warehouse Stock Sync** | Every transaction updates `Item_Warehouse_Stock` + rolls up to `Item.Current_Stock` |
| 4 | **Budget Alerts** | Scheduled workflow triggers at 80%, 90%, 100% consumption |
| 5 | **Overrun Approval Workflow** | Expense exceeding component budget routes to PM + Finance Manager |
| 6 | **PO Lifecycle** | `Draft → Open → Partially Invoiced → Invoiced → Closed / Cancelled` |
| 7 | **Goods Receipt** | Accepted qty → Stock In + PO update; rejected qty logged for returns |
| 8 | **Transfer Orders** | Completion auto-generates paired Stock Out / Stock In transactions |
| 9 | **Multi-Stage PR Approval** | Dept Manager → Finance → Procurement, with email notifications |

## User Roles

| Role | Key Actions |
|------|------------|
| Administrator | Full access to all modules and settings |
| Project Manager | Manage projects, track budgets, approve overruns |
| Finance Manager | Budget approvals, financial reporting, cost oversight |
| Procurement Team | Create requisitions, manage POs, vendor communication |
| Inventory Manager | Stock transactions, warehouse management, transfer orders |
| Employee/User | Submit expenses, request purchases |

## Quick Reference

- **Platform**: Zoho Creator (Deluge scripts, forms, workflows, reports)
- **Forms**: ~18 primary forms including line-item subforms
- **Workflows**: ~18 Deluge automations (17 On Submit + 1 Scheduled Cron)
- **Integration Ready**: Data model aligned with Zoho Inventory, Books, Projects, Analytics
- **Design Constraints**: See [IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md) Section A for Zoho Creator constraints (no foreign keys, no transactions, subform limitations, etc.)

## How to Contribute

This repository holds **design artifacts only** — FRD, data models, workflow diagrams, role matrices, form/dashboard designs, and the implementation roadmap.

1. **Design changes** are made via markdown files in this repo
2. **Implementation** happens in the Zoho Creator console — never in this repo
3. When designing a new module or modifying an existing one, follow this pattern:
   - Form fields → Validation rules → Deluge workflow → Report/Dashboard → Role permissions
4. Use the [solution template](../templates/solution-template.md) for new client solutions

## Key Documents

| Document | Description |
|----------|-------------|
| [AGENTS.md](./AGENTS.md) | Project overview for AI agents: modules, automation points, roles, reporting |
| [IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md) | Full implementation plan: 14 module designs, Deluge workflows, lookup maps, risks |

---

**ITOTCloud Systems Pvt. Ltd.** — Aston Plaza, Ambegaon BK, Pune — 411046  
Confidential — © 2026
