# Phase 1K Build Guide — Customer Credit Notes + Manufacturing Orders + Sales Orders

## Dependencies
Requires Phase 1J complete (approval workflows, SoD, committed budget tracking). Phase 1K adds three modules that complete the 27-module architecture.

---

## 1. Customer Credit Notes (`Customer_Credit_Notes`)

### Module Type
New standalone form with embedded subform `CCN_Line_Items`. Mirrors Supplier Credit Notes on the AR side for customer returns/credit.

### Field Configuration — Main Form
| Label | Field Type | API Name | Required | Notes |
|---|---|---|---|---|
| CCN No | Auto Number | `CCN_No` | Yes | Format: `CCN-{0000}` |
| Account | Lookup → Accounts | `Account` | Yes | Customer receiving credit |
| Invoice Reference | Lookup → Invoices | `Invoice_Reference` | No | Link to original invoice |
| Original Invoice No | Text | `Original_Invoice_No` | No | Invoice number (in case not linked) |
| CCN Date | Date | `CCN_Date` | Yes | Date of credit note issuance |
| Reason | Dropdown | `Reason` | Yes | `Customer Return`, `Defective Goods`, `Service Credit`, `Price Adjustment`, `Goodwill`, `Other` |
| Reference No | Text | `Reference_No` | No | Customer's RMA or return reference |
| Subtotal | Currency | `Subtotal` | Yes | Sum of line item totals |
| Tax Total | Currency | `Tax_Total` | No | Total tax amount |
| Total Amount | Currency (Formula) | `Total_Amount` | No | `Subtotal + Tax_Total` — negative value, reduces AR |
| Status | Dropdown | `Status` | Yes | `Draft`, `Issued`, `Applied`, `Cancelled` |
| Notes | Multi Line | `Notes` | No | Additional notes |
| Attachment | Upload | `Attachment` | No | Supporting documents |

### Embedded Subform — `CCN_Line_Items`
| Label | Field Type | API Name | Required | Notes |
|---|---|---|---|---|
| Item | Lookup → Inventory_Items | `Item` | No | Optional — for goods returns |
| Description | Text | `Description` | No | Line item description |
| Quantity | Decimal | `Quantity` | No | Number of units returned |
| Unit Rate | Currency | `Unit_Rate` | Yes | Per-unit credit amount |
| Tax (%) | Decimal | `Tax_Pct` | No | Tax percentage |
| Tax Amount | Currency (Formula) | `Tax_Amount` | No | `(Quantity × Unit_Rate) × (Tax_Pct / 100)` |
| Line Total | Currency (Formula) | `Line_Total` | No | `(Quantity × Unit_Rate) + Tax_Amount` |

### Validation Rules
1. **Total > 0** — Total_Amount must be > 0 (credit note must reduce AR)
2. **At least one line item** — CCN_Line_Items must not be empty
3. **Invoice exists** — If Status = Issued or Applied, either Invoice_Reference or Original_Invoice_No must be provided
4. **Cancellation guard** — Cannot cancel if Status = Applied
5. **No duplicate CCN for same invoice+reason** — Optional warning

### Deluge Scripts

