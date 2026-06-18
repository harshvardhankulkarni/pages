# Phase 1D Build Guide — Budget Approvals → Purchase Orders → Goods Receipts → Transfer Orders

## Dependencies
Requires Phase 1C complete (Expenses, Purchase_Requisitions forms exist).

---

## 1.10 Budget Approvals Form (`Budget_Approvals`)

Tracks overrun approval requests. Auto-created by Expense workflow.

### Field Configuration
| Label | Field Type | API Name | Required | Notes |
|---|---|---|---|---|
| Approval No | Auto Number | `Approval_No` | Yes | Format: `APPR-{0000}` |
| Expense | Lookup → Expenses | `Expense` | Yes | Source expense |
| Project | Lookup → Projects | `Project` | Yes | |
| Budget Component | Lookup → Budget_Components | `Budget_Component` | Yes | |
| Requested Amount | Currency | `Requested_Amount` | Yes | Original expense amount |
| Excess Amount | Currency | `Excess_Amount` | Yes | Overrun amount |
| Utilization % | Decimal | `Utilization_Pct` | No | Current utilization |
| Justification | Multi Line | `Justification` | No | From expense |
| Status | Dropdown | `Status` | No | `Pending, Approved, Rejected` |
| Approved By | User Picker | `Approved_By` | No | |
| Approval Date | Date | `Approval_Date` | No | |
| Remarks | Multi Line | `Remarks` | No | |

### Validation Rules
1. **Cannot approve without Expense** — On Submit, if Status = "Approved" or "Rejected", Expense field must not be null.
2. **Status change only from Pending** — Only records with Status = "Pending" can be updated to "Approved" or "Rejected".

### Approval Process

```
Overrun Expense Submitted
    │
    └── Budget_Approval auto-created (Status = "Pending")
            │
            ├── PM / Finance Manager approves
            │       ├── Expense Status → "Approved"
            │       ├── Budget_Component.Spent_Amount → incremented
            │       └── Approval_Date + Approved_By recorded
            │
            └── PM / Finance Manager rejects
                    ├── Expense Status → "Rejected"
                    └── Submitter notified
```

### Deluge Scripts

#### On Status = Approved — Update Expense + Budget
```deluge
/* Phase 1D — Budget_Approvals: On Submit
   When overrun is approved, update expense and budget component */
status_val = ifnull(input.Status.toMap().get("display_value"), "");
expense_id = input.Expense;
comp_id = input.Budget_Component;

if (status_val == "Approved" && !expense_id.isNull())
{
    /* Approve the expense */
    exp_data = Map();
    exp_data.put("Status", "Approved");
    zoho.creator.updateRecord("budget_tracking", "Expenses", expense_id, exp_data);

    /* Update Budget Component spent amount */
    if (!comp_id.isNull())
    {
        comp = zoho.creator.getRecordById("budget_tracking", "Budget_Components", comp_id);
        if (!comp.isNull())
        {
            current_spent = ifnull(comp.get("Spent_Amount"), 0);
            expense_amount = ifnull(input.Requested_Amount, 0);
            comp_data = Map();
            comp_data.put("Spent_Amount", current_spent + expense_amount);
            zoho.creator.updateRecord("budget_tracking", "Budget_Components", comp_id, comp_data);
        }
    }

    /* Record approval */
    appr_data = Map();
    appr_data.put("Approval_Date", today());
    appr_data.put("Approved_By", zoho.login.getCurrentUserID());
    zoho.creator.updateRecord("budget_tracking", "Budget_Approvals", input.ID, appr_data);
}

if (status_val == "Rejected" && !expense_id.isNull())
{
    /* Reject the expense */
    exp_data = Map();
    exp_data.put("Status", "Rejected");
    zoho.creator.updateRecord("budget_tracking", "Expenses", expense_id, exp_data);

    /* Notify submitter */
    /* zoho.creator.sendMail("user@company.com",
        "Expense Rejected",
        "Your expense has been rejected due to budget overrun being denied."); */
}
```

