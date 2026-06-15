# Phase 1C Build Guide — Expenses → Purchase Requisitions

## Dependencies
Requires Phase 1B complete (Budget_Plans, Budget_Components, Inventory_Transactions forms exist).

---

## 1.8 Expenses Form (`Expenses`)

### Field Configuration
| Label | Field Type | API Name | Required | Notes |
|---|---|---|---|---|
| Expense No | Auto Number | `Expense_No` | Yes | Format: `EXP-{0000}` |
| Expense Type | Dropdown | `Expense_Type` | Yes | `Material Purchase, Service, Travel, Equipment, Labor, Miscellaneous` |
| Project | Lookup → Projects | `Project` | Yes | |
| Budget Component | Lookup → Budget_Components | `Budget_Component` | Yes | Which budget line this hits |
| Vendor | Lookup → Vendors | `Vendor` | No | |
| Amount | Currency | `Amount` | Yes | Total expense amount |
| Expense Date | Date | `Expense_Date` | No | Defaults to today |
| Description | Multi Line | `Description` | No | |
| Billable | Checkbox | `Billable` | No | Can be billed to client |
| Status | Dropdown | `Status` | No | `Draft, Submitted, Approved, Rejected, Overrun-Pending Approval` |
| Receipt | Upload | `Receipt` | No | |
| Created By | User Picker | `Created_By` | No | Defaults to current user |

### Validation Rules
1. **Positive Amount** — On Submit, if `Amount <= 0` → `throw "Amount must be positive."`
2. **Budget Component belongs to Project** — On Submit, verify Budget_Component.Budget_Plan.Project matches input.Project.

### Deluge Scripts

#### On Submit — Budget Check & Auto-Approval
```deluge
/* Phase 1C — Expenses: On Submit
   Check budget consumption and auto-approve or flag overrun */
expense_amount = ifnull(input.Amount, 0);
comp_id = input.Budget_Component;
proj_id = input.Project;

if (!comp_id.isNull() && expense_amount > 0)
{
    /* Get budget component */
    comp = zoho.creator.getRecordById("budget_tracking", "Budget_Components", comp_id);
    if (comp.isNull())
    {
        throw "Budget Component not found.";
    }

    allocated = ifnull(comp.get("Allocated_Amount"), 0);
    spent = ifnull(comp.get("Spent_Amount"), 0);

    /* Validate component belongs to this project's budget plan */
    plan_id = comp.get("Budget_Plan");
    plan = zoho.creator.getRecordById("budget_tracking", "Budget_Plans", plan_id);
    if (!plan.isNull())
    {
        plan_project = plan.get("Project");
        if (!plan_project.isNull() && plan_project.toString() != proj_id.toString())
        {
            throw "Selected Budget Component does not belong to this project.";
        }

        plan_status = ifnull(plan.get("Status").toMap().get("display_value"), "");
        if (plan_status != "Active")
        {
            throw "The budget plan for this component is not Active.";
        }
    }

    new_spent = spent + expense_amount;
    utilization = (new_spent / allocated) * 100;

    if (new_spent > allocated)
    {
        /* Overrun — set status to pending approval */
        status_data = Map();
        status_data.put("Status", "Overrun-Pending Approval");
        zoho.creator.updateRecord("budget_tracking", "Expenses", input.ID, status_data);

        /* Create budget approval request */
        approval_data = Map();
        approval_data.put("Expense", input.ID);
        approval_data.put("Project", proj_id);
        approval_data.put("Budget_Component", comp_id);
        approval_data.put("Requested_Amount", expense_amount);
        approval_data.put("Excess_Amount", new_spent - allocated);
        approval_data.put("Status", "Pending");
        approval_data.put("Utilization_Pct", utilization);
        zoho.creator.createRecord("budget_tracking", "Budget_Approvals", approval_data);
    }
    else
    {
        /* Within budget — auto-approve */
        status_data = Map();
        status_data.put("Status", "Approved");
        zoho.creator.updateRecord("budget_tracking", "Expenses", input.ID, status_data);
    }
}
```

#### On Post Submit — Update Budget Component Spent Amount
```deluge
/* Phase 1C — Expenses: On Post Submit
   Update Budget_Component.Spent_Amount */
expense_amount = ifnull(input.Amount, 0);
comp_id = input.Budget_Component;
expense_status = ifnull(input.Status.toMap().get("display_value"), "");

if (!comp_id.isNull() && expense_amount > 0 && expense_status == "Approved")
{
    comp = zoho.creator.getRecordById("budget_tracking", "Budget_Components", comp_id);
    if (!comp.isNull())
    {
        current_spent = ifnull(comp.get("Spent_Amount"), 0);
        update_data = Map();
        update_data.put("Spent_Amount", current_spent + expense_amount);
        zoho.creator.updateRecord("budget_tracking", "Budget_Components", comp_id, update_data);
    }
}
```