#### On Submit — Main Workflow
```deluge
/* JUSTIFICATION: Customer Credit Notes are a standalone finance form. Deluge handles:
   1) Invoice Balance Due reduction when status = Issued or Applied
   2) Inventory return transaction creation for goods returns
   3) CCN lifecycle status transitions
   4) Cancellation reversal of invoice adjustments
   These cross-form side effects cannot be handled by form-level validation. */

status_val = ifnull(input.Status.toMap().get("display_value"), "");
ccn_lines = input.CCN_Line_Items;
invoice_id = input.Invoice_Reference;

if (status_val == "Issued" && !invoice_id.isNull())
{
    /* ── Reduce Invoice Balance Due ── */
    inv_data = Map();
    current_paid = ifnull(invoice_id.Amount_Paid, 0);
    inv_total = ifnull(invoice_id.Total, 0);
    ccn_total = ifnull(input.Total_Amount, 0);

    /* Amount_Paid is effectively reduced by credit note */
    new_balance = inv_total - current_paid - ccn_total;
    inv_data.put("Balance_Due", max(new_balance, 0));
    inv_data.put("Credit_Note_Total", ifnull(invoice_id.Credit_Note_Total, 0) + ccn_total);
    zoho.creator.updateRecord("budget_tracking", "Invoices", invoice_id, inv_data);

    /* ── Inventory Handling for Goods Returns ── */
    if (!ccn_lines.isNull() && ccn_lines.size() > 0)
    {
        for each line in ccn_lines
        {
            item_id = line.get("Item");
            qty = ifnull(line.get("Quantity"), 0);

            if (!item_id.isNull() && qty > 0)
            {
                /* Create Return to Customer transaction (reverse of Stock Out) */
                return_data = Map();
                return_data.put("Transaction_Type", "Stock In");
                return_data.put("Item", item_id);
                return_data.put("Quantity", qty);
                return_data.put("Reference_Type", "CCN");
                return_data.put("Reference_No", input.CCN_No);
                return_data.put("Notes", "Customer return — CCN " + input.CCN_No);
                zoho.creator.createRecord("budget_tracking", "Inventory_Transactions", return_data);
            }
        }
    }

    /* Notification to Accounts Receivable team */
}

/* ── Applied — Credit fully utilized ── */
if (status_val == "Applied" && !invoice_id.isNull())
{
    /* CCN is fully applied against invoice — mark invoice accordingly */
    inv_data = Map();
    inv_data.put("Has_Credit_Note", true);
    zoho.creator.updateRecord("budget_tracking", "Invoices", invoice_id, inv_data);
}

/* ── Cancelled — Reverse Invoice Adjustments ── */
if (status_val == "Cancelled" && !invoice_id.isNull())
{
    if (input.Previous_Status == "Issued" || input.Previous_Status == "Applied")
    {
        inv_data = Map();
        ccn_total = ifnull(input.Total_Amount, 0);
        inv_data.put("Credit_Note_Total", max(ifnull(invoice_id.Credit_Note_Total, 0) - ccn_total, 0));
        zoho.creator.updateRecord("budget_tracking", "Invoices", invoice_id, inv_data);
    }
}
```

---

## 2. Manufacturing Orders (`Manufacturing_Orders`)

### Module Type
New standalone form with embedded subform `MO_Components`. Governs the manufacturing lifecycle from raw material reservation through finished goods receipt.

### Field Configuration — Main Form
| Label | Field Type | API Name | Required | Notes |
|---|---|---|---|---|
| MO No | Auto Number | `MO_No` | Yes | Format: `MO-{0000}` |
| Production Item | Lookup → Inventory_Items | `Production_Item` | Yes | The finished good being produced |
| BOM Reference | Lookup → BOM | `BOM_Reference` | No | Bill of Materials governing this run |
| Project | Lookup → Projects | `Project` | No | Optional project link |
| Warehouse (Output) | Lookup → Warehouses | `Output_Warehouse` | Yes | Where finished goods are received |
| Quantity to Produce | Decimal | `Qty_To_Produce` | Yes | Target production quantity |
| Date Released | Date | `Date_Released` | No | When MO was released to production |
| Date Completed | Date | `Date_Completed` | No | When manufacturing finished |
| Status | Dropdown | `Status` | Yes | `Draft`, `Released`, `In Progress`, `Completed`, `Cancelled` |
| Notes | Multi Line | `Notes` | No | Production notes |

### Embedded Subform — `MO_Components`
| Label | Field Type | API Name | Required | Notes |
|---|---|---|---|---|
| Component Item | Lookup → Inventory_Items | `Component_Item` | Yes | Raw material or sub-assembly |
| Required Qty | Decimal | `Required_Qty` | Yes | Qty needed per BOM × production qty |
| Reserved Qty | Decimal | `Reserved_Qty` | No | Qty reserved for this MO |
| Consumed Qty | Decimal | `Consumed_Qty` | No | Qty actually consumed on completion |
| Unit Cost | Currency | `Unit_Cost` | No | Cost at time of consumption |
| Line Cost | Currency (Formula) | `Line_Cost` | No | `Consumed_Qty × Unit_Cost` |

