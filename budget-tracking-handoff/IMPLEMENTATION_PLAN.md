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
| Subform limitations | Subforms are great for < 100 line items. For Budget Components (vary by project) and PO Line Items, use **separate forms** with lookups + Add-As-Subform view. Better for reporting. |
| No dynamic SQL | All aggregation is `Map` + `List` in Deluge or Zoho Creator Report widgets. Prefer Reports over Deluge for performance. |
| Role-based access is per-form, not record-level | For department-specific data (e.g., Procurement sees only their POs), use **form filters** on report views or dedicated forms per role. |
| Formula fields can't look up external data | Complex validation (budget checks) must go in **Deluge workflows on form submit**, not formula fields. |
| Lookup fields cache stale data | When Inventory Master stock changes, any previous lookup reference still shows old value. Use **Formula Lookup** fields (recalculated on load) for live values. |

---

## B. Implementation Sequence (Build Order)

Each phase depends on the previous. Build in this order:

```
Phase 1A:  Vendor Management  →  Project Master  →  Warehouses  →  Inventory Master
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

## C. Module-by-Module Design (17 Modules)

### 1. Project Master (`Projects`)

| Field | Type | Notes |
|---|---|---|
| Project Name | Text | Required |
| Project Code | Text (auto-number) | e.g., `PROJ-0001` |
| Account | Lookup → Vendors | Client/company associated with the project |
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

### 2. Vendor Management (`Vendors`)

Matches Zoho Inventory's vendor master structure. **Also serves as Accounts/Clients** — the Project Master's `Account` field looks up here. Use `Type` (or a tag) to distinguish vendors from clients.

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
| Payment Options | Multi-select | `Cheque`, `Cash`, `Bank Transfer`, `Credit Card`, `Online Payment` |
| Opening Balance | Currency | Starting balance if carried forward |
| Account Number | Text | Internal account reference |
| Tax ID | Text | GSTIN / VAT / HST registration number |
| PAN | Text | Permanent Account Number (India) |
| Billing Address — Attention | Text | |
| Billing Address — Street | Multi-line | |
| Billing Address — City | Text | |
| Billing Address — State | Text | |
| Billing Address — Zip | Text | |
| Billing Address — Country | Text | |
| Shipping Address | Same-as-billing toggle + full address block | |
| Vendor Category | Dropdown | `Materials`, `Services`, `Equipment`, `Labor`, `Logistics` |
| Performance Rating | Decimal (1-5) | Manually updated after deliveries |
| Status | Dropdown | `Active`, `Inactive` |
| Portal Access | Checkbox | Enable vendor self-service portal |
| Remarks | Multi-line | |
| Tags | Multi-select | Custom classification |

**Contact Persons — Separate form `Vendor_Contacts` with Add-as-Subform:**

| Field | Type |
|---|---|
| Vendor | Lookup → Vendors |
| Salutation | Dropdown: `Mr`, `Ms`, `Mrs`, `Dr` |
| First Name | Text |
| Last Name | Text |
| Email | Email |
| Phone | Phone |
| Mobile | Phone |
| Designation | Text |
| Department | Text |
| Skype ID | Text |
| Is Primary | Checkbox |

**Documents — Separate form `Vendor_Documents` with Add-as-Subform:**

| Field | Type |
|---|---|
| Vendor | Lookup → Vendors |
| Document Name | Text |
| File | Upload |
| Expiry Date | Date |
| Notes | Text |

---

### 3. Warehouses (`Warehouses`)

Multi-warehouse support — every inventory transaction references a warehouse (or a default "Main Warehouse" is created on setup).

| Field | Type | Notes |
|---|---|---|
| Warehouse Name | Text | Required |
| Warehouse Code | Text (auto-number) | e.g., `WH-0001` |
| Address | Multi-line | |
| City | Text | |
| State | Text | |
| Country | Text | |
| Contact Person | Text | |
| Phone | Phone | |
| Status | Dropdown | `Active`, `Inactive` |

A **default warehouse** is seeded on app creation so single-warehouse users never notice.

---

### 4. Inventory Master — Items (`Inventory_Items`)

Matches Zoho Inventory's item master structure. Items are goods or services tracked at the SKU level.

| Field | Type | Notes |
|---|---|---|
| Item Name | Text | Required |
| SKU | Text (auto-number) | e.g., `SKU-0001` — unique identifier |
| Item Type | Dropdown | `Goods`, `Services` — services have no stock tracking |
| Category | Dropdown | `Raw Material`, `Component`, `Consumable`, `Equipment`, `Service`, `Subcontract` |
| Unit | Dropdown | `Pcs`, `Kg`, `Ltr`, `Box`, `Meter`, `Hour`, `Day`, `Set`, `Pair` |
| Dimensions — Length | Decimal (cm) | |
| Dimensions — Width | Decimal (cm) | |
| Dimensions — Height | Decimal (cm) | |
| Weight | Decimal (kg) | |
| Brand | Text | |
| Manufacturer | Text | |
| HSN/SAC Code | Text | Tax classification code |
| Taxability | Dropdown | `Taxable`, `Non-Taxable`, `Zero-Rated` |
| Tax Rate | Decimal (%) | Default tax % applied in POs |
| Purchase Price | Currency | Default unit cost for purchases |
| Sales Price | Currency | For internal reference |
| Reorder Level | Decimal | Min stock before alert |
| Preferred Vendor | Lookup → Vendors | Default vendor for POs |
| Current Stock | Decimal (Formula/Subform) | **Aggregated across warehouses** — see stock-by-warehouse below |
| Stock Value | Formula | `Current Stock * Purchase Price` |
| Description | Multi-line | Internal notes |
| Image | Upload | Item photo |
| Status | Dropdown | `Active`, `Inactive` |

**Stock by Warehouse — Separate form `Item_Warehouse_Stock` with Add-as-Subform:**

| Field | Type |
|---|---|
| Item | Lookup  Inventory_Items |
| Warehouse | Lookup  Warehouses |
| Current Stock | Decimal (maintained by Deluge on each transaction) |
| Reserved Qty | Decimal (maintained by Deluge — Reservation/Release transactions) |
| Available Stock | Formula (read-only) | `Current Stock − Reserved Qty` |
| Reorder Level | Decimal (warehouse-specific, overrides item default) |

**Deluge approach for `Current_Stock` and `Reserved_Qty` :**
```
On every Inventory Transaction:
  Update Item_Warehouse_Stock for the specific warehouse:
    Stock In:              Current_Stock += Quantity
    Stock Out:             Current_Stock -= Quantity; Reserved_Qty -= Quantity (capped)
    Adjustment:            Current_Stock = Adjusted_Qty (Reserved_Qty unchanged)
    Return to Vendor:      Current_Stock -= Quantity
    Reservation:           Reserved_Qty += Quantity; validate Reserved_Qty <= Current_Stock
    Release:               Reserved_Qty -= Quantity
  Then recompute Inventory_Item.Current_Stock = SUM of all Item_Warehouse_Stock records
