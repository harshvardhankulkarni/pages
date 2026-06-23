# Phase 1E Build Guide — BOM → Delivery Challans → Invoicing

## Dependencies
Requires Phase 1D complete (Budget_Approvals, Purchase_Orders, Goods_Receipts, Transfer_Orders forms exist).

---

## 1.14 BOM — Bill of Materials (`BOM`)

### Field Configuration
| Label | Field Type | API Name | Required | Notes |
|---|---|---|---|---|
| BOM No | Auto Number | `BOM_No` | Yes | Format: `BOM-{0000}` |
| BOM Name | Single Line | `BOM_Name` | Yes | |
| Product Item | Lookup → Inventory_Items | `Product_Item` | Yes | The finished good |
| Quantity | Decimal | `Quantity` | No | Batch size (default 1) |
| Labor Cost | Currency | `Labor_Cost` | No | |
| Overhead Cost | Currency | `Overhead_Cost` | No | |
| Total Material Cost | Currency | `Total_Material_Cost` | No | Formula sum of components |
| Total Mfg Cost | Formula | `Total_Mfg_Cost` | — | `Total_Material_Cost + Labor_Cost + Overhead_Cost` |
| Status | Dropdown | `Status` | No | `Draft, Active, Archived` |
| Notes | Multi Line | `Notes` | No | |

### Embedded Subform: BOM Line Items (API Name: BOM_Line_Items)
| Label | Field Type | API Name | Required | Notes |
|---|---|---|---|---|
| Component Item | Lookup → Inventory_Items | `Component_Item` | Yes | |
| Quantity | Decimal | `Quantity` | Yes | Units of component per batch |
| Unit Cost | Currency | `Unit_Cost` | Yes | Copied from Item.Purchase_Price |
| Total Cost | Formula | `Total_Cost` | No (Formula) | `Quantity * Unit_Cost` |
| Notes | Multi Line | `Notes` | No | |

### Validation Rules
1. **At least one component** — On Submit, there must be at least one line item in the BOM_Line_Items subform.
2. **Quantity > 0** — All component quantities must be greater than 0.
3. **No duplicate components** — Same component item cannot appear twice in one BOM.

### Workflow Process

```
BOM Created (Status = Draft)
    │
    └── Submit
            │
            ├── For each line in embedded BOM_Line_Items:
            │       ├── Auto-fill Unit_Cost from Item.Purchase_Price
            │       └── Calculate Total_Cost = Quantity × Unit_Cost
            │
            ├── Sum all line Total_Cost → Total_Material_Cost
            ├── Total_Mfg_Cost = Total_Material_Cost + Labor_Cost + Overhead_Cost
            │
            └── BOM ready for manufacturing routing
```

### Deluge Scripts