### Validation Rules
1. **Production Item ≠ Component Items** — Cannot produce an item that is also listed as a component (prevents circular BOM references)
2. **At least one component** — MO_Components must not be empty
3. **Qty > 0** — Quantity to Produce must be > 0
4. **Stock availability on Release** — Check each component's available stock >= Required Qty
5. **Status transition guard** — Only Draft→Released→In Progress→Completed or Cancelled (no skipping)

### Deluge Scripts

#### On Submit — Main Workflow
```deluge
/* JUSTIFICATION: Manufacturing Orders orchestrate multi-step inventory transactions.
   Release reserves stock, Complete issues components and receives finished goods.
   Status-based side effects and stock validation cannot be handled by form-level rules. */

status_val = ifnull(input.Status.toMap().get("display_value"), "");
mo_components = input.MO_Components;
output_wh = input.Output_Warehouse;
prod_item = input.Production_Item;
qty = ifnull(input.Qty_To_Produce, 0);

/* ── Draft → Released — Reserve Components ── */
if (status_val == "Released")
{
    if (mo_components.isNull() || mo_components.size() == 0)
    {
        alert "MO must have at least one component.";
        return;
    }

    for each comp in mo_components
    {
        comp_item = comp.get("Component_Item");
        req_qty = ifnull(comp.get("Required_Qty"), 0);

        if (!comp_item.isNull() && req_qty > 0)
        {
            /* Check stock availability */
            stock_available = checkComponentStock(comp_item, req_qty);
            if (!stock_available)
            {
                alert "Insufficient stock for component: " + comp_item.get("Item_Name").toString() + ". Required: " + req_qty.toString();
                return;
            }

            /* Reserve stock: create Reservation transaction */
            reserve_data = Map();
            reserve_data.put("Transaction_Type", "Reservation");
            reserve_data.put("Item", comp_item);
            reserve_data.put("Quantity", req_qty);
            reserve_data.put("Reference_Type", "MO");
            reserve_data.put("Reference_No", input.MO_No);
            reserve_data.put("Notes", "MO reservation — " + input.MO_No);
            zoho.creator.createRecord("budget_tracking", "Inventory_Transactions", reserve_data);

            /* Update Reserved_Qty in MO_Components */
            comp.put("Reserved_Qty", req_qty);
        }
    }

    /* Set Date Released */
    mo_data = Map();
    mo_data.put("Date_Released", today());
    mo_data.put("MO_Components", mo_components);
    zoho.creator.updateRecord("budget_tracking", "Manufacturing_Orders", input.ID, mo_data);
}

/* ── Completed — Issue Components + Receive Finished Goods ── */
if (status_val == "Completed")
{
    /* Process each component: Stock Out */
    for each comp in mo_components
    {
        comp_item = comp.get("Component_Item");
        req_qty = ifnull(comp.get("Required_Qty"), 0);

        if (!comp_item.isNull() && req_qty > 0)
        {
            /* Stock Out — issue materials to production */
            issue_data = Map();
            issue_data.put("Transaction_Type", "Stock Out");
            issue_data.put("Item", comp_item);
            issue_data.put("Quantity", req_qty);
            issue_data.put("Reference_Type", "MO");
            issue_data.put("Reference_No", input.MO_No);
            issue_data.put("Notes", "MO component issuance — " + input.MO_No);
            zoho.creator.createRecord("budget_tracking", "Inventory_Transactions", issue_data);

            comp.put("Consumed_Qty", req_qty);
        }
    }

    /* Stock In — receive finished goods */
    if (!prod_item.isNull() && qty > 0 && !output_wh.isNull())
    {
        finish_data = Map();
        finish_data.put("Transaction_Type", "Stock In");
        finish_data.put("Item", prod_item);
        finish_data.put("Warehouse", output_wh);
        finish_data.put("Quantity", qty);
        finish_data.put("Reference_Type", "MO");
        finish_data.put("Reference_No", input.MO_No);
        finish_data.put("Notes", "MO finished goods receipt — " + input.MO_No);
        zoho.creator.createRecord("budget_tracking", "Inventory_Transactions", finish_data);
    }

    /* Set Date Completed */
    mo_data = Map();
    mo_data.put("Date_Completed", today());
    mo_data.put("MO_Components", mo_components);
    zoho.creator.updateRecord("budget_tracking", "Manufacturing_Orders", input.ID, mo_data);
}

/* ── Cancelled — Release Reserved Stock ── */
if (status_val == "Cancelled")
{
    if (!mo_components.isNull() && mo_components.size() > 0)
    {
        for each comp in mo_components
        {
            reserved_qty = ifnull(comp.get("Reserved_Qty"), 0);
            comp_item = comp.get("Component_Item");

            if (!comp_item.isNull() && reserved_qty > 0)
            {
                release_data = Map();
                release_data.put("Transaction_Type", "Release");
                release_data.put("Item", comp_item);
                release_data.put("Quantity", reserved_qty);
                release_data.put("Reference_Type", "MO");
                release_data.put("Reference_No", input.MO_No);
                zoho.creator.createRecord("budget_tracking", "Inventory_Transactions", release_data);

                comp.put("Reserved_Qty", 0);
            }
        }

        mo_data = Map();
        mo_data.put("MO_Components", mo_components);
        zoho.creator.updateRecord("budget_tracking", "Manufacturing_Orders", input.ID, mo_data);
    }
}

/* ── Helper: checkComponentStock ── */
function checkComponentStock(item, required_qty)
{
    item_rec = zoho.creator.getRecordById("budget_tracking", "Inventory_Items", item);
    if (!item_rec.isNull())
    {
        current = ifnull(item_rec.get("Current_Stock"), 0);
        return current >= required_qty;
    }
    return false;
}
```

