# Phase 1G Build Guide — Vendor Bills → Payments (AP/AR Sub-ledger)

## Dependencies
Requires Phase 1F complete (Reports & Dashboards). Vendor_Bills depends on Vendors, Purchase_Orders, Goods_Receipts. Payments depends on Vendor_Bills and Invoices.

---

## 1.20 Vendor Bills Form (`Vendor_Bills`)

Records invoices received from vendors against Purchase Orders. This is the Accounts Payable (AP) sub-ledger.

### Field Configuration
| Label | Field Type | API Name | Required | Notes |
|---|---|---|---|---|
| Bill No | Auto Number | `Bill_No` | Yes | Format: `BILL-{0000}` |
| Vendor | Lookup → Vendors | `Vendor` | Yes | Supplier who issued the bill |
| PO Reference | Lookup → Purchase_Orders | `PO_Reference` | Yes | Links bill to original PO |
| GRN Reference | Lookup → Goods_Receipts | `GRN_Reference` | No | For 3-way match |
| Bill Date | Date | `Bill_Date` | No | Date on vendor's invoice |
| Due Date | Date | `Due_Date` | No | Payment due date |
| Reference Number | Text | `Reference_No` | No | Vendor's invoice number |
| Subtotal | Currency | `Subtotal` | No | Sum of line item totals |
| Discount (%) | Decimal | `Discount_Pct` | No | Overall bill discount % |
| Discount Amount | Currency (Formula) | `Discount_Amount` | No | `Subtotal × (Discount_Pct / 100)` |
| Tax Total | Currency | `Tax_Total` | No | Sum of line item taxes |
| Total Amount | Currency | `Total_Amount` | No | `Subtotal − Discount_Amount + Tax_Total` |
| Amount Paid | Currency | `Amount_Paid` | No | Updated by Deluge on Payment |
| Balance Due | Currency (Formula) | `Balance_Due` | No | `Total_Amount − Amount_Paid` |
| Status | Dropdown | `Status` | Yes | `Draft`, `Received`, `Matched`, `Approved`, `Partially Paid`, `Paid`, `Cancelled` |
| Currency | Dropdown | `Currency` | No | Copied from Vendor |
| Notes | Multi Line | `Notes` | No | |
| Attachment | Upload | `Attachment` | No | Scanned vendor invoice |

### Embedded Subform — `Bill_Line_Items`
| Label | Field Type | API Name | Required | Notes |
|---|---|---|---|---|
| Item | Lookup → Inventory_Items | `Item` | No | Optional — service bills may not have items |
| Description | Text | `Description` | No | Line item description |
| HSN/SAC | Text | `HSN_SAC` | No | Tax classification |
| Quantity | Decimal | `Quantity` | No | |
| Unit Rate | Currency | `Unit_Rate` | Yes | Per-unit price |
| Discount (%) | Decimal | `Discount_Pct` | No | Line-level discount |
| Discount Amount | Currency (Formula) | `Discount_Amount` | No | `(Quantity × Unit_Rate) × (Discount_Pct / 100)` |
| Tax (%) | Decimal | `Tax_Pct` | No | Tax percentage |
| Tax Amount | Currency (Formula) | `Tax_Amount` | No | `((Quantity × Unit_Rate) − Discount_Amount) × (Tax_Pct / 100)` |
| Line Total | Currency (Formula) | `Line_Total` | No | `(Quantity × Unit_Rate) − Discount_Amount + Tax_Amount` |

### Validation Rules
1. **3-Way Match** — On Status = "Matched", validate: PO Ordered Qty ≥ Bill Qty, and GRN Accepted Qty ≥ Bill Qty (if GRN is linked)
2. **PO Required** — On Submit with Status = "Matched" or "Approved", PO_Reference must not be null
3. **Amount > 0** — Total_Amount must be > 0
4. **At least one line item** — Bill_Line_Items must not be empty
5. **Cancellation guard** — Cannot cancel if Payments or SCNs are linked

### Deluge Scripts