```

This gives both warehouse-level visibility and item-level totals without on-demand aggregation.

**Item Attributes (optional — for variants like size/color):**
Create a form `Item_Attributes` with fields: Item (lookup), Attribute Name (e.g., "Size"), Attribute Value (e.g., "XL"). Linked via Add-as-Subform.

---

### 5. Budget Planning (`Budget_Plans`)

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

**Recommendation for Budget Components:** Use a **separate form** `Budget_Components` with `Add-as-Subform` in Budget_Plans. This gives the user a seamless inline experience while enabling rich reporting.

---

### 6. Budget Components (`Budget_Components`)

| Field | Type | Notes |
|---|---|---|
| Component Name | Text | e.g., "Labor", "Materials" |
| Budget Plan | Lookup → Budget_Plans | Links to parent |
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

### 7. Expense Management (`Expenses`)

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

### 8. Budget Approval Workflow (`Budget_Approvals`)

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

### 9. Inventory Transactions (`Inventory_Transactions`)

Matches Zoho Inventory's stock transaction structure. Every transaction ties to a specific warehouse.

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
1. Locate Item_Warehouse_Stock record for (Item, Warehouse)
2. Calculate new stock:
   - Stock In:              Current_Stock += Quantity
   - Stock Out:             Current_Stock -= Quantity;  Reserved_Qty -= min(Reserved_Qty, Quantity)
   - Adjustment:            Current_Stock = Adjusted_Qty
   - Return to Vendor:      Current_Stock -= Quantity
   - Reservation:           Reserved_Qty += Quantity;  validate Reserved_Qty <= Current_Stock
   - Release:               Reserved_Qty -= Quantity
3. Validate Current_Stock >= 0 AND unreserved stock (Current_Stock - Reserved_Qty) >= 0 for Stock Out
4. Update Item_Warehouse_Stock.Current_Stock and Reserved_Qty
5. Recalculate Inventory_Item.Current_Stock = SUM of all warehouse stock
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

### 10. Transfer Orders (`Transfer_Orders`)

Matches Zoho Inventory's transfer order module — moving stock between warehouses.

| Field | Type | Notes |
|---|---|---|
| Transfer Order No | Auto-number | `TO-0001` |
| Date | Date | |
| From Warehouse | Lookup → Warehouses | Source |
| To Warehouse | Lookup → Warehouses | Destination |
| Status | Dropdown | `Draft`, `In Transit`, `Completed`, `Cancelled` |

**Line Items — Separate form `TO_Line_Items` with Add-as-Subform:**

| Field | Type |
|---|---|
| Transfer Order | Lookup → Transfer_Orders |
| Item | Lookup → Inventory_Items |
| Quantity | Decimal |
| Rate | Currency |
| Total | Formula |

**Deluge Workflow (on Status = "Completed"):**
```
For each line item:
  Create Stock Out transaction from From_Warehouse (Type = "Stock Transfer")
  Create Stock In  transaction to   To_Warehouse   (Type = "Stock Transfer")
  → Both trigger the Inventory_Transactions workflow → update stock counts