#### On Submit — Calculate BOM Cost
```deluge
/* JUSTIFICATION: Processes embedded BOM_Line_Items subform data to calculate and update Total_Material_Cost on the parent BOM record. */
/* ===== PSEUDOCODE =====
   Trigger: On Submit — when BOM record is created or updated
   
   1. Access the embedded BOM_Line_Items subform data via input
   2. Initialize total_material cost to 0
   3. If line items exist:
      For each line item: calculate Unit_Cost × Quantity and add to total
   4. Build a data map with the calculated Total_Material_Cost
   5. Update the current BOM record with the calculated total
   6. Total_Mfg_Cost formula field auto-computes:
      Total_Material_Cost + Labor_Cost + Overhead_Cost
   ===== END PSEUDOCODE ===== */
bom_id = input.ID;
components = input.BOM_Line_Items;
total_material = 0;
if (!components.isNull())
{
    for each comp in components
    {
        unit_cost = ifnull(comp.get("Unit_Cost"), 0);
        qty = ifnull(comp.get("Quantity"), 0);
        total_material = total_material + (unit_cost * qty);
    }
}
bom_data = Map();
bom_data.put("Total_Material_Cost", total_material);
zoho.creator.updateRecord("budget_tracking", "BOM", bom_id, bom_data);
```
```

#### ~~REMOVED~~ BOM_Line_Items On Submit
> **REMOVED in Phase 1E:** Embedded subforms cannot have standalone On Submit scripts.
> Unit_Cost auto-fill from Item.Purchase_Price should be handled in the parent BOM's
> On Submit script or configured as a lookup mapping from the Component_Item field.

---

## 1.15 Delivery Challans (`Delivery_Challans`)

### Field Configuration
| Label | Field Type | API Name | Required | Notes |
|---|---|---|---|---|
| DC No | Auto Number | `DC_No` | Yes | Format: `DC-{0000}` |
| Project | Lookup → Projects | `Project` | Yes | |
| Account | Lookup → Accounts | `Account` | Yes | Client |
| DC Date | Date | `DC_Date` | No | Default today |
| Status | Dropdown | `Status` | No | `Draft, Shipped, Delivered, Returned` |
| Warehouse | Lookup → Warehouses | `Warehouse` | Yes | Source warehouse |
| Notes | Multi Line | `Notes` | No | |

### Embedded Subform: DC Line Items (API Name: DC_Line_Items)
| Label | Field Type | API Name | Required | Notes |
|---|---|---|---|---|
| Item | Lookup → Inventory_Items | `Item` | Yes | |
| Description | Single Line | `Description` | No | |
| Quantity | Decimal | `Quantity` | Yes | |
| Unit | Single Line | `Unit` | No | Formula: Item.Unit (auto-fills from selected Item) |
| Warehouse | Lookup → Warehouses | `Warehouse` | No | Override |

### Validation Rules
1. **Warehouse required for Shipped** — On Status = "Shipped", Warehouse must not be null.
2. **At least one line item** — On Status = "Shipped", at least one line item in the DC_Line_Items subform required.
3. **Sufficient stock** — On Status = "Shipped", validate available stock at the source warehouse per line item ≥ dispatch quantity.

### Workflow Process

```
DC Created (Status = Draft)
    │
    ├── Mark Shipped → Status = Shipped
    │       ├── Validate warehouse and stock
    │       ├── Use line item Warehouse (override) or fall back to parent Warehouse
    │       └── For each line item: Create Stock Out transaction
    │
    ├── Mark Delivered → Status = Delivered
    │       └── Carrier confirmed delivery
    │
    └── Mark Returned → Status = Returned
            └── Create Stock In transaction (reverse)
```

### Deluge Scripts

#### ~~REMOVED~~ DC_Line_Items On Submit
> **REMOVED in Phase 1E:** Embedded subforms cannot have standalone On Submit scripts.
> The Warehouse default-fill should be handled by setting a default value on the subform's
> Warehouse field (use formula: `DC.Warehouse` or configure as lookup default).

#### On Submit — Process Stock Deduction on Ship
```deluge
/* JUSTIFICATION: Processes embedded DC_Line_Items subform data to create Inventory_Transactions (Stock Out) when Delivery Challan status changes to "Shipped". */
/* ===== PSEUDOCODE =====
   Trigger: On Submit — when Delivery_Challan Status changes to "Shipped"
   
   1. Get the status display value from the current record
   2. If status is "Shipped":
      a. Get the parent Warehouse from the DC
      b. If warehouse is null: alert error — required before shipping
      c. Access the embedded DC_Line_Items subform data via input
      d. If line items exist:
         For each line item:
         i.   Get Item ID and Quantity
         ii.  If item is valid AND quantity is positive:
              - Determine warehouse: use line item's Warehouse override if set,
                otherwise fall back to the parent DC's Warehouse
              - Create "Stock Out" Inventory_Transaction:
                - Item and Warehouse as determined above
                - Quantity from the line item
                - Project from the DC
                - Date from DC_Date
                - Reference Type: "DC"
                - Reference ID: this DC's ID
   3. If status is not "Shipped": skip all processing
   ===== END PSEUDOCODE ===== */
status_val = ifnull(input.Status.toMap().get("display_value"), "");

if (status_val == "Shipped")
{
    parent_wh = input.Warehouse;

    if (parent_wh.isNull())
    {
        alert "Warehouse is required before shipping.";
    }
    
    dc_lines = input.DC_Line_Items;
    if (!dc_lines.isNull())
    {
        for each li in dc_lines
        {
            item_id = li.get("Item");
            qty = ifnull(li.get("Quantity"), 0);

            if (!item_id.isNull() && qty > 0)
            {
                li_wh = li.get("Warehouse");
                wh_id = ifnull(li_wh, parent_wh);

                txn_data = Map();
                txn_data.put("Transaction_Type", "Stock Out");
                txn_data.put("Item", item_id);
                txn_data.put("Warehouse", wh_id);
                txn_data.put("Quantity", qty);
                txn_data.put("Project", input.Project);
                txn_data.put("Transaction_Date", input.DC_Date);
                txn_data.put("Reference_Type", "DC");
                txn_data.put("Reference_ID", input.ID.toString());
                zoho.creator.createRecord("budget_tracking", "Inventory_Transactions", txn_data);
            }
        }
    }
}
```
```

