# Phase 1D Build Guide — Budget Approvals → Purchase Orders → Goods Receipts → Supplier Credit Notes → Transfer Orders

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
/* JUSTIFICATION: Approve/reject cascade updates Expense status and Budget_Component Spent_Amount across forms — cannot be handled by embedded subform submission */
/* ===== PSEUDOCODE =====
   Trigger: On Submit — when Budget_Approval Status changes to Approved or Rejected
   
   1. Get the status display value, expense ID, and component ID
   
   CASE A — Status is "Approved" AND expense exists:
      a. Update the linked Expense record Status to "Approved"
      b. If budget component is linked:
         - Fetch the Budget_Component record
         - Get current Spent_Amount
         - Add the Requested_Amount from the approval
         - Update Spent_Amount with the new total
      c. Record approval metadata:
         - Set Approval_Date to today
         - Set Approved_By to the current logged-in user
   
   CASE B — Status is "Rejected" AND expense exists:
      a. Update the linked Expense record Status to "Rejected"
      b. (Placeholder) Send rejection email notification to submitter
   
   3. If status is neither Approved nor Rejected: skip all actions
   ===== END PSEUDOCODE ===== */
status_val = ifnull(input.Status.toMap().get("display_value"), "");
expense_id = input.Expense;
comp_id = input.Budget_Component;

if (status_val == "Approved" && !expense_id.isNull())
{
    exp_data = Map();
    exp_data.put("Status", "Approved");
    zoho.creator.updateRecord("budget_tracking", "Expenses", expense_id, exp_data);

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

    appr_data = Map();
    appr_data.put("Approval_Date", today());
    appr_data.put("Approved_By", zoho.login.getCurrentUserID());
    zoho.creator.updateRecord("budget_tracking", "Budget_Approvals", input.ID, appr_data);
}

if (status_val == "Rejected" && !expense_id.isNull())
{
    exp_data = Map();
    exp_data.put("Status", "Rejected");
    zoho.creator.updateRecord("budget_tracking", "Expenses", expense_id, exp_data);
}
```

---

## 1.11 Purchase Orders Form (`Purchase_Orders`)

### Field Configuration
| Label | Field Type | API Name | Required | Notes |
|---|---|---|---|---|
| PO Number | Auto Number | `PO_Number` | Yes | Format: `PO-{0000}` |
| Vendor | Lookup → Vendors | `Vendor` | Yes | |
| Requisition | Lookup → Purchase_Requisitions | `Requisition` | No | Linked if from PR |
| Project | Lookup → Projects | `Project` | No | |
| PO Date | Date | `PO_Date` | No | Default today |
| Delivery Date | Date | `Delivery_Date` | No | |
| Due Date | Date | `Due_Date` | No | Payment due |
| Reference Number | Single Line | `Reference_Number` | No | Vendor contract ref |
| Status | Dropdown | `Status` | No | `Draft, Open, Partially Invoiced, Billed, Closed, Cancelled` |
| Subtotal | Currency | `Subtotal` | No | Formula sum |
| Discount | Decimal | `Discount` | No | % or flat |
| Discount Amount | Currency | `Discount_Amount` | No | Formula |
| Tax Total | Currency | `Tax_Total` | No | Formula sum |
| Total | Currency | `Total` | No | Formula |
| Terms | Multi Line | `Terms` | No | Printed on PO |
| Notes | Multi Line | `Notes` | No | Internal |
| Attachment | Upload | `Attachment` | No | |

### Embedded Subform: PO Line Items (API Name: PO_Line_Items)

| Label | Field Type | API Name | Required | Notes |
|---|---|---|---|---|
| Item | Lookup → Inventory_Items | `Item` | Yes | |
| Description | Single Line | `Description` | No | |
| Unit | Single Line | `Unit` | No | |
| HSN/SAC | Single Line | `HSN_SAC` | No | |
| Quantity | Decimal | `Quantity` | Yes | |
| Unit Rate | Currency | `Unit_Rate` | Yes | |
| Discount % | Decimal | `Discount_Percent` | No | Line-level |
| Discount Amount | Formula | `Discount_Amount` | No | Formula: (Discount_Percent / 100) * (Quantity * Unit_Rate) |
| Tax % | Decimal | `Tax_Percent` | No | Default from Item |
| Tax Amount | Formula | `Tax_Amount` | No | Formula: ((Quantity * Unit_Rate - Discount_Amount) * (Tax_Percent / 100)) |
| Item Total | Formula | `Item_Total` | No | Formula: (Quantity * Unit_Rate) + Tax_Amount - Discount_Amount |

### Validation Rules
1. **Cannot cancel with linked GRNs** — On Status = "Cancelled", check for Goods_Receipts linked to this PO. If found, alert error.
2. **Open requires Vendor** — On Status = "Open", Vendor field must not be null.
3. **At least one line item** — On Status = "Open" or "Closed", there must be at least one PO_Line_Items.

### Approval Process (PO Lifecycle)

```
PO Created (Status = Draft)
    │
    ├── Send to Vendor → Status = Open
    │       ├── Email PO PDF to vendor
    │       └── Inventory expected
    │
    ├── Goods Received → GRN created
    │       └── GRN creates Stock In transaction
    │
    ├── Partially Invoiced → Status = Partially Invoiced
    │       └── Some line items billed
    │
    ├── Fully Invoiced → Status = Billed
    │
    ├── All items received → Status = Closed (manual)
    │
    └── Cancel (if no GRNs) → Status = Cancelled