```

---

### 11. Purchase Requisition (`Purchase_Requisitions`)

Custom Zoho Creator module (Zoho Books has no native PR). Designed to feed into Zoho Books Purchase Orders via Phase 2 API sync.

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

**Line Items — Separate form `PR_Line_Items` with Add-as-Subform:**

| Field | Type | Notes |
|---|---|---|
| Requisition | Lookup → Purchase_Requisitions | |
| Item | Lookup → Inventory_Items | Optional — can enter free-text description |
| Item Description | Text | Free text if Item not selected |
| Quantity | Decimal | |
| Estimated Unit Rate | Currency | |
| Estimated Total | Formula | `Quantity * Estimated Unit Rate` |
| Item Type | Text | Copied from Item or manual |
| Account | Lookup → Chart of Accounts | Maps to Zoho Books `account_id` for Phase 2 |
| Unit | Text | Copied from Item or manual; maps to Zoho Books `unit` |

**Multi-stage Approval + Auto-PO Workflow:**
1. User submits (Status = "Open")
2. Department Manager approves → Approval_Stage = "Pending Finance Approval"
3. Finance approves → Approval_Stage = "Pending Procurement"
4. Procurement approves → Approval_Stage = "Approved"
5. **Auto-create PO** (Deluge on final approval): create Purchase_Order in Draft status, copy all PR_Line_Items → PO_Line_Items, link PO.Requisition = this PR

Each step sends email notification. Procurement then reviews the auto-created PO and sends to vendor.

---

### 12. Purchase Orders (`Purchase_Orders`)

1:1 aligned with Zoho Books Purchase Order API (`/books/v3/purchaseorder`). Full line-item detail, discount/tax support, address tracking, and status lifecycle. All fields map directly to Zoho Books JSON payload for Phase 2 API sync.

| Field | Type | Zoho Books API Field | Notes |
|---|---|---|---|
| PO Number | Auto-number | `purchaseorder_number` | `PO-0001` — auto-numbering in Zoho Books |
| Vendor | Lookup → Vendors | `vendor_id` | Required |
| Vendor Email | Email | — | Copied from Vendor; convenience field |
| Contact Person | Lookup → Vendor_Contacts | `contact_persons_associated` | Maps to Zoho Books contact persons array |
| Requisition | Lookup → Purchase_Requisitions | — | Optional — linked if created from PR |
| Project | Lookup → Projects | `project_id` (line items) | |
| PO Date | Date | `date` | Defaults to today; YYYY-MM-DD |
| Delivery Date | Date | `delivery_date` | Expected delivery |
| Expected Arrival Date | Date | `expected_delivery_date` | |
| Due Date | Date | `due_date` | Payment due date |
| Reference Number | Text | `reference_number` | Vendor's reference or contract no. |
| Ship Via | Dropdown | `ship_via` | `Courier`, `Freight`, `Air`, `Sea`, `Road`, `Pickup` |
| Attention | Text | `attention` | Person to receive |
| Billing Address | Multi-line | `billing_address_id` | Copied from Vendor, editable |
| Shipping Address | Multi-line | — | Copied from Vendor, editable |
| Status | Dropdown | `status` | `Draft`, `Open`, `Partially Invoiced`, `Invoiced`, `Closed`, `Cancelled` |
| Currency | Lookup → Currencies | `currency_id` | Defaults to org base currency |
| Exchange Rate | Decimal | `exchange_rate` | Defaults to 1 |
| Is Inclusive Tax | Checkbox | `is_inclusive_tax` | Tax included in item rates |
| Subtotal | Currency | `sub_total` | Sum of line item totals |
| Discount (%) | Decimal | `discount` | Overall PO-level discount (e.g. `10` or `10%`) |
| Discount Account | Lookup → Chart of Accounts | `discount_account_id` | GL account for discount |
| Discount Before Tax | Checkbox | `is_discount_before_tax` | Apply discount before tax calc |
| Discount Amount | Currency | — | Calculated |
| Tax Total | Currency | `total_tax` | Sum of line item taxes |
| Total | Currency | `total` | `Subtotal - Discount + Tax Total` |
| Terms & Conditions | Multi-line | `terms` | Printed on PO |
| Notes | Multi-line | `notes` | Internal instructions |
| Attachment | Upload | — | PO document file |
| Location | Lookup → Warehouses | `location_id` | Zoho Books location/warehouse |
| Template | Lookup → Templates | `template_id` | Zoho Books PDF template |
| Price Book | Lookup → Price Books | `pricebook_id` | Zoho Books price book |
| GST Treatment | Dropdown | `gst_treatment` | India: `business_gst`, `consumer_gst`, etc. |
| GST No | Text | `gst_no` | Vendor GSTIN |
| Source of Supply | Text | `source_of_supply` | GST state code |
| Destination of Supply | Text | `destination_of_supply` | GST state code |
| Reverse Charge | Checkbox | `is_reverse_charge_applied` | India reverse charge |
| Custom Fields | JSON | `custom_fields` | Zoho Books custom field values |

**Line Items — Separate form `PO_Line_Items` with Add-as-Subform:**

| Field | Type | Zoho Books API Field | Notes |
|---|---|---|---|
| PO | Lookup → Purchase_Orders | — | |
| Line Item ID | Text | `line_item_id` | Zoho Books internal ID (Phase 2 sync) |
| Item | Lookup → Inventory_Items | `item_id` | |
| SKU | Text | `sku` | Auto-filled from Item |
| Name | Text | `name` | Auto-filled from Item Name, editable |
| Description | Text | `description` | Item description |
| Unit | Text | `unit` | `Nos`, `Kg`, `Hours`, etc. |
| HSN/SAC | Text | `hsn_or_sac` | Tax classification code |
| Quantity | Decimal | `quantity` | |
| Unit Rate | Currency | `rate` | |
| BCY Rate | Currency | `bcy_rate` | Rate in base currency |
| Discount (%) | Decimal | — | Line-level discount |
| Discount Amount | Formula | — | `(Unit Rate * Quantity) * (Discount% / 100)` |
| Tax (%) | Decimal | `tax_id` | Defaults from Item's Tax Rate |
| Tax Amount | Formula | — | `((Unit Rate * Quantity) - Discount Amount) * (Tax% / 100)` |
| Item Total | Formula | `item_total` | `(Unit Rate * Quantity) - Discount + Tax` |
| Tax Exemption | Lookup | `tax_exemption_id` | Tax exemption reference |
| TDS Tax | Lookup → TDS | `tds_tax_id` | TDS applicable |
| Account | Lookup → Chart of Accounts | `account_id` | Expense account for this line |
| Received Quantity | Decimal | — | Updated by Goods Receipt |
| Warehouse | Lookup → Warehouses | `location_id` | Default warehouse on receipt |
| Product Type | Dropdown | `product_type` | `goods`, `service`, `digital` |
| Item Order | Number | `item_order` | Display order in line items |
| Tags | Multi-select | `tags` | Zoho Books tags |
| Project | Lookup → Projects | `project_id` | Project tracking per line item |

**PO Lifecycle (matches Zoho Books status model):**
- **Draft**: Being created, not yet submitted → `status: "draft"`
- **Open**: Approved and sent to vendor → `status: "open"`
- **Partially Invoiced**: Some line items billed (Phase 2)
- **Invoiced**: Fully billed (Phase 2) → `status: "billed"`
- **Closed**: Items received, PO fulfilled
- **Cancelled**: Voided before completion → via Cancel PO endpoint

**Deluge Workflow:**
- On Status = "Open": trigger email to vendor with PO PDF
- On Goods Receipt: update `Received_Quantity` in line items
- When Status ≠ "Closed" and all line items `Received_Quantity >= Quantity`: auto-set Status to "Closed"
- On Status = "Cancelled": validate no GRN linked to this PO
- **Phase 2**: On Status = "Open" → POST to Zoho Books `purchaseorder` endpoint to sync

---

### 13. Goods Receipt (`Goods_Receipts`)

Matches Zoho Inventory's Goods Receipt Note (GRN) structure — supports accepted vs rejected quantities, and auto-updates inventory + PO.

| Field | Type | Notes |
|---|---|---|
| GRN Number | Auto-number | `GRN-0001` |
| PO | Lookup → Purchase_Orders | Required — auto-fills Vendor from PO |
| Vendor | Lookup → Vendors | Copied from PO |
| Receipt Date | Date/Time | Defaults to now |
| Received By | User picker | Defaults to current user |
| Status | Dropdown | `Draft`, `Open`, `Closed` |

**Line Items — Separate form `GRN_Line_Items` with Add-as-Subform:**

| Field | Type | Notes |
|---|---|---|
| GRN | Lookup → Goods_Receipts | |
| PO Line Item | Lookup → PO_Line_Items | |
| Item | Lookup → Inventory_Items | Auto-filled from PO Line Item |
| PO Quantity | Decimal (Read Only) | Quantity ordered on PO |
| Accepted Quantity | Decimal | Quantity received in good condition |
| Rejected Quantity | Decimal | Quantity damaged or不合格 |
| Reason for Rejection | Text | Required if Rejected Qty > 0 |
| Actual Unit Cost | Currency | Copied from PO, editable if cost changed |
| Total | Formula | `Accepted Quantity * Actual Unit Cost` |
| Warehouse | Lookup → Warehouses | Where to stock the accepted items |
| Condition Notes | Text | |

**Deluge Workflow (on Submit when Status = "Open"):**
```
1. For each line item:
     If Accepted_Quantity > 0:
       Create Stock In transaction:
         Item = Line Item.Item
         Warehouse = Line Item.Warehouse
         Quantity = Accepted_Quantity
         Rate = Actual_Unit_Cost
         Reference = GRN Number
         Type = "Stock In"
       → Inventory_Transactions workflow fires → updates stock

     Update PO_Line_Item:
       Received_Quantity += Accepted_Quantity

