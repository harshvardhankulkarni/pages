# Phase 1C Build Guide — Expenses → Purchase Requisitions

## Dependencies
Requires Phase 1B complete (Budget_Plans, Budget_Components, Inventory_Transactions forms exist).

---

## 1.8 Expenses Form (`Expenses`)

### Field Configuration
| Label | Field Type | API Name | Required | Notes |
|---|---|---|---|---|
| Expense No | Auto Number | `Expense_No` | Yes | Format: `EXP-{0000}` |
| Project | Lookup → Projects | `Project` | Yes | |
| Budget Component | Lookup → Budget_Components | `Budget_Component` | Yes | Which budget line this hits |
| Vendor | Lookup → Vendors | `Vendor` | No | |
| Amount | Currency | `Amount` | Yes | Total expense amount |
| Expense Type | Dropdown | `Expense_Type` | Yes | `Material, Labour, Equipment, Travel, Subcontract, Overhead, Other` — Category for reporting |
| Expense Date | Date | `Expense_Date` | No | Defaults to today |
| Description | Multi Line | `Description` | No | |
| Billable | Checkbox | `Billable` | No | Can be billed to client |
| Status | Dropdown | `Status` | No | `Draft, Submitted, Approved, Rejected, Overrun-Pending Approval` |
| Receipt | Upload | `Receipt` | No | |
| Created By | User Picker | `Created_By` | No | Defaults to current user |

### Validation Rules
1. **Positive Amount** — On Submit, if `Amount <= 0` → `alert "Amount must be positive."`
2. **Budget Component belongs to Project** — On Submit, verify Budget_Component.Budget_Plan.Project matches input.Project.
3. **Budget Plan must be Active** — On Submit, verify parent Budget_Plan.Status = "Active".
4. **Duplicate Prevention** — On Submit, check no duplicate expense with same Project + Component + Date + Amount.

### Workflow / Approval Process

```
Expense Submitted
    │
    ├── Budget Component found? ── No ──→ Alert error
    │
    ├── Belongs to this Project? ── No ──→ Alert error
    │
    ├── Budget Plan is Active? ── No ──→ Alert error
    │
    ├── Amount ≤ Allocated Budget?
    │       ├── Yes → Auto-Approve (Status = "Approved")
    │       │         → Update Budget_Component.Spent_Amount
    │       │
    │       └── No  → Overrun (Status = "Overrun-Pending Approval")
    │                   → Create Budget_Approval record
    │                   → Notify PM + Finance Manager
    │
    └── Approved? ── Yes → Spent_Amount updated
        └── Rejected?    → Expense stays Rejected
```

### Deluge Scripts

#### On Submit — Budget Check & Auto-Approval
```deluge
/* JUSTIFICATION: Budget check and overrun approval creation require cross-form queries to Budget_Components and Budget_Plans — cannot be handled by embedded subform submission alone */
/* ===== PSEUDOCODE =====
   Trigger: On Submit — when Expense record is created or updated
   
   1. Get the expense amount, budget component ID, and project ID from input
   2. If budget component is set AND amount is positive:
      a. Fetch the Budget_Component record by ID
      b. If not found: alert error "Budget Component not found"
      c. Get Allocated_Amount and current Spent_Amount from the component
      d. Fetch the parent Budget_Plan record
      e. If plan exists:
         - Verify the component's plan project matches the expense project
         - If mismatch: alert error "does not belong to this project"
         - Verify the plan Status is "Active"
         - If not active: alert error "budget plan is not Active"
      f. Calculate projected new spent amount and utilization percentage
      g. If new spent exceeds allocated:
         - Update expense Status to "Overrun-Pending Approval"
         - Create a Budget_Approval record with Pending status
         - Include expense, project, component, amounts, and utilization
      h. If within budget:
         - Update expense Status to "Approved" (auto-approve)
   3. If no component or amount is 0: skip all budget checks
   ===== END PSEUDOCODE ===== */
expense_amount = ifnull(input.Amount, 0);
comp_id = input.Budget_Component;
proj_id = input.Project;

if (!comp_id.isNull() && expense_amount > 0)
{
    comp = zoho.creator.getRecordById("budget_tracking", "Budget_Components", comp_id);
    if (comp.isNull())
    {
        alert "Budget Component not found.";
    }

    allocated = ifnull(comp.get("Allocated_Amount"), 0);
    spent = ifnull(comp.get("Spent_Amount"), 0);

    plan_id = comp.get("Budget_Plan");
    plan = zoho.creator.getRecordById("budget_tracking", "Budget_Plans", plan_id);
    if (!plan.isNull())
    {
        plan_project = plan.get("Project");
        if (!plan_project.isNull() && plan_project.toString() != proj_id.toString())
        {
            alert "Selected Budget Component does not belong to this project.";
        }

        plan_status = ifnull(plan.get("Status").toMap().get("display_value"), "");
        if (plan_status != "Active")
        {
            alert "The budget plan for this component is not Active.";
        }
    }

    new_spent = spent + expense_amount;
    utilization = (new_spent / allocated) * 100;

    if (new_spent > allocated)
    {
        status_data = Map();
        status_data.put("Status", "Overrun-Pending Approval");
        zoho.creator.updateRecord("budget_tracking", "Expenses", input.ID, status_data);

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
        status_data = Map();
        status_data.put("Status", "Approved");
        zoho.creator.updateRecord("budget_tracking", "Expenses", input.ID, status_data);
    }
}
```

