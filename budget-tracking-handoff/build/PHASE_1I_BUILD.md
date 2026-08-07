# Phase 1I Build Guide — Audit Log → Expense Allocations → Budget Revisions

## Dependencies
Requires Phase 1H complete. Audit_Log is a new standalone form. Expense_Allocations is an embedded subform added to Expenses. Budget_Revisions is an embedded subform added to Budget_Plans.

---

## 1. Audit Log Form (`Audit_Log`)

Immutable log for all financial transactions and status changes. This form is **write-only via Deluge** — users should not create records directly.

### Field Configuration
| Label | Field Type | API Name | Required | Notes |
|---|---|---|---|---|
| Log ID | Auto Number | `Log_ID` | Yes | Format: `AUD-{0000}` |
| Module | Dropdown | `Module` | Yes | `Expenses`, `Budget_Approvals`, `Purchase_Orders`, `Goods_Receipts`, `Supplier_Credit_Notes`, `Vendor_Bills`, `Invoices`, `Payments`, `Transfer_Orders` |
| Record ID | Text | `Record_ID` | Yes | Zoho Creator record ID of the changed record |
| Action | Dropdown | `Action` | Yes | `Created`, `Updated`, `Status Changed`, `Cancelled`, `Reversed` |
| Field Changed | Text | `Field_Changed` | No | Which field was modified |
| Old Value | Multi Line | `Old_Value` | No | Previous value |
| New Value | Multi Line | `New_Value` | No | New value |
| Changed By | User Picker | `Changed_By` | Yes | Auto-set to current user |
| Changed At | Date/Time | `Changed_At` | Yes | Auto timestamp |
| Notes | Multi Line | `Notes` | No | Additional context |

### Permission
- **Finance Manager**: Read-only access
- **Administrator**: Full access
- **All other roles**: No access (no read, no write)

### Deluge — Standard Audit Log Snippet

Add this to the On Submit workflow of every P0 financial form (Expenses, Budget_Approvals, POs, GRNs, SCNs, Vendor_Bills, Invoices, Payments, Transfer_Orders):

```deluge
/* JUSTIFICATION: Audit trail must capture status changes and financial edits across all P0 forms for compliance and forensic accounting. Zoho Creator's built-in audit history is not accessible via API or reports — we need this data in a form for custom reporting */

/* ===== PSEUDOCODE =====
   Trigger: On Submit — on every financial P0 form

   1. On Status change:
        If form has a "Status" field and the value differs from the prior stored value:
          Create Audit_Log record:
            Module = [current form API name]
            Record_ID = [input.ID or triggering record ID]
            Action = "Status Changed"
            Field_Changed = "Status"
            Old_Value = [prior status display value, if available]
            New_Value = [new status display value]
            Changed_By = [zoho.currentuser]
            Changed_At = [now]
            Notes = "Status changed to " + new status

   2. On financial field changes (for update scenarios):
        If Amount, Quantity, Rate, or Total changed:
          Log each changed field as a separate Audit_Log entry
          Action = "Updated"
          Field_Changed = [field label]
          Old_Value = [prior value]
          New_Value = [new value]

   3. For new records:
        Action = "Created"
        Notes = "Record created in " + Module
   ===== END PSEUDOCODE ===== */
```

Implementation notes:
- For **new records** (On Submit, first time): log Action = "Created"
- For **existing record updates** (On Submit, subsequent): compare status, log if changed
- For **specific actions** (Cancelled, Reversed): always log with those action types
- Use `zoho.currentuser` for Changed_By
- Use `zoho.datetime.now()` or `now()` for timestamp

---

## 2. Expense Allocations (Embedded Subform Enhancement)

Add an embedded subform `Expense_Allocations` to the existing Expenses form.