---

## 1.11 Purchase Orders Form (`Purchase_Orders`)

1:1 aligned with Zoho Books PO API. See `IMPLEMENTATION_PLAN.md` for full field mapping.

### Field Configuration
| Label | Field Type | API Name | Required | Notes |
|---|---|---|---|---|
| PO Number | Auto Number | `PO_Number` | Yes | Format: `PO-{0000}` |
| Vendor | Lookup → Vendors | `Vendor` | Yes | |
| Vendor Email | Email | `Vendor_Email` | No | Convenience |
| Contact Person | Lookup → Vendor_Contacts | `Contact_Person` | No | Books `contact_persons_associated` |
| Requisition | Lookup → Purchase_Requisitions | `Requisition` | No | Linked if from PR |
| Project | Lookup → Projects | `Project` | No | |
| PO Date | Date | `PO_Date` | No | Default today |
| Delivery Date | Date | `Delivery_Date` | No | |
| Expected Arrival | Date | `Expected_Arrival` | No | |
| Due Date | Date | `Due_Date` | No | Payment due |
| Reference Number | Single Line | `Reference_Number` | No | Vendor contract ref |
| Ship Via | Dropdown | `Ship_Via` | No | `Courier, Freight, Air, Sea, Road, Pickup` |
| Attention | Single Line | `Attention` | No | |
| Billing Address | Multi Line | `Billing_Address` | No | |
| Shipping Address | Multi Line | `Shipping_Address` | No | |
| Status | Dropdown | `Status` | No | `Draft, Open, Partially Invoiced, Billed, Closed, Cancelled` |
| Currency | Dropdown | `Currency` | No | Default base |
| Exchange Rate | Decimal | `Exchange_Rate` | No | Default 1 |
| Is Inclusive Tax | Checkbox | `Is_Inclusive_Tax` | No | |
| Subtotal | Currency | `Subtotal` | No | Formula sum |
| Discount | Decimal | `Discount` | No | % or flat |
| Discount Account | Lookup → Chart_of_Accounts | `Discount_Account` | No | |
| Discount Before Tax | Checkbox | `Discount_Before_Tax` | No | |
| Discount Amount | Currency | `Discount_Amount` | No | Formula |
| Tax Total | Currency | `Tax_Total` | No | Formula sum |
| Total | Currency | `Total` | No | Formula |
| Terms | Multi Line | `Terms` | No | Printed on PO |
| Notes | Multi Line | `Notes` | No | Internal |
| Attachment | Upload | `Attachment` | No | |
| Location | Lookup → Warehouses | `Location` | No | Books `location_id` |
| GST Treatment | Dropdown | `GST_Treatment` | No | `business_gst, consumer_gst` |
| GST No | Single Line | `GST_No` | No | Vendor GSTIN |
| Source of Supply | Single Line | `Source_Of_Supply` | No | GST state code |
| Destination of Supply | Single Line | `Destination_Of_Supply` | No | GST state code |
| Reverse Charge | Checkbox | `Reverse_Charge` | No | |
| Custom Fields | Multi Line | `Custom_Fields` | No | JSON |

### Subforms (Add-as-Subform)

