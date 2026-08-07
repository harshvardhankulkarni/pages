# Implementation Plan — Project Budget Tracking & Inventory Management (Zoho Creator)

**ITOTCloud Systems Pvt. Ltd. — Internal Delivery Document**
**Author:** Implementation Team | **Status:** Ready for Phase 1A | **Confidential**

---

> This is the field-level implementation blueprint for the ITOTCloud delivery team.
> Build from this document in the Zoho Creator console. Update it when design decisions change.
> Refer to `AGENTS.md` for AI assistant context and `index.html` for an interactive version.
> Modules: **21 primary forms** with embedded subforms for line items, contacts, and documents.

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
Phase 1D:  Budget Approval         Purchase Orders (enhanced)    Transfer Orders
                                               ↓                    ↓
                                          Goods Receipt (enhanced) ←┘
                                               ↓
                                     Supplier Credit Notes (NEW)
                                               ↓
Phase 1E:  BOM  →  Delivery Challan  →  Invoicing
                                                 ↓
Phase 1F:  Reports & Dashboards (all modules incl. Project P&L)
                                                 ↓
Phase 1G:  Vendor Bills  →  Payments (AP/AR sub-ledger)
                                                 ↓
Phase 1H:  FX Rates → Accounting Periods → Tax/GST enhancements (cross-cutting)
                                                 ↓
Phase 1I:  Audit Log → Expense Allocations → Budget Revisions (governance)
                                                  ↓
Phase 1J:  PO Approval → Bill Approval → Payment Approval → Committed Budget (SoD)
                                                  ↓
Phase 1K:  Customer Credit Notes → Manufacturing Orders → Sales Orders (gaps closure)
```

---

## C. Module-by-Module Design (19 Modules)

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
| Category | Dropdown | `Raw Material`, `Service`, `Equipment`, `Logistics`, `Consulting`, `Other` |
| Performance Rating | Dropdown | `Excellent`, `Good`, `Average`, `Poor` |
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
| Valuation Method | Dropdown | `Weighted Average`, `Standard Cost`, `FIFO` — Default: Weighted Average. Determines how stock value is calculated |
| Average Cost | Currency | Maintained by Deluge — updated on every Stock In transaction using weighted average formula: `((Current_Stock × Avg_Cost) + (Qty_In × Unit_Cost)) / (Current_Stock + Qty_In)` |

**Embedded subform — Item_Warehouse_Stock:** Item (Lookup → Inventory_Items), Warehouse (Lookup → Warehouses), Current Stock, Reserved Qty, Available Stock (Formula), Reorder Level, Unit Cost (Currency — Maintained by Deluge — updated on each Stock In from GRN actual cost. Used for weighted average calculation)

**Deluge approach for `Current_Stock` and `Reserved_Qty` :**
```
On every Inventory Transaction:
  Locate the matching Item_Warehouse_Stock subform row within the Item record:
    Stock In:              Current_Stock += Quantity; 
                           Update Average_Cost via weighted average: ((Old_Stock × Old_Avg) + (Qty_In × Rate)) / (Old_Stock + Qty_In)
                           Update Item_Warehouse_Stock.Unit_Cost = Rate
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
| Spent Amount | Currency | Updated by Deluge on Expense Submit / Stock Out |
| Remaining | Formula | `Allocated Amount - Spent Amount` |
| Consumption % | Formula | `(Spent Amount / Allocated Amount) * 100` |
| Committed Amount | Currency | Updated by Deluge — sum of all Open/Approved PO totals allocated to this component; shows committed spend not yet expensed |
| Available Budget | Formula | `Allocated_Amount − Spent_Amount − Committed_Amount` — true remaining budget |
| Status | Dropdown | `Within Budget`, `80% Alert`, `90% Alert`, `Exceeded` | Auto-calculated by Deluge based on Consumption % |

**Key Relationship:** This is the central pivot form. Expenses reference it. Reports group by it.

**Deluge Workflow for Status:**
```
On Expense Submit (if within budget):
  Update Budget_Component.Spent_Amount
  Recalculate consumption %
  If >= 100%: Status = "Exceeded", trigger alert
  If >= 90%:  Status = "90% Alert", trigger alert
   If >= 80%:  Status = "80% Alert", trigger alert
```

**Enhancement: Committed Cost Tracking**
On PO Status = "Open": Budget_Component.Committed_Amount += PO.Total (allocated proportionally across components)
On PO Status = "Closed" or "Cancelled": reverse the commitment
On Expense Submit: Committed_Amount remains unchanged (Spent_Amount increments as before)
The Available Budget formula gives PMs the true remaining budget picture.

**Enhancement: Budget Revision Tracking**

Add an embedded subform `Budget_Revisions` to the Budget_Plans form for tracking changes to budget allocations over time:

| Field | Type | Notes |
|---|---|---|
| Revision No | Auto-number | `REV-{0000}` |
| Budget Component | Lookup → Budget_Components | Which component was revised |
| Previous Allocated Amount | Currency | Amount before revision |
| New Allocated Amount | Currency | Amount after revision |
| Change Amount | Formula | `New_Amount − Previous_Amount` |
| Reason | Dropdown | `Overrun Approval`, `Scope Change`, `Management Adjustment`, `Reallocation`, `Other` |
| Approved By | User picker | Who approved this change |
| Revised Date | Date/Time | Auto timestamp |
| Notes | Multi-line | Details |

**Deluge:**
- On Budget_Approval Approve (when Modified_Budget_Amount is set):
  1. Calculate the change from current allocated amount
  2. Create a Budget_Revisions record in the Budget_Plans subform:
     - Budget_Component = the affected component
     - Previous_Allocated_Amount = current allocated before change
     - New_Allocated_Amount = Modified_Budget_Amount from approval
     - Reason = "Overrun Approval"
     - Approved_By = approver
  3. Update Budget_Component.Allocated_Amount to Modified_Budget_Amount

- On manual Budget_Component field change (Admin/PM adjusting allocation):
  1. Track the change via a form script
  2. Auto-create Budget_Revisions record with Reason = "Management Adjustment"

**Reports:**
- Budget Revision History — all revisions for a given budget plan
- Component Change Log — track changes to a specific budget component over time
- Revision Reason Analysis — revisions grouped by reason

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
| Expense Type | Dropdown | `Material`, `Labour`, `Equipment`, `Travel`, `Subcontract`, `Overhead`, `Other` |
| Status | Dropdown | `Draft`, `Submitted`, `Approved`, `Overrun-Pending Approval`, `Rejected`, `Modified` |

**Enhancement: Expense Allocation Subform**

Add an embedded subform `Expense_Allocations` to the Expenses form for splitting an expense across multiple budget components:

| Field | Type | Notes |
|---|---|---|
| Budget Component | Lookup → Budget_Components | Filtered by selected Project |
| Allocated Amount | Currency | Portion of expense allocated to this component |
| Percentage | Formula | `Allocated_Amount / Expense.Amount × 100` |

