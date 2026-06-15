# Project Budget Tracking & Inventory Management — Developer Handoff

**Platform:** Zoho Creator + Deluge  
**Modules:** 14 primary + 7 sub-forms  
**Automations:** ~18 Deluge workflows  
**Status:** Phase 1 — Ready for implementation

## Files

| File | Purpose |
|---|---|
| `index.html` | GitHub Pages entry — full handoff spec with all module designs, workflows, roles, and edge cases |
| `IMPLEMENTATION_PLAN.md` | Detailed implementation plan with field-level specs, relationship maps, risks |
| `AGENTS.md` | Compact instructions for AI coding assistants working in this repo |

## Quick Links

- [View Handoff Spec (HTML)](https://harshvardhankulkarni.github.io/pages/budget-tracking-handoff/)
- [Implementation Plan (Markdown)](./IMPLEMENTATION_PLAN.md)
- [AGENTS.md](./AGENTS.md)

## Build Order

1. **Phase 1A** — Projects, Vendors, Warehouses, Inventory Items
2. **Phase 1B** — Budget Plans, Budget Components, Inventory Transactions
3. **Phase 1C** — Expenses, Purchase Requisitions, Budget Alerts
4. **Phase 1D** — Budget Approvals, POs, Transfer Orders, Goods Receipt
5. **Phase 1E** — Reports & Dashboards

## Key Decision

Maintain `Item_Warehouse_Stock.Current_Stock` via Deluge on every transaction — never aggregate stock on demand.