---

## 1.16 Invoicing (`Invoices`)

### Field Configuration
| Label | Field Type | API Name | Required | Notes |
|---|---|---|---|---|
| Invoice No | Auto Number | `Invoice_No` | Yes | Format: `INV-{0000}` |
| Project | Lookup → Projects | `Project` | Yes | |
| Account | Lookup → Accounts | `Account` | Yes | Client |
| Invoice Date | Date | `Invoice_Date` | No | Default today |
| Due Date | Date | `Due_Date` | No | |
| Status | Dropdown | `Status` | No | `Draft, Sent, Partially Paid, Paid, Overdue, Cancelled` |
| Subtotal | Currency | `Subtotal` | No | Formula sum |
| Tax Total | Currency | `Tax_Total` | No | |
| Total | Currency | `Total` | No | `Subtotal + Tax` |
| Amount Paid | Currency | `Amount_Paid` | No | Updated by payment |
| Balance Due | Formula | `Balance_Due` | — | `Total - Amount_Paid` |
| Notes | Multi Line | `Notes` | No | |

### Embedded Subform: Invoice Line Items (API Name: Invoice_Line_Items)
| Label | Field Type | API Name | Required | Notes |
|---|---|---|---|---|
| Item | Lookup → Inventory_Items | `Item` | Yes | |
| Description | Single Line | `Description` | No | |
| Quantity | Decimal | `Quantity` | Yes | |
| Rate | Currency | `Rate` | Yes | |
| Discount Percent | Decimal | `Discount_Percent` | No | |
| Discount Amount | Formula | `Discount_Amount` | No (Formula) | `(Quantity * Rate) * (Discount_Percent / 100)` — Calculated discount amount |
| Tax Percent | Decimal | `Tax_Percent` | No | |
| Tax Amount | Formula | `Tax_Amount` | No (Formula) | `((Quantity * Rate) - Discount_Amount) * (Tax_Percent / 100)` — Calculated tax on net amount |
| Total | Formula | `Total` | No (Formula) | `(Quantity * Rate) - Discount_Amount + Tax_Amount` — Line total after discount and tax |

### Validation Rules
1. **At least one line item** — On Status = "Sent", at least one line item in the Invoice_Line_Items subform required.
2. **Due Date ≥ Invoice Date** — On Submit, Due_Date must be on or after Invoice_Date.
3. **Balance non-negative** — Balance_Due = Total − Amount_Paid must not be negative.
4. **Account required for Sent** — On Status = "Sent", Account must not be null.

### Workflow Process

```
Invoice Created (Status = Draft)
    │
    ├── Send to Client → Status = Sent
    │       ├── Update Project.Total_Invoiced
    │       └── Track for P&L calculation
    │
    ├── Partial Payment → Status = Partially Paid
    │       ├── Amount_Paid updated
    │       └── Balance_Due recalculated
    │
    ├── Full Payment → Status = Paid
    │       ├── Amount_Paid = Total
    │       └── Balance_Due = 0
    │
    ├── Due Date Passed (scheduled daily)
    │       └── Status = Overdue
    │
    └── Cancelled → Status = Cancelled
            └── No financial impact

**Custom Actions:**
| Button | Source Form | Action |
|---|---|---|
| Create Invoice | Projects | Opens Invoice form pre-filled with Project |
| Create DC | Invoices | Auto-creates Delivery Challan from line items |
```

### Deluge Scripts

#### Custom Action — Create Invoice from Project
```deluge
/* JUSTIFICATION: Custom action button that opens the Invoice form pre-filled with Project and Account context from the selected Project record. */
/* ===== PSEUDOCODE =====
   Trigger: Custom Action Button — when user clicks "Create Invoice" on Project form
   
   1. Get the current Project record's ID
   2. Fetch the full Project record by ID
   3. Extract the Account (client) ID and Project Name
   4. Open the Invoice form with pre-filled fields:
      - Project = current project ID (auto-filled by Zoho Creator param)
      - Account = project's linked account
   5. Note: Actual form opening is handled by Zoho Creator's
      custom action URL parameter configuration, not Deluge
   ===== END PSEUDOCODE ===== */
proj_id = input.ID;
proj = zoho.creator.getRecordById("budget_tracking", "Projects", proj_id);

account_id = proj.get("Account");
proj_name = ifnull(proj.get("Project_Name"), "");
```