**PO Line Items** — Form: `PO_Line_Items`
| Label | Field Type | API Name | Notes |
|---|---|---|---|
| PO | Lookup → Purchase_Orders | `PO` | |
| Item | Lookup → Inventory_Items | `Item` | |
| SKU | Single Line | `SKU` | Auto fill |
| Name | Single Line | `Name` | Auto fill |
| Description | Single Line | `Description` | |
| Unit | Single Line | `Unit` | |
| HSN/SAC | Single Line | `HSN_SAC` | |
| Quantity | Decimal | `Quantity` | |
| Unit Rate | Currency | `Unit_Rate` | |
| BCY Rate | Currency | `BCY_Rate` | Base currency rate |
| Account | Lookup → Chart_of_Accounts | `Account` | |
| Discount % | Decimal | `Discount_Pct` | Line-level |
| Discount Amount | Formula | `Discount_Amount` | |
| Tax % | Decimal | `Tax_Pct` | Default from Item |
| Tax ID | Lookup | `Tax_ID` | |
| Tax Amount | Formula | `Tax_Amount` | |
| Item Total | Formula | `Item_Total` | |
| Tax Exemption | Single Line | `Tax_Exemption` | |
| TDS Tax | Single Line | `TDS_Tax` | |
| Received Quantity | Decimal | `Received_Quantity` | GRN updates |
| Warehouse | Lookup → Warehouses | `Warehouse` | Receipt location |
| Product Type | Dropdown | `Product_Type` | `goods, service, digital` |
| Item Order | Number | `Item_Order` | |
| Project | Lookup → Projects | `Project` | Per-line tracking |

### Validation Rules
1. **Cannot cancel with linked GRNs** — On Status = "Cancelled", check for Goods_Receipts linked to this PO. If found, throw error.
2. **Open requires Vendor** — On Status = "Open", Vendor field must not be null.
3. **At least one line item** — On Status = "Open" or "Closed", there must be at least one PO_Line_Item.

### Approval Process (PO Lifecycle)

```
PO Created (Status = Draft)
    │
    ├── Send to Vendor → Status = Open
    │       ├── Email PO PDF to vendor
    │       └── Inventory expected
    │
    ├── Goods Received → Status = Open (stays Open)
    │       ├── GRN creates Stock In
    │       ├── PO_Line_Item.Received_Quantity updated
    │       └── All received? → Auto-Close
    │
    ├── Partially Invoiced → Status = Partially Invoiced
    │       └── Some line items billed
    │
    ├── Fully Invoiced → Status = Billed
    │       └── All line items billed
    │
    ├── All received + invoiced → Status = Closed
    │
    └── Cancel (if no GRNs) → Status = Cancelled
```

**State Transitions:**
| From | To | Condition |
|---|---|---|
| Draft | Open | User sends PO |
| Open | Partially Invoiced | Some line items invoiced |
| Open / Partially Invoiced | Billed | All line items invoiced |
| Open / Partially Invoiced / Billed | Closed | All items received + invoiced |
| Draft / Open | Cancelled | No linked GRNs |
| Any | Closed | Scheduled auto-close (30 days after fully received) |

### Deluge Scripts

#### On Submit — PO Open Workflow
```deluge
/* Phase 1D — Purchase_Orders: On Submit
   When Status = "Open", send email to vendor with PO details */
status_val = ifnull(input.Status.toMap().get("display_value"), "");
po_no = ifnull(input.PO_Number, "");
vendor_id = input.Vendor;

if (status_val == "Open" && !vendor_id.isNull())
{
    vendor = zoho.creator.getRecordById("budget_tracking", "Vendors", vendor_id);
    if (!vendor.isNull())
    {
        vendor_email = ifnull(vendor.get("Email"), "");
        if (vendor_email != "")
        {
            email_body = "Dear Sir/Madam,\n\n"
                + "Please find our Purchase Order " + po_no + " dated "
                + ifnull(input.PO_Date.toString(), today().toString()) + ".\n\n"
                + "Total Amount: " + ifnull(input.Total, 0).toString() + "\n\n"
                + "Kindly acknowledge receipt and confirm delivery schedule.\n\n"
                + "Terms: " + ifnull(input.Terms, "As agreed") + "\n\n"
                + "Thank you.\nProcurement Team";

            /* zoho.creator.sendMail(vendor_email,
                "Purchase Order: " + po_no, email_body); */
        }
    }
}

/* Validate cancellation */
if (status_val == "Cancelled")
{
    /* Check for linked GRNs */
    criteria = "PO == " + input.ID;
    grns = zoho.creator.getRecords("budget_tracking", "Goods_Receipts", criteria, 1, 10);
    if (!grns.isNull() && grns.size() > 0)
    {
        throw "Cannot cancel PO: " + grns.size().toString() + " Goods Receipt(s) are linked.";
    }
}
```