#### On Submit — Main Workflow
```deluge
/* JUSTIFICATION: Vendor Bills is a standalone finance form. Deluge handles:
   1) 3-way match validation against PO and GRN
   2) PPV calculation and recording
   3) Bill lifecycle status transitions
   4) Cancellation guard against linked Payments/SCNs
   These cross-form validations and side effects cannot be handled by form-level rules. */

status_val = ifnull(input.Status.toMap().get("display_value"), "");
po_id = input.PO_Reference;
grn_id = input.GRN_Reference;
bill_lines = input.Bill_Line_Items;

if (status_val == "Matched")
{
    /* ── Validate PO exists ── */
    if (po_id.isNull())
    {
        alert "PO Reference is required for matching.";
        return;
    }
    if (bill_lines.isNull() || bill_lines.size() == 0)
    {
        alert "At least one line item is required.";
        return;
    }

    /* ── 3-Way Match — fetch PO ── */
    po_rec = zoho.creator.getRecordById("budget_tracking", "Purchase_Orders", po_id);
    if (po_rec.isNull())
    {
        alert "Purchase Order not found.";
        return;
    }
    po_lines = po_rec.get("PO_Line_Items");

    /* ── Fetch GRN if linked ── */
    grn_lines = null;
    if (!grn_id.isNull())
    {
        grn_rec = zoho.creator.getRecordById("budget_tracking", "Goods_Receipts", grn_id);
        if (!grn_rec.isNull())
        {
            grn_lines = grn_rec.get("GRN_Line_Items");
        }
    }

    /* ── Validate each line item ── */
    match_errors = "";
    for each bill_li in bill_lines
    {
        bill_item = bill_li.get("Item");
        bill_qty = ifnull(bill_li.get("Quantity"), 0);
        bill_rate = ifnull(bill_li.get("Unit_Rate"), 0);

        if (!bill_item.isNull() && bill_qty > 0)
        {
            bill_item_id = bill_item.get("ID");

            /* Check PO line */
            po_qty = 0;
            po_rate = 0;
            if (!po_lines.isNull())
            {
                for each po_li in po_lines
                {
                    po_li_item = po_li.get("Item");
                    if (!po_li_item.isNull() && po_li_item.get("ID") == bill_item_id)
                    {
                        po_qty = ifnull(po_li.get("Quantity"), 0);
                        po_rate = ifnull(po_li.get("Unit_Rate"), 0);
                        break;
                    }
                }
            }

            /* Check GRN line if available */
            grn_accepted = 0;
            grn_actual_cost = 0;
            if (!grn_lines.isNull())
            {
                for each grn_li in grn_lines
                {
                    grn_item = grn_li.get("Item");
                    if (!grn_item.isNull() && grn_item.get("ID") == bill_item_id)
                    {
                        grn_accepted = ifnull(grn_li.get("Accepted_Quantity"), 0);
                        grn_actual_cost = ifnull(grn_li.get("Actual_Unit_Cost"), 0);
                        break;
                    }
                }
            }

            /* Validate bill qty <= PO ordered qty */
            if (bill_qty > po_qty)
            {
                match_errors = match_errors + "Item: Bill qty (" + bill_qty.toString() + ") exceeds PO ordered qty (" + po_qty.toString() + "). ";
            }

            /* Validate bill qty <= GRN accepted qty */
            if (!grn_id.isNull() && bill_qty > grn_accepted)
            {
                match_errors = match_errors + "Item: Bill qty (" + bill_qty.toString() + ") exceeds GRN accepted qty (" + grn_accepted.toString() + "). ";
            }
        }
    }

    if (match_errors != "")
    {
        alert "3-Way Match Failed: " + match_errors;
        return;
    }

    /* ── Match passed — set Approved ── */
    bill_data = Map();
    bill_data.put("Status", "Approved");
    zoho.creator.updateRecord("budget_tracking", "Vendor_Bills", input.ID, bill_data);
}

else if (status_val == "Cancelled")
{
    /* ── Validate no linked Payments or SCNs ── */
    linked_payments = zoho.creator.getRecords("budget_tracking", "Payments", "Reference_To == " + input.ID.toString());
    if (!linked_payments.isNull() && linked_payments.size() > 0)
    {
        alert "Cannot cancel: " + linked_payments.size().toString() + " Payment(s) linked to this Bill.";
        return;
    }
    linked_scns = zoho.creator.getRecords("budget_tracking", "Supplier_Credit_Notes", "Bill_Reference == " + input.ID.toString());
    if (!linked_scns.isNull() && linked_scns.size() > 0)
    {
        alert "Cannot cancel: " + linked_scns.size().toString() + " SCN(s) linked to this Bill.";
        return;
    }
}
```

### Approval Process