---

## 3. Sales Orders (`Sales_Orders`)

### Module Type
New standalone form with embedded subform `SO_Line_Items`. Optional module — service-only businesses can skip and create Invoices directly.

### Field Configuration — Main Form
| Label | Field Type | API Name | Required | Notes |
|---|---|---|---|---|
| SO No | Auto Number | `SO_No` | Yes | Format: `SO-{0000}` |
| Account | Lookup → Accounts | `Account` | Yes | Customer placing the order |
| Project | Lookup → Projects | `Project` | No | Optional project link |
| SO Date | Date | `SO_Date` | Yes | Order received date |
| Delivery Date | Date | `Delivery_Date` | No | Requested delivery date |
| Payment Terms | Dropdown | `Payment_Terms` | No | Copied from Account |
| Currency | Dropdown | `Currency` | No | Copied from Account |
| Subtotal | Currency | `Subtotal` | No | Sum of line item totals |
| Discount (%) | Decimal | `Discount_Pct` | No | Overall order discount % |
| Discount Amount | Currency (Formula) | `Discount_Amount` | No | `Subtotal × (Discount_Pct / 100)` |
| Tax Total | Currency | `Tax_Total` | No | Sum of line item taxes |
| Total Amount | Currency (Formula) | `Total_Amount` | No | `Subtotal − Discount_Amount + Tax_Total` |
| Amount Invoiced | Currency | `Amount_Invoiced` | No | Total invoiced so far |
| Balance to Invoice | Currency (Formula) | `Balance_To_Invoice` | No | `Total_Amount − Amount_Invoiced` |
| Status | Dropdown | `Status` | Yes | `Draft`, `Confirmed`, `In Progress`, `Shipped`, `Invoiced`, `Completed`, `Cancelled` |
| Notes | Multi Line | `Notes` | No | Order notes |
| Attachment | Upload | `Attachment` | No | Customer PO or order document |