### Subform Field Configuration
| Label | Field Type | API Name | Required | Notes |
|---|---|---|---|---|
| Budget Component | Lookup → Budget_Components | `Budget_Component` | Yes | Must belong to same Project as Expense |
| Allocated Amount | Currency | `Allocated_Amount` | Yes | Portion of expense amount |
| Percentage | Formula | `Allocation_Pct` | No | `Allocated_Amount / Parent_Expense.Amount × 100` |

### Validation Rules
1. **Sum equals Expense Amount** — On Submit, validate Sum(Allocated_Amount) = Expense.Amount
2. **Same Project** — Each Budget_Component.Budget_Plan.Project must match Expense.Project
3. **At least one allocation** — If any allocations exist, must have at least one non-zero row

### Enhanced Deluge — On Expense Submit

Update the existing Expense Submit Deluge to handle allocations:

```deluge
/* JUSTIFICATION: Expense allocations allow splitting a single expense across multiple budget components. This cannot be handled by the single header-level Budget_Component lookup — the subform provides 1:N mapping with validation */

/* ===== PSEUDOCODE =====
   Trigger: On Submit — Expense form

   1. Check if Expense_Allocations subform has data
   2. If allocations exist:
        a. Validate Sum(Allocated_Amount) == Expense.Amount
        b. Validate each Budget_Component belongs to Expense.Project
        c. For each allocation row:
             Update Budget_Component.Spent_Amount += Allocated_Amount
             Recalculate Budget_Component status (Within Budget / 80% / 90% / Exceeded)
        d. Skip the single Budget_Component update (header field is informational)
   3. If no allocations exist (legacy behavior):
        a. Use the header Budget_Component lookup
        b. Update single component's Spent_Amount
        c. Recalculate status as before
   ===== END PSEUDOCODE ===== */

allocations = input.Expense_Allocations;
expense_amt = ifnull(input.Amount, 0);

if (!allocations.isNull() && allocations.size() > 0)
{
    /* Validate sum equals expense amount */
    total_allocated = 0;
    for each alloc in allocations
    {
        total_allocated = total_allocated + ifnull(alloc.get("Allocated_Amount"), 0);
    }

    if (total_allocated != expense_amt)
    {
        alert "Total allocated amount (" + total_allocated.toString() + ") must equal Expense Amount (" + expense_amt.toString() + ").";
        return;
    }

    /* Update each budget component */
    for each alloc in allocations
    {
        comp_id = alloc.get("Budget_Component");
        alloc_amt = ifnull(alloc.get("Allocated_Amount"), 0);

        if (!comp_id.isNull() && alloc_amt > 0)
        {
            comp = zoho.creator.getRecordById("budget_tracking", "Budget_Components", comp_id);
            if (!comp.isNull())
            {
                current_spent = ifnull(comp.get("Spent_Amount"), 0);
                comp_data = Map();
                comp_data.put("Spent_Amount", current_spent + alloc_amt);

                /* Recalculate status based on consumption % */
                allocated_amt = ifnull(comp.get("Allocated_Amount"), 0);
                if (allocated_amt > 0)
                {
                    consumption = ((current_spent + alloc_amt) / allocated_amt) * 100;
                    if (consumption >= 100) { comp_data.put("Status", "Exceeded"); }
                    else if (consumption >= 90) { comp_data.put("Status", "90% Alert"); }
                    else if (consumption >= 80) { comp_data.put("Status", "80% Alert"); }
                    else { comp_data.put("Status", "Within Budget"); }
                }

                zoho.creator.updateRecord("budget_tracking", "Budget_Components", comp_id, comp_data);
            }
        }
    }
}
else
{
    /* Legacy: single Budget_Component via header field */
    /* (existing logic — keep unchanged) */
}
```

---

## 3. Budget Revisions (Embedded Subform Enhancement)

Add an embedded subform `Budget_Revisions` to the existing Budget_Plans form.

