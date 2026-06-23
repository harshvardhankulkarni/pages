# Implementation Plan — Project Budget Tracking & Inventory Management (Zoho Creator)

**ITOTCloud Systems Pvt. Ltd. — Internal Delivery Document**
**Author:** Implementation Team | **Status:** Ready for Phase 1A | **Confidential**

---

> This is the field-level implementation blueprint for the ITOTCloud delivery team.
> Build from this document in the Zoho Creator console. Update it when design decisions change.
> Refer to `AGENTS.md` for AI assistant context and `index.html` for an interactive version.

---

## A. Zoho Creator Design Constraints (Key Factors)

| Constraint | Design Impact |
|---|---|
| No true foreign keys | All relationships are **Lookup fields** referencing another form's `Form.Name` field. Plan for orphaned records — archive, don't delete. |
| No transactions | If a multi-step Deluge workflow fails mid-way (e.g., deduct stock + create expense record), partial updates persist. Add **safety checks in Deluge**: verify state before each write, log failures to a Debug Log form. |
| Deluge runs per-record, not set-based | Avoid looping large datasets in `on form submit`. Use **Scheduled Workflows** (cron) for mass operations: budget alerts, auto-PO closure, monthly rollups. |
| Subform limitations | Subforms are great for < 100 line items. All line items, contacts, and documents use **embedded subforms** inside the parent form. Budget Components is an embedded subform inside Budget_Plans for inline entry. |
| No dynamic SQL | All aggregation is `Map` + `List` in Deluge or Zoho Creator Report widgets. Prefer Reports over Deluge for performance. |
| Role-based access is per-form, not record-level | For department-specific data (e.g., Procurement sees only their POs), use **form filters** on report views or dedicated forms per role. |
| Formula fields can't look up external data | Complex validation (budget checks) must go in **Deluge workflows on form submit**, not formula fields. |
| Lookup fields cache stale data | When Inventory Master stock changes, any previous lookup reference still shows old value. Use **Formula Lookup** fields (recalculated on load) for live values. |

---

## B. Implementation Sequence (Build Order)

Each phase depends on the previous. Build in this order:

```
Phase 1A:  Vendor Management  →  Account Management  →  Project Master  →  Warehouses  →  Inventory Master
                   ↓                    ↓                               ↓
Phase 1B:  Budget Planning  →  Budget Components              Inventory Transactions
                   ↓                                               ↓
Phase 1C:  Expense Management  →  Purchase Requisition            ↓
                   ↓                       ↓                       ↓
Phase 1D:  Budget Approval             Purchase Orders            Transfer Orders
                                               ↓                    ↓
                                          Goods Receipt  ←─────────┘
                                               ↓
Phase 1E:  BOM  →  Delivery Challan  →  Invoicing
                                                ↓
Phase 1F:  Reports & Dashboards (all modules incl. Project P&L)
```

---

## C. Module-by-Module Design (18 Modules)

### 1. Project Master (`Projects`)

| Field | Type | Notes |
|---|---|---|
| Project Name | Text | Required |
| Project Code | Text (auto-number) | e.g., `PROJ-0001` |
| Account | Lookup → Accounts | Client/company associated with the project |
| Start Date | Date | |
| End Date | Date | |
| Project Manager | User picker | Links to Zoho Creator user |
| Total Approved Budget | Currency (Decimal) | In your base currency |
| Status | Dropdown | `Planning`, `Active`, `On Hold`, `Completed`, `Closed` |

**Lookups from other modules:** This is the most-referenced form. Almost every other module has a lookup to Projects.

**Deluge:**
- On Create: generate Project Code
- On Status = `Completed`: validate no pending expenses/POs
- On Status = `Completed`: auto-create final Invoice for any unbilled DCs or remaining budget balance

**Custom Actions (Form Buttons):**
- **Create Invoice** — opens Invoice form with Project + Account pre-filled
- **Request Part Repair** — opens Purchase Requisition form with Project pre-filled, Request Type = "Part Repair"

---

### 2. Vendor Management (`Vendors` — with embedded Contacts + Documents subforms)

| Field | Type | Notes |
|---|---|---|
| Vendor Name | Text | Required — display name |
| Company Name | Text | Legal entity name |
| Email | Email | Primary contact email |
| Phone | Phone | |
| Mobile | Phone | |
| Website | URL | |
| Currency | Dropdown | `USD`, `EUR`, `INR`, etc. — affects PO totals |
| Payment Terms | Dropdown | `Due on Receipt`, `Net 15`, `Net 30`, `Net 45`, `Net 60` |
| Tax ID | Text | GSTIN / VAT / HST registration number |
| PAN | Text | Permanent Account Number (India) |
| Billing Address | Address | Zoho Creator Address type (composite) |
| Shipping Address | Address | Zoho Creator Address type (composite) |
| Status | Dropdown | `Active`, `Inactive` |
| Remarks | Multi-line | |