---

## 1.12 Goods Receipt (GRN) Form (`Goods_Receipts`)

### Field Configuration
| Label | Field Type | API Name | Required | Notes |
|---|---|---|---|---|
| GRN Number | Auto Number | `GRN_Number` | Yes | Format: `GRN-{0000}` |
| PO | Lookup → Purchase_Orders | `PO` | Yes | |
| Vendor | Lookup → Vendors | `Vendor` | No | Auto-filled from PO |
| Receipt Date | Date | `Receipt_Date` | No | Defaults to today |
| Received By | User Picker | `Received_By` | No | |
| Status | Dropdown | `Status` | No | `Draft, Open, Closed` |

### Subforms (Add-as-Subform)

**GRN Line Items** — Form: `GRN_Line_Items`
| Label | Field Type | API Name | Notes |
|---|---|---|---|
| GRN | Lookup → Goods_Receipts | `GRN` | |
| PO Line Item | Lookup → PO_Line_Items | `PO_Line_Item` | |
| Item | Lookup → Inventory_Items | `Item` | Auto-filled |
| PO Quantity | Decimal | `PO_Quantity` | From PO line |
| Accepted Quantity | Decimal | `Accepted_Quantity` | |
| Rejected Quantity | Decimal | `Rejected_Quantity` | |
| Rejection Reason | Single Line | `Rejection_Reason` | Required if Rejected > 0 |
| Actual Unit Cost | Currency | `Actual_Unit_Cost` | Editable |
| Warehouse | Lookup → Warehouses | `Warehouse` | Destination |

### Validation Rules
1. **Accepted + Rejected ≤ PO Quantity** — On Submit, validate `Accepted_Quantity + Rejected_Quantity ≤ PO_Quantity` for each line.
2. **Rejection Reason required** — If `Rejected_Quantity > 0`, `Rejection_Reason` must not be empty.
3. **PO must be Open** — GRN can only be created against POs with Status = "Open".
4. **Warehouse required for accepted items** — If `Accepted_Quantity > 0`, Warehouse must be set.

### Workflow Process

```
GRN Created (Status = Draft)
    │
    └── Submit (Status → Open)
            │
            ├── For each line item with Accepted_Quantity > 0:
            │       ├── Create Stock In transaction
            │       ├── Update PO_Line_Item.Received_Quantity
            │       └── Alert if partial receipt
            │
            ├── For each line with Rejected_Quantity > 0:
            │       └── Log rejection reason for vendor return
            │
            └── All PO line items fully received?
                    ├── Yes → Auto-close PO (Status = Closed)
                    └── No  → PO stays Open
```

### Deluge Scripts