#### Scheduled Workflow — Daily Budget Alerts
```deluge
/* Phase 1C — Scheduled (Daily Midnight)
   Send budget alerts at 80%, 90%, 100% consumption */
active_plans = zoho.creator.getRecords("budget_tracking", "Budget_Plans", "Status == 'Active'", 1, 200);

if (!active_plans.isNull())
{
    for each plan in active_plans
    {
        plan_id = plan.get("ID");
        criteria = "Budget_Plan == " + plan_id;
        components = zoho.creator.getRecords("budget_tracking", "Budget_Components", criteria, 1, 200);

        if (!components.isNull())
        {
            for each comp in components
            {
                allocated = ifnull(comp.get("Allocated_Amount"), 0);
                spent = ifnull(comp.get("Spent_Amount"), 0);

                if (allocated > 0)
                {
                    pct = (spent / allocated) * 100;

                    if (pct >= 100)
                    {
                        /* Send 100% alert */
                        comp_name = ifnull(comp.get("Component_Name"), "Unknown");
                        subject = "Budget Exhausted: " + comp_name;
                        msg = "Component '" + comp_name + "' has reached 100% utilization. Amount: "
                            + spent.toString() + " / " + allocated.toString();
                        /* zoho.creator.sendMail("admin@company.com", subject, msg); */
                        /* Log to notification form or email */
                    }
                    else if (pct >= 90)
                    {
                        /* Send 90% alert */
                    }
                    else if (pct >= 80)
                    {
                        /* Send 80% alert */
                    }
                }
            }
        }
    }
}
```

---

## 1.9 Purchase Requisitions Form (`Purchase_Requisitions`)

Custom module (Zoho Books has no native PR). Feeds into Purchase Orders.

### Field Configuration
| Label | Field Type | API Name | Required | Notes |
|---|---|---|---|---|
| Requisition No | Auto Number | `Requisition_No` | Yes | Format: `REQ-{0000}` |
| Request Type | Dropdown | `Request_Type` | No | `General, Part Repair, Service` — default General |
| Subject | Single Line | `Subject` | No | Brief title |
| Project | Lookup → Projects | `Project` | No | |
| Requested By | User Picker | `Requested_By` | No | Defaults to current user |
| Requested Date | Date | `Requested_Date` | No | Defaults to today |
| Delivery Date | Date | `Delivery_Date` | No | Required by date |
| Urgency | Dropdown | `Urgency` | No | `Low, Medium, High, Critical` |
| Justification | Multi Line | `Justification` | No | |
| Status | Dropdown | `Status` | No | `Draft, Open, Approved, Rejected, Closed` |
| Approval Stage | Dropdown | `Approval_Stage` | No | `Pending Dept Approval, Pending Finance Approval, Pending Procurement, Approved` |
| Notes | Multi Line | `Notes` | No | Internal |

### Subforms (Add-as-Subform)

**PR Line Items** — Form: `PR_Line_Items`
| Label | Field Type | API Name | Notes |
|---|---|---|---|
| Requisition | Lookup → Purchase_Requisitions | `Requisition` | |
| Item | Lookup → Inventory_Items | `Item` | Optional — free-text description fallback |
| Item Description | Single Line | `Item_Description` | Free text |
| Quantity | Decimal | `Quantity` | |
| Estimated Unit Rate | Currency | `Estimated_Unit_Rate` | |
| Estimated Total | Formula | `Estimated_Total` | `Quantity * Estimated_Unit_Rate` |
| Item Type | Single Line | `Item_Type` | Copied from Item |
| Account | Lookup → Chart_of_Accounts | `Account` | Maps to Books `account_id` |
| Unit | Single Line | `Unit` | Copied from Item |

### Deluge Scripts