```

**State Transitions:**
| From | To | Condition |
|---|---|---|
| Draft | Open | User sends PO |
| Open | Partially Invoiced | Some line items invoiced |
| Open / Partially Invoiced | Billed | All line items invoiced |
| Open / Partially Invoiced / Billed | Closed | Manual close after all items received |
| Draft / Open | Cancelled | No linked GRNs |

### Deluge Scripts

#### On Submit — PO Open Workflow
```deluge
/* JUSTIFICATION: Vendor email notification and cancellation guard with GRN check require standalone form processing */
/* ===== PSEUDOCODE =====
   Trigger: On Submit — when Purchase_Order Status changes
   
   CASE A — Status changed to "Open" AND vendor is linked:
      a. Fetch the Vendor record by ID
      b. If vendor exists and has an email:
         - Build email body with PO number, date, total amount, and terms
         - (Placeholder) Send PO notification email to vendor
   
   CASE B — Status changed to "Cancelled":
      a. Query Goods_Receipts linked to this PO
      b. If any GRNs exist: alert error with count — cannot cancel
      c. If no GRNs: allow cancellation
   
   3. If status is neither "Open" nor "Cancelled": skip all actions
   ===== END PSEUDOCODE ===== */
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
        }
    }
}

if (status_val == "Cancelled")
{
    criteria = "PO == " + input.ID;
    grns = zoho.creator.getRecords("budget_tracking", "Goods_Receipts", criteria, 1, 10);
    if (!grns.isNull() && grns.size() > 0)
    {
        alert "Cannot cancel PO: " + grns.size().toString() + " Goods Receipt(s) are linked.";
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
| Receipt Date | Date | `Receipt_Date` | No | Defaults to today |
| Received By | User Picker | `Received_By` | No | |
| Status | Dropdown | `Status` | No | `Draft, Open, Closed` |

### Embedded Subform: GRN Line Items (API Name: GRN_Line_Items)

| Label | Field Type | API Name | Required | Notes |
|---|---|---|---|---|
| Item | Lookup → Inventory_Items | `Item` | Yes | Auto-filled |
| PO Quantity | Decimal | `PO_Quantity` | No | Copied from PO (Read Only) |
| Accepted Quantity | Decimal | `Accepted_Quantity` | No | |
| Rejected Quantity | Decimal | `Rejected_Quantity` | No | |
| Reason for Rejection | Single Line | `Reason_for_Rejection` | No | Required if Rejected > 0 |
| Actual Unit Cost | Currency | `Actual_Unit_Cost` | No | Editable |
| Warehouse | Lookup → Warehouses | `Warehouse` | No | Destination |
| Total | Formula | `Total` | No | Formula: Accepted_Quantity * Actual_Unit_Cost |
| Condition Notes | Multi Line | `Condition_Notes` | No | Goods condition notes upon receipt |

### Validation Rules
1. **Accepted + Rejected ≤ PO Quantity** — On Submit, validate `Accepted_Quantity + Rejected_Quantity ≤ PO_Quantity` for each line.
2. **Reason for Rejection required** — If `Rejected_Quantity > 0`, `Reason_for_Rejection` must not be empty.
3. **PO must be Open** — GRN can only be created against POs with Status = "Open".
4. **Warehouse required for accepted items** — If `Accepted_Quantity > 0`, Warehouse must be set.

### Workflow Process

```
GRN Created (Status = Draft)
    │
    └── Submit (Status → Open)
            │
            ├── For each line item with Accepted_Quantity > 0:
            │       └── Create Stock In transaction
            │
            └── For each line with Rejected_Quantity > 0:
                    └── Log rejection reason for vendor return
```

### Deluge Scripts

#### On Submit — Process GRN
```deluge
/* JUSTIFICATION: Stock In transaction creation from accepted GRN line items requires standalone form processing to create audit log entries */
/* ===== PSEUDOCODE =====
   Trigger: On Submit — when Goods_Receipt Status changes to "Open"
   
   1. Get the status display value and linked PO ID
   2. If status is "Open" AND PO is linked:
      a. Access GRN_Line_Items via input.GRN_Line_Items (embedded subform)
      b. If line items exist:
         For each line item:
         i.   Get Accepted_Quantity, Item ID, and Warehouse ID
         ii.  If accepted > 0 AND item and warehouse are both valid:
              - Create an Inventory_Transaction record:
                - Type: "Stock In"
                - Item: the accepted item
                - Warehouse: the destination warehouse
                - Quantity: accepted quantity
                - Date: receipt date from the GRN
                - Reference Type: "GRN"
                - Reference ID: this GRN's ID
              - If Actual_Unit_Cost is set: include Unit_Rate
   3. If status is not "Open" or no PO: skip processing
   ===== END PSEUDOCODE ===== */
status_val = ifnull(input.Status.toMap().get("display_value"), "");
po_id = input.PO;

if (status_val == "Open" && !po_id.isNull())
{
    grn_lines = input.GRN_Line_Items;

    if (!grn_lines.isNull())
    {
        for each grn_li in grn_lines
        {
            accepted = ifnull(grn_li.get("Accepted_Quantity"), 0);
            item_id = grn_li.get("Item");
            wh_id = grn_li.get("Warehouse");

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

                actual_cost = ifnull(grn_li.get("Actual_Unit_Cost"), 0);
                if (actual_cost > 0)
                {
                    txn_data.put("Unit_Rate", actual_cost);
                }

                zoho.creator.createRecord("budget_tracking", "Inventory_Transactions", txn_data);
            }
        }
    }
}
```

### PPV Enhancement — GRN_Line_Items Additional Fields

Add these fields to the existing `GRN_Line_Items` subform in the Zoho Creator console:

| Label | Field Type | API Name | Required | Notes |
|---|---|---|---|---|
| PO Unit Rate | Currency | `PO_Unit_Rate` | No | Read Only — copied from PO_Line_Items.Unit_Rate on form load via Deluge |
| PPV Amount | Currency (Formula) | `PPV_Amount` | No | `(Actual_Unit_Cost − PO_Unit_Rate) × Accepted_Quantity`. Positive = Unfavorable (cost higher), Negative = Favorable |

### Deluge Addition — On GRN Create (Before Submit)

Add this to the On Load / On User Input of the GRN form to pre-fill PO Unit Rate:

```deluge
/* JUSTIFICATION: Pre-fill PO Unit Rate from PO_Line_Items for PPV calculation — cannot use formula lookup because PO line items change after GRN creation */
po_id = input.PO;
if (!po_id.isNull())
{
    po_rec = zoho.creator.getRecordById("budget_tracking", "Purchase_Orders", po_id);
    if (!po_rec.isNull())
    {
        po_lines = po_rec.get("PO_Line_Items");
        grn_lines = input.GRN_Line_Items;
        if (!po_lines.isNull() && !grn_lines.isNull())
        {
            updated_lines = List();
            for each grn_li in grn_lines
            {
                grn_item = grn_li.get("Item");
                if (!grn_item.isNull())
                {
                    for each po_li in po_lines
                    {
                        po_item = po_li.get("Item");
                        if (!po_item.isNull() && po_item.get("ID") == grn_item.get("ID"))
                        {
                            po_rate = ifnull(po_li.get("Unit_Rate"), 0);
                            grn_li.put("PO_Unit_Rate", po_rate);
                            break;
                        }
                    }
                }
                updated_lines.add(grn_li);
            }
            input.GRN_Line_Items = updated_lines;
        }
    }
}
```

---

## 1.13 Supplier Credit Notes Form (`Supplier_Credit_Notes`)

Finance-initiated form for raising credit notes / debit notes against suppliers for defective or rejected items discovered during QA/QC.

### Field Configuration
| Label | Field Type | API Name | Required | Notes |
|---|---|---|---|---|
| Credit Note No | Auto Number | `Credit_Note_No` | Yes | Format: `SCN-{0000}` |
| Type | Dropdown | `CN_Type` | Yes | `Credit Note (Supplier owes us)`, `Debit Note (We charge supplier)` |
| Vendor | Lookup → Vendors | `Vendor` | Yes | Supplier to credit/debit |
| PO Reference | Lookup → Purchase_Orders | `PO_Reference` | Yes | Links credit to original PO |
| GRN Reference | Lookup → Goods_Receipts | `GRN_Reference` | No | Links to receipt where defect found |
| Credit Note Date | Date | `CN_Date` | No | Defaults to today |
| Total Amount | Currency | `Total_Amount` | No | Sum of line item totals |
| Status | Dropdown | `Status` | Yes | `Draft`, `Issued`, `Partially Settled`, `Settled`, `Cancelled` |
| Reason | Dropdown | `Reason` | No | `Defective Item`, `Damaged in Transit`, `Wrong Item`, `Shortage`, `Quality Issue`, `Price Discrepancy`, `Other` |
| QA/QC Reference | Text | `QC_Reference` | No | Inspection report/QC batch reference |
| Payment Adjustment Ref | Text | `Payment_Adjustment_Ref` | No | How this was settled |
| Notes | Multi Line | `Notes` | No | |
| Attachment | Upload | `Attachment` | No | Scanned CN/DN document |

### Embedded Subform — `SCN_Line_Items`
| Label | Field Type | API Name | Required | Notes |
|---|---|---|---|---|
| Item | Lookup → Inventory_Items | `Item` | Yes | The defective/credited item |
| PO Line Reference | Text | `PO_Line_Ref` | No | Optional reference to specific PO line |
| Quantity Returned | Decimal | `Quantity_Returned` | Yes | Qty being credited |
| Rate per Unit | Currency | `Rate_per_Unit` | Yes | From PO or current purchase price |
| Total Amount | Formula | `Total_Amount` | No | `Quantity_Returned × Rate_per_Unit` |
| Defect Reason | Text | `Defect_Reason` | No | Specific defect description |
| Stock Disposition | Dropdown | `Stock_Disposition` | Yes | `Returned to Supplier`, `Scrapped`, `Reworked`, `Under Inspection` |

### Validation Rules
1. **Total Amount > 0** — On Submit with Status = Issued, validate Total Amount > 0
2. **At least one line item** — On Submit with Status = Issued, validate at least one SCN_Line_Items row exists
3. **PO must be linked** — On Submit with Status = Issued, PO_Reference must not be null
4. **Status transition** — Only Draft → Issued → Partially Settled → Settled; Cancelled from any active state

### Deluge Script (On Submit — Main Workflow)

Paste into the form's On Submit workflow:

```deluge
/* JUSTIFICATION: Supplier Credit Notes is a standalone finance form. Deluge handles:
   1) Validating the credit note before issuing
   2) Updating PO_Line_Items.Credited_Qty and PO.Has_Outstanding_Credit
   3) Auto-creating Return to Vendor inventory transaction for returned goods
   4) Marking linked GRN_Line_Items as credited
   5) Reversing all effects on cancellation
   These cross-form side effects cannot be handled by form-level validation alone. */

status_val = ifnull(input.Status.toMap().get("display_value"), "");
po_id = input.PO_Reference;
vendor_id = input.Vendor;

if (status_val == "Issued")
{
    /* ── Validate — ensure total > 0 and line items exist ── */
    total_amt = ifnull(input.Total_Amount, 0);
    scn_lines = input.SCN_Line_Items;

    if (total_amt <= 0)
    {
        alert "Total Amount must be greater than 0 before issuing.";
        return;
    }
    if (scn_lines.isNull() || scn_lines.size() == 0)
    {
        alert "At least one line item is required.";
        return;
    }
    if (po_id.isNull())
    {
        alert "PO Reference is required to issue a credit note.";
        return;
    }
    if (vendor_id.isNull())
    {
        alert "Vendor is required.";
        return;
    }

    /* ── Update PO: set Has_Outstanding_Credit = true ── */
    po_data = Map();
    po_data.put("Has_Outstanding_Credit", true);
    zoho.creator.updateRecord("budget_tracking", "Purchase_Orders", po_id, po_data);

    /* ── Process each line item ── */
    for each scn_li in scn_lines
    {
        item_id = scn_li.get("Item");
        qty = ifnull(scn_li.get("Quantity_Returned"), 0);
        rate = ifnull(scn_li.get("Rate_per_Unit"), 0);
        disposition = scn_li.get("Stock_Disposition");
        if (disposition != null) { disposition = disposition.toMap().get("display_value"); }

        /* Update PO_Line_Items.Credited_Qty — fetch PO, update its subform */
        if (!po_id.isNull() && !item_id.isNull() && qty > 0)
        {
            po_rec = zoho.creator.getRecordById("budget_tracking", "Purchase_Orders", po_id);
            if (!po_rec.isNull())
            {
                po_lines = po_rec.get("PO_Line_Items");
                if (!po_lines.isNull())
                {
                    updated_lines = List();
                    for each po_li in po_lines
                    {
                        po_li_item = po_li.get("Item");
                        if (!po_li_item.isNull() && po_li_item.get("ID") == item_id.get("ID"))
                        {
                            existing_credited = ifnull(po_li.get("Credited_Qty"), 0);
                            po_li.put("Credited_Qty", existing_credited + qty);
                        }
                        updated_lines.add(po_li);
                    }
                    po_update = Map();
                    po_update.put("PO_Line_Items", updated_lines);
                    zoho.creator.updateRecord("budget_tracking", "Purchase_Orders", po_id, po_update);
                }
            }
        }

        /* Auto-create Return to Vendor inventory transaction */
        if (disposition == "Returned to Supplier")
        {
            /* Find a warehouse — use Main Warehouse or first available */
            wh_records = zoho.creator.getRecords("budget_tracking", "Warehouses", "Status == 'Active'");
            wh_id = null;
            if (!wh_records.isNull() && wh_records.size() > 0)
            {
                wh_id = wh_records.get(0).get("ID");
            }

            if (!wh_id.isNull())
            {
                txn_data = Map();
                txn_data.put("Transaction_Type", "Return to Vendor");
                txn_data.put("Item", item_id);
                txn_data.put("Warehouse", wh_id);
                txn_data.put("Quantity", qty);
                txn_data.put("Unit_Rate", rate);
                txn_data.put("Transaction_Date", input.CN_Date);
                txn_data.put("Reference_Type", "SCN");
                txn_data.put("Reference_ID", input.ID.toString());
                txn_data.put("Notes", "Auto: SCN " + input.Credit_Note_No + " — Return to " + vendor_id.toString());
                zoho.creator.createRecord("budget_tracking", "Inventory_Transactions", txn_data);
            }
        }
    }

    /* ── Mark linked GRN line items as credited ── */
    grn_id = input.GRN_Reference;
    cn_no = input.Credit_Note_No;
    if (!grn_id.isNull())
    {
        grn_rec = zoho.creator.getRecordById("budget_tracking", "Goods_Receipts", grn_id);
        if (!grn_rec.isNull())
        {
            grn_lines = grn_rec.get("GRN_Line_Items");
            if (!grn_lines.isNull())
            {
                updated_grn_lines = List();
                for each grn_li in grn_lines
                {
                    grn_li.put("Is_Credited", true);
                    grn_li.put("Credit_Note_Ref", cn_no);
                    updated_grn_lines.add(grn_li);
                }
                grn_update = Map();
                grn_update.put("GRN_Line_Items", updated_grn_lines);
                zoho.creator.updateRecord("budget_tracking", "Goods_Receipts", grn_id, grn_update);
            }
        }
    }

    /* ── Send notification ── */
    notify_data = Map();
    notify_data.put("to", "finance@itotcloud.com, procurement@itotcloud.com");
    notify_data.put("subject", "Supplier Credit Note Issued: " + cn_no);
    notify_data.put("body", "Credit Note " + cn_no + " issued to Vendor. Total Amount: " + total_amt.toString());
    // Use Zoho Creator email notification or workflow alert here
}
else if (status_val == "Settled")
{
    /* ── On settlement: clear PO credit flag if no other outstanding SCNs ── */
    if (!po_id.isNull())
    {
        criteria = "PO_Reference == " + po_id.toString() + " && Status == 'Issued'";
        other_scns = zoho.creator.getRecords("budget_tracking", "Supplier_Credit_Notes", criteria);
        if (other_scns.isNull() || other_scns.size() == 0)
        {
            po_data = Map();
            po_data.put("Has_Outstanding_Credit", false);
            zoho.creator.updateRecord("budget_tracking", "Purchase_Orders", po_id, po_data);
        }
    }
}
else if (status_val == "Cancelled")
{
    /* ── Reverse all side effects ── */
    if (!po_id.isNull())
    {
        po_rec = zoho.creator.getRecordById("budget_tracking", "Purchase_Orders", po_id);
        if (!po_rec.isNull())
        {
            po_lines = po_rec.get("PO_Line_Items");
            scn_lines = input.SCN_Line_Items;
            if (!po_lines.isNull() && !scn_lines.isNull())
            {
                updated_lines = List();
                for each po_li in po_lines
                {
                    po_li_item = po_li.get("Item");
                    for each scn_li in scn_lines
                    {
                        scn_item = scn_li.get("Item");
                        if (!po_li_item.isNull() && !scn_item.isNull()
                            && po_li_item.get("ID") == scn_item.get("ID"))
                        {
                            reversal_qty = ifnull(scn_li.get("Quantity_Returned"), 0);
                            existing_credited = ifnull(po_li.get("Credited_Qty"), 0);
                            po_li.put("Credited_Qty", max(0, existing_credited - reversal_qty));
                        }
                    }
                    updated_lines.add(po_li);
                }
                po_update = Map();
                po_update.put("PO_Line_Items", updated_lines);
                po_update.put("Has_Outstanding_Credit", false);
                zoho.creator.updateRecord("budget_tracking", "Purchase_Orders", po_id, po_update);
            }
        }

        /* Reverse GRN credit flags */
        grn_id = input.GRN_Reference;
        if (!grn_id.isNull())
        {
            grn_rec = zoho.creator.getRecordById("budget_tracking", "Goods_Receipts", grn_id);
            if (!grn_rec.isNull())
            {
                grn_lines = grn_rec.get("GRN_Line_Items");
                if (!grn_lines.isNull())
                {
                    updated_grn_lines = List();
                    for each grn_li in grn_lines
                    {
                        grn_li.put("Is_Credited", false);
                        grn_li.put("Credit_Note_Ref", "");
                        updated_grn_lines.add(grn_li);
                    }
                    grn_update = Map();
                    grn_update.put("GRN_Line_Items", updated_grn_lines);
                    zoho.creator.updateRecord("budget_tracking", "Goods_Receipts", grn_id, grn_update);
                }
            }
        }
    }
}
```

### Enhancement — SCN Bill Reference (Added after SCN module initial build)

Add a new `Bill_Reference` field (Lookup → Vendor_Bills, optional) to the Supplier_Credit_Notes form.

**Enhanced Deluge — On SCN Issue (add after PO credit flag update):**

```deluge
/* ── If Bill Reference is set, adjust Bill Balance_Due ── */
bill_id = input.Bill_Reference;
if (!bill_id.isNull())
{
    bill_rec = zoho.creator.getRecordById("budget_tracking", "Vendor_Bills", bill_id);
    if (!bill_rec.isNull())
    {
        scn_total = ifnull(input.Total_Amount, 0);
        current_paid = ifnull(bill_rec.get("Amount_Paid"), 0);
        current_total = ifnull(bill_rec.get("Total_Amount"), 0);
        new_balance = current_total - current_paid - scn_total;
        bill_data = Map();
        bill_data.put("Balance_Due", max(new_balance, 0));
        /* Note: Balance_Due is a formula field. If Zoho Creator restricts formula updates,
           store the adjustment in a Notes field or a dedicated Adjustment_Amount field instead. */
        zoho.creator.updateRecord("budget_tracking", "Vendor_Bills", bill_id, bill_data);
    }
}
```

**Enhanced Deluge — On SCN Cancel (add after existing reversal logic):**

```deluge
/* ── If Bill Reference was set, reverse the Balance_Due adjustment ── */
if (!bill_id.isNull())
{
    bill_rec = zoho.creator.getRecordById("budget_tracking", "Vendor_Bills", bill_id);
    if (!bill_rec.isNull())
    {
        scn_total = ifnull(input.Total_Amount, 0);
        current_paid = ifnull(bill_rec.get("Amount_Paid"), 0);
        current_total = ifnull(bill_rec.get("Total_Amount"), 0);
        restored_balance = current_total - current_paid;
        bill_data = Map();
        bill_data.put("Balance_Due", max(restored_balance, 0));
        zoho.creator.updateRecord("budget_tracking", "Vendor_Bills", bill_id, bill_data);
    }
}
```

### Reports to Create
1. **Outstanding Supplier Credits** — Tabular report, filter: Status IN ("Issued", "Partially Settled"), grouped by Vendor
2. **Supplier Credit History** — Summary report grouped by Vendor, display total credited
3. **Defective Item Analysis** — Summary grouped by Item + Reason + Stock Disposition
4. **Credits by PO** — Tabular report grouped by PO_Reference

---

## 1.14 Transfer Orders Form (`Transfer_Orders`)

### Field Configuration
| Label | Field Type | API Name | Required | Notes |
|---|---|---|---|---|
| Transfer No | Auto Number | `Transfer_No` | Yes | Format: `TO-{0000}` |
| From Warehouse | Lookup → Warehouses | `From_Warehouse` | Yes | |
| To Warehouse | Lookup → Warehouses | `To_Warehouse` | Yes | |
| Transfer Date | Date | `Transfer_Date` | No | Default today |
| Status | Dropdown | `Status` | No | `Draft, Open, Completed, Cancelled` |
| Notes | Multi Line | `Notes` | No | |

### Embedded Subform: TO Line Items (API Name: TO_Line_Items)

| Label | Field Type | API Name | Required | Notes |
|---|---|---|---|---|
| Item | Lookup → Inventory_Items | `Item` | Yes | |
| Quantity | Decimal | `Quantity` | Yes | |
| Rate | Currency | `Rate` | Yes | Unit rate of the item |
| Total | Formula | `Total` | No | Formula: Quantity * Rate |

### Validation Rules
1. **Different warehouses** — From_Warehouse and To_Warehouse must be different.
2. **At least one line item** — On Status = "Completed", at least one TO_Line_Items required.
3. **Sufficient stock** — On Status = "Completed", validate `From_Warehouse` has enough stock for each item.

### Workflow Process

```
TO Created (Status = Draft)
    │
    └── Mark Completed → Status = Completed
            │
            ├── Validate From ≠ To Warehouse
            ├── Validate stock availability at From_Warehouse
            │
            └── For each line item:
                    ├── Stock Out at From_Warehouse
                    └── Stock In at To_Warehouse
```

### Deluge Scripts
#### On Submit — Process Transfer Completion
```deluge
/* JUSTIFICATION: Paired Stock Out/Stock In transaction creation from embedded subform data requires standalone form processing */
/* ===== PSEUDOCODE =====
   Trigger: On Submit — when Transfer_Order Status changes to "Completed"
   
   1. Get the status display value
   2. If status is "Completed":
      a. Get From_Warehouse and To_Warehouse from the record
      b. If either is null: alert error — both warehouses required
      c. Access TO_Line_Items via input.TO_Line_Items (embedded subform)
      d. If line items exist:
         For each line item:
         i.   Get Item ID and Quantity
         ii.  If item is valid AND quantity is positive:
              - Create "Stock Out" transaction at source warehouse:
                - Reference Type: "TO", Reference ID: this TO
                - Notes indicate destination warehouse
              - Create "Stock In" transaction at destination warehouse:
                - Reference Type: "TO", Reference ID: this TO
                - Notes indicate source warehouse
   3. If status is not "Completed": skip all processing
   ===== END PSEUDOCODE ===== */
status_val = ifnull(input.Status.toMap().get("display_value"), "");

if (status_val == "Completed")
{
    from_wh = input.From_Warehouse;
    to_wh = input.To_Warehouse;

    if (from_wh.isNull() || to_wh.isNull())
    {
        alert "Both From and To Warehouse are required.";
    }

    to_lines = input.TO_Line_Items;

    if (!to_lines.isNull())
    {
        for each li in to_lines
        {
            item_id = li.get("Item");
            qty = ifnull(li.get("Quantity"), 0);

            if (!item_id.isNull() && qty > 0)
            {
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
9. GRN Submit recalculates PO.Receipt_Status per line item (Received_Qty, Pending_Qty)
10. Supplier Credit Notes creates SCN-0001...
11. SCN Issued → PO.Has_Outstanding_Credit = true; GRN lines credited
12. SCN Issued with Return to Supplier → auto-creates Return to Vendor inventory transaction
13. SCN Settled → clears PO credit flag
14. SCN Cancelled → reverses credits
15. Transfer Orders creates TO-0001, TO-0002...
16. TO Completed → paired Stock Out/In transactions

## Next Phase
→ Proceed to `PHASE_1E_BUILD.md` when all above forms are verified.
