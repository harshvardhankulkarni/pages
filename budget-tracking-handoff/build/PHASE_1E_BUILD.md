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

### Subforms (Add-as-Subform)

**BOM Line Items** — Form: `BOM_Line_Items`
| Label | Field Type | API Name | Notes |
|---|---|---|---|
| BOM | Lookup → BOM | `BOM` | |
| Component Item | Lookup → Inventory_Items | `Component_Item` | |
| Quantity | Decimal | `Quantity` | Units of component per batch |
| Unit Cost | Currency | `Unit_Cost` | Copied from Item.Purchase_Price |
| Total Cost | Formula | `Total_Cost` | `Quantity * Unit_Cost` |
| Notes | Single Line | `Notes` | |

### Deluge Scripts

#### On Submit — Calculate BOM Cost
```deluge
/* Phase 1E — BOM: On Submit
   Calculate Total Material Cost from components */
bom_id = input.ID;
li_criteria = "BOM == " + bom_id;
components = zoho.creator.getRecords("budget_tracking", "BOM_Line_Items", li_criteria, 1, 200);

total_material = 0;
if (!components.isNull())
{
    for each comp in components
    {
        total_material = total_material + ifnull(comp.get("Total_Cost"), 0);
    }
}

bom_data = Map();
bom_data.put("Total_Material_Cost", total_material);
zoho.creator.updateRecord("budget_tracking", "BOM", bom_id, bom_data);
```

#### On BOM Line Item Submit — Auto-fill Unit Cost
```deluge
/* Phase 1E — BOM_Line_Items: On Submit
   Auto-fill Unit_Cost from Item.Purchase_Price */
item_id = input.Component_Item;
if (!item_id.isNull())
{
    item = zoho.creator.getRecordById("budget_tracking", "Inventory_Items", item_id);
    if (!item.isNull())
    {
        purchase_price = ifnull(item.get("Purchase_Price"), 0);
        li_data = Map();
        li_data.put("Unit_Cost", purchase_price);
        zoho.creator.updateRecord("budget_tracking", "BOM_Line_Items", input.ID, li_data);
    }
}
```

---

## 1.15 Delivery Challans (`Delivery_Challans`)

### Field Configuration
| Label | Field Type | API Name | Required | Notes |
|---|---|---|---|---|
| DC No | Auto Number | `DC_No` | Yes | Format: `DC-{0000}` |
| Invoice | Lookup → Invoices | `Invoice` | No | Linked invoice |
| Project | Lookup → Projects | `Project` | Yes | |
| Account | Lookup → Vendors | `Account` | Yes | Client/vendor |
| DC Date | Date | `DC_Date` | No | Default today |
| Status | Dropdown | `Status` | No | `Draft, Shipped, Delivered, Returned` |
| Warehouse | Lookup → Warehouses | `Warehouse` | Yes | Source warehouse |
| Notes | Multi Line | `Notes` | No | |

### Subforms (Add-as-Subform)

**DC Line Items** — Form: `DC_Line_Items`
| Label | Field Type | API Name | Notes |
|---|---|---|---|
| DC | Lookup → Delivery_Challans | `DC` | |
| Item | Lookup → Inventory_Items | `Item` | |
| Description | Single Line | `Description` | |
| Quantity | Decimal | `Quantity` | |
| Unit | Single Line | `Unit` | Copied from Item |
| Warehouse | Lookup → Warehouses | `Warehouse` | Override |

### Deluge Scripts

#### On Submit — Process Stock Deduction on Ship
```deluge
/* Phase 1E — Delivery_Challans: On Submit
   When Status = "Shipped", auto-create Stock Out for each line item */
status_val = ifnull(input.Status.toMap().get("display_value"), "");

if (status_val == "Shipped")
{
    wh_id = input.Warehouse;
    dc_id = input.ID;

    if (wh_id.isNull())
    {
        throw "Warehouse is required before shipping.";
    }

    li_criteria = "DC == " + dc_id;
    dc_lines = zoho.creator.getRecords("budget_tracking", "DC_Line_Items", li_criteria, 1, 200);

    if (!dc_lines.isNull())
    {
        for each li in dc_lines
        {
            item_id = li.get("Item");
            qty = ifnull(li.get("Quantity"), 0);

            if (!item_id.isNull() && qty > 0)
            {
                /* Create Stock Out transaction */
                txn_data = Map();
                txn_data.put("Transaction_Type", "Stock Out");
                txn_data.put("Item", item_id);
                txn_data.put("Warehouse", wh_id);
                txn_data.put("Quantity", qty);
                txn_data.put("Project", input.Project);
                txn_data.put("Transaction_Date", input.DC_Date);
                txn_data.put("Reference_Type", "DC");
                txn_data.put("Reference_ID", dc_id.toString());
                zoho.creator.createRecord("budget_tracking", "Inventory_Transactions", txn_data);
            }
        }
    }
}
```