### Embedded Subform — `SO_Line_Items`
| Label | Field Type | API Name | Required | Notes |
|---|---|---|---|---|
| Item | Lookup → Inventory_Items | `Item` | No | Product or service |
| Description | Text | `Description` | No | Line description |
| Quantity | Decimal | `Quantity` | Yes | Order qty |
| Unit Rate | Currency | `Unit_Rate` | Yes | Per-unit price |
| Discount (%) | Decimal | `Discount_Pct` | No | Line-level discount |
| Discount Amount | Currency (Formula) | `Discount_Amount` | No | `(Quantity × Unit_Rate) × (Discount_Pct / 100)` |
| Tax (%) | Decimal | `Tax_Pct` | No | Tax percentage |
| Tax Amount | Currency (Formula) | `Tax_Amount` | No | `((Quantity × Unit_Rate) − Discount_Amount) × (Tax_Pct / 100)` |
| Line Total | Currency (Formula) | `Line_Total` | No | `(Quantity × Unit_Rate) − Discount_Amount + Tax_Amount` |
| Delivered Qty | Decimal | `Delivered_Qty` | No | Updated by DC creation |
| Invoiced Qty | Decimal | `Invoiced_Qty` | No | Updated by Invoice creation |

### Custom Action Buttons
1. **Create Invoice** — Creates Invoice from SO line items (uninvoiced qty only)
2. **Create DC** — Creates Delivery Challan from SO line items (undelivered qty only)

### Validation Rules
1. **At least one line item** — SO_Line_Items must not be empty
2. **Total > 0** — Total_Amount must be > 0
3. **Cancellation guard** — Cannot cancel if any line has Delivered_Qty > 0 or Invoiced_Qty > 0
4. **Delivery Date after SO Date** — Validation check

### Deluge Scripts

#### On Submit — Main Workflow
```deluge
/* JUSTIFICATION: Sales Orders is a standalone order management form. Deluge handles:
   1) Status transitions and guard conditions
   2) Integration with Inventory (stock reservation on Confirm)
   3) Custom action buttons for Invoice/DC creation
   4) Cancellation guard against partial fulfillment
   These cross-form orchestration requirements cannot be handled by form-level validation. */

status_val = ifnull(input.Status.toMap().get("display_value"), "");
so_lines = input.SO_Line_Items;

/* ── Draft → Confirmed — Reserve Stock ── */
if (status_val == "Confirmed" && !so_lines.isNull())
{
    for each line in so_lines
    {
        item_id = line.get("Item");
        qty = ifnull(line.get("Quantity"), 0);

        if (!item_id.isNull() && qty > 0)
        {
            reserve_data = Map();
            reserve_data.put("Transaction_Type", "Reservation");
            reserve_data.put("Item", item_id);
            reserve_data.put("Quantity", qty);
            reserve_data.put("Reference_Type", "SO");
            reserve_data.put("Reference_No", input.SO_No);
            zoho.creator.createRecord("budget_tracking", "Inventory_Transactions", reserve_data);
        }
    }
}

/* ── Shipped — Create Stock Out for each line ── */
if (status_val == "Shipped")
{
    if (!so_lines.isNull())
    {
        for each line in so_lines
        {
            item_id = line.get("Item");
            qty = ifnull(line.get("Quantity"), 0);
            delivered = ifnull(line.get("Delivered_Qty"), 0);
            remaining = qty - delivered;

            if (!item_id.isNull() && remaining > 0)
            {
                issue_data = Map();
                issue_data.put("Transaction_Type", "Stock Out");
                issue_data.put("Item", item_id);
                issue_data.put("Quantity", remaining);
                issue_data.put("Reference_Type", "SO");
                issue_data.put("Reference_No", input.SO_No);
                zoho.creator.createRecord("budget_tracking", "Inventory_Transactions", issue_data);

                line.put("Delivered_Qty", qty);
            }
        }

        so_data = Map();
        so_data.put("SO_Line_Items", so_lines);
        zoho.creator.updateRecord("budget_tracking", "Sales_Orders", input.ID, so_data);
    }
}

/* ── Cancelled — Release Reserved Stock ── */
if (status_val == "Cancelled" && !so_lines.isNull())
{
    for each line in so_lines
    {
        item_id = line.get("Item");
        qty = ifnull(line.get("Quantity"), 0);
        delivered = ifnull(line.get("Delivered_Qty"), 0);
        invoiced = ifnull(line.get("Invoiced_Qty"), 0);

        if (delivered > 0 || invoiced > 0)
        {
            alert "Cannot cancel. Line item has " + delivered.toString() + " delivered and " + invoiced.toString() + " invoiced.";
            return;
        }

        if (!item_id.isNull() && qty > 0)
        {
            release_data = Map();
            release_data.put("Transaction_Type", "Release");
            release_data.put("Item", item_id);
            release_data.put("Quantity", qty);
            release_data.put("Reference_Type", "SO");
            release_data.put("Reference_No", input.SO_No);
            zoho.creator.createRecord("budget_tracking", "Inventory_Transactions", release_data);
        }
    }
}
```