**Validation:**
- Sum of all Allocated_Amounts must equal Expense.Amount
- Each Budget Component must belong to the same Project as the Expense

**Enhanced Deluge (On Submit):**
```
1. If Expense_Allocations subform exists and has rows:
     For each allocation row:
       Update Budget_Component.Spent_Amount += Allocated_Amount
       Check Budget_Component budget thresholds (80/90/100%)
   Else (no allocations — single component, legacy behavior):
     Use existing logic: update single Budget_Component.Spent_Amount
2. Total of all Allocated_Amounts must equal Expense.Amount
```

**Note:** The single Budget_Component lookup field on the Expense header remains for backward compatibility. When allocations are used, the header field is informational only. If no allocations exist, the header Budget_Component is used as before.

**Deluge Workflow (on Submit):**
```
1. Read Allocated_Amount from Budget_Component
2. Read Spent_Amount from Budget_Component
3. New_Total = Spent_Amount + Expense.Amount
4. If New_Total <= Allocated_Amount:
     Set Status = "Approved"
     Update Budget_Component.Spent_Amount = New_Total
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
4. Procurement approves → Deluge validates: for the linked Project, check Budget_Components where remaining budget (Allocated − Spent − Committed) ≥ PR line item estimated totals. If sufficient: Approval_Stage = "Approved". If insufficient: alert "Project budget insufficient for this requisition. Estimated total: $X. Available budget: $Y."
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
| PO Total | Formula | `Sum(PO_Line_Items.Line_Total)` | Auto-computed total of all line items |
| Status | Dropdown | `Draft`, `Open`, `Partially Invoiced`, `Billed`, `Closed`, `Cancelled` |
| Receipt Status | Dropdown | `Not Received`, `Partially Received`, `Fully Received` — **auto-calculated by Deluge from GRN line items** |
| Has Outstanding Credit | Checkbox | Set to true when Supplier Credit Note is Issued against this PO; reset on full settlement |
| Approval Status | Dropdown | `Not Required`, `Pending Approval`, `Approved`, `Rejected` — controls whether PO needs explicit approval before going Open |
| Approver | User picker | Who approved this PO |
| Approval Date | Date/Time | When approved |
| Approval Notes | Multi-line | Approval comments |
| Budget Check Status | Dropdown | `Passed`, `Failed — Over Budget`, `Not Checked` — result of budget availability check on issue |
| PO Value (Base) | Currency | PO Total converted to base currency for commitment tracking |
| Subtotal | Currency | Sum of line item totals |
| Discount (%) | Decimal | Overall PO-level discount |
| Discount Amount | Currency | Calculated |
| Tax Total | Currency | Sum of line item taxes |
| Total | Currency | `Subtotal - Discount + Tax Total` |
| Terms & Conditions | Multi-line | Printed on PO |
| Notes | Multi-line | Internal instructions |
| Attachment | Upload | PO document file |

**Embedded subform — PO_Line_Items:** Item (Lookup → Inventory_Items), Description, Unit, HSN/SAC, Quantity, Unit Rate, Discount (%), Discount Amount (Formula), Tax (%), Tax Amount (Formula), Item Total (Formula), **Received Qty (Decimal — updated by Deluge from GRN)**, **Pending Qty (Formula — `Quantity - Received Qty`)**, **Credited Qty (Decimal — updated by Deluge from SCN)**


**PO Lifecycle:**
- **Draft**: Being created, not yet submitted
- **Pending Approval**: Submitted for approval (if PO exceeds approval threshold)
- **Approved**: PO approved by manager/finance
- **Rejected**: PO rejected by approver — can be revised and resubmitted
- **Open**: Approved and sent to vendor — budget committed
- **Partially Invoiced**: Some line items billed
- **Billed**: Fully invoiced
- **Closed**: Items received, PO fulfilled
- **Cancelled**: Voided before completion

**Deluge Workflow:**
- On Status = "Pending Approval": check if PO exceeds approval threshold (configurable amount, e.g., $5,000). If below threshold, auto-approve. If above, send notification to approver
- On Status = "Approved": change status to "Open", proceed with vendor email
- On Status = "Open": validate budget availability — check Budget_Component.Remaining (Allocated − Spent − Committed) ≥ PO.Total. If insufficient budget: set Budget_Check_Status = "Failed", show alert, block opening. If sufficient: commit budget by incrementing Budget_Component.Committed_Amount, set Budget_Check_Status = "Passed", trigger email to vendor with PO PDF
- On Status = "Cancelled": release committed budget by decrementing Budget_Component.Committed_Amount, validate no GRN linked to this PO
- On Status = "Closed": release any remaining committed budget
- On GRN Submit: update PO_Line_Items.Received_Qty and PO.Receipt_Status
- On SCN Submit: update PO_Line_Items.Credited_Qty, set PO.Has_Outstanding_Credit

---

### 14. Goods Receipt (`Goods_Receipts` — with embedded Line Items subform)

Supports accepted vs rejected quantities, credit tracking, and auto-updates inventory + PO.

| Field | Type | Notes |
|---|---|---|
| GRN Number | Auto-number | `GRN-0001` |
| PO | Lookup → Purchase_Orders | Required |
| Receipt Date | Date/Time | Defaults to now |
| Received By | User picker | Defaults to current user |
| Status | Dropdown | `Draft`, `Open`, `Closed` |

**Embedded subform — GRN_Line_Items:** Item (Lookup → Inventory_Items), PO Quantity (Read Only), Accepted Quantity, Rejected Quantity, Reason for Rejection, Actual Unit Cost, Total (Formula), Warehouse (Lookup → Warehouses), Condition Notes, **Is_Credited (Checkbox — set by Deluge when SCN references this GRN line)**, **Credit_Note_Ref (Text — auto-populated with SCN number)**, PO Unit Rate (Currency — Read Only — copied from PO_Line_Items.Unit_Rate when GRN is created — used for PPV calculation), PPV Amount (Formula — `(Actual_Unit_Cost − PO_Unit_Rate) × Accepted_Quantity` — Purchase Price Variance. Positive = Unfavorable (cost higher than PO), Negative = Favorable)

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

      Update PO line item actual costs if row.Actual_Unit_Cost differs from PO rate

2. After processing all rows, recalculate PO.Receipt_Status:
      For each PO_Line_Item in the linked PO:
        Sum Accepted Qty from all GRNs → update PO_Line_Item.Received_Qty
        Calculate PO_Line_Item.Pending_Qty = Quantity - Received_Qty
      If any PO_Line_Item.Pending_Qty > 0 → PO.Receipt_Status = "Partially Received"
      If all PO_Line_Items.Pending_Qty = 0 → PO.Receipt_Status = "Fully Received"
```

