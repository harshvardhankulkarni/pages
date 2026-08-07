# AGENTS.md — Project Budget Tracking & Inventory Management (Internal)

## Project type
Zoho Creator low-code application. All logic is in **Deluge scripts**, forms, workflows, and reports. This repo holds the internal implementation blueprint for the ITOTCloud delivery team.

## What this repo holds
Internal implementation plan: field-level module specs, Deluge pseudocode, lookup relationship maps, build phases, role permissions matrix, and deployment checklist. This is the single source of truth for the Zoho Creator console build.

## 27 canonical modules

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
15. Supplier Credit Notes — `Supplier_Credit_Notes` (embedded subform: `SCN_Line_Items`)
16. Reports & Dashboards — Reports + Dashboard widgets
17. Invoicing — `Invoices` (embedded subform: `Invoice_Line_Items`)
18. Delivery Challan — `Delivery_Challans` (embedded subform: `DC_Line_Items`)
19. BOM (Bill of Materials) — `BOM` (embedded subform: `BOM_Line_Items`)
20. Customer Credit Notes — `Customer_Credit_Notes` (embedded subform: `CCN_Line_Items`)
21. Manufacturing Orders — `Manufacturing_Orders` (embedded subform: `MO_Components`)
22. Sales Orders — `Sales_Orders` (embedded subform: `SO_Line_Items`)

## Deluge Scripting Conventions
- **User-facing validation**: Use `alert "message";` NOT `throw "message"` — `throw` throws a system exception, `alert` shows a popup and stops submission
- **Embedded subform access**: Use `parent_rec = zoho.creator.getRecordById("app", "Parent_Form", id); rows = parent_rec.get("Subform_Name");` to read embedded subform data — no direct `getRecords` on subform API names
- **Embedded subform update**: Iterate rows, `row.put("Field", new_val)` to modify, rebuild as `List`, update parent record with `data_map.put("Subform_Name", updated_list)` — this preserves row IDs
- **JUSTIFICATION comments**: Every Deluge script must have a `/* JUSTIFICATION: ... */` comment explaining why this script must exist (cannot be handled by embedded subform submission alone)
- **Standalone form scripts**: `Inventory_Transactions` is standalone (audit log); its On Post Submit syncs stock back to embedded `Item_Warehouse_Stock` via getRecordById + subform iteration — justified as real-time stock sync
- **Scheduled workflow subform access**: Same pattern — fetch parent form records, iterate, access `.get("Subform_Name")` for each

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
- **PO Receipt_Status per line item**: On GRN submit, Deluge aggregates Accepted Qty from all linked GRNs → updates each PO_Line_Item.Received_Qty + Pending_Qty; sets PO.Receipt_Status to "Partially Received" or "Fully Received"
- **Supplier Credit Notes (finance-initiated)**: Manual finance entry against defective items post-QA/QC; updates PO_Line_Items.Credited_Qty; sets PO.Has_Outstanding_Credit = true
- **SCN → Return to Vendor**: When Stock Disposition = "Returned to Supplier", Deluge auto-creates Return to Vendor inventory transaction
- **GRN_Line_Items credit tracking**: When SCN references a GRN, Is_Credited flag + Credit_Note_Ref are set automatically
- **Weighted Average Cost**: On every Stock In transaction, Deluge recalculates Average_Cost: ((Old_Stock × Old_Avg) + (Qty × Rate)) / (Old_Stock + Qty). Updates Item_Warehouse_Stock.Unit_Cost
- **Expense Allocations**: Split a single expense across multiple Budget Components via embedded Expense_Allocations subform; validates sum = expense amount
- **Budget Revisions**: Auto-creates revision record when Budget_Approval modifies budget amount; tracks component allocation changes over time
- **CCN Issued (AR)**: On Issue, reduces Invoice Balance Due; for goods items, auto-creates Stock In (Return to Customer) inventory transaction
- **CCN Applied**: Marks Invoice Has_Credit_Note = true when CCN fully utilized
- **CCN Cancelled**: Reverses Invoice Balance Due adjustment
- **MO Released**: Reserves all component stock via Reservation inventory transactions; validates stock availability
- **MO Completed**: Issues components via Stock Out transactions; receives finished goods via Stock In
- **MO Cancelled**: Releases all reserved component stock
- **SO Confirmed**: Reserves stock for all line items
- **SO Shipped**: Auto-creates Stock Out for each line item
- **SO Cancelled**: Releases reserved stock (blocked if partial delivery/invoicing exists)
- **SO → Invoice (Custom Button)**: Creates Invoice from uninvoiced line items
- **SO → DC (Custom Button)**: Creates Delivery Challan from undelivered line items

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
Phase 1D: Budget_Approvals → Purchase_Orders (enhanced) → Goods_Receipts (enhanced) → Supplier_Credit_Notes (NEW) → Transfer_Orders
Phase 1E: BOM → Delivery_Challans → Invoices
Phase 1F: Reports & Dashboards (incl. Project P&L)
Phase 1G: PO approval workflows + committed budget tracking + Segregation of Duties
Phase 1H: Customer_Credit_Notes → Manufacturing_Orders → Sales_Orders (gaps closure)
```