#### Custom Button — Create Invoice
```deluge
/* JUSTIFICATION: Custom action button creates an Invoice from uninvoiced SO line items.
   Must calculate remaining qty per line and create corresponding Invoice_Line_Items.
   This is a standalone button action, not a form submit workflow. */

so_id = input.ID;
so_lines = input.SO_Line_Items;
so_account = input.Account;
so_project = input.Project;

if (so_lines.isNull() || so_lines.size() == 0)
{
    alert "No line items to invoice.";
    return;
}

invoice_lines = List();
has_remaining = false;

for each line in so_lines
{
    qty = ifnull(line.get("Quantity"), 0);
    invoiced = ifnull(line.get("Invoiced_Qty"), 0);
    remaining = qty - invoiced;

    if (remaining > 0)
    {
        inv_line = Map();
        inv_line.put("Item", line.get("Item"));
        inv_line.put("Description", ifnull(line.get("Description"), ""));
        inv_line.put("Quantity", remaining);
        inv_line.put("Unit_Rate", ifnull(line.get("Unit_Rate"), 0));
        inv_line.put("Discount_Pct", ifnull(line.get("Discount_Pct"), 0));
        inv_line.put("Tax_Pct", ifnull(line.get("Tax_Pct"), 0));
        invoice_lines.add(inv_line);
        has_remaining = true;
    }
}

if (!has_remaining)
{
    alert "All line items already invoiced.";
    return;
}

/* Create Invoice */
inv_data = Map();
inv_data.put("Account", so_account);
inv_data.put("Project", so_project);
inv_data.put("Invoice_Date", today());
inv_data.put("Due_Date", today().addDays(30));
inv_data.put("Status", "Draft");
inv_data.put("Invoice_Line_Items", invoice_lines);
new_inv = zoho.creator.createRecord("budget_tracking", "Invoices", inv_data);

/* Update SO_Line_Items with invoiced quantities */
if (!new_inv.isNull())
{
    for each line in so_lines
    {
        qty = ifnull(line.get("Quantity"), 0);
        invoiced = ifnull(line.get("Invoiced_Qty"), 0);
        line.put("Invoiced_Qty", qty);
    }

    so_data = Map();
    so_data.put("SO_Line_Items", so_lines);
    zoho.creator.updateRecord("budget_tracking", "Sales_Orders", input.ID, so_data);

    /* Navigate to the new Invoice */
    openUrl(new_inv.get("URL"));
}
```