---

### 15. Supplier Credit Notes (`Supplier_Credit_Notes` — with embedded Line Items subform)

Tracks credit notes raised by finance against suppliers for defective, rejected, or disputed items discovered during QA/QC after goods receipt. This is a **finance-initiated** module — always created manually by the finance team, never auto-generated.

**Relationship to Procurement Cycle:**

```
PO → Goods Receipt → QA/QC Inspection → Defective/Rejected Items
                                               ↓
                                    Finance creates Supplier Credit Note
                                               ↓
                                    Issued to Supplier → PO flagged
                                    Stock Returned/Scrapped/Reworked
                                    Settled → Credit resolved
```

| Field | Type | Notes |
|---|---|---|
| Credit Note No | Auto-number | `SCN-{0000}` — Supplier Credit Note reference |
| Type | Dropdown | `Credit Note (Supplier owes us)`, `Debit Note (We charge supplier)` |
| Vendor | Lookup → Vendors | Required — supplier to credit/debit |
| PO Reference | Lookup → Purchase_Orders | Required — links credit to original PO |
| GRN Reference | Lookup → Goods_Receipts | Links to the receipt where the defect was found |
| Credit Note Date | Date | Defaults to today |
| Total Amount | Currency | Sum of all line item totals |
| Status | Dropdown | `Draft`, `Issued`, `Partially Settled`, `Settled`, `Cancelled` |
| Reason | Dropdown | `Defective Item`, `Damaged in Transit`, `Wrong Item`, `Shortage`, `Quality Issue`, `Price Discrepancy`, `Other` |
| QA/QC Reference | Text | Inspection report number, QC batch reference |
| Payment Adjustment Ref | Text | How this was settled — adjusted against next payment, separate refund, credit memo, etc. |
| Notes | Multi-line | |
| Attachment | Upload | Scanned supplier credit note / debit note document |
| Bill Reference | Lookup → Vendor_Bills | Optional — links SCN to a specific Vendor Bill for AP adjustment. When set, Issuing the SCN reduces the Bill's Balance Due |

**Embedded subform — SCN_Line_Items:** Item (Lookup → Inventory_Items), PO Line Reference (Text — optional reference to specific PO line item), Quantity Returned (Decimal — qty being credited), Rate per Unit (Currency — from PO or current purchase price), Total Amount (Formula — `Quantity × Rate`), Defect Reason (Text — specific defect description per item), Stock Disposition (Dropdown — `Returned to Supplier`, `Scrapped`, `Reworked`, `Under Inspection`)

**Deluge Workflow (on Submit):**

```
On Submit (Status = "Issued"):
  1. Validate Total Amount > 0
  2. Validate at least one SCN_Line_Items row exists
  3. For each row in input.SCN_Line_Items subform:
       Update PO_Line_Items.Credited_Qty += row.Quantity_Returned
       If row.Stock_Disposition = "Returned to Supplier":
         Create Return to Vendor Inventory Transaction:
           Item = row.Item
           Quantity = row.Quantity_Returned
           Rate = row.Rate_per_Unit
           Reference = Credit Note No
           Type = "Return to Vendor"
           → Inventory_Transactions workflow fires → deducts stock
  4. Set PO.Has_Outstanding_Credit = true
  5. Mark linked GRN_Line_Items as Is_Credited = true, populate Credit_Note_Ref = Credit Note No
  6. Send notification to finance team and procurement team

On Submit (Status = "Settled"):
  1. Validate no other Issued SCNs exist for this PO before clearing flag
  2. If no other outstanding SCNs → set PO.Has_Outstanding_Credit = false
  3. Update linked GRN credit status if applicable

On Submit (Status = "Cancelled"):
  1. Reverse PO_Line_Items.Credited_Qty for referenced items
  2. If no other outstanding SCNs → set PO.Has_Outstanding_Credit = false
  3. Reverse GRN_Line_Items.Is_Credited flag
```

**Reports:**
- Outstanding Supplier Credits — filter: Status IN ("Issued", "Partially Settled")
- Supplier Credit History — by Vendor, date range
- Defective Item Analysis — grouped by Item, Reason, Stock Disposition
- Credits by PO — all SCNs linked to a specific PO

---

### 20. Vendor Bills (`Vendor_Bills` — with embedded Line Items subform)

Records invoices received from vendors against Purchase Orders. This is the Accounts Payable (AP) sub-ledger — finance records the bill, matches it to PO + GRN (3-way match), tracks payment status, and manages AP aging.

**Relationship to Procurement Cycle:**

```
PO → Goods Receipt → Vendor Bill (AP liability recorded) → SCN (adjusts Bill if defective) → Payment
```

| Field | Type | Notes |
|---|---|---|
| Bill No | Auto-number | `BILL-{0000}` — unique vendor bill reference |
| Vendor | Lookup → Vendors | Required — supplier who issued the bill |
| PO Reference | Lookup → Purchase_Orders | Required — links bill to original PO |
| GRN Reference | Lookup → Goods_Receipts | Optional — links to goods receipt for 3-way match |
| Bill Date | Date | Date on vendor's invoice |
| Due Date | Date | Payment due date based on vendor payment terms |
| Reference Number | Text | Vendor's own invoice/bill number |
| Subtotal | Currency | Sum of line item totals |
| Discount (%) | Decimal | Overall bill-level discount |
| Discount Amount | Currency | Formula — calculated |
| Tax Total | Currency | Sum of line item taxes |
| Total Amount | Currency | Formula — `Subtotal − Discount_Amount + Tax_Total` |
| Amount Paid | Currency | Updated by Deluge on Payment record creation |
| Balance Due | Currency (Formula) | `Total_Amount − Amount_Paid` |
| Status | Dropdown | `Draft`, `Received`, `Matched`, `Pending Approval`, `Approved`, `Partially Paid`, `Paid`, `Cancelled` |
| Currency | Dropdown | Copied from Vendor |
| Notes | Multi-line | Internal notes |
| Attachment | Upload | Scanned vendor invoice document |

**Embedded subform — Bill_Line_Items:** Item (Lookup → Inventory_Items, optional — service bills may not have items), Description, HSN/SAC, Quantity, Unit Rate, Discount (%), Discount Amount (Formula), Tax (%), Tax Amount (Formula), Line Total (Formula)

**3-Way Match Validation (Deluge on Submit when Status = "Matched"):**
```
1. Validate PO Reference is set
2. Fetch the Purchase_Order record and its PO_Line_Items subform
3. If GRN Reference is set, fetch Goods_Receipt and its GRN_Line_Items
4. Compare:
   - PO Ordered Qty ≥ Bill Qty (cannot bill more than ordered)
   - GRN Accepted Qty ≥ Bill Qty (cannot bill more than received)
5. If mismatch found: alert user, prevent Status = "Matched"
6. Calculate PPV for each line item where GRN Actual_Unit_Cost differs from PO Unit Rate
7. If matched successfully: set Status = "Pending Approval" — finance manager must manually approve before it's finalized
```