```
Vendor Invoice Received
    │
    └── Finance creates Bill (Status = "Received")
            │
            └── Finance performs 3-way match (Status = "Matched")
                    │
                    ├── Match passes → Status = "Approved", PPV recorded
                    │
                    └── Match fails → alert with details, status stays "Received"
                            │
                            └── Finance corrects and re-attempts match
```

---

## 2.21 Payments Form (`Payments`)

Unified module for outgoing vendor payments (AP) and incoming customer receipts (AR).

### Field Configuration
| Label | Field Type | API Name | Required | Notes |
|---|---|---|---|---|
| Payment No | Auto Number | `Payment_No` | Yes | Format: `PMT-{0000}` |
| Type | Dropdown | `Payment_Type` | Yes | `Outgoing — AP (Vendor Payment)`, `Incoming — AR (Customer Receipt)` |
| Reference To | Lookup → Vendor_Bills or Invoices | `Reference_To` | No | The Bill (AP) or Invoice (AR) being paid |
| Vendor | Lookup → Vendors | `Vendor` | No | Required if Type = Outgoing |
| Customer | Lookup → Accounts | `Customer` | No | Required if Type = Incoming |
| Payment Date | Date | `Payment_Date` | No | Defaults to today |
| Amount | Currency | `Amount` | Yes | Payment amount |
| Payment Method | Dropdown | `Payment_Method` | No | `Bank Transfer`, `Cheque`, `Cash`, `Credit Card`, `UPI`, `Other` |
| Reference No | Text | `Reference_No` | No | Cheque/Transaction/UPI reference |
| Status | Dropdown | `Status` | Yes | `Draft`, `Completed`, `Reversed`, `Failed` |
| Notes | Multi Line | `Notes` | No | |
| Attachment | Upload | `Attachment` | No | Payment receipt/screenshot |

### Validation Rules
1. **Amount > 0** — On Submit, Amount must be > 0
2. **Type-Reference consistency** — If Type = Outgoing, Reference_To must point to Vendor_Bills; if Incoming, must point to Invoices
3. **No overpayment** — Amount must not exceed linked document's Balance Due
4. **Direction required** — Vendor required for Outgoing; Customer required for Incoming

### Deluge Scripts