#### On Submit — Process GRN
```deluge
/* Phase 1D — Goods_Receipts: On Submit
   When Status = "Open", process accepted/rejected quantities */
status_val = ifnull(input.Status.toMap().get("display_value"), "");
po_id = input.PO;

if (status_val == "Open" && !po_id.isNull())
{
    po_line_criteria = "PO == " + po_id;
    po_lines = zoho.creator.getRecords("budget_tracking", "PO_Line_Items", po_line_criteria, 1, 200);

    /* Get GRN line items */
    grn_li_criteria = "GRN == " + input.ID;
    grn_lines = zoho.creator.getRecords("budget_tracking", "GRN_Line_Items", grn_li_criteria, 1, 200);

    all_received = true;

    if (!grn_lines.isNull())
    {
        for each grn_li in grn_lines
        {
            accepted = ifnull(grn_li.get("Accepted_Quantity"), 0);
            rejected = ifnull(grn_li.get("Rejected_Quantity"), 0);
            item_id = grn_li.get("Item");
            wh_id = grn_li.get("Warehouse");

            /* Update PO Line Item - Received Quantity */
            po_li_id = grn_li.get("PO_Line_Item");
            if (!po_li_id.isNull())
            {
                po_li = zoho.creator.getRecordById("budget_tracking", "PO_Line_Items", po_li_id);
                if (!po_li.isNull())
                {
                    current_received = ifnull(po_li.get("Received_Quantity"), 0);
                    po_data = Map();
                    po_data.put("Received_Quantity", current_received + accepted);
                    zoho.creator.updateRecord("budget_tracking", "PO_Line_Items", po_li_id, po_data);
                }
            }

            /* Stock In for accepted items */
            if (accepted > 0 && !item_id.isNull() && !wh_id.isNull())
            {
                txn_data = Map();
                txn_data.put("Transaction_Type", "Stock In");
                txn_data.put("Item", item_id);
                txn_data.put("Warehouse", wh_id);
                txn_data.put("Quantity", accepted);
                txn_data.put("Transaction_Date", input.Receipt_Date);
                txn_data.put("Reference_Type", "GRN");
                txn_data.put("Reference_ID", input.ID.toString());

                /* Get unit cost from GRN line item or PO line */
                actual_cost = ifnull(grn_li.get("Actual_Unit_Cost"), 0);
                if (actual_cost > 0)
                {
                    txn_data.put("Unit_Rate", actual_cost);
                }

                inv_txn = zoho.creator.createRecord("budget_tracking", "Inventory_Transactions", txn_data);
            }

            /* Check if this PO line item is fully received */
            if (!po_li_id.isNull())
            {
                po_li = zoho.creator.getRecordById("budget_tracking", "PO_Line_Items", po_li_id);
                if (!po_li.isNull())
                {
                    po_qty = ifnull(po_li.get("Quantity"), 0);
                    recv_qty = ifnull(po_li.get("Received_Quantity"), 0);
                    if (recv_qty < po_qty)
                    {
                        all_received = false;
                    }
                }
            }
        }
    }

    /* Auto-close PO if all items fully received */
    if (all_received)
    {
        po_data = Map();
        po_data.put("Status", "Closed");
        zoho.creator.updateRecord("budget_tracking", "Purchase_Orders", po_id, po_data);
    }
}
```

---

## 1.13 Transfer Orders Form (`Transfer_Orders`)

### Field Configuration
| Label | Field Type | API Name | Required | Notes |
|---|---|---|---|---|
| Transfer No | Auto Number | `Transfer_No` | Yes | Format: `TO-{0000}` |
| From Warehouse | Lookup → Warehouses | `From_Warehouse` | Yes | |
| To Warehouse | Lookup → Warehouses | `To_Warehouse` | Yes | |
| Transfer Date | Date | `Transfer_Date` | No | Default today |
| Status | Dropdown | `Status` | No | `Draft, Open, Completed, Cancelled` |
| Notes | Multi Line | `Notes` | No | |

### Subforms (Add-as-Subform)

**TO Line Items** — Form: `TO_Line_Items`
| Label | Field Type | API Name |
|---|---|---|
| Transfer Order | Lookup → Transfer_Orders | `Transfer_Order` |
| Item | Lookup → Inventory_Items | `Item` |
| Quantity | Decimal | `Quantity` |
| Warehouse | Lookup → Warehouses | `Warehouse` |

### Validation Rules
1. **Different warehouses** — From_Warehouse and To_Warehouse must be different.
2. **At least one line item** — On Status = "Completed", at least one TO_Line_Item required.
3. **Sufficient stock** — On Status = "Completed", validate `From_Warehouse` has enough stock for each item.

### Workflow Process

```
TO Created (Status = Draft)
    │
    └── Mark Completed → Status = Completed
            │
            ├── Validate From ≠ To Warehouse
            ├── Sync each TO_Line_Item.Warehouse → From_Warehouse
            ├── Validate stock availability at From_Warehouse
            │
            └── For each line item:
                    ├── Stock Out at From_Warehouse
                    └── Stock In at To_Warehouse
```

### Deluge Scripts