**Deluge Workflow:**
- On Status = "Matched": 3-way match validation passes, status advances to "Pending Approval" (not auto-Approved)
- On Status = "Pending Approval → Approved": Finance Manager manually approves; calculate and record PPV for each line item against PO + GRN
- On Status = "Pending Approval → Rejected": return to "Matched" with rejection notes for revision
- On Status = "Cancelled": validate no Payments or SCNs linked to this Bill
- On Payment creation: update Amount_Paid, recalculate Balance_Due; if Balance_Due = 0, set Status = "Paid"; if partially paid, set Status = "Partially Paid"

**Reports:**
- AP Aging — Bills grouped by Due Date range (Current, 1-30, 31-60, 61-90, 90+ days overdue) — filter: Status IN ("Approved", "Partially Paid")
- Outstanding Bills — filter: Status IN ("Approved", "Partially Paid")
- Bill Register — all bills in date range
- PPV Register — all bills with PPV > 0, grouped by Vendor
- Vendor Payment History — all bills + payments per vendor

**Tax Fields on Bill_Line_Items subform (additional fields to add):**
| Tax Classification | Dropdown | `Input GST`, `Input IGST`, `CESS`, `Non-Taxable`, `Zero-Rated`, `Exempt` — determines how ITC is booked |
| ITC Eligibility | Dropdown | `Full ITC`, `50% ITC` (for personal use), `No ITC` (blocked credit) | Default: Full ITC |

**GST Return Reporting:** The combination of HSN/SAC + Tax Classification + ITC Eligibility enables GST return (GSTR-2) preparation. Filter Bills by period, group by HSN/SAC, sum eligible ITC.

---

### 21. Payments (`Payments`)

Unified module for recording both outgoing payments to vendors (AP) and incoming receipts from customers (AR). Every payment updates the linked Bill or Invoice.

| Field | Type | Notes |
|---|---|---|
| Payment No | Auto-number | `PMT-{0000}` |
| Type | Dropdown | `Outgoing — AP (Vendor Payment)`, `Incoming — AR (Customer Receipt)` |
| Reference To | Lookup → Vendor_Bills or Invoices | Polymorphic — links to the Bill (AP) or Invoice (AR) being paid/received |
| Vendor | Lookup → Vendors | Required if Type = Outgoing |
| Customer | Lookup → Accounts | Required if Type = Incoming |
| Payment Date | Date | Defaults to today |
| Amount | Currency | Payment amount |
| Payment Method | Dropdown | `Bank Transfer`, `Cheque`, `Cash`, `Credit Card`, `UPI`, `Other` |
| Reference No | Text | Cheque number, transaction ID, UPI ref |
| Status | Dropdown | `Draft`, `Pending Approval`, `Approved`, `Completed`, `Reversed`, `Failed` |
| Approval Threshold | Currency | Read-only — shows the auto-approval threshold. Payments below this amount auto-approve |
| Approver | User picker | Who approved this payment |
| Approval Date | Date/Time | When approved |
| Notes | Multi-line | |
| Attachment | Upload | Payment receipt/screenshot |

**Deluge Workflow (On Submit):**

```
On Submit (Status = "Completed"):
  1. Validate Amount > 0
  2. If Type = "Outgoing — AP":
       Fetch linked Vendor_Bill
       Update Bill.Amount_Paid += Amount
       Recalculate Bill.Balance_Due
       If Bill.Balance_Due <= 0: Bill.Status = "Paid"
       Else: Bill.Status = "Partially Paid"
  3. If Type = "Incoming — AR":
       Fetch linked Invoice
       Update Invoice.Amount_Paid += Amount
       Recalculate Invoice.Balance_Due
       If Invoice.Balance_Due <= 0: Invoice.Status = "Paid"
       Else: Invoice.Status = "Partially Paid"
  4. Validate Amount <= linked document's Balance_Due (prevent overpayment)

On Submit (Status = "Reversed"):
  1. Reverse the Amount_Paid update on the linked document
  2. Restore previous Status on Bill/Invoice
```

**Validation Rules:**
1. Amount must be > 0
2. Reference To must match Type direction (Bill for Outgoing, Invoice for Incoming)
3. Cannot exceed Balance Due of the linked document
4. Status can only transition: Draft → Pending Approval → Approved → Completed; Completed → Reversed (with reason)
5. Payments above threshold ($5,000 default) require explicit approval; below threshold auto-approve

**Reports:**
- Payment Register — all payments in date range, filterable by Type
- AP Payment Summary — outgoing payments grouped by Vendor
- AR Receipt Summary — incoming receipts grouped by Customer
- Payment Method Analysis — payments grouped by method

---

### 25. Customer Credit Notes (`Customer_Credit_Notes`)

Handles credit notes raised against customers for returned goods, service credits, invoice disputes, or refunds. This is the customer-side equivalent of Supplier Credit Notes — reduces Accounts Receivable.

**Relationship to Revenue Cycle:**
```
Invoice → Customer disputes/returns → Customer Credit Note Issued → AR reduced → Refund or credit applied
```

| Field | Type | Notes |
|---|---|---|
| Credit Note No | Auto-number | `CCN-{0000}` |
| Type | Dropdown | `Credit Note (We owe customer)`, `Debit Note (Customer owes us)` |
| Invoice Reference | Lookup → Invoices | Required — links credit to original invoice |
| Customer | Lookup → Accounts | Required |
| Project | Lookup → Projects | Denormalized from Invoice |
| Credit Note Date | Date | Defaults to today |
| Total Amount | Currency | Sum of line item totals |
| Reason | Dropdown | `Goods Returned`, `Service Credit`, `Price Dispute`, `Shortage`, `Damage`, `Cancellation`, `Other` |
| Refund Method | Dropdown | `Adjusted Against Invoice`, `Separate Refund`, `Credit Memo`, `Bank Transfer` |
| Status | Dropdown | `Draft`, `Issued`, `Applied`, `Partially Applied`, `Cancelled` |
| Adjustment Reference | Text | Refund transaction ID, credit memo number |
| Notes | Multi-line | |
| Attachment | Upload | Supporting document |

**Embedded subform — CCN_Line_Items:** Item (Lookup → Inventory_Items, optional), Description, Quantity, Rate, Total Amount (Formula), Reason (Text)

**Deluge Workflow:**
```
On Submit (Status = "Issued"):
  1. Validate Total Amount > 0
  2. Validate at least one line item
  3. If Reason = "Goods Returned": create Return from Customer inventory transaction (stock added back)
  4. Reduce Invoice Balance Due:
       invoice = getRecordById(Invoices, Invoice_Reference)
       new_balance = invoice.Balance_Due - Total_Amount
       Update Invoice.Balance_Due = max(new_balance, 0)

On Submit (Status = "Applied"):
  1. Finalize — reduce Invoice Amount_Paid if refund processed
  2. Update Invoice Status if fully applied

On Submit (Status = "Cancelled"):
  1. Reverse the AR reduction
  2. Reverse inventory transaction if goods were returned
```