**Embedded subform — Vendor_Contacts:** Salutation, First Name, Last Name, Email, Phone, Mobile, Designation, Department, Is Primary

**Embedded subform — Vendor_Documents:** Document Name, File, Expiry Date, Notes

---

### 3. Account Management (`Accounts` — with embedded Contacts + Documents subforms)

Stores customer/client information separate from Vendors. Used by Projects, Invoices, and Delivery Challans.

| Field | Type | Notes |
|---|---|---|
| Account Name | Single Line | Required — display name |
| Company Name | Single Line | Legal entity name |
| Email | Email | Primary contact email |
| Phone | Phone | |
| Mobile | Phone | |
| Website | URL | |
| Currency | Dropdown | `USD`, `EUR`, `INR`, `GBP`, `AED` |
| Payment Terms | Dropdown | `Due on Receipt`, `Net 15`, `Net 30`, `Net 45`, `Net 60` |
| Tax ID | Text | GSTIN / VAT registration number |
| PAN | Text | Permanent Account Number (India) |
| Billing Address | Address | Zoho Creator Address type (composite) |
| Shipping Address | Address | Zoho Creator Address type (composite) |
| Status | Dropdown | `Active`, `Inactive` — default Active |
| Remarks | Multi-line | |

**Embedded subform — Account_Contacts:** Salutation, First Name, Last Name, Email, Phone, Mobile, Designation, Department, Is Primary

**Embedded subform — Account_Documents:** Document Name, File, Expiry Date, Notes

---

### 4. Warehouses (`Warehouses`)

Multi-warehouse support — every inventory transaction references a warehouse (or a default "Main Warehouse" is created on setup).

| Field | Type | Notes |
|---|---|---|
| Warehouse Name | Text | Required |
| Warehouse Code | Text (auto-number) | e.g., `WH-0001` |
| Address | Multi-line | |
| City | Text | |
| State | Text | |
| Country | Text | |
| Phone | Phone | |
| Status | Dropdown | `Active`, `Inactive` |

A **default warehouse** is seeded on app creation so single-warehouse users never notice.

---

### 5. Inventory Master (`Inventory_Items` — with embedded Item_Warehouse_Stock subform)

Items are goods or services tracked at the SKU level.

| Field | Type | Notes |
|---|---|---|
| Item Name | Text | Required |
| SKU | Text (auto-number) | e.g., `SKU-0001` — unique identifier |
| Item Type | Dropdown | `Goods`, `Services` — services have no stock tracking |
| Category | Dropdown | `Raw Material`, `Component`, `Consumable`, `Equipment`, `Service`, `Subcontract` |
| Unit | Dropdown | `Pcs`, `Kg`, `Ltr`, `Box`, `Meter`, `Hour`, `Day`, `Set`, `Pair` |
| HSN/SAC Code | Text | Tax classification code |
| Taxability | Dropdown | `Taxable`, `Non-Taxable`, `Zero-Rated` |
| Tax Rate | Decimal (%) | Default tax % applied in POs |
| Purchase Price | Currency | Default unit cost for purchases |
| Reorder Level | Decimal | Min stock before alert |
| Preferred Vendor | Lookup → Vendors | Default vendor for POs |
| Current Stock | Decimal | Maintained by Deluge — updated on every Inventory Transaction via SUM aggregation across Item_Warehouse_Stock |
| Stock Value | Formula | `Current Stock * Purchase Price` |
| Description | Multi-line | Internal notes |
| Status | Dropdown | `Active`, `Inactive` |

**Embedded subform — Item_Warehouse_Stock:** Item (Lookup → Inventory_Items), Warehouse (Lookup → Warehouses), Current Stock, Reserved Qty, Available Stock (Formula), Reorder Level

**Deluge approach for `Current_Stock` and `Reserved_Qty` :**
```
On every Inventory Transaction:
  Locate the matching Item_Warehouse_Stock subform row within the Item record:
    Stock In:              Current_Stock += Quantity
    Stock Out:             Current_Stock -= Quantity; Reserved_Qty -= Quantity (capped)
    Adjustment:            Current_Stock = Adjusted_Qty (Reserved_Qty unchanged)
    Return to Vendor:      Current_Stock -= Quantity
    Reservation:           Reserved_Qty += Quantity; validate Reserved_Qty <= Current_Stock
    Release:               Reserved_Qty -= Quantity
  Then update Inventory_Item.Current_Stock = SUM of all Item_Warehouse_Stock subform rows
```

This gives both warehouse-level visibility and item-level totals without on-demand aggregation.

---



### 6. Budget Planning (`Budget_Plans`)