2. Check PO completion:
   If all PO_Line_Items have Received_Quantity >= PO_Line_Item.Quantity:
     PO.Status = "Closed"

3. Update PO line item actual costs if Actual_Unit_Cost differs from PO rate
```

---

### 14. Reports & Dashboards

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
| Stock Availability | Tabular (group by Warehouse) | Item_Warehouse_Stock | Inventory Manager |
| Low Stock Alert | Tabular (filter: Stock <= Reorder Level) | Item_Warehouse_Stock | Inventory Manager |
| Stock Consumption by Project | Summary | Inventory_Transactions | PM, Inventory |
| Inventory Valuation | Summary | Inventory_Items | Finance |
| Stock Movement by Warehouse | Summary by Item + Warehouse | Inventory_Transactions | Inventory Manager |
| Open Transfer Orders | Tabular (filter: Status = In Transit) | Transfer_Orders | Inventory Manager |
| Invoice Aging | Tabular (group by Due Date, Status != Paid) | Invoices | Finance |
| DC Register | Tabular (filter by date range) | Delivery_Challans | Inventory, Logistics |
| Vendor List with Contacts | Tabular | Vendors + Vendor_Contacts | Procurement |
| BOM Cost Summary | Summary (group by Item) | BOM + BOM_Line_Items | Production |
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
- Low Stock Items = Count of Item_Warehouse_Stock where Current_Stock <= Reorder_Level
- Active POs = Count of POs where Status IN ("Open", "Partially Invoiced")
- Pending Receipts = Count of POs where Status = "Open" and past Delivery_Date
- Overdue Invoices = Count of Invoices where Due Date < Today and Status != "Paid"

**Scheduled Workflow (runs daily at midnight):**
- Recalculate all KPI values
- Check for budget alerts (80%, 90%, 100%)
- Check for low stock items and send alerts
- Auto-close POs where all items Received_Quantity >= Quantity and older than 30 days
- Mark Invoices as "Overdue" if Due Date passed and Status IN ("Sent", "Partially Paid")

---

### 15. Invoicing (`Invoices`)

Matches Zoho Books invoice structure. Captures revenue per project. Future Zoho Books sync maps fields 1:1.

| Field | Type | Notes |
|---|---|---|
| Invoice No | Auto-number | `INV-0001` |
| Project | Lookup → Projects | Required — ties revenue to a project for P&L |
| Customer / Account | Lookup → Vendors | Billed party (vendor form serves dual purpose) |
| Invoice Date | Date | Defaults to today |
| Due Date | Date | Based on payment terms |
| Payment Terms | Dropdown | `Due on Receipt`, `Net 15`, `Net 30`, `Net 45`, `Net 60` |
| PO Reference | Text | Customer PO number if applicable |
| Delivery Challan Ref | Lookup → Delivery_Challans (optional) | Link to DC if applicable |
| Status | Dropdown | `Draft`, `Sent`, `Partially Paid`, `Paid`, `Overdue`, `Cancelled` |
| Subtotal | Currency | Sum of line item totals |
| Discount (%) | Decimal | Overall invoice discount |
| Discount Amount | Currency | Calculated |
| Tax Total | Currency | Sum of line item taxes |
| Total | Currency | `Subtotal - Discount + Tax Total` |
| Balance Due | Currency (Formula) | `Total - Amount Paid` |
| Amount Paid | Currency | Updated on payment receipt |
| Notes | Multi-line | Internal |
| Terms & Conditions | Multi-line | |
| Attachment | Upload | Invoice PDF |

**Line Items — Separate form `Invoice_Line_Items` with Add-as-Subform:**

| Field | Type | Notes |
|---|---|---|
| Invoice | Lookup → Invoices | |
| Item | Lookup → Inventory_Items | Optional — can enter free-text |
| Description | Text | Auto-filled from Item, editable |
| Quantity | Decimal | |
| Rate | Currency | |
| Discount (%) | Decimal | Line-level |
| Discount Amount | Formula | |
| Tax (%) | Decimal | |
| Tax Amount | Formula | |
| Total | Formula | `(Quantity * Rate) - Discount + Tax` |

**Deluge / Custom Actions:**
- On Status = "Sent": update Project Budget Component's Total Invoiced (for P&L reporting)
- On Status = "Paid": update Amount Paid, auto-set Balance Due = 0
- On Status = "Cancelled": validate no payments received
- **Custom Button "Create DC"** (when Status = "Sent" + line items have stock Items): auto-create Delivery Challan with same Project, Customer, and line items copied to DC_Line_Items; link DC.Ref to Invoice

---

### 16. Delivery Challan (`Delivery_Challans`)

Tracks physical dispatch of goods. Customer-facing document. Future Zoho Books Delivery Challan sync.

| Field | Type | Notes |
|---|---|---|
| DC No | Auto-number | `DC-0001` |
| Project | Lookup → Projects | |
| Customer | Lookup → Vendors | Recipient |
| Reference | Text | Customer PO / Sales Order ref |
| Date | Date | Defaults to today |
| Ship Via | Dropdown | `Courier`, `Freight`, `Own Vehicle`, `Pickup` |
| Vehicle No | Text | If own transport |
| Driver Name | Text | |
| Driver Contact | Phone | |
| Status | Dropdown | `Draft`, `Shipped`, `Delivered`, `Cancelled` |
| Remarks | Multi-line | |
| Attachment | Upload | Signed DC copy |

**Line Items — Separate form `DC_Line_Items` with Add-as-Subform:**

| Field | Type | Notes |
|---|---|---|
| Delivery Challan | Lookup → Delivery_Challans | |
| Item | Lookup → Inventory_Items | |
| Description | Text | |
| Quantity | Decimal | |
| Unit | Text | Copied from Item |
| Condition | Text | `Good`, `Damaged`, `Partial` |

**Deluge / Custom Actions:**
- On Create: validate stock availability for each line item
- On Status = "Shipped": reduce stock for each line item (auto create Stock Out transaction)
- On Status = "Shipped" + no Invoice linked: prompt user to create Invoice
- Can also be created automatically from Invoice via "Create DC" button on Invoice form

---

### 17. BOM — Bill of Materials (`BOM`)

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

**Line Items — Separate form `BOM_Line_Items` with Add-as-Subform:**

| Field | Type | Notes |
|---|---|---|
| BOM | Lookup → BOM | |
| Component Item | Lookup → Inventory_Items | Raw material / sub-component |
| Quantity Required | Decimal | Per BOM Quantity output |
| Unit | Text | Copied from Item |
| Unit Cost | Currency | Current purchase price or standard cost |
| Total Cost | Formula | `Quantity Required * Unit Cost` |
| Scrap % | Decimal | Allowance for waste |
| Notes | Text | |

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
          ├── Expenses (N:1)
          ├── Goods_Receipts (1:N)
          ├── Invoices (1:N)
          └── Delivery_Challans (1:N)

Warehouses ──┬── Item_Warehouse_Stock (1:N)
             ├── Inventory_Transactions (1:N)
             ├── Transfer_Orders — From (1:N)
             ├── Transfer_Orders — To (1:N)
             ├── PO_Line_Items (default receipt warehouse)
             ├── GRN_Line_Items (receipt warehouse)
             └── DC_Line_Items (dispatch warehouse)

Inventory_Items ──┬── Item_Warehouse_Stock (1:N)
                  ├── Inventory_Transactions (1:N)
                  ├── PO_Line_Items (1:N)
                  ├── PR_Line_Items (1:N)
                  ├── GRN_Line_Items (1:N)
                  ├── TO_Line_Items (1:N)
                  ├── Invoice_Line_Items (1:N)
                  ├── DC_Line_Items (1:N)
                  ├── BOM (1:N, as finished item)
                  └── BOM_Line_Items (1:N, as component)

Item_Warehouse_Stock ──┬── Items (N:1)
                       └── Warehouses (N:1)

Inventory_Transactions ──┬── Items (N:1)
                         ├── Warehouses (N:1)
                         └── Projects (N:1, Stock Out only)

Transfer_Orders ──┬── Warehouses — From (N:1)
                  ├── Warehouses — To (N:1)
                  └── TO_Line_Items (1:N)
                       └── Items (N:1)

Purchase_Requisitions ──┬── PR_Line_Items (1:N)
                         └── Items (N:1)
                       └── Purchase_Orders (1:N)  ← when converted

Purchase_Orders ──┬── PO_Line_Items (1:N)
                  │     └── Items (N:1)
                  │     └── Warehouses (N:1)
                  ├── Goods_Receipts (1:N)
                  └── Requisition (optional, N:1)

Goods_Receipts ──── GRN_Line_Items (1:N)
                       ├── Items (N:1)
                       ├── PO_Line_Items (N:1)
                       └── Warehouses (N:1)

Invoices ──── Invoice_Line_Items (1:N)
                 ├── Items (N:1)
                 └── Delivery_Challans (N:1, optional)

Delivery_Challans ──── DC_Line_Items (1:N)
                         ├── Items (N:1)
                         └── Warehouses (N:1, dispatch warehouse)

BOM ──── BOM_Line_Items (1:N)
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
| Inventory Transaction (Stock In/Out/Adj) | On Submit | Update Item_Warehouse_Stock, recompute Item.Current_Stock |
| Inventory Transaction (Stock Out + Project) | On Submit | Also auto-create Expense record |
| Transfer Order Status = "Completed" | On Submit | Generate paired Stock Out / Stock In transactions |
| Goods Receipt Status = "Open" | On Submit | Create Stock In for Accepted Qty, update PO_Line_Item.Received_Qty |
| Goods Receipt (all items received) | On Submit | Auto-set PO.Status = "Closed" |
| PO Status = "Open" | On Submit | Send email to vendor with PO details |
| PR Approval Stage Change | On Submit | Send notification to next approver in chain |
| PR Fully Approved (Stage = "Approved") | On Submit | Auto-create Purchase Order (Draft), copy line items, link PO.Requisition to PR |
| Invoice — Create DC | Custom Button | Auto-create Delivery Challan with same Project, Customer, and line items |
| Inventory Reservation | On Submit | Increment Reserved_Qty on Item_Warehouse_Stock; validate ≤ Current_Stock |
| Inventory Release | On Submit | Decrement Reserved_Qty |
| Project Status = "Completed" | On Submit | Validate no pending expenses/POs; auto-create final Invoice for unbilled items |
| Invoice Sent | On Submit | Update project P&L — add to Total Invoiced for revenue tracking |
| Invoice Paid | On Submit | Update Amount Paid, set Balance Due = 0, Status = "Paid" |
| DC Status = "Shipped" | On Submit | Auto-create Stock Out transaction for dispatched items |
| DC Shipped (no Invoice) | On Submit | Prompt user to create Invoice |
| BOM Submit | On Submit | Calculate Total Component Cost, Total Manufacturing Cost |
| Scheduled (Daily) | Cron | Budget alerts (80/90/100%), low stock alerts, KPI refresh, auto-close POs, mark overdue invoices |

---

## F. Phase 1 vs Phase 2 Strategy

**Phase 1 (All in Zoho Creator):**
Everything above is Phase 1 — one Zoho Creator application with modules mirroring Zoho Inventory's data model. No external integrations. The forms, fields, and statuses are designed to make Phase 2 migration seamless.

**Phase 2 (Optional Integrations):**
- **Zoho Inventory** sync: Connect via API so Inventory Items, Purchase Orders, and Vendor records sync bidirectionally. The Phase 1 data model is already aligned — mostly field mapping.
- **Zoho Projects** sync: Link Zoho Projects tasks to budget tracking. Log time as expense against the budget.
- **Zoho Books** sync: Push Invoices, Delivery Challans, POs, and Expenses to Zoho Books for accounting. Each new module was designed for 1:1 field mapping:
  - `Invoices` → Zoho Books Invoices (customer invoices)
  - `Delivery_Challans` → Zoho Books Delivery Challan
  - `Expenses` → Zoho Books Expenses
  - `Purchase_Orders` → Zoho Books Purchase Orders
  - `Vendors` → Zoho Books Contacts (with vendor type)
  - `Projects` → Zoho Books Projects (for project-based accounting)
  - Enables true "Invoiced" PO status, GST returns, and financial statements
- **Zoho Analytics**: For advanced dashboards beyond Zoho Creator Reports (drill-down, cross-filter, custom charts).

**Why Phase 1 in Zoho Creator alone is sufficient:**
- All modules share the same application, so lookups are fast with no API latency
- Zoho Creator Reports + Dashboards cover 90% of reporting needs
- You maintain full control over data and workflows without managing API auth
- The data model is already Zoho-Inventory-compatible — migration is a copy operation, not a redesign

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
| Forms to create | ~24 primary forms (Projects, Vendors, Vendor_Contacts, Vendor_Documents, Warehouses, Inventory_Items, Item_Warehouse_Stock, Item_Attributes, Budget_Plans, Budget_Components, Expenses, Budget_Approvals, Inventory_Transactions, Transfer_Orders, TO_Line_Items, Purchase_Requisitions, PR_Line_Items, Purchase_Orders, PO_Line_Items, Goods_Receipts, GRN_Line_Items, Invoices, Invoice_Line_Items, Delivery_Challans, DC_Line_Items, BOM, BOM_Line_Items) |
| Deluge workflows | ~23 (22 On Submit + 1 Scheduled Cron) |
| User roles | 6 (Admin, PM, Finance, Procurement, Inventory, Employee) |
| Lookup forms (most referenced) | Projects, Vendors, Inventory_Items, Warehouses |
| Seed data | "Main Warehouse" record, sample Budget Component categories |
| Critical performance rule | Maintain `Item_Warehouse_Stock.Current_Stock` via Deluge on every transaction — never aggregate on demand |

**Start with Phase 1A in Zoho Creator console: Vendors → Projects → Warehouses → Inventory_Items**