**Reports:**
- Outstanding Customer Credits — filter: Status IN (Issued, Partially Applied)
- Customer Credit History — by Customer, date range
- Credits by Invoice — all CCNs linked to a specific invoice

---

### 26. Manufacturing Orders (`Manufacturing_Orders`)

Manages the production process — issuing raw materials from inventory, tracking work-in-progress, and receiving finished goods. The BOM defines the recipe; the Manufacturing Order executes it.

**Production Flow:**
```
BOM → Manufacturing Order (Planned) → Released → In Progress (materials issued) → Completed (finished goods received) → Cancelled
```

| Field | Type | Notes |
|---|---|---|
| MO No | Auto-number | `MO-{0000}` |
| BOM Reference | Lookup → BOM | Required — which recipe to produce |
| Finished Item | Lookup → Inventory_Items | Denormalized from BOM |
| Quantity to Produce | Decimal | Target output quantity |
| Unit | Text | Copied from BOM |
| Planned Start Date | Date | |
| Planned End Date | Date | |
| Actual Start Date | Date/Time | Set when status = "In Progress" |
| Actual End Date | Date/Time | Set when status = "Completed" |
| Status | Dropdown | `Planned`, `Released`, `In Progress`, `Completed`, `Cancelled` |
| Warehouse | Lookup → Warehouses | Where materials are issued from and finished goods go to |
| Project | Lookup → Projects | Optional — if production is for a specific project |
| Standard Material Cost | Currency (Formula) | `BOM.Total_Component_Cost × Qty` |
| Actual Material Cost | Currency | Sum of material issued (tracked via Inventory Transactions) |
| Actual Labor Cost | Currency | Entered manually at completion |
| Actual Overhead Cost | Currency | Entered manually at completion |
| Total Actual Cost | Formula | `Actual_Material + Actual_Labor + Actual_Overhead` |
| Cost Variance | Formula | `Total_Actual_Cost − Standard_Material_Cost` |
| Notes | Multi-line | |

**Embedded subform — MO_Components:** Component Item (Lookup → Inventory_Items, from BOM), Quantity Required (from BOM), Quantity Issued (Decimal — updated by Deluge), Unit, Unit Cost, Total Cost (Formula)

**Deluge Workflow:**
```
On Submit (Status = "Released"):
  1. Validate stock availability for all component items based on BOM quantities
  2. If any component has insufficient stock: alert with details, block release
  3. Reserve component quantities (create Reservation inventory transactions)
  4. Set status = "In Progress", record Actual_Start_Date

On Submit (Status = "Completed"):
  1. For each MO_Components row:
       Issue components from warehouse:
         Create Stock Out transaction for each component:
           Item = component
           Quantity = Quantity_Required (adjusted for scrap %)
           Warehouse = selected warehouse
           Type = "Stock Out"
           Reference = MO Number
           → Inventory_Transactions workflow fires → deducts stock
       Update MO_Components.Quantity_Issued
       Calculate Actual_Material_Cost = sum of (Qty × Unit_Cost)
  2. Receive finished goods:
       Create Stock In transaction:
         Item = Finished_Item
         Quantity = Quantity_to_Produce
         Warehouse = selected warehouse
         Type = "Stock In"
         Reference = MO Number
         Rate = Total_Actual_Cost / Quantity_to_Produce (unit cost for finished item)
       → Inventory_Transactions workflow fires → adds stock
  3. Record Actual_End_Date
  4. Calculate Cost_Variance = Actual_Total - Standard_Material_Cost

On Submit (Status = "Cancelled"):
  1. If In Progress: reverse any material reservations
  2. No stock changes recorded
```

**Reports:**
- Production Order Status — all MOs grouped by status
- Manufacturing Cost vs Standard — cost variance analysis
- Production by Finished Item — quantity produced, cost per unit
- Material Consumption — components used across all MOs

---

### 27. Sales Orders (`Sales_Orders` — with embedded Line Items subform)

Records customer orders/quotes before invoicing. A Sales Order can be converted to an Invoice + Delivery Challan (for goods) or just an Invoice (for services). Useful for product/retail deployments.

| Field | Type | Notes |
|---|---|---|
| SO No | Auto-number | `SO-{0000}` |
| Customer | Lookup → Accounts | Required |
| Project | Lookup → Projects | Optional — links order to project |
| Order Date | Date | Defaults to today |
| Delivery Date | Date | Requested delivery date |
| Status | Dropdown | `Draft`, `Confirmed`, `Invoiced`, `Partially Delivered`, `Delivered`, `Cancelled` |
| Subtotal | Currency | Sum of line item totals |
| Discount (%) | Decimal | Overall order discount |
| Tax Total | Currency | Sum of line item taxes |
| Total | Currency | `Subtotal − Discount + Tax` |
| Customer Reference | Text | Customer's PO/reference number |
| Notes | Multi-line | |

**Embedded subform — SO_Line_Items:** Item (Lookup → Inventory_Items, optional), Description, Quantity, Unit, Rate, Discount (%), Discount Amount (Formula), Tax (%), Tax Amount (Formula), Line Total (Formula)

**Deluge / Custom Actions:**
- On Status = "Confirmed": if line items have stock Items → prompt user to create DC; auto-create Invoice
- On Status = "Confirmed" (services only): auto-create Invoice from SO line items
- **Custom Button "Create Invoice"**: creates Invoice with same Customer, Project, and line items
- **Custom Button "Create DC"**: creates Delivery Challan for goods items
- On Status = "Cancelled": validate no linked Invoices or DCs

**Reports:**
- Open Sales Orders — filter: Status = Confirmed
- Sales Order Register — by date range
- Order Fulfillment Status — SOs with linked DC/Invoice status

---

### Cross-Cutting Enhancement: Multi-Currency Support

Enhances Vendors, Accounts, POs, Bills, Invoices, and Payments with foreign exchange tracking.

**New form — Currency Exchange Rates (`Currency_Rates`):**
| Field | Type | Notes |
|---|---|---|
| Base Currency | Dropdown | `USD`, `EUR`, `GBP`, `INR`, `AED`, `SGD` — Fixed; chosen at setup |
| Target Currency | Dropdown | The foreign currency |
| Rate | Decimal | Exchange rate: 1 Base Currency = X Target Currency |
| Effective Date | Date | Date this rate is valid from |
| Source | Text | `Manual`, `API Feed`, `Bank Rate` |