#### On Status = Sent or Paid — Update Project Revenue Tracking
```deluge
/* JUSTIFICATION: On Submit workflow that queries invoices for a project and updates calculated revenue totals (Total_Invoiced_Calc, Total_Paid_Calc) on the Projects form. */
/* ===== PSEUDOCODE =====
   Trigger: On Submit — when Invoice Status changes to "Sent" or "Paid"
   Note: Invoice_Line_Items is an embedded subform; revenue totals
   are computed from Invoice-level fields, not from line items directly.
   
   1. Get the status display value and project ID from the current record
   2. If project is valid AND status is "Sent" or "Paid":
      a. Build criteria to find all non-cancelled invoices for this project
      b. Query Invoices matching the criteria (up to 200 records)
      c. For each invoice found:
         - Add Total to running total_invoiced sum
         - Add Amount_Paid to running total_paid sum
      d. Note: Project form stores Total_Invoiced_Calc, Total_Paid_Calc, 
         and Total_Expenses_Calc as formula/summary fields
      e. These fields auto-calculate from report summaries
      f. Actual P&L is computed via reports and dashboard widgets
   3. If no project or status is not Sent/Paid: skip all processing
   ===== END PSEUDOCODE ===== */
status_val = ifnull(input.Status.toMap().get("display_value"), "");
proj_id = input.Project;

if (!proj_id.isNull() && (status_val == "Sent" || status_val == "Paid"))
{
    inv_criteria = "Project == " + proj_id + " && (Status == 'Sent' || Status == 'Paid' || Status == 'Partially Paid')";
    project_invoices = zoho.creator.getRecords("budget_tracking", "Invoices", inv_criteria, 1, 200);

    total_invoiced = 0;
    total_paid = 0;
    if (!project_invoices.isNull())
    {
        for each inv in project_invoices
        {
            total_invoiced = total_invoiced + ifnull(inv.get("Total"), 0);
            total_paid = total_paid + ifnull(inv.get("Amount_Paid"), 0);
        }
    }
}
```

#### Custom Action — Create DC from Invoice
```deluge
/* JUSTIFICATION: Custom action button that creates a Delivery_Challan record with embedded DC_Line_Items copied from the Invoice's Invoice_Line_Items subform data. */
/* ===== PSEUDOCODE =====
   Trigger: Custom Action Button — when user clicks "Create DC" on Invoice form
   NOTE: Both Invoice_Line_Items and DC_Line_Items are embedded subforms.
   Line items are copied via embedded subform data maps, not via getRecords().
   
   1. Get the current Invoice ID and fetch the full Invoice record
   2. Build a new Delivery_Challan data map:
      a. Project: copied from the invoice
      b. Account: copied from the invoice
      c. Status: "Draft"
      d. Notes: reference the source invoice number
   3. Copy Invoice line items as embedded DC_Line_Items subform data
   4. Create the Delivery_Challan record (with embedded line items)
   ===== END PSEUDOCODE ===== */
inv_id = input.ID;
inv = zoho.creator.getRecordById("budget_tracking", "Invoices", inv_id);

dc_data = Map();
dc_data.put("Project", inv.get("Project"));
dc_data.put("Account", inv.get("Account"));
dc_data.put("Status", "Draft");
dc_data.put("Notes", "Auto-created from Invoice " + ifnull(input.Invoice_No, ""));

/* Copy Invoice line items as embedded DC_Line_Items subform data */
inv_lines = inv.get("Invoice_Line_Items");
if (!inv_lines.isNull())
{
    dc_line_items_list = List();
    for each li in inv_lines
    {
        dc_li = Map();
        dc_li.put("Item", li.get("Item"));
        dc_li.put("Description", li.get("Description"));
        dc_li.put("Quantity", li.get("Quantity"));
        dc_li.put("Unit", "Nos");
        dc_line_items_list.add(dc_li);
    }
    dc_data.put("DC_Line_Items", dc_line_items_list);
}

created_dc = zoho.creator.createRecord("budget_tracking", "Delivery_Challans", dc_data);
```
```

#### Scheduled Workflow — Mark Overdue Invoices
```deluge
/* JUSTIFICATION: Scheduled daily workflow that updates Invoice status to "Overdue" when Due_Date has passed and status is still "Sent". */
/* ===== PSEUDOCODE =====
   Trigger: Scheduled (Daily Midnight) — runs once per day
   
   1. Get today's date
   2. Build criteria: find all Invoices where Status = "Sent" AND
      Due_Date is before today (past due)
   3. Query matching invoices (up to 200 records)
   4. If overdue invoices found:
      For each invoice:
      a. Build a data map with Status = "Overdue"
      b. Update the invoice record
   5. If no overdue invoices: exit (nothing to update)
   ===== END PSEUDOCODE ===== */