#### TO_Line_Items On Submit — Sync Warehouse with Parent
```deluge
/* Phase 1D — TO_Line_Items: On Submit
   Auto-fill Warehouse from parent Transfer_Order.From_Warehouse for consistency */
to_id = input.Transfer_Order;
if (!to_id.isNull())
{
    to_record = zoho.creator.getRecordById("budget_tracking", "Transfer_Orders", to_id);
    if (!to_record.isNull())
    {
        from_wh = to_record.get("From_Warehouse");
        if (!from_wh.isNull())
        {
            li_data = Map();
            li_data.put("Warehouse", from_wh);
            zoho.creator.updateRecord("budget_tracking", "TO_Line_Items", input.ID, li_data);
        }
    }
}
```

#### On Submit — Process Transfer Completion
```deluge
/* Phase 1D — Transfer_Orders: On Submit
   When Status = "Completed", generate paired Stock Out / Stock In transactions */
status_val = ifnull(input.Status.toMap().get("display_value"), "");

if (status_val == "Completed")
{
    from_wh = input.From_Warehouse;
    to_wh = input.To_Warehouse;

    if (from_wh.isNull() || to_wh.isNull())
    {
        throw "Both From and To Warehouse are required.";
    }

    /* Get TO line items */
    li_criteria = "Transfer_Order == " + input.ID;
    to_lines = zoho.creator.getRecords("budget_tracking", "TO_Line_Items", li_criteria, 1, 200);

    if (!to_lines.isNull())
    {
        for each li in to_lines
        {
            /* Sync subform Warehouse with parent From_Warehouse for consistency */
            li_id = li.get("ID");
            li_wh = li.get("Warehouse");
            if (li_wh != from_wh)
            {
                li_data = Map();
                li_data.put("Warehouse", from_wh);
                zoho.creator.updateRecord("budget_tracking", "TO_Line_Items", li_id, li_data);
            }

            item_id = li.get("Item");
            qty = ifnull(li.get("Quantity"), 0);

            if (!item_id.isNull() && qty > 0)
            {
                /* Stock Out from source */
                out_data = Map();
                out_data.put("Transaction_Type", "Stock Out");
                out_data.put("Item", item_id);
                out_data.put("Warehouse", from_wh);
                out_data.put("Quantity", qty);
                out_data.put("Transaction_Date", input.Transfer_Date);
                out_data.put("Reference_Type", "TO");
                out_data.put("Reference_ID", input.ID.toString());
                out_data.put("Notes", "Transfer to " + to_wh.toString());
                zoho.creator.createRecord("budget_tracking", "Inventory_Transactions", out_data);

                /* Stock In at destination */
                in_data = Map();
                in_data.put("Transaction_Type", "Stock In");
                in_data.put("Item", item_id);
                in_data.put("Warehouse", to_wh);
                in_data.put("Quantity", qty);
                in_data.put("Transaction_Date", input.Transfer_Date);
                in_data.put("Reference_Type", "TO");
                in_data.put("Reference_ID", input.ID.toString());
                in_data.put("Notes", "Transfer from " + from_wh.toString());
                zoho.creator.createRecord("budget_tracking", "Inventory_Transactions", in_data);
            }
        }
    }
}
```

---

## Build Verification Checklist
1. Budget_Approvals auto-creates on expense overrun
2. Approving Budget_Approval updates Expense status + Budget Component spent
3. Purchase Orders creates PO-0001, PO-0002...
4. PO Status = "Open" triggers vendor email notification
5. PO Status = "Cancelled" blocked if GRNs exist
6. PR → auto-PO copies line items correctly
7. Goods Receipt (GRN) creates GRN-0001, GRN-0002...
8. GRN Open → Stock In transaction created for accepted items
9. GRN updates PO_Line_Item.Received_Quantity
10. All items received → PO auto-closes
11. Transfer Orders creates TO-0001, TO-0002...
12. TO Completed → paired Stock Out/In transactions

## Next Phase
→ Proceed to `PHASE_1E_BUILD.md` when all above forms are verified.
