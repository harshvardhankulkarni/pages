# Project Budget Tracking & Inventory Management

## What This Is

A Zoho Creator-based project budget tracking and inventory management system for ITOTCloud Systems Pvt. Ltd. It manages 17 modules spanning vendor management, project master data, budget planning with component breakdown, expense tracking, inventory with multi-warehouse support, purchase requisition/ordering, goods receipt, invoicing, delivery challans, and BOM manufacturing — all connected through Deluge automation workflows.

## Core Value

Accurate, real-time budget vs actual visibility per project, with automated procurement and inventory synchronization that prevents overspend and stockouts.

## Requirements

### Validated

<!-- Shipped and confirmed valuable. -->

(None yet — Phase 1 design complete, awaiting console implementation)

### Active

<!-- Current scope. Building toward these. -->

- [ ] Foundation modules: Vendors, Projects, Warehouses, Inventory Items (Phase 1A)
- [ ] Budget engine: Budget Plans, Components, Inventory Transactions (Phase 1B)
- [ ] Spend management: Expenses, Purchase Requisitions (Phase 1C)
- [ ] Procurement cycle: Budget Approvals, POs, Goods Receipt, Transfers (Phase 1D)
- [ ] Revenue & manufacturing: BOM, Delivery Challans, Invoicing (Phase 1E)
- [ ] Reports & Dashboards: KPIs, Budget vs Actual, alerts (Phase 1F)
- [ ] AI Integration: Budget forecasting, anomaly detection, smart procurement, natural language reporting (Phase 2)

### Out of Scope

<!-- Explicit boundaries. Includes reasoning to prevent re-adding. -->

- Full Zoho Books/Inventory integration — deferred to Phase 2 planning (post Phase 1F)
- Mobile app — Zoho Creator provides mobile forms natively; no standalone app needed
- External user portal — vendor self-service portal is planned but deferred

## Context

ITOTCloud delivers Zoho-based implementation services. This project is an internal delivery blueprint for a 17-module Project Budget Tracking & Inventory Management system built on Zoho Creator. The implementation plan (IMPLEMENTATION_PLAN.md) is design-complete with field-level specs, Deluge pseudocode, lookup maps, and deployment checklists for all modules.

The system serves: Project Managers, Finance Managers, Procurement Team, Inventory Managers, and Employees. It tracks project budgets, inventory across warehouses, purchase lifecycles, and generates executive dashboards.

Integration touchpoints deferred to Phase 2 include Zoho Books, Zoho Inventory, Zoho Projects, and Zoho Analytics.

## Constraints

- **Platform**: Zoho Creator (low-code) — no custom backend code; all logic is Deluge scripts, form workflows, and reports
- **No foreign keys**: All relationships use Lookup fields — orphaned records handled via archive, not delete
- **No transactions**: Multi-step Deluge workflows need safety checks (verify state before each write)
- **Deluge runs per-record**: Use scheduled workflows for mass operations, not form-triggered scripts
- **Role-based access**: Per-form, not record-level — use form filters for department-specific views

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Zoho Creator (low-code) | ITOTCloud's core delivery platform; fastest time-to-value for clients | ✓ Good |
| Separate forms for line items | Subforms limited to <100 items; reporting requires separate forms | ✓ Good |
| Maintain Current_Stock via Deluge | Avoids on-demand aggregation across Item_Warehouse_Stock | ✓ Good |
| Formula Lookup for live values | Regular lookups cache stale data | ✓ Good |