#### On Post Submit — Update Budget Component Spent Amount
```deluge
/* JUSTIFICATION: Spent_Amount update on Budget_Component requires cross-form update — cannot be handled by embedded subform submission alone */
/* ===== PSEUDOCODE =====
   Trigger: On Post Submit — after Expense record is saved
   
   1. Get the expense amount, budget component ID, and expense status from input
   2. If component is valid AND amount is positive AND status is "Approved":
      a. Fetch the Budget_Component record by ID
      b. If component exists:
         - Get the current Spent_Amount value
         - Add this expense amount to the spent total
         - Update the component's Spent_Amount with the new total
   3. If status is not "Approved" (Overrun-Pending, Rejected, Draft, etc.):
      skip — amount is not yet committed to the budget
   ===== END PSEUDOCODE ===== */
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
/* JUSTIFICATION: Scheduled periodic check across all active budget plans — cannot be handled by any On Submit/embedded subform trigger */
/* ===== PSEUDOCODE =====
   Trigger: Scheduled (Daily Midnight) — runs once per day
   
   1. Fetch all Budget_Plans with Status = "Active" (up to 200 records)
   2. If active plans exist:
      For each plan:
      a. Query all Budget_Components linked to this plan
      b. If components exist:
         For each component:
         i.   Get Allocated_Amount and current Spent_Amount
         ii.  If allocated > 0, calculate utilization percentage
         iii. If utilization >= 100%:
              - Build email subject and body with component details
              - (Placeholder) Send email alert — uncomment sendMail call with admin address
         iv.  If utilization >= 90%:
              - (Placeholder) Send 90% threshold warning email
         v.   If utilization >= 80%:
              - (Placeholder) Send 80% threshold warning email
         vi.  If utilization < 80%: no alert needed
   3. If no active plans: exit (nothing to check)
   ===== END PSEUDOCODE ===== */
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
                        comp_name = ifnull(comp.get("Component_Name"), "Unknown");
                        subject = "Budget Exhausted: " + comp_name;
                        msg = "Component '" + comp_name + "' has reached 100% utilization. Amount: "
                            + spent.toString() + " / " + allocated.toString();
                    }
                    else if (pct >= 90)
                    {
                    }
                    else if (pct >= 80)
                    {
                    }
                }
            }
        }
    }
}
```

---

## 1.9 Purchase Requisitions Form (`Purchase_Requisitions`)

Feeds into Purchase Orders via auto-PO on approval.

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

### Embedded Subform: PR Line Items (API Name: PR_Line_Items)
| Label | Field Type | API Name | Required | Notes |
|---|---|---|---|---|
| Item | Lookup → Inventory_Items | Item | No | Lookup → Inventory_Items. One of Item or Item Description required — add validation rule |
| Item Description | Single Line | Item_Description | No | Free-text fallback |
| Quantity | Decimal | Quantity | Yes | |
| Unit | Single Line | Unit | No | Formula: Item.Unit (auto-fills from selected Item) |
| Estimated Unit Rate | Currency | Estimated_Unit_Rate | Yes | |
| Item Type | Single Line | Item_Type | No | Formula: Item.Item_Type (auto-fills from selected Item) |
| Total | Currency | Total | No | Formula: Quantity * Estimated_Unit_Rate |
| Notes | Multi Line | Notes | No | |

### Validation Rules
1. **Required fields on Submit** — Subject, Project, and at least one line item required when Status = "Open".
2. **Urgency validation** — If Urgency = "Critical", justification is required.

### Approval Process (3-Stage Blueprint)

```
PR Created (Status = Draft)
    │
    └── User submits (Status → Open)
            │
            ├── Stage 1: Pending Dept Approval
            │       ├── Approve → Stage 2
            │       └── Reject  → Status = Rejected
            │
            ├── Stage 2: Pending Finance Approval
            │       ├── Approve → Stage 3
            │       └── Reject  → Status = Rejected
            │
            ├── Stage 3: Pending Procurement
            │       ├── Approve → Status = Approved
            │       │            → Auto-create PO (Draft)
            │       │            → Copy PR line items to PO
            │       └── Reject  → Status = Rejected
            │
            └── Approved → PO auto-generated in Draft
```

