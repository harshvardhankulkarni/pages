# AGENTS.md — Project Budget Tracking & Inventory Management

## Project type
Zoho Creator low-code application. All logic is in **Deluge scripts**, forms, workflows, and reports — no traditional source code lives in this repo.

## What this repo holds
Design artifacts only: FRD, data model, workflow diagrams, role matrix, form/dashboard designs, implementation roadmap. No Zoho Creator deployable artifacts (those live on the Zoho platform).

## 14 canonical modules (matches Zoho Creator + Zoho Inventory structure)
1. Project Master
2. Vendor Management (multi-contact, multi-address, tax IDs, payment terms)
3. Warehouses (multi-warehouse stock tracking)
4. Inventory Master — Items (SKU, goods/services, dimensions, HSN/SAC, price lists)
5. Budget Planning
6. Budget Components (dynamic per project)
7. Expense Management
8. Budget Approval Workflow
9. Inventory Transactions (Stock In/Out/Adjustment/Return, per-warehouse)
10. Transfer Orders (inter-warehouse stock movement)
11. Purchase Requisition (multi-line item, multi-stage approval)
12. Purchase Orders (line-level discount/tax, billing/shipping addresses, Zoho Inventory statuses)
13. Goods Receipt (accepted/rejected qty, auto-inventory + PO update)
14. Reports & Dashboards

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
Executive dashboard KPIs: Total Project Budget, Total Spent, Budget Utilization %, Open PO Value, Inventory Value, Cost Overruns. Budget vs Actual, category analysis, monthly trends — all Zoho Creator Report/Dashboard widgets or Zoho Analytics.

## Integration touchpoints
Zoho Books, Zoho Inventory (optional), Zoho Analytics, Zoho Projects, email notifications, vendor communication.

## How to contribute
Design docs live as markdown in this repo. Implementation happens in the Zoho Creator console — not here. When designing a module, always follow the pattern: form fields → validation rules → Deluge workflow → report/dashboard → role permissions.
