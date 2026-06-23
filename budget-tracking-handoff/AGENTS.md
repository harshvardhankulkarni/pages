# AGENTS.md — Project Budget Tracking & Inventory Management (Internal)

## Project type
Zoho Creator low-code application. All logic is in **Deluge scripts**, forms, workflows, and reports. This repo holds the internal implementation blueprint for the ITOTCloud delivery team.

## What this repo holds
Internal implementation plan: field-level module specs, Deluge pseudocode, lookup relationship maps, build phases, role permissions matrix, and deployment checklist. This is the single source of truth for the Zoho Creator console build.

## 18 canonical modules

Subforms are **embedded** inside the parent form — they are NOT separate forms. Users enter subform data while filling the main form, and Deluge accesses them via `input.<subform_name>` during On Submit.

1. Project Master — `Projects`
2. Vendor Management — `Vendors` (embedded subforms: `Vendor_Contacts`, `Vendor_Documents`)
3. Account Management — `Accounts` (embedded subforms: `Account_Contacts`, `Account_Documents`)
4. Warehouses — `Warehouses`
5. Inventory Master — `Inventory_Items` (embedded subform: `Item_Warehouse_Stock`)
6. Budget Planning — `Budget_Plans` (embedded subform: `Budget_Components`)
7. Budget Components — `Budget_Components`
8. Expense Management — `Expenses`
9. Budget Approval Workflow — `Budget_Approvals`
10. Inventory Transactions — `Inventory_Transactions`
11. Transfer Orders — `Transfer_Orders` (embedded subform: `TO_Line_Items`)
12. Purchase Requisition — `Purchase_Requisitions` (embedded subform: `PR_Line_Items`)
13. Purchase Orders — `Purchase_Orders` (embedded subform: `PO_Line_Items`)
14. Goods Receipt — `Goods_Receipts` (embedded subform: `GRN_Line_Items`)
15. Reports & Dashboards — Reports + Dashboard widgets
16. Invoicing — `Invoices` (embedded subform: `Invoice_Line_Items`)
17. Delivery Challan — `Delivery_Challans` (embedded subform: `DC_Line_Items`)
18. BOM (Bill of Materials) — `BOM` (embedded subform: `BOM_Line_Items`)

## Key Deluge automation points (non-obvious)
- **Budget validation**: sum of component budgets must not exceed approved project budget
- **Auto-inventory deduction**: Stock Out on a project → auto-create Expense record and update budget
- **Warehouse stock sync**: every transaction updates `Item_Warehouse_Stock` + rolls up to `Item.Current_Stock`
- **Budget alerts**: trigger at 80%, 90%, 100% consumption via scheduled workflow
- **Overrun approval workflow**: expense exceeding component budget → status "Overrun-Pending Approval" → notify PM + Finance Manager
- **PO lifecycle**: `Draft → Open → Partially Invoiced → Invoiced → Closed / Cancelled`
- **Goods receipt**: accepted qty → Stock In transaction; rejected qty logged for returns (PO is closed manually, no auto-update)
- **Transfer orders**: completing a transfer auto-generates paired Stock Out / Stock In transactions
- **Multi-stage PR approval**: Dept Manager → Finance → Procurement, each step triggers email notification
- **PR → Auto-PO**: On final approval, Deluge auto-creates Purchase Order (Draft) with line items from PR
- **Invoice revenue tracking**: Sent → updates Project Total Invoiced; Paid → auto-sets Balance Due
- **Invoice → DC**: Custom button on Invoice creates Delivery Challan with same line items
- **Stock Reservation per Project**: Reservation transaction type increments Reserved_Qty on Item_Warehouse_Stock; Stock Out checks unreserved stock
- **Project Completed → final Invoice**: On project completion, auto-creates Invoice for any unbilled items
- **Delivery Challan stock deduction**: Shipped → auto-creates Stock Out for each line item
- **BOM Cost calculation**: On Submit → sums component costs + labor + overhead for Total Mfg Cost

## User roles and their scope
| Role | Key actions |
|---|---|
| Administrator | Full access |
| Project Manager | Manage projects, track budgets, approve overruns |
| Finance Manager | Budget approvals, financial reporting |
| Procurement Team | Requisitions, POs |
| Inventory Manager | Stock transactions |
| Employee/User | Submit expenses, request purchases |

## Reporting
Executive dashboard KPIs: Total Project Budget, Total Spent, Budget Utilization %, Open PO Value, Inventory Value, Cost Overruns. Reports: Budget vs Actual, Project P&L (Invoiced − Expenses), Invoice Aging, DC Register, BOM Cost Summary, category analysis, monthly trends — all Zoho Creator Report/Dashboard widgets or Zoho Analytics.

## Future enhancements (Phase 2)
Zoho Analytics integration, email notifications, vendor communication.

## Internal workflow
1. Implementation happens in the **Zoho Creator console** — not in this repo
2. Update this repo when design decisions change during implementation
3. Module design pattern: Form fields → Validation rules → Deluge workflow → Report/Dashboard → Role permissions
4. Refer to `IMPLEMENTATION_PLAN.md` for field-level specs during console build
5. Log implementation blockers/issues in the repo for team discussion

## Build order quick reference
```
Phase 1A: Vendors → Accounts → Projects → Warehouses → Inventory_Items
Phase 1B: Budget_Plans → Budget_Components → Inventory_Transactions
Phase 1C: Expenses → Purchase_Requisitions
Phase 1D: Budget_Approvals → Purchase_Orders → Goods_Receipts → Transfer_Orders
Phase 1E: BOM → Delivery_Challans → Invoices
Phase 1F: Reports & Dashboards (incl. Project P&L)
```