| Field | Type | Notes |
|---|---|---|
| Plan Name | Text | Auto-generated |
| Project | Lookup → Projects | One project can have ONE active budget plan |
| Total Budget Amount | Currency | Copied from Project's Total Approved Budget or entered here |
| Status | Dropdown | `Draft`, `Active`, `Revised`, `Closed` |
| Approval Status | Dropdown | `Pending`, `Approved`, `Rejected` |

**Validation (Deluge on Submit):**
- Ensure project doesn't already have an active budget plan
- Total of all Budget Components must be ≤ `Total Budget Amount`

**Recommendation for Budget Components:** Use an **embedded subform** `Budget_Components` inside `Budget_Plans`. This gives the user a seamless inline experience while enabling rich reporting.

---

### 7. Budget Components (`Budget_Components`)

| Field | Type | Notes |
|---|---|---|
| Component Name | Text | e.g., "Labor", "Materials" |
| Project | Lookup → Projects | Denormalized for reporting ease |
| Allocated Amount | Currency | |
| Total Spent | Currency (Formula) | Aggregated from Expense Management records |
| Remaining | Formula | `Allocated Amount - Total Spent` |
| Consumption % | Formula | `(Total Spent / Allocated Amount) * 100` |
| Status | Dropdown | `Within Budget`, `80% Alert`, `90% Alert`, `Exceeded` |

**Key Relationship:** This is the central pivot form. Expenses reference it. Reports group by it.

**Deluge Workflow for Status:**
```
On Expense Submit (if within budget):
  Update Budget_Component.Total_Spent
  Recalculate consumption %
  If >= 100%: Status = "Exceeded", trigger alert
  If >= 90%:  Status = "90% Alert", trigger alert
  If >= 80%:  Status = "80% Alert", trigger alert
```

---

### 8. Expense Management (`Expenses`)

| Field | Type | Notes |
|---|---|---|
| Expense No | Auto-number | `EXP-0001` |
| Project | Lookup → Projects | |
| Budget Component | Lookup → Budget_Components | Filtered by selected Project |
| Date | Date | |
| Amount | Currency | |
| Vendor | Lookup → Vendors (optional) | |
| Description | Multi-line | |
| Supporting Document | Upload | File attachment |
| Status | Dropdown | `Draft`, `Submitted`, `Approved`, `Overrun-Pending Approval`, `Rejected`, `Modified` |

**Deluge Workflow (on Submit):**
```
1. Read Allocated_Amount from Budget_Component
2. Read Total_Spent from Budget_Component
3. New_Total = Total_Spent + Expense.Amount
4. If New_Total <= Allocated_Amount:
     Set Status = "Approved"
     Update Budget_Component.Total_Spent = New_Total
     Update Budget_Component status based on % consumed
   Else:
     Set Status = "Overrun-Pending Approval"
     Create record in Budget_Approvals
     Send email notification to Project Manager + Finance Manager
```

---

### 9. Budget Approval Workflow (`Budget_Approvals`)

| Field | Type | Notes |
|---|---|---|
| Expense | Lookup → Expenses | Related expense that triggered overrun |
| Project | Lookup → Projects | Denormalized |
| Budget Component | Lookup → Budget_Components | Denormalized |
| Original Budget Amount | Currency | Copied from Budget_Component on creation |
| Expense Amount | Currency | From Expense |
| Exceeded Amount | Currency | `Expense.Amount - Budget_Component.Remaining` |
| Approval Status | Dropdown | `Pending`, `Approved`, `Rejected`, `Request Modification` |
| Approver | User picker | Who approved/rejected |
| Approval Date | Date/Time | |
| Comments | Multi-line | |
| Modified Budget Amount | Currency | If approver increases the component budget |

**Deluge Workflow:**
- On Approval: update Budget Component's allocated amount (if modified), approve the Expense, update Expense Status to "Approved"
- On Rejection: update Expense Status to "Rejected"
- On Request Modification: update Expense Status to "Modified", notify requester