#### Custom Button — Create DC
```deluge
/* JUSTIFICATION: Custom action button creates a Delivery Challan from undelivered SO line items.
   Must calculate remaining qty and create corresponding DC_Line_Items. */

so_id = input.ID;
so_lines = input.SO_Line_Items;
so_account = input.Account;
so_project = input.Project;

if (so_lines.isNull() || so_lines.size() == 0)
{
    alert "No line items to deliver.";
    return;
}

dc_lines = List();
has_remaining = false;

for each line in so_lines
{
    qty = ifnull(line.get("Quantity"), 0);
    delivered = ifnull(line.get("Delivered_Qty"), 0);
    remaining = qty - delivered;

    if (remaining > 0)
    {
        dc_line = Map();
        dc_line.put("Item", line.get("Item"));
        dc_line.put("Description", ifnull(line.get("Description"), ""));
        dc_line.put("Quantity", remaining);
        dc_lines.add(dc_line);
        has_remaining = true;
    }
}

if (!has_remaining)
{
    alert "All line items already delivered.";
    return;
}

dc_data = Map();
dc_data.put("Account", so_account);
dc_data.put("Project", so_project);
dc_data.put("Status", "Draft");
dc_data.put("DC_Line_Items", dc_lines);
new_dc = zoho.creator.createRecord("budget_tracking", "Delivery_Challans", dc_data);

if (!new_dc.isNull())
{
    for each line in so_lines
    {
        qty = ifnull(line.get("Quantity"), 0);
        line.put("Delivered_Qty", qty);
    }

    so_data = Map();
    so_data.put("SO_Line_Items", so_lines);
    zoho.creator.updateRecord("budget_tracking", "Sales_Orders", input.ID, so_data);

    openUrl(new_dc.get("URL"));
}
```

---

## 4. Reports

| Report | Type | Source | Audience |
|--------|------|--------|----------|
| Customer Credit Notes Register | Tabular | Customer_Credit_Notes | AR Clerk, AR Manager |
| Outstanding CCNs | Tabular (filter: Status ≠ Applied/Cancelled) | Customer_Credit_Notes | AR Manager |
| Manufacturing Orders Register | Tabular | Manufacturing_Orders | Production Manager |
| Open Manufacturing Orders | Tabular (filter: Status ≠ Completed/Cancelled) | Manufacturing_Orders | Production Manager |
| Sales Orders Register | Tabular | Sales_Orders | Sales Team |
| SO Backlog | Tabular (filter: Status = Confirmed/In Progress) | Sales_Orders | Sales Team |
| Completed Sales Orders | Tabular (filter: Status = Completed) | Sales_Orders | Management |
| CCN Impact on Invoicing | Summary by Account | Customer_Credit_Notes + Invoices | Finance Manager |
| Production Cost Summary | Summary by MO | Manufacturing_Orders | Production Manager |

---

## Verification Checklist

- [ ] CCN auto-number CCN-0001 works
- [ ] CCN Issued reduces Invoice Balance Due
- [ ] CCN Issued with goods items creates Stock In (Return to Customer) for each line
- [ ] CCN Applied marks Invoice with Has_Credit_Note = true
- [ ] CCN Cancelled reverses invoice adjustments
- [ ] CCN validation: Total > 0 required
- [ ] CCN validation: at least one line item required
- [ ] MO auto-number MO-0001 works
- [ ] MO Released creates Reservation transactions for all components
- [ ] MO Released validates stock availability before reserving
- [ ] MO Completed creates Stock Out (issue) for each component
- [ ] MO Completed creates Stock In for finished goods
- [ ] MO Cancelled releases all reserved stock
- [ ] MO validation: Production Item ≠ Component Item
- [ ] MO validation: at least one component required
- [ ] SO auto-number SO-0001 works
- [ ] SO Confirmed reserves stock
- [ ] SO Shipped creates Stock Out
- [ ] SO "Create Invoice" button creates Invoice with uninvoiced line items
- [ ] SO "Create DC" button creates DC with undelivered line items
- [ ] SO Cancelled releases reserved stock
- [ ] SO Cancellation blocked if any line has delivered/invoiced qty
- [ ] Count of SO_Line_Items.Delivered_Qty / Invoiced_Qty updated correctly
- [ ] All reports render with correct data