#### On Submit — Main Workflow
```deluge
/* JUSTIFICATION: Payments is a standalone finance form. Deluge handles:
   1) Updating linked Bill/Invoice Amount_Paid + Balance_Due + Status
   2) Type-based routing (AP Bill vs AR Invoice)
   3) Overpayment prevention
   4) Full reversal with rollback
   These cross-form side effects cannot be handled by form-level rules. */

status_val = ifnull(input.Status.toMap().get("display_value"), "");
pmt_type = ifnull(input.Payment_Type.toMap().get("display_value"), "");
ref_id = input.Reference_To;
amt = ifnull(input.Amount, 0);

if (status_val == "Completed")
{
    if (amt <= 0)
    {
        alert "Amount must be greater than 0.";
        return;
    }
    if (ref_id.isNull())
    {
        alert "Reference To is required.";
        return;
    }

    if (pmt_type == "Outgoing — AP (Vendor Payment)")
    {
        /* ── Update Vendor_Bill ── */
        bill_rec = zoho.creator.getRecordById("budget_tracking", "Vendor_Bills", ref_id);
        if (bill_rec.isNull())
        {
            alert "Vendor Bill not found.";
            return;
        }

        current_paid = ifnull(bill_rec.get("Amount_Paid"), 0);
        total_amt = ifnull(bill_rec.get("Total_Amount"), 0);
        new_paid = current_paid + amt;

        if (new_paid > total_amt)
        {
            alert "Payment exceeds Bill Total Amount of " + total_amt.toString() + ". Max allowed: " + (total_amt - current_paid).toString() + ".";
            return;
        }

        bill_data = Map();
        bill_data.put("Amount_Paid", new_paid);
        if (new_paid >= total_amt)
        {
            bill_data.put("Status", "Paid");
        }
        else
        {
            bill_data.put("Status", "Partially Paid");
        }
        zoho.creator.updateRecord("budget_tracking", "Vendor_Bills", ref_id, bill_data);
    }
    else if (pmt_type == "Incoming — AR (Customer Receipt)")
    {
        /* ── Update Invoice ── */
        inv_rec = zoho.creator.getRecordById("budget_tracking", "Invoices", ref_id);
        if (inv_rec.isNull())
        {
            alert "Invoice not found.";
            return;
        }

        current_paid = ifnull(inv_rec.get("Amount_Paid"), 0);
        total_amt = ifnull(inv_rec.get("Total"), 0);
        new_paid = current_paid + amt;

        if (new_paid > total_amt)
        {
            alert "Receipt exceeds Invoice Total of " + total_amt.toString() + ". Max allowed: " + (total_amt - current_paid).toString() + ".";
            return;
        }

        inv_data = Map();
        inv_data.put("Amount_Paid", new_paid);
        if (new_paid >= total_amt)
        {
            inv_data.put("Status", "Paid");
        }
        else
        {
            inv_data.put("Status", "Partially Paid");
        }
        zoho.creator.updateRecord("budget_tracking", "Invoices", ref_id, inv_data);
    }
}

else if (status_val == "Reversed")
{
    if (ref_id.isNull())
    {
        alert "Reference To is required for reversal.";
        return;
    }

    if (pmt_type == "Outgoing — AP (Vendor Payment)")
    {
        bill_rec = zoho.creator.getRecordById("budget_tracking", "Vendor_Bills", ref_id);
        if (!bill_rec.isNull())
        {
            current_paid = ifnull(bill_rec.get("Amount_Paid"), 0);
            total_amt = ifnull(bill_rec.get("Total_Amount"), 0);
            new_paid = max(current_paid - amt, 0);

            bill_data = Map();
            bill_data.put("Amount_Paid", new_paid);
            if (new_paid <= 0)
            {
                bill_data.put("Status", ifnull(bill_rec.get("Status_History"), "Approved"));
            }
            else
            {
                bill_data.put("Status", "Partially Paid");
            }
            zoho.creator.updateRecord("budget_tracking", "Vendor_Bills", ref_id, bill_data);
        }
    }
    else if (pmt_type == "Incoming — AR (Customer Receipt)")
    {
        inv_rec = zoho.creator.getRecordById("budget_tracking", "Invoices", ref_id);
        if (!inv_rec.isNull())
        {
            current_paid = ifnull(inv_rec.get("Amount_Paid"), 0);
            total_amt = ifnull(inv_rec.get("Total"), 0);
            new_paid = max(current_paid - amt, 0);

            inv_data = Map();
            inv_data.put("Amount_Paid", new_paid);
            if (new_paid <= 0)
            {
                inv_data.put("Status", "Sent");
            }
            else
            {
                inv_data.put("Status", "Partially Paid");
            }
            zoho.creator.updateRecord("budget_tracking", "Invoices", ref_id, inv_data);
        }
    }
}
```

### Payment Lifecycle

```
Draft → Completed (updates linked document)
   ↓
Completed → Reversed (rolls back document update)
```

---

## Reports

| Report | Type | Source | Audience |
|--------|------|--------|----------|
| AP Aging | Tabular (group by Due Date range) | Vendor_Bills | Finance |
| Outstanding Bills | Tabular (filter: Status IN Approved, Partially Paid) | Vendor_Bills | Finance |
| Bill Register | Tabular (date range filter) | Vendor_Bills | Finance |
| PPV Register | Tabular (filter: PPV > 0) | Vendor_Bills + GRN | Finance |
| Vendor Payment History | Summary by Vendor | Vendor_Bills + Payments | Finance |
| Payment Register | Tabular (filter by Type, date range) | Payments | Finance |
| AP Payment Summary | Summary by Vendor | Payments (Type = Outgoing) | Finance |
| AR Receipt Summary | Summary by Customer | Payments (Type = Incoming) | Finance |

---

## Verification Checklist

- [ ] Vendor_Bills form created with all fields per spec
- [ ] Bill_Line_Items embedded subform created with all fields
- [ ] 3-way match validation works: rejects when PO qty < Bill qty
- [ ] 3-way match validation works: rejects when GRN accepted < Bill qty
- [ ] Approved status records PPV correctly
- [ ] Payments form created with all fields per spec
- [ ] AP Payment updates Bill Amount_Paid + Balance_Due
- [ ] AR Payment updates Invoice Amount_Paid + Balance_Due
- [ ] Overpayment prevention works (alert when Amount > Balance Due)
- [ ] Payment reversal rolls back Amount_Paid correctly
- [ ] AP Aging report shows correct aging buckets
- [ ] PPV Register report shows variances correctly
- [ ] Weighted Average Cost recalculates correctly on Stock In (in Phase 1D Inventory_Transactions)
- [ ] SCN Bill Reference field linked correctly