**Enhanced fields on Vendor_Bills (module 20):**
Add after existing Currency field: `FX Rate (Decimal — from Currency_Rates table, auto-populated by Bill Date)` and `Base Currency Amount (Currency — Formula: Total_Amount / FX_Rate)`

**Enhanced fields on Invoices (module 17):**
Add: `Currency (Dropdown — copied from Account)`, `FX Rate (Decimal)`, `Base Currency Amount (Formula: Total / FX_Rate)`

**Enhanced fields on Payments (module 21):**
Add: `FX Rate (Decimal)`, `Base Currency Amount (Formula: Amount / FX_Rate)`, `FX Gain/Loss (Currency — Formula: difference between payment rate and bill/invoice rate)`

**Deluge:**
- On Bill/Invoice create: look up Currency_Rates for the matching currency + date (or nearest prior date), populate FX_Rate
- On Payment: calculate FX Gain/Loss = (Bill Rate − Payment Rate) × Payment Amount in Base Currency

**Reports:**
- FX Gain/Loss Register — all payments with FX difference > 0
- Currency Exposure — outstanding Bills/Invoices grouped by currency

---

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
| Stock Availability | List View on Inventory_Items | Inventory_Items | Show Item_Warehouse_Stock.Current_Stock as subform aggregate column |
| Low Stock Alert | Summary on Inventory_Items | Inventory_Items | Filter: Item_Warehouse_Stock.Current_Stock ≤ Item_Warehouse_Stock.Reorder_Level |
| Stock Consumption by Project | Summary | Inventory_Transactions | PM, Inventory |
| Inventory Valuation | Summary | Inventory_Items | Finance |
| Stock Movement by Warehouse | Summary by Item + Warehouse | Inventory_Transactions | Inventory Manager |
| Open Transfer Orders | Tabular (filter: Status = In Transit) | Transfer_Orders | Inventory Manager |
| Invoice Aging | Tabular (group by Due Date, Status != Paid) | Invoices | Finance |
| DC Register | Tabular (filter by date range) | Delivery_Challans | Inventory, Logistics |
| Vendor List with Contacts | Tabular | Vendors (Contacts subform) | Procurement |
| BOM Cost Summary | Summary (group by Finished_Item) | BOM (Line Items subform) | Production |
| Outstanding Supplier Credits | Tabular (filter: Status IN Issued, Partially Settled) | Supplier_Credit_Notes | Finance |
| Supplier Credit History | Summary by Vendor | Supplier_Credit_Notes | Finance, Procurement |
| Defective Item Analysis | Summary by Item, Reason, Stock Disposition | Supplier_Credit_Notes | Finance, QA/QC |
| Credits by PO | Tabular (group by PO_Reference) | Supplier_Credit_Notes | Finance, Procurement |
| AP Aging | Tabular (group by Due Date range) | Vendor_Bills | Finance |
| PPV Register | Summary (group by Vendor, PPV > 0) | Vendor_Bills | Finance |
| Executive Dashboard | Dashboard with KPI cards + charts | All | All |

**Dashboard KPIs — Deluge Scheduled Workflow to calculate and store in a Summary_Data form:**
- Total Project Budget = Sum of all active Budget_Plans.Total_Budget_Amount
- Spent Amount = Sum of approved Expenses.Amount
- Total Invoiced = Sum of Invoices where Status IN ("Sent", "Partially Paid", "Paid")
- Budget Utilization % = `Spent Amount / Total Project Budget * 100`
- Project P&L = `Total Invoiced per Project - Total Expenses per Project`
| Open PO Value | Sum(PO_Line_Items.Line_Total) × PO.Currency | Purchase_Orders | Formula field PO_Total on Purchase_Orders = Sum(PO_Line_Items.Line_Total) |
- Inventory Value = Sum of (Current_Stock × Purchase_Price) across all items
- Cost Overruns = Count of Budget_Components where Status = "Exceeded"
- Low Stock Items = Count of Item_Warehouse_Stock subform rows where Current_Stock <= Reorder_Level
- Active POs = Count of POs where Status IN ("Open", "Partially Invoiced")
- Pending Receipts = Count of POs where Status = "Open" and past Delivery_Date
- Overdue Invoices = Count of Invoices where Due Date < Today and Status != "Paid"
- Outstanding Supplier Credits = Sum of SCN.Total_Amount where Status IN ("Issued", "Partially Settled")
- Pending Supplier Returns = Count of SCNs with Stock Disposition = "Returned to Supplier" and Status IN ("Issued", "Partially Settled")
- AP Aging (Overdue) = Count of Vendor_Bills where Due Date < Today and Status IN ("Approved", "Partially Paid")
- Total AP Outstanding = Sum of Vendor_Bills.Balance_Due where Status IN ("Approved", "Partially Paid")
- Total AR Outstanding = Sum of Invoices.Balance_Due where Status IN ("Sent", "Partially Paid")

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

**Tax Fields on Invoice_Line_Items subform (additional fields):**
| Tax Classification | Dropdown | `Output GST`, `Output IGST`, `CESS`, `Non-Taxable`, `Zero-Rated`, `Exempt` | Default: Output GST |
| GST Liability | Formula | `Tax_Amount` — automatically treated as Output GST liability |

**Deluge / Custom Actions:**
- On Status = "Sent": update Project Budget Component's Total Invoiced (for P&L reporting)
- On Status = "Paid": update Amount Paid, auto-set Balance Due = 0
- On Status = "Cancelled": validate no payments received
- **Custom Button "Create DC"** (when Status = "Sent" + line items have stock Items): auto-create Delivery Challan with same Project, Customer, and line items copied to DC's embedded Line Items subform; link DC.Ref to Invoice

**GST Reports:**
- **GSTR-1 Summary (Sales)** — Invoices grouped by HSN/SAC, tax period, GST liability per rate slab
- **GSTR-2 Summary (Purchases)** — Bills grouped by HSN/SAC, ITC claimed per rate slab
- **GST Reconciliation** — Compare GSTR-2A (vendor uploaded) vs Books (Bills in system)
- **ITC Register** — All Bills with ITC eligibility status

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

### Cross-Cutting Enhancement: Period Close & Accounting Periods

Enables month-end / quarter-end financial close with period locking and GRNI accruals.

**New form — Accounting Periods (`Accounting_Periods`):**
| Field | Type | Notes |
|---|---|---|
| Period Name | Text | e.g., "April 2026" |
| Period Type | Dropdown | `Monthly`, `Quarterly`, `Yearly` |
| Start Date | Date | First day of period |
| End Date | Date | Last day of period |
| Status | Dropdown | `Open`, `Closing`, `Closed` |
| Closed By | User picker | Who closed this period |
| Closed Date | Date/Time | When it was closed |

**Enhanced field on all financial forms (Expenses, POs, Bills, Invoices, Payments):**
Add to each: `Accounting Period (Lookup → Accounting_Periods — auto-populated from transaction date on create)`

