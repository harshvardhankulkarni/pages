# AGENTS.md — Project Budget Tracking & Inventory Management (Internal)

## Project type
Zoho Creator low-code application. All logic is in **Deluge scripts**, forms, workflows, and reports. This repo holds the internal implementation blueprint for the ITOTCloud delivery team.

## What this repo holds
Internal implementation plan: field-level module specs, Deluge pseudocode, lookup relationship maps, build phases, role permissions matrix, and deployment checklist. This is the single source of truth for the Zoho Creator console build.

## 17 canonical modules
1. Project Master — `Projects`
2. Vendor Management — `Vendors`, `Vendor_Contacts`, `Vendor_Documents`
3. Warehouses — `Warehouses`
4. Inventory Master — `Inventory_Items`, `Item_Warehouse_Stock`, `Item_Attributes`
5. Budget Planning — `Budget_Plans`
6. Budget Components — `Budget_Components`
7. Expense Management — `Expenses`
8. Budget Approval Workflow — `Budget_Approvals`
9. Inventory Transactions — `Inventory_Transactions`
10. Transfer Orders — `Transfer_Orders`, `TO_Line_Items`
11. Purchase Requisition — `Purchase_Requisitions`, `PR_Line_Items`
12. Purchase Orders — `Purchase_Orders`, `PO_Line_Items`
13. Goods Receipt — `Goods_Receipts`, `GRN_Line_Items`
14. Reports & Dashboards — Reports + Dashboard widgets
15. Invoicing — `Invoices`, `Invoice_Line_Items`
16. Delivery Challan — `Delivery_Challans`, `DC_Line_Items`
17. BOM (Bill of Materials) — `BOM`, `BOM_Line_Items`

## Key Deluge automation points (non-obvious)
- **Budget validation**: sum of component budgets must not exceed approved project budget
- **Auto-inventory deduction**: Stock Out on a project → auto-create Expense record and update budget
- **Warehouse stock sync**: every transaction updates `Item_Warehouse_Stock` + rolls up to `Item.Current_Stock`
- **Budget alerts**: trigger at 80%, 90%, 100% consumption via scheduled workflow
- **Overrun approval workflow**: expense exceeding component budget → status "Overrun-Pending Approval" → notify PM + Finance Manager
- **PO lifecycle**: `Draft → Open → Partially Invoiced → Invoiced → Closed / Cancelled`
- **Goods receipt**: accepted qty → Stock In transaction + PO line item update; rejected qty logged for returns
- **Transfer orders**: completing a transfer auto-generates paired Stock Out / Stock In transactions
- **Multi-stage PR approval**: Dept Manager → Finance → Procurement, each step triggers email notification
- **PR → Auto-PO**: On final approval, Deluge auto-creates Purchase Order (Draft) with line items from PR
- **Invoice revenue tracking**: Sent → updates Project Total Invoiced; Paid → auto-sets Balance Due
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

## Integration touchpoints (Phase 2)
Zoho Books, Zoho Inventory (optional), Zoho Analytics, Zoho Projects, email notifications, vendor communication.

## Internal workflow
1. Implementation happens in the **Zoho Creator console** — not in this repo
2. Update this repo when design decisions change during implementation
3. Module design pattern: Form fields → Validation rules → Deluge workflow → Report/Dashboard → Role permissions
4. Refer to `IMPLEMENTATION_PLAN.md` for field-level specs during console build
5. Log implementation blockers/issues in the repo for team discussion

## Build order quick reference
```
Phase 1A: Vendors → Projects → Warehouses → Inventory_Items
Phase 1B: Budget_Plans → Budget_Components → Inventory_Transactions
Phase 1C: Expenses → Purchase_Requisitions
Phase 1D: Budget_Approvals → Purchase_Orders → Goods_Receipts → Transfer_Orders
Phase 1E: BOM → Delivery_Challans → Invoices
Phase 1F: Reports & Dashboards (incl. Project P&L)
```