**Stage Transitions:**
| From | To | Trigger | Action |
|---|---|---|---|
| Draft | Open | User clicks Submit | Notify Dept Manager |
| Pending Dept Approval | Pending Finance | Dept Manager approves | Notify Finance Manager |
| Pending Finance | Pending Procurement | Finance approves | Notify Procurement |
| Pending Procurement | Approved | Procurement approves | Auto-create PO + copy line items |
| Any | Rejected | Any approver rejects | Status = Rejected, notify requester |

### Deluge Scripts

#### On Submit — Multi-Stage Approval Email
```deluge
/* JUSTIFICATION: Multi-stage approval email notification and stage advancement require standalone form processing — cannot be handled by embedded subform submission alone */
/* ===== PSEUDOCODE =====
   Trigger: On Submit — when Purchase_Requisition is created/updated
   
   1. Get the status display value, approval stage, requisition number, and subject
   2. If status is "Open" (first submission after Draft):
      a. Build email body with requisition details (number, subject, estimated total)
      b. (Placeholder) Send notification email to Department Manager
      c. Update the Approval_Stage to "Pending Dept Approval"
   3. If status is not "Open": skip — no notification needed
   ===== END PSEUDOCODE ===== */
status_val = ifnull(input.Status.toMap().get("display_value"), "");
approval_stage = ifnull(input.Approval_Stage.toMap().get("display_value"), "");
req_no = ifnull(input.Requisition_No, "");
subject_line = ifnull(input.Subject, "No Subject");

if (status_val == "Open")
{
    email_body = "A new Purchase Requisition requires your approval:\n\n"
        + "Requisition: " + req_no + "\n"
        + "Subject: " + subject_line + "\n"
        + "Amount: " + ifnull(input.Estimated_Total, 0).toString() + "\n\n"
        + "Please review and approve in the system.";

    stage_data = Map();
    stage_data.put("Approval_Stage", "Pending Dept Approval");
    zoho.creator.updateRecord("budget_tracking", "Purchase_Requisitions", input.ID, stage_data);
}
```

#### On Approval Stage Change — Cascade to Next Approver
```deluge
/* JUSTIFICATION: Auto-PO creation with line item copy, stage cascading, and email notifications require cross-form processing — cannot be handled by embedded subform submission */
/* ===== PSEUDOCODE =====
   Trigger: On Submit — when Approval_Stage field changes on Purchase_Requisition
   
   1. Get the current approval stage display value and requisition number
   2. Initialize next_email and next_stage as empty strings
   
   CASE A — Current stage is "Pending Dept Approval":
      a. Set next email to finance manager
      b. Set next stage to "Pending Finance Approval"
   
   CASE B — Current stage is "Pending Finance Approval":
      a. Set next email to procurement team
      b. Set next stage to "Pending Procurement"
   
   CASE C — Current stage is "Pending Procurement" (final approval):
      a. Set next stage to "Approved"
      b. Build Purchase_Order data map with:
         - Linked requisition ID
         - Project from the PR
         - Status = "Draft"
         - Notes referencing the PR number
      c. Access PR_Line_Items via input.PR_Line_Items (embedded subform)
      d. If line items exist:
         - Try to get the first item's Preferred_Vendor
         - If vendor found: add to PO data
         - Build PO_Line_Items list as embedded subform data
         - Add PO_Line_Items to the PO data map
      e. Create the Purchase_Order record with embedded PO_Line_Items
   
   3. If next_stage is not empty AND not "Approved":
      a. Build email body notifying the next approver
      b. (Placeholder) Send notification email
   
   4. If next_stage is not empty:
      a. Update the Approval_Stage field on the PR
   ===== END PSEUDOCODE ===== */
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

    pr_id = input.ID;
    po_data = Map();
    po_data.put("Requisition", pr_id);
    po_data.put("Project", input.Project);
    po_data.put("Status", "Draft");
    po_data.put("Notes", "Auto-created from PR: " + req_no);

    /* PR_Line_Items is embedded subform — access via input */
    line_items = input.PR_Line_Items;

    if (!line_items.isNull() && line_items.size() > 0)
    {
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

        /* Include PO_Line_Items as embedded subform data in the PO */
        po_line_items_list = List();
        for each li in line_items
        {
            po_li = Map();
            po_li.put("Item", li.get("Item"));
            po_li.put("Description", li.get("Item_Description"));
            po_li.put("Quantity", li.get("Quantity"));
            po_li.put("Unit_Rate", li.get("Estimated_Unit_Rate"));
            po_li.put("Unit", li.get("Unit"));
            po_line_items_list.add(po_li);
        }
        po_data.put("PO_Line_Items", po_line_items_list);
    }

    created_po = zoho.creator.createRecord("budget_tracking", "Purchase_Orders", po_data);
}

if (next_stage != "" && next_stage != "Approved")
{
    email_body = "Purchase Requisition " + req_no + " has been approved at stage '" + approval_stage
        + "'. Please review for " + next_stage + ".";
}

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