today_date = today();
overdue_criteria = "Status == 'Sent' && Due_Date < '" + today_date.toString() + "'";
overdue_invs = zoho.creator.getRecords("budget_tracking", "Invoices", overdue_criteria, 1, 200);

if (!overdue_invs.isNull())
{
    for each inv in overdue_invs
    {
        inv_data = Map();
        inv_data.put("Status", "Overdue");
        zoho.creator.updateRecord("budget_tracking", "Invoices", inv.get("ID"), inv_data);
    }
}
```

#### Project Completed — Auto-create Final Invoice
```deluge
/* JUSTIFICATION: On Submit workflow that creates a final Invoice with embedded Invoice_Line_Items from uninvoiced DCs when a Project status changes to "Completed". */
/* ===== PSEUDOCODE =====
   Trigger: On Submit — when Project Status changes to "Completed"
   NOTE: Both DC_Line_Items and Invoice_Line_Items are embedded subforms.
   Line items are passed as subform data maps, not via separate getRecords/createRecord calls.
   
   1. Get the status display value from the current record
   2. If status is "Completed":
      a. Get the Project ID and Account ID from the current record
      b. If account exists:
         i.   Query all Delivery_Challans for this project (any status)
         ii.  If uninvoiced DCs exist:
              - Build Invoice_Line_Items list from all DC line items
              - Create a new Invoice record with embedded line items:
                Project = this project, Account = this account
                Status = "Draft", Notes = "auto-created on project completion"
                Invoice_Line_Items = built list (Rate = 0 for manual fill)
   3. If status is not "Completed" or no account linked: skip
   ===== END PSEUDOCODE ===== */
status_val = ifnull(input.Status.toMap().get("display_value"), "");

if (status_val == "Completed")
{
    proj_id = input.ID;
    account_id = input.Account;

    if (!account_id.isNull())
    {
        dc_criteria = "Project == " + proj_id;
        uninvoiced_dcs = zoho.creator.getRecords("budget_tracking", "Delivery_Challans", dc_criteria, 1, 200);

        if (!uninvoiced_dcs.isNull() && uninvoiced_dcs.size() > 0)
        {
            inv_data = Map();
            inv_data.put("Project", proj_id);
            inv_data.put("Account", account_id);
            inv_data.put("Status", "Draft");
            inv_data.put("Notes", "Final invoice - auto-created on project completion");

            inv_line_items_list = List();
            for each dc in uninvoiced_dcs
            {
                dc_lines = dc.get("DC_Line_Items");
                if (!dc_lines.isNull())
                {
                    for each dcli in dc_lines
                    {
                        inv_li = Map();
                        inv_li.put("Item", dcli.get("Item"));
                        inv_li.put("Description", dcli.get("Description"));
                        inv_li.put("Quantity", dcli.get("Quantity"));
                        inv_li.put("Rate", 0);
                        inv_line_items_list.add(inv_li);
                    }
                }
            }

            if (inv_line_items_list.size() > 0)
            {
                inv_data.put("Invoice_Line_Items", inv_line_items_list);
                created_inv = zoho.creator.createRecord("budget_tracking", "Invoices", inv_data);
            }
        }
    }
}
```
```

---

## Build Verification Checklist
1. Accounts form creates records with all fields saving correctly
2. Account Contacts subform adds contact persons
3. Account Documents subform uploads files
4. BOM creates BOM-0001, BOM-0002... with component costs calculated
5. BOM On Submit calculates Total_Material_Cost from embedded subform
6. Delivery Challans creates DC-0001, DC-0002...
7. DC Status = "Shipped" → auto-Stock Out for each line via embedded subform
8. Invoices creates INV-0001, INV-0002...
9. Invoice Status = "Overdue" set by scheduled workflow
10. Project Completed → auto-creates Invoice with uninvoiced DCs via embedded subform data
11. Invoice financial calculations (Subtotal, Discount, Tax, Total, Balance Due) correct

## Next Phase
→ Proceed to `PHASE_1F_BUILD.md` when all above forms are verified.