**Deluge Validation on all financial form submits:**
```
On Submit (all financial forms):
  1. Determine Accounting_Period from transaction date
  2. If Accounting_Period.Status == "Closed": alert "Cannot post to a closed period. Period: [Period_Name]"
  3. If Accounting_Period.Status == "Closing": add warning note but allow with PM approval flag
```

**GRNI (Goods Received Not Invoiced) Report:**
- Find all GRN line items that have no linked Bill with Status = "Approved" or "Paid"
- Calculate accrual: Sum(GRN_Line_Items.Accepted_Quantity × Actual_Unit_Cost) for unmatched items
- Report: GRNI Aging — by GRN date, by PO

**Reports:**
- Trial Balance by Period — Sum of Bills (AP) + Expenses (Cost) + Invoices (Revenue) grouped by period
- GRNI Accrual — month-end accrual for goods received but not yet billed
- Period Close Checklist — automated status of each close step

---

### Cross-Cutting Enhancement: Audit Trail

Comprehensive immutable audit log for all financial transactions and status changes.

**New form — Audit Log (`Audit_Log`):**
| Field | Type | Notes |
|---|---|---|
| Log ID | Auto-number | `AUD-{0000}` |
| Module | Dropdown | Which form was changed |
| Record ID | Text | ID of the changed record |
| Action | Dropdown | `Created`, `Updated`, `Status Changed`, `Deleted`, `Cancelled`, `Reversed` |
| Field Changed | Text | Which field was modified (for updates) |
| Old Value | Multi-line | Previous value |
| New Value | Multi-line | New value |
| Changed By | User picker | Who made the change |
| Changed At | Date/Time | Auto timestamp |
| IP Address | Text | Optional — for security audit |
| Notes | Multi-line | Additional context |

**Deluge — Add Audit Log Entry on Status Changes (all P0 modules):**

Attach a Deluge script to the On Submit workflow of every financial module:

```
On Submit of: Expenses, Budget_Approvals, POs, GRNs, SCNs, Vendor_Bills, Invoices, Payments, Transfer_Orders:
  1. For each status change, create Audit_Log record:
     - Module = [form name]
     - Record_ID = [current record ID]
     - Action = "Status Changed"
     - Field_Changed = "Status"
     - Old_Value = [prior status] (or null for new records)
     - New_Value = [new status]
     - Changed_By = [current user]
  2. For financial edits (Amount, Quantity changes):
     - Compare old and new values where possible
     - Log field-level changes
```

**Additional Audit Reports:**
- Audit Log by Date — all changes in a date range
- Audit Log by Module — changes to a specific form
- User Activity — all changes by a specific user
- Status Change History — full lifecycle of a specific record

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
                         ├── Warehouses (N:1)
                         └── Supplier_Credit_Notes (1:N, via GRN_Reference)

Supplier_Credit_Notes ──┬── SCN_Line_Items (embedded subform, 1:N)
                          │       └── Items (N:1)
                          ├── Vendors (N:1)
                          ├── Purchase_Orders (N:1)
                          └── Goods_Receipts (N:1)

Invoices ──── Invoice_Line_Items (embedded subform, 1:N)
                   └── Items (N:1)

Delivery_Challans ──── DC_Line_Items (embedded subform, 1:N)
                          ├── Items (N:1)
                          └── Warehouses (N:1, dispatch warehouse)

BOM ──── BOM_Line_Items (embedded subform, 1:N)
             └── Items (N:1, as component)

Vendor_Bills ──┬── Bill_Line_Items (embedded subform, 1:N)
               │        └── Items (N:1)
               ├── Vendors (N:1)
               ├── Purchase_Orders (N:1)
               ├── Goods_Receipts (N:1)
               ├── Supplier_Credit_Notes (1:N, via Bill_Reference)
               └── Payments (1:N)

Payments ──┬── Vendor_Bills (N:1, for AP)
             ├── Invoices (N:1, for AR)
             ├── Vendors (N:1)
             └── Accounts (N:1)

Currency_Rates (standalone — lookup target for FX rates)

Accounting_Periods (standalone — lookup target for period validation)

Audit_Log (standalone — no inbound lookups)

Expenses ──┬── Expense_Allocations (embedded subform, 1:N)
               └── Budget_Components (N:1)

Budget_Plans ──┐── Budget_Revisions (embedded subform, 1:N)
                   └── Budget_Components (N:1)

Manufacturing_Orders ──┬── MO_Components (embedded subform, 1:N)
                       │        └── Items (N:1, as component)
                       ├── BOM (N:1)
                       ├── Inventory_Items (N:1, as finished item)
                       └── Warehouses (N:1)

Customer_Credit_Notes ──┬── CCN_Line_Items (embedded subform, 1:N)
                        │        └── Items (N:1)
                        ├── Invoices (N:1)
                        └── Accounts (N:1)

