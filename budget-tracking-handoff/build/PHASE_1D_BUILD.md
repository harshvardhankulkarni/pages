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
9. Transfer Orders creates TO-0001, TO-0002...
10. TO Completed → paired Stock Out/In transactions

## Next Phase
→ Proceed to `PHASE_1E_BUILD.md` when all above forms are verified.