---

## 1.16 Invoicing (`Invoices`)

### Field Configuration
| Label | Field Type | API Name | Required | Notes |
|---|---|---|---|---|
| Invoice No | Auto Number | `Invoice_No` | Yes | Format: `INV-{0000}` |
| Project | Lookup → Projects | `Project` | Yes | |
| Account | Lookup → Vendors | `Account` | Yes | Client |
| Invoice Date | Date | `Invoice_Date` | No | Default today |
| Due Date | Date | `Due_Date` | No | |
| Payment Terms | Dropdown | `Payment_Terms` | No | `Due on Receipt, Net 15, Net 30, Net 45` |
| Status | Dropdown | `Status` | No | `Draft, Sent, Partially Paid, Paid, Overdue, Cancelled` |
| Subtotal | Currency | `Subtotal` | No | Formula sum |
| Discount % | Decimal | `Discount_Pct` | No | |
| Discount Amount | Currency | `Discount_Amount` | No | |
| Tax Total | Currency | `Tax_Total` | No | |
| Total | Currency | `Total` | No | `Subtotal - Discount + Tax` |
| Amount Paid | Currency | `Amount_Paid` | No | Updated by payment |
| Balance Due | Formula | `Balance_Due` | — | `Total - Amount_Paid` |
| Notes | Multi Line | `Notes` | No | |
| Terms | Multi Line | `Terms` | No | |

### Subforms (Add-as-Subform)

**Invoice Line Items** — Form: `Invoice_Line_Items`
| Label | Field Type | API Name | Notes |
|---|---|---|---|
| Invoice | Lookup → Invoices | `Invoice` | |
| Item | Lookup → Inventory_Items | `Item` | |
| Description | Single Line | `Description` | |
| Quantity | Decimal | `Quantity` | |
| Rate | Currency | `Rate` | |
| Discount % | Decimal | `Discount_Pct` | |
| Discount Amount | Formula | `Discount_Amount` | |
| Tax % | Decimal | `Tax_Pct` | |
| Tax Amount | Formula | `Tax_Amount` | |
| Total | Formula | `Total` | |
| Project | Lookup → Projects | `Project` | Per-line project |

### Deluge Scripts

#### Custom Action — Create Invoice from Project
```deluge
/* Phase 1E — Projects Custom Action: Create Invoice
   Pre-fills Invoice form with Project details */
/* This runs when user clicks "Create Invoice" button on Project */
proj_id = input.ID;
proj = zoho.creator.getRecordById("budget_tracking", "Projects", proj_id);

account_id = proj.get("Account");
proj_name = ifnull(proj.get("Project_Name"), "");

/* Open invoice form with pre-filled data */
/* Handled by Zoho Creator custom action URL params */
```

#### On Status = Sent — Update Project Revenue Tracking
```deluge
/* Phase 1E — Invoices: On Submit
   Track revenue when invoice is sent */
status_val = ifnull(input.Status.toMap().get("display_value"), "");

if (status_val == "Sent" && !input.Project.isNull())
{
    /* Update project invoice totals (Phase 1E — placeholder for P&L) */
    /* Full P&L aggregation handled in reports */
}

/* Auto-create DC from Invoice (custom button) */
/* This is handled by a custom action button on Invoice form */
```