### Subform Field Configuration
| Label | Field Type | API Name | Required | Notes |
|---|---|---|---|---|
| Revision No | Auto Number | `Revision_No` | Yes | Format: `REV-{0000}` |
| Budget Component | Lookup → Budget_Components | `Budget_Component` | Yes | Which component was revised |
| Previous Allocated Amount | Currency | `Prev_Allocated_Amount` | Yes | Amount before revision |
| New Allocated Amount | Currency | `New_Allocated_Amount` | Yes | Amount after revision |
| Change Amount | Currency (Formula) | `Change_Amount` | No | `New_Amount − Previous_Amount` |
| Reason | Dropdown | `Reason` | No | `Overrun Approval`, `Scope Change`, `Management Adjustment`, `Reallocation`, `Other` |
| Approved By | User Picker | `Approved_By` | No | Who approved this change |
| Revised Date | Date/Time | `Revised_Date` | No | Auto timestamp |
| Notes | Multi Line | `Notes` | No | Details |

### Deluge — Auto-Create Budget Revision on Approval

Add this enhancement to the existing Budget_Approval On Submit Deluge (when Status = "Approved" with Modified_Budget_Amount):

```deluge
/* JUSTIFICATION: Budget revisions must be tracked with audit trail whenever the allocated amount changes — whether from overrun approval or manual adjustment. This creates an immutable history for budget changes */

/* ===== PSEUDOCODE =====
   Trigger: Extend existing Budget_Approval On Submit workflow

   When Status = "Approved" AND Modified_Budget_Amount is set AND > 0:
     1. Fetch the linked Budget_Component
     2. Get current Allocated_Amount
     3. If Modified_Budget_Amount != current Allocated_Amount:
          a. Fetch the parent Budget_Plan record
          b. Get the Budget_Revisions subform
          c. Create new revision row:
               Budget_Component = the linked component
               Previous_Allocated_Amount = current Allocated_Amount
               New_Allocated_Amount = Modified_Budget_Amount
               Reason = "Overrun Approval"
               Approved_By = current user (approver)
               Revised_Date = now
               Notes = "Approved by " + approver_name
          d. Append to Budget_Revisions list
          e. Update Budget_Plan record
          f. Update Budget_Component.Allocated_Amount = Modified_Budget_Amount
   ===== END PSEUDOCODE ===== */
```

---

## 4. Reports

| Report | Type | Source | Audience |
|--------|------|--------|----------|
| Audit Log by Date | Tabular (date range) | Audit_Log | Finance, Admin |
| Audit Log by Module | Tabular (filter by Module) | Audit_Log | Finance, Admin |
| User Activity Log | Tabular (group by Changed_By) | Audit_Log | Admin |
| Record Status History | Tabular (filter by Record_ID) | Audit_Log | Finance |
| Budget Revision History | Summary by Budget_Plan | Budget_Revisions | PM, Finance |
| Component Change Log | Tabular by Budget_Component | Budget_Revisions | PM, Finance |
| Expense Allocation Summary | Summary by Budget_Component | Expense_Allocations | PM, Finance |

---

## Verification Checklist

- [ ] Audit_Log form created with correct field types
- [ ] Audit_Log permissions set to Finance/Admin only (write-only via Deluge)
- [ ] Audit log entry created on Expense Submit status change
- [ ] Audit log entry created on PO status change
- [ ] Audit log entry created on Bill status change
- [ ] Audit log entry created on Invoice status change
- [ ] Audit log entry created on Payment status change
- [ ] Audit log entry created on SCN status change
- [ ] Audit log entry created on GRN status change
- [ ] Expense_Allocations subform added to Expenses
- [ ] Sum validation: total allocation must equal expense amount
- [ ] Multi-component budget update works correctly
- [ ] Legacy single-component behavior preserved when no allocations exist
- [ ] Budget_Revisions subform added to Budget_Plans
- [ ] Revision auto-created when Budget_Approval modifies budget amount
- [ ] Budget_Component.Allocated_Amount updates correctly on revision
- [ ] Budget Revision History report works
- [ ] User Activity report works