Sales_Orders ──┬── SO_Line_Items (embedded subform, 1:N)
               │        └── Items (N:1)
               ├── Accounts (N:1)
               ├── Invoices (1:N)
               └── Delivery_Challans (1:N)
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
| SCN Issued | On Submit (Status = "Issued") | Validate total > 0; update PO_Line_Items.Credited_Qty; set PO.Has_Outstanding_Credit = true; mark linked GRN lines as credited; auto-create Return to Vendor inventory transaction if Stock Disposition = "Returned to Supplier"; notify finance + procurement |
| SCN Settled | On Submit (Status = "Settled") | Clear PO.Has_Outstanding_Credit if no other outstanding SCNs |
| SCN Cancelled | On Submit | Reverse Credited_Qty on PO_Line_Items; reverse GRN Is_Credited flag; clear PO.Has_Outstanding_Credit if applicable |
| Bill Received | On Submit (Status = "Received") | Record vendor bill, send notification to finance for 3-way match |
| Bill Matched | On Submit (Status = "Matched") | Execute 3-way match validation (PO Qty ≥ Bill Qty, GRN Accepted ≥ Bill Qty); calculate PPV per line item |
| Bill Approved | On Submit (Status = "Approved") | Record PPV, update AP aging metrics |
| Bill Cancelled | On Submit (Status = "Cancelled") | Validate no linked Payments or SCNs |
| Payment Completed (AP) | On Submit (Status = "Completed") | Update linked Vendor_Bill Amount_Paid + Balance_Due + Status; validate no overpayment |
| Payment Completed (AR) | On Submit (Status = "Completed") | Update linked Invoice Amount_Paid + Balance_Due + Status; validate no overpayment |
| Payment Reversed | On Submit (Status = "Reversed") | Reverse Amount_Paid update on linked Bill/Invoice; restore previous Status |
| Inventory Valuation — Weighted Avg | On Stock In | Recalculate Average_Cost on Inventory_Item: `((Old_Stock × Old_Avg) + (Qty × Rate)) / (Old_Stock + Qty)` |
| GRN Submit (enhanced) | On Submit (Status = "Open") | After Stock In creation, recalculate PO.Receipt_Status per line item using aggregate Accepted Qty from all linked GRNs |
| Scheduled (Daily) | Cron | Budget alerts (80/90/100%), low stock alerts, KPI refresh, mark overdue invoices, outstanding supplier credit summary |
| Weighted Avg Cost Recalculation | On Stock In | Recalculate Average_Cost using ((Old_Stock × Old_Avg) + (Qty × Rate)) / (Old_Stock + Qty) on Inventory_Item |
| FX Rate Lookup | On Bill/Invoice Create | Auto-populate FX_Rate from Currency_Rates table by date |
| FX Gain/Loss Calc | On Payment Submit | Calculate FX Gain/Loss = (Bill_Rate − Payment_Rate) × Amount |
| Period Lock Validation | On Submit (all financial) | Reject if Accounting_Period.Status = "Closed" |
| Audit Log — Status Change | On Submit (all P0 modules) | Create Audit_Log entry for every status change |
| Audit Log — Financial Edit | On Submit (all P0) | Log field-level changes to Amount, Quantity, Rate on financial forms |
| Expense Allocation Validation | On Expense Submit | Validate sum of allocations = Expense.Amount; update multiple Budget_Components |
| Budget Revision Create | On Budget Approval | Auto-create Budget_Revisions record when Modified_Budget_Amount is set |
| GRN → Bill Accrual Check | Scheduled (month-end) | Generate GRNI report: GRN line items without matched Bills |
| Period Close Validation | On Period Status = "Closed" | Verify no transactions posted after period end date in the closed period |
| PO Budget Check | On PO Status = "Open" | Validate Budget_Component.Available ≥ PO.Total; block if insufficient; commit budget |
| PO Approval Status | On PO Status = "Pending Approval" | Route to approver based on PO value; auto-approve below threshold |
| PO Budget Release | On PO Status = "Cancelled" or "Closed" | Release committed budget back to Budget_Component |
| PR Budget Check | On PR Final Approval | Validate remaining budget (Allocated − Spent − Committed) ≥ estimated total |
| Bill Manual Approval | On Bill Status = "Pending Approval" → "Approved" | Finance Manager reviews and approves; PPV finalized on approval |
| Payment Approval | On Payment Submit | Check against threshold; route to approver if above; auto-approve below |
| CCN Issued | On CCN Status = "Issued" | Reduce Invoice Balance Due; create Return from Customer inventory txn if goods returned |
| CCN Cancelled | On CCN Status = "Cancelled" | Reverse AR reduction; reverse inventory txn |
| MO Released | On MO Status = "Released" | Validate stock for BOM components; reserve materials; set In Progress |
| MO Completed | On MO Status = "Completed" | Issue components (Stock Out), receive finished goods (Stock In), calculate cost variance |
| MO Cancelled | On MO Status = "Cancelled" | Release material reservations; no stock impact |
| SO Confirmed | On SO Status = "Confirmed" | Auto-create Invoice from SO line items; prompt DC creation for goods |
| SO Cancelled | On SO Status = "Cancelled" | Validate no linked Invoices or DCs |
| Committed Budget Sync | Scheduled (Daily) | Recalculate Budget_Component.Committed_Amount by aggregating Open PO totals per component |
  
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

### G.1 Segregation of Duties (Role-Based Access)

| Role | Can Create | Can Approve | Can View Reports |
|------|-----------|-------------|------------------|
| Administrator | All | All | All |
| Project Manager | Projects, Expenses, PRs | Budget Overruns | Budget vs Actual, Project P&L |
| Finance Manager | Accounting Periods | Budget Overruns, Bills, Payments (>threshold) | All financial reports |
| AP Clerk | Vendor Bills | — | Bill Register, AP Aging |
| AP Manager | — | Vendor Bills, Payments (>$5K) | AP Aging, Payment Register |
| AR Clerk | Invoices, Customer Credit Notes | — | AR Aging, Invoice Register |
| AR Manager | — | Customer Credit Notes, Refunds | AR Aging, Customer Credit History |
| Procurement Manager | Purchase Orders | POs (>$5K), PRs (final stage) | Open POs, Vendor Spend |
| Procurement User | PRs, POs (Draft) | — | PR Status, PO Status |
| Inventory Manager | Inventory Transactions, Transfer Orders, Manufacturing Orders, GRNs | — | Stock reports, Production Status |
| Employee | Expenses, PRs (own) | — | Own expense/PR status |

**Approval Thresholds (configurable):**
- PO Approval Required: > $5,000 (default)
- Bill Approval Required: All bills (3-way match is automatic validation, but finance approval is manual)
- Payment Approval Required: > $5,000 (default)

---

## H. Quick Reference for Console Build

| Item | Details |
|------|---------|
| Forms to create | ~27 primary forms (Projects, Vendors, Accounts, Warehouses, Inventory_Items, Budget_Plans, Budget_Components, Expenses, Budget_Approvals, Inventory_Transactions, Transfer_Orders, Purchase_Requisitions, Purchase_Orders, Goods_Receipts, Supplier_Credit_Notes, Invoices, Delivery_Challans, BOM, Vendor_Bills, Payments, Reports, Currency_Rates, Accounting_Periods, Audit_Log) — each with embedded subforms for line items, contacts, documents |
| Deluge workflows | ~58+ (57+ On Submit + 1 Scheduled Cron) |
| User roles | 10 (Admin, PM, Finance Manager, AP Clerk, AP Manager, AR Clerk, Procurement Manager, Procurement User, Inventory Manager, Employee) |
| Lookup forms (most referenced) | Projects, Vendors, Accounts, Inventory_Items, Warehouses |
| Seed data | "Main Warehouse" record, sample Budget Component categories |
| Critical performance rule | Maintain `Item_Warehouse_Stock.Current_Stock` via Deluge on every transaction — never aggregate on demand |

**Start with Phase 1A in Zoho Creator console: Vendors → Accounts → Projects → Warehouses → Inventory_Items**

**Phase 1D extended order:** Budget Approvals → Purchase Orders (enhanced with Receipt_Status) → Goods Receipt (enhanced with Is_Credited) → **Supplier Credit Notes (new)** → Transfer Orders

**Phase 1G:** Vendor Bills → Payments (AP/AR sub-ledger — extends procurement cycle)

**Phase 1H:** FX Rates → Accounting Periods → Tax/GST enhancements (cross-cutting financial)

**Phase 1I:** Audit Log → Expense Allocations → Budget Revisions (governance & controls)

**Phase 1J:** PO Approval → Bill Approval → Payment Approval → Committed Budget (segregation of duties)

**Phase 1K:** Customer Credit Notes → Manufacturing Orders → Sales Orders (gaps closure)