#### Custom Action — Create DC from Invoice
```deluge
/* Phase 1E — Invoices Custom Action: Create Delivery Challan
   Copies Invoice line items to new DC */
inv_id = input.ID;
inv = zoho.creator.getRecordById("budget_tracking", "Invoices", inv_id);

dc_data = Map();
dc_data.put("Invoice", inv_id);
dc_data.put("Project", inv.get("Project"));
dc_data.put("Account", inv.get("Account"));
dc_data.put("Status", "Draft");
dc_data.put("Notes", "Auto-created from Invoice " + ifnull(input.Invoice_No, ""));

created_dc = zoho.creator.createRecord("budget_tracking", "Delivery_Challans", dc_data);

if (!created_dc.isNull())
{
    dc_id = created_dc.get("ID");

    /* Copy invoice line items to DC line items */
    li_criteria = "Invoice == " + inv_id;
    inv_lines = zoho.creator.getRecords("budget_tracking", "Invoice_Line_Items", li_criteria, 1, 200);

    if (!inv_lines.isNull())
    {
        for each li in inv_lines
        {
            dc_li = Map();
            dc_li.put("DC", dc_id);
            dc_li.put("Item", li.get("Item"));
            dc_li.put("Description", li.get("Description"));
            dc_li.put("Quantity", li.get("Quantity"));
            dc_li.put("Unit", "Nos");
            zoho.creator.createRecord("budget_tracking", "DC_Line_Items", dc_li);
        }
    }
}
```

#### Scheduled Workflow — Mark Overdue Invoices
```deluge
/* Phase 1E — Scheduled (Daily Midnight)
   Mark overdue invoices */
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
/* Phase 1E — Projects: On Submit (Status = "Completed")
   Auto-create Invoice for unbilled items */
status_val = ifnull(input.Status.toMap().get("display_value"), "");

if (status_val == "Completed")
{
    proj_id = input.ID;
    account_id = input.Account;

    if (!account_id.isNull())
    {
        /* Check if there are any Delivery Challans not yet invoiced */
        dc_criteria = "Project == " + proj_id + " && Invoice == NULL";
        uninvoiced_dcs = zoho.creator.getRecords("budget_tracking", "Delivery_Challans", dc_criteria, 1, 200);

        if (!uninvoiced_dcs.isNull() && uninvoiced_dcs.size() > 0)
        {
            /* Create final invoice */
            inv_data = Map();
            inv_data.put("Project", proj_id);
            inv_data.put("Account", account_id);
            inv_data.put("Status", "Draft");
            inv_data.put("Notes", "Final invoice - auto-created on project completion");

            created_inv = zoho.creator.createRecord("budget_tracking", "Invoices", inv_data);

            if (!created_inv.isNull())
            {
                inv_id = created_inv.get("ID");

                for each dc in uninvoiced_dcs
                {
                    /* Link DC to this invoice */
                    dc_data = Map();
                    dc_data.put("Invoice", inv_id);
                    zoho.creator.updateRecord("budget_tracking", "Delivery_Challans", dc.get("ID"), dc_data);

                    /* Copy DC line items to Invoice line items */
                    dc_li_criteria = "DC == " + dc.get("ID");
                    dc_lines = zoho.creator.getRecords("budget_tracking", "DC_Line_Items", dc_li_criteria, 1, 200);

                    if (!dc_lines.isNull())
                    {
                        for each dcli in dc_lines
                        {
                            inv_li = Map();
                            inv_li.put("Invoice", inv_id);
                            inv_li.put("Item", dcli.get("Item"));
                            inv_li.put("Description", dcli.get("Description"));
                            inv_li.put("Quantity", dcli.get("Quantity"));
                            inv_li.put("Rate", 0); /* Rate to be filled by user */
                            zoho.creator.createRecord("budget_tracking", "Invoice_Line_Items", inv_li);
                        }
                    }
                }
            }
        }
    }
}
```

---

## Build Verification Checklist
1. BOM creates BOM-0001, BOM-0002... with component costs calculated
2. BOM Line Items auto-fill Unit_Cost from Item.Purchase_Price
3. Delivery Challans creates DC-0001, DC-0002...
4. DC Status = "Shipped" → auto-Stock Out for each line
5. Invoices creates INV-0001, INV-0002...
6. Invoice Status = "Overdue" set by scheduled workflow
7. Custom button "Create DC from Invoice" copies line items correctly
8. Project Completed → auto-creates Invoice with uninvoiced DCs
9. Invoice financial calculations (Subtotal, Discount, Tax, Total, Balance Due) correct

## Next Phase
→ Proceed to `PHASE_1F_BUILD.md` when all above forms are verified.