#### On Submit — Multi-Stage Approval Email
```deluge
/* Phase 1C — Purchase_Requisitions: On Submit
   Send email notification on status change */
status_val = ifnull(input.Status.toMap().get("display_value"), "");
approval_stage = ifnull(input.Approval_Stage.toMap().get("display_value"), "");
req_no = ifnull(input.Requisition_No, "");
subject_line = ifnull(input.Subject, "No Subject");

if (status_val == "Open")
{
    /* First submission — notify Department Manager */
    /* Email to dept manager role */
    email_body = "A new Purchase Requisition requires your approval:\n\n"
        + "Requisition: " + req_no + "\n"
        + "Subject: " + subject_line + "\n"
        + "Amount: " + ifnull(input.Estimated_Total, 0).toString() + "\n\n"
        + "Please review and approve in the system.";

    /* zoho.creator.sendMail("dept.manager@company.com",
        "PR Approval Required: " + req_no, email_body); */

    /* Set initial approval stage */
    stage_data = Map();
    stage_data.put("Approval_Stage", "Pending Dept Approval");
    zoho.creator.updateRecord("budget_tracking", "Purchase_Requisitions", input.ID, stage_data);
}
```

#### On Approval Stage Change — Cascade to Next Approver
```deluge
/* Phase 1C — Purchase_Requisitions: On Submit
   Approval stage progression */
approval_stage = ifnull(input.Approval_Stage.toMap().get("display_value"), "");
req_no = ifnull(input.Requisition_No, "");

next_email = "";
next_stage = "";

if (approval_stage == "Pending Dept Approval")
{
    next_email = "finance@company.com";
    next_stage = "Pending Finance Approval";
}
else if (approval_stage == "Pending Finance Approval")
{
    next_email = "procurement@company.com";
    next_stage = "Pending Procurement";
}
else if (approval_stage == "Pending Procurement")
{
    next_stage = "Approved";

    /* Auto-create Purchase Order */
    pr_id = input.ID;
    po_data = Map();
    po_data.put("Requisition", pr_id);
    po_data.put("Project", input.Project);
    po_data.put("Status", "Draft");
    po_data.put("Notes", "Auto-created from PR: " + req_no);

    /* Get vendor from PR items if available */
    items_criteria = "Requisition == " + pr_id;
    line_items = zoho.creator.getRecords("budget_tracking", "PR_Line_Items", items_criteria, 1, 200);

    if (!line_items.isNull() && line_items.size() > 0)
    {
        /* Take first item's preferred vendor if available */
        first_item = line_items.get(0);
        item_id = first_item.get("Item");
        if (!item_id.isNull())
        {
            item = zoho.creator.getRecordById("budget_tracking", "Inventory_Items", item_id);
            if (!item.isNull())
            {
                pref_vendor = item.get("Preferred_Vendor");
                if (!pref_vendor.isNull())
                {
                    po_data.put("Vendor", pref_vendor);
                }
            }
        }
    }

    /* Create the PO */
    created_po = zoho.creator.createRecord("budget_tracking", "Purchase_Orders", po_data);

    /* Copy PR line items to PO line items */
    if (!line_items.isNull() && !created_po.isNull())
    {
        po_id = created_po.get("ID");
        for each li in line_items
        {
            po_li = Map();
            po_li.put("PO", po_id);
            po_li.put("Item", li.get("Item"));
            po_li.put("Description", li.get("Item_Description"));
            po_li.put("Quantity", li.get("Quantity"));
            po_li.put("Unit_Rate", li.get("Estimated_Unit_Rate"));
            po_li.put("Account", li.get("Account"));
            po_li.put("Unit", li.get("Unit"));
            zoho.creator.createRecord("budget_tracking", "PO_Line_Items", po_li);
        }
    }
}

/* Send email notification to next approver */
if (next_stage != "" && next_stage != "Approved")
{
    email_body = "Purchase Requisition " + req_no + " has been approved at stage '" + approval_stage
        + "'. Please review for " + next_stage + ".";
    /* zoho.creator.sendMail(next_email, "PR Next Approval: " + req_no, email_body); */
}

/* Update approval stage */
if (next_stage != "")
{
    stage_data = Map();
    stage_data.put("Approval_Stage", next_stage);
    zoho.creator.updateRecord("budget_tracking", "Purchase_Requisitions", input.ID, stage_data);
}
```

---

## Build Verification Checklist
1. Expenses form creates EXP-0001, EXP-0002...
2. Budget check works: expenses within budget auto-approve
3. Budget check works: expenses exceeding budget → Overrun-Pending Approval
4. Overrun creates Budget_Approval record automatically
5. Approved expenses update Budget_Component.Spent_Amount
6. Purchase Requisitions creates REQ-0001, REQ-0002...
7. PR 3-stage approval chain works (Dept → Finance → Procurement)
8. PR final approval auto-creates PO in Draft with copied line items
9. PR Request Type "Part Repair" correctly pre-fills from Project custom action

## Next Phase
→ Proceed to `PHASE_1D_BUILD.md` when all above forms are verified.