**Audit Trail:** Every status change on Budget_Approvals creates a log entry in a dedicated Audit Log form (or use Zoho Creator's built-in audit history).

---

### 10. Inventory Transactions (`Inventory_Transactions`)

Every stock movement is recorded as an Inventory Transaction tied to a specific warehouse.

| Field | Type | Notes |
|---|---|---|
| Transaction No | Auto-number | `TXN-0001` |
| Type | Dropdown | `Stock In`, `Stock Out`, `Stock Adjustment`, `Return to Vendor`, `Return from Customer`, `Reservation`, `Release` |
| Item | Lookup → Inventory_Items | |
| Warehouse | Lookup → Warehouses | Required — which warehouse stock changes |
| Quantity | Decimal | Always positive. Direction determined by Type |
| Unit | Text | Copied from Item |
| Rate / Unit Cost | Currency | Cost at time of transaction |
| Total Value | Formula | `Quantity * Rate` |
| Reference | Text | PO Number, GRN Number, Adjustment Reason |
| Project | Lookup → Projects | Required for Stock Out (consumption) and Reservation |
| Transaction Date | Date/Time | |
| Notes | Multi-line | |
| Created By | User picker | Auto-set |

**Deluge Workflow (on Submit):**
```
1. Fetch the Inventory_Item record (via Item lookup field); locate the matching Item_Warehouse_Stock subform row for the selected Warehouse
2. Calculate new stock on that row:
   - Stock In:              Current_Stock += Quantity
   - Stock Out:             Current_Stock -= Quantity;  Reserved_Qty -= min(Reserved_Qty, Quantity)
   - Adjustment:            Current_Stock = Adjusted_Qty
   - Return to Vendor:      Current_Stock -= Quantity
   - Reservation:           Reserved_Qty += Quantity;  validate Reserved_Qty <= Current_Stock
   - Release:               Reserved_Qty -= Quantity
3. Validate Current_Stock >= 0 AND unreserved stock (Current_Stock - Reserved_Qty) >= 0 for Stock Out
4. Update the subform row's Current_Stock and Reserved_Qty
5. Update Inventory_Item.Current_Stock = SUM of all subform rows for this Item
6. If Type = "Stock Out" AND Project is set:
      Create Expense record automatically:
        Amount = Quantity * Rate
        Project = selected Project
        Budget_Component = selected (or auto-map via item category)
        Description = "Auto: Stock consumed — [Item Name] for [Project]"
        Status = "Approved"
```

**Important:** The Stock Out → Expense flow is the highest-value automation. It closes the loop between inventory and budget tracking.

---

### 11. Transfer Orders (`Transfer_Orders` — with embedded Line Items subform)

Moving stock between warehouses.

| Field | Type | Notes |
|---|---|---|
| Transfer Order No | Auto-number | `TO-0001` |
| Date | Date | |
| From Warehouse | Lookup → Warehouses | Source |
| To Warehouse | Lookup → Warehouses | Destination |
| Status | Dropdown | `Draft`, `In Transit`, `Completed`, `Cancelled` |

**Embedded subform — TO_Line_Items:** Item (Lookup → Inventory_Items), Quantity, Rate, Total (Formula)

**Deluge Workflow (on Status = "Completed"):**
```
For each row in input.TO_Line_Items subform:
  Create Stock Out transaction from From_Warehouse (Type = "Stock Transfer")
  Create Stock In  transaction to   To_Warehouse   (Type = "Stock Transfer")
  → Both trigger the Inventory_Transactions workflow → update stock counts
```

---

### 12. Purchase Requisition (`Purchase_Requisitions` — with embedded Line Items subform)

Handles internal purchase requests and approval workflow.

| Field | Type | Notes |
|---|---|---|
| Requisition No | Auto-number | `REQ-0001` |
| Request Type | Dropdown | `General`, `Part Repair`, `Service` — defaults to General |
| Subject | Text | Brief title for the requisition |
| Project | Lookup → Projects | |
| Requested By | User picker | Defaults to current user |
| Requested Date | Date | Defaults to today |
| Delivery Date | Date | Required by date |
| Urgency | Dropdown | `Low`, `Medium`, `High`, `Critical` |
| Justification | Multi-line | |
| Status | Dropdown | `Draft`, `Open`, `Approved`, `Rejected`, `Closed` |
| Approval Stage | Dropdown | `Pending Dept Approval`, `Pending Finance Approval`, `Pending Procurement`, `Approved` |
| Notes | Multi-line | Internal notes |

**Embedded subform — PR_Line_Items:** Item (Lookup → Inventory_Items, optional), Item Description, Quantity, Estimated Unit Rate, Estimated Total (Formula), Item Type, Unit

**Multi-stage Approval + Auto-PO Workflow:**
1. User submits (Status = "Open")
2. Department Manager approves → Approval_Stage = "Pending Finance Approval"
3. Finance approves → Approval_Stage = "Pending Procurement"
4. Procurement approves → Approval_Stage = "Approved"
5. **Auto-create PO** (Deluge on final approval): create Purchase_Order in Draft status, copy all PR Line Items subform rows → PO Line Items subform rows, link PO.Requisition = this PR

Each step sends email notification. Procurement then reviews the auto-created PO and sends to vendor.

---

### 13. Purchase Orders (`Purchase_Orders` — with embedded Line Items subform)

| Field | Type | Notes |
|---|---|---|
| PO Number | Auto-number | `PO-0001` |
| Vendor | Lookup → Vendors | Required |
| Requisition | Lookup → Purchase_Requisitions | Optional — linked if created from PR |
| Project | Lookup → Projects | |
| PO Date | Date | Defaults to today |
| Delivery Date | Date | Expected delivery |
| Due Date | Date | Payment due date |
| Reference Number | Text | Vendor's reference or contract no. |
| Status | Dropdown | `Draft`, `Open`, `Partially Invoiced`, `Billed`, `Closed`, `Cancelled` |
| Subtotal | Currency | Sum of line item totals |
| Discount (%) | Decimal | Overall PO-level discount |
| Discount Amount | Currency | Calculated |
| Tax Total | Currency | Sum of line item taxes |
| Total | Currency | `Subtotal - Discount + Tax Total` |
| Terms & Conditions | Multi-line | Printed on PO |
| Notes | Multi-line | Internal instructions |
| Attachment | Upload | PO document file |

**Embedded subform — PO_Line_Items:** Item (Lookup → Inventory_Items), Description, Unit, HSN/SAC, Quantity, Unit Rate, Discount (%), Discount Amount (Formula), Tax (%), Tax Amount (Formula), Item Total (Formula)


**PO Lifecycle:**
- **Draft**: Being created, not yet submitted
- **Open**: Approved and sent to vendor
- **Partially Invoiced**: Some line items billed
- **Billed**: Fully invoiced
- **Closed**: Items received, PO fulfilled
- **Cancelled**: Voided before completion

**Deluge Workflow:**
- On Status = "Open": trigger email to vendor with PO PDF
- On Status = "Cancelled": validate no GRN linked to this PO
- PO Lifecycle: `Draft → Open → Closed` (manual close only — no auto-close based on GRN)

---

### 14. Goods Receipt (`Goods_Receipts` — with embedded Line Items subform)

Supports accepted vs rejected quantities, and auto-updates inventory + PO.

| Field | Type | Notes |
|---|---|---|
| GRN Number | Auto-number | `GRN-0001` |
| PO | Lookup → Purchase_Orders | Required |
| Receipt Date | Date/Time | Defaults to now |
| Received By | User picker | Defaults to current user |
| Status | Dropdown | `Draft`, `Open`, `Closed` |

**Embedded subform — GRN_Line_Items:** Item (Lookup → Inventory_Items), PO Quantity (Read Only), Accepted Quantity, Rejected Quantity, Reason for Rejection, Actual Unit Cost, Total (Formula), Warehouse (Lookup → Warehouses), Condition Notes

**Deluge Workflow (on Submit when Status = "Open"):**
```
1. For each row in input.GRN_Line_Items subform:
      If row.Accepted_Quantity > 0:
        Create Stock In transaction:
          Item = row.Item
          Warehouse = row.Warehouse
          Quantity = row.Accepted_Quantity
          Rate = row.Actual_Unit_Cost
          Reference = GRN Number
          Type = "Stock In"
        → Inventory_Transactions workflow fires → updates stock

      GRN is the receipt record — PO lines no longer track receipt quantities
      Update PO line item actual costs if row.Actual_Unit_Cost differs from PO rate
```

---

### 15. Reports & Dashboards

**Zoho Creator Reports (one per audience):**

| Report | Type | Source Module | Audience |
|---|---|---|---|---|
| Budget vs Actual | Pivot (Rows: Budget Component, Columns: Month) | Expenses + Budget_Components | PM, Finance |
| Budget Utilization % | Summary | Budget_Components | PM |
| Overrun Analysis | Summary (filter: status = Exceeded) | Budget_Components | PM, Finance |
| Monthly Spend Trend | Chart (Line) | Expenses | All |
| Project P&L | Pivot (Project, Total Revenue, Total Expense, Profit/Loss) | Invoices + Expenses | PM, Finance |
| Open POs | Tabular (filter: Status != Closed, Cancelled) | Purchase_Orders | Procurement |
| Vendor Spend | Summary (group by Vendor) | Purchase_Orders | Procurement, Finance |
| Stock Availability | Tabular (group by Warehouse) | Inventory_Items (Item_Warehouse_Stock subform) | Inventory Manager |
| Low Stock Alert | Tabular (filter: Stock <= Reorder Level) | Inventory_Items (Item_Warehouse_Stock subform) | Inventory Manager |
| Stock Consumption by Project | Summary | Inventory_Transactions | PM, Inventory |
| Inventory Valuation | Summary | Inventory_Items | Finance |
| Stock Movement by Warehouse | Summary by Item + Warehouse | Inventory_Transactions | Inventory Manager |
| Open Transfer Orders | Tabular (filter: Status = In Transit) | Transfer_Orders | Inventory Manager |
| Invoice Aging | Tabular (group by Due Date, Status != Paid) | Invoices | Finance |
| DC Register | Tabular (filter by date range) | Delivery_Challans | Inventory, Logistics |
| Vendor List with Contacts | Tabular | Vendors (Contacts subform) | Procurement |
| BOM Cost Summary | Summary (group by Item) | BOM (Line Items subform) | Production |
| Executive Dashboard | Dashboard with KPI cards + charts | All | All |

**Dashboard KPIs — Deluge Scheduled Workflow to calculate and store in a Summary_Data form:**
- Total Project Budget = Sum of all active Budget_Plans.Total_Budget_Amount
- Total Spent = Sum of approved Expenses.Amount
- Total Invoiced = Sum of Invoices where Status IN ("Sent", "Partially Paid", "Paid")
- Budget Utilization % = `Total Spent / Total Project Budget * 100`
- Project P&L = `Total Invoiced per Project - Total Expenses per Project`
- Open PO Value = Sum of POs with Status = "Open"
- Inventory Value = Sum of (Current_Stock × Purchase_Price) across all items
- Cost Overruns = Count of Budget_Components where Status = "Exceeded"
- Low Stock Items = Count of Item_Warehouse_Stock subform rows where Current_Stock <= Reorder_Level
- Active POs = Count of POs where Status IN ("Open", "Partially Invoiced")
- Pending Receipts = Count of POs where Status = "Open" and past Delivery_Date
- Overdue Invoices = Count of Invoices where Due Date < Today and Status != "Paid"

**Scheduled Workflow (runs daily at midnight):**
- Recalculate all KPI values
- Check for budget alerts (80%, 90%, 100%)
- Check for low stock items and send alerts
- (POs are manually closed only — no auto-close logic)
- Mark Invoices as "Overdue" if Due Date passed and Status IN ("Sent", "Partially Paid")

---

### 16. Invoicing (`Invoices` — with embedded Line Items subform)

Captures revenue per project.

| Field | Type | Notes |
|---|---|---|
| Invoice No | Auto-number | `INV-0001` |
| Project | Lookup → Projects | Required — ties revenue to a project for P&L |
| Customer / Account | Lookup → Accounts | Billed party |
| Invoice Date | Date | Defaults to today |
| Due Date | Date | Based on payment terms |
| PO Reference | Text | Customer PO number if applicable |
| Status | Dropdown | `Draft`, `Sent`, `Partially Paid`, `Paid`, `Overdue`, `Cancelled` |
| Subtotal | Currency | Sum of line item totals |
| Tax Total | Currency | Sum of line item taxes |
| Total | Currency | `Subtotal + Tax Total` |
| Balance Due | Currency (Formula) | `Total - Amount Paid` |
| Amount Paid | Currency | Updated on payment receipt |
| Notes | Multi-line | Internal |
| Attachment | Upload | Invoice PDF |

**Embedded subform — Invoice_Line_Items:** Item (Lookup → Inventory_Items, optional), Description, Quantity, Rate, Discount (%), Discount Amount (Formula), Tax (%), Tax Amount (Formula), Total (Formula)

**Deluge / Custom Actions:**
- On Status = "Sent": update Project Budget Component's Total Invoiced (for P&L reporting)
- On Status = "Paid": update Amount Paid, auto-set Balance Due = 0
- On Status = "Cancelled": validate no payments received
- **Custom Button "Create DC"** (when Status = "Sent" + line items have stock Items): auto-create Delivery Challan with same Project, Customer, and line items copied to DC's embedded Line Items subform; link DC.Ref to Invoice

---

### 17. Delivery Challan (`Delivery_Challans` — with embedded Line Items subform)

Tracks physical dispatch of goods to customers.

| Field | Type | Notes |
|---|---|---|
| DC No | Auto-number | `DC-0001` |
| Project | Lookup → Projects | |
| Customer | Lookup → Accounts | Recipient |
| Reference | Text | Customer PO / Sales Order ref |
| Date | Date | Defaults to today |
| Vehicle No | Text | If own transport |
| Driver Name | Text | |
| Driver Contact | Phone | |
| Status | Dropdown | `Draft`, `Shipped`, `Delivered`, `Cancelled` |
| Remarks | Multi-line | |
| Attachment | Upload | Signed DC copy |

**Embedded subform — DC_Line_Items:** Item (Lookup → Inventory_Items), Description, Quantity, Unit, Condition

**Deluge / Custom Actions:**
- On Create: validate stock availability for each row in input.DC_Line_Items subform
- On Status = "Shipped": reduce stock for each row (auto create Stock Out transaction)
- On Status = "Shipped" + no Invoice linked: prompt user to create Invoice
- Can also be created automatically from Invoice via "Create DC" button on Invoice form

---

### 18. BOM — Bill of Materials (`BOM` — with embedded Line Items subform)

Defines component structure for manufactured/assembled items. Useful for manufacturing projects and cost estimation.

| Field | Type | Notes |
|---|---|---|
| BOM No | Auto-number | `BOM-0001` |
| Finished Item | Lookup → Inventory_Items | The output/assembled item |
| BOM Name | Text | Auto-generated or manual |
| Quantity | Decimal | Output quantity this BOM produces (e.g., 1 unit) |
| Total Component Cost | Currency (Formula) | Sum of all line item costs |
| Labor Cost | Currency | Optional — added to Total Cost |
| Overhead Cost | Currency | Optional |
| Total Manufacturing Cost | Currency (Formula) | `Total Component Cost + Labor + Overhead` |
| Status | Dropdown | `Draft`, `Active`, `Inactive`, `Revised` |
| Version | Decimal | Track revisions |
| Notes | Multi-line | |

**Embedded subform — BOM_Line_Items:** Component Item (Lookup → Inventory_Items), Quantity Required, Unit, Unit Cost, Total Cost (Formula), Scrap %, Notes

**Deluge:**
- On Submit: calculate Total Component Cost = SUM of line item Total Costs
- On Submit: calculate Total Manufacturing Cost = `Total Component Cost + Labor Cost + Overhead Cost`
- On Status = "Active": ensure no other active BOM for same Finished Item (or increment version)

---

## D. Lookup Relationship Map

```
Projects ──┬── Budget_Plans (1:1)
           ├── Budget_Components (1:N, via Budget_Plan)
           ├── Expenses (1:N)
           ├── Inventory_Transactions (1:N, Stock Out only)
           ├── Purchase_Requisitions (1:N)
           ├── Purchase_Orders (1:N)
           ├── Budget_Approvals (1:N)
           ├── Invoices (1:N)
           ├── Delivery_Challans (1:N)
           └── BOM (1:N)

Budget_Plans ── Budget_Components (1:N)

Budget_Components ──┬── Expenses (1:N)
                    └── Budget_Approvals (1:N)

Expenses ──┬── Budget_Approvals (1:1 for overruns)
           └── Vendors (N:1)

Vendors ──┬── Vendor_Contacts (1:N, subform)
           ├── Vendor_Documents (1:N, subform)
           ├── Purchase_Orders (1:N)
           ├── Inventory_Items (1:N, preferred vendor)
           └── Expenses (N:1)

Accounts ──┬── Account_Contacts (1:N, subform)
           ├── Account_Documents (1:N, subform)
           ├── Projects (1:N, as Account)
           ├── Invoices (1:N)
           └── Delivery_Challans (1:N)

Warehouses ──┬── Item_Warehouse_Stock (1:N, embedded subform)
              ├── Inventory_Transactions (1:N)
              ├── Transfer_Orders — From (1:N)
              ├── Transfer_Orders — To (1:N)

Inventory_Items ──┬── Item_Warehouse_Stock (1:N, embedded subform)
                   ├── Inventory_Transactions (1:N)
                   ├── BOM (1:N, as finished item)
                   └── BOM_Line_Items (1:N, embedded subform, as component)

Item_Warehouse_Stock ──┬── Items (N:1)
                       └── Warehouses (N:1)

Inventory_Transactions ──┬── Items (N:1)
                         ├── Warehouses (N:1)
                         └── Projects (N:1, Stock Out only)

Transfer_Orders ──┬── Warehouses — From (N:1)
                   ├── Warehouses — To (N:1)
                   └── TO_Line_Items (embedded subform, 1:N)
                        └── Items (N:1)

Purchase_Requisitions ──┬── PR_Line_Items (embedded subform, 1:N)
                          └── Items (N:1)
                        └── Purchase_Orders (1:N)  ← when converted

Purchase_Orders ──┬── PO_Line_Items (embedded subform, 1:N)
                   │     └── Items (N:1)
                   ├── Goods_Receipts (1:N)
                   └── Requisition (optional, N:1)

Goods_Receipts ──── GRN_Line_Items (embedded subform, 1:N)
                        ├── Items (N:1)
                        └── Warehouses (N:1)

Invoices ──── Invoice_Line_Items (embedded subform, 1:N)
                   └── Items (N:1)

Delivery_Challans ──── DC_Line_Items (embedded subform, 1:N)
                          ├── Items (N:1)
                          └── Warehouses (N:1, dispatch warehouse)

BOM ──── BOM_Line_Items (embedded subform, 1:N)
            └── Items (N:1, as component)
```

---

## E. Deluge Automation Summary

| Trigger | Event | Action |
|---|---|---|---|---|
| Project Create | On Submit | Generate Project Code |
| Budget Plan Submit | On Submit | Validate sum of components ≤ Total Budget |
| Expense Submit | On Submit | Budget check → auto-approve or trigger overrun workflow |
| Expense Overrun | On Submit | Create Budget_Approval record, send notification |
| Budget Approval Status Change | On Submit | Update Expense status, notify requester |
| Inventory Transaction (Stock In/Out/Adj) | On Submit | Update Item_Warehouse_Stock subform row; recompute Item.Current_Stock via Deluge |
| Inventory Transaction (Stock Out + Project) | On Submit | Also auto-create Expense record |
| Transfer Order Status = "Completed" | On Submit | Generate paired Stock Out / Stock In transactions (from TO_Line_Items subform) |
| Goods Receipt Status = "Open" | On Submit | Create Stock In for Accepted Qty from GRN_Line_Items subform rows |
| Goods Receipt (all items received) | On Submit | POs are manually closed — no auto-close logic |
| PO Status = "Open" | On Submit | Send email to vendor with PO details |
| PR Approval Stage Change | On Submit | Send notification to next approver in chain |
| PR Fully Approved (Stage = "Approved") | On Submit | Auto-create Purchase Order (Draft); copy line items from PR_Line_Items subform, link PO.Requisition to PR |
| Invoice — Create DC | Custom Button | Auto-create Delivery Challan with same Project, Customer, and line items from Invoice_Line_Items subform |
| Inventory Reservation | On Submit | Increment Reserved_Qty on Item_Warehouse_Stock subform row; validate ≤ Current_Stock |
| Inventory Release | On Submit | Decrement Reserved_Qty on Item_Warehouse_Stock subform row |
| Project Status = "Completed" | On Submit | Validate no pending expenses/POs; auto-create final Invoice for unbilled items |
| Invoice Sent | On Submit | Update project P&L — add to Total Invoiced for revenue tracking |
| Invoice Paid | On Submit | Update Amount Paid, set Balance Due = 0, Status = "Paid" |
| DC Status = "Shipped" | On Submit | Auto-create Stock Out transaction for dispatched items |
| DC Shipped (no Invoice) | On Submit | Prompt user to create Invoice |
| BOM Submit | On Submit | Calculate Total Component Cost, Total Manufacturing Cost |
| Scheduled (Daily) | Cron | Budget alerts (80/90/100%), low stock alerts, KPI refresh, mark overdue invoices |

---

## F. Phase 1 vs Phase 2 Strategy

**Phase 1 (All in Zoho Creator):**
Everything above is Phase 1 — one Zoho Creator application with no external integrations.

**Phase 2 (Optional Integrations):**
- **Zoho Projects** sync: Link Zoho Projects tasks to budget tracking. Log time as expense against the budget.
- **Zoho Analytics**: For advanced dashboards beyond Zoho Creator Reports (drill-down, cross-filter, custom charts).

**Why Phase 1 in Zoho Creator alone is sufficient:**
- All modules share the same application, so lookups are fast with no API latency
- Zoho Creator Reports + Dashboards cover 90% of reporting needs
- You maintain full control over data and workflows without managing API auth

---

## G. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Deluge timeouts on large datasets (e.g., recalculating all budget components) | Use Scheduled Workflows for mass updates, keep On Submit workflows lightweight |
| Negative stock due to out-of-sequence transactions | Validate `Current_Stock >= Quantity` before Stock Out; use Deluge to enforce |
| Overrun notification emails going to spam | Configure Zoho Creator email settings; add sender to contacts |
| Lookup field shows stale inventory count | Use Formula Lookup (recalculated on load) instead of regular Lookup for stock fields |
| Concurrent users submitting expenses for the same budget component | Zoho Creator handles record-level locking on submit; still, consider a retry pattern in Deluge |
| Formula field performance for large datasets | Keep calculations in Deluge, not formula fields, for aggregation across many records |

---

## H. Quick Reference for Console Build

| Item | Details |
|------|---------|
| Forms to create | ~17 primary forms (Projects, Vendors, Accounts, Warehouses, Inventory_Items, Budget_Plans, Budget_Components, Expenses, Budget_Approvals, Inventory_Transactions, Transfer_Orders, Purchase_Requisitions, Purchase_Orders, Goods_Receipts, Invoices, Delivery_Challans, BOM) — each with embedded subforms for line items, contacts, documents |
| Deluge workflows | ~23 (22 On Submit + 1 Scheduled Cron) |
| User roles | 6 (Admin, PM, Finance, Procurement, Inventory, Employee) |
| Lookup forms (most referenced) | Projects, Vendors, Accounts, Inventory_Items, Warehouses |
| Seed data | "Main Warehouse" record, sample Budget Component categories |
| Critical performance rule | Maintain `Item_Warehouse_Stock.Current_Stock` via Deluge on every transaction — never aggregate on demand |

**Start with Phase 1A in Zoho Creator console: Vendors → Accounts → Projects → Warehouses → Inventory_Items**
