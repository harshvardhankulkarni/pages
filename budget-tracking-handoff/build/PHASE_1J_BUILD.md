# Phase 1J Build Guide — PO/Bill/Payment Approval + Budget Checks + Segregation of Duties

## Dependencies
Requires all prior phases complete. Enhances Purchase_Orders, Vendor_Bills, Payments, Purchase_Requisitions, and Budget_Components forms with approval workflows and budget checks.

---

## 1. Purchase Orders — Approval Workflow Enhancement

### New/Modified Fields
Add these fields to the existing Purchase_Orders form:

| Label | Field Type | API Name | Required | Notes |
|---|---|---|---|---|
| Approval Status | Dropdown | `Approval_Status` | No | `Not Required`, `Pending Approval`, `Approved`, `Rejected` |
| Approver | User Picker | `Approver` | No | Who approved/rejected this PO |
| Approval Date | Date/Time | `Approval_Date` | No | When approved |
| Approval Notes | Multi Line | `Approval_Notes` | No | Approval comments |
| Budget Check Status | Dropdown | `Budget_Check_Status` | No | `Passed`, `Failed — Over Budget`, `Not Checked` |

### Updated Status Lifecycle
Change the Status dropdown to include:
`Draft`, `Pending Approval`, `Approved`, `Rejected`, `Open`, `Partially Invoiced`, `Billed`, `Closed`, `Cancelled`

### Deluge — Budget Check + Approval Routing

Add this to the On Submit workflow:

```deluge
/* JUSTIFICATION: PO approval routing and budget commitment are cross-form operations that cannot be handled by form-level validation. Budget check reads Budget_Components across the linked project; approval routing depends on PO value thresholds. */

status_val = ifnull(input.Status.toMap().get("display_value"), "");
po_total = ifnull(input.Total, 0);
project_id = input.Project;

/* ── Draft → Pending Approval ── */
if (status_val == "Pending Approval")
{
    approval_threshold = 5000; /* Configurable: default $5,000 */

    if (po_total <= approval_threshold)
    {
        /* Auto-approve below threshold */
        po_data = Map();
        po_data.put("Approval_Status", "Approved");
        po_data.put("Status", "Open");
        po_data.put("Approver", zoho.currentuser);
        po_data.put("Approval_Date", now());

        /* Budget check */
        budget_ok = checkBudgetAvailability(project_id, po_total);
        if (budget_ok)
        {
            po_data.put("Budget_Check_Status", "Passed");
            commitBudget(project_id, po_total);
        }
        else
        {
            po_data.put("Budget_Check_Status", "Failed — Over Budget");
            alert "Warning: Project budget may be insufficient. PO created but flag manually reviewed.";
        }

        zoho.creator.updateRecord("budget_tracking", "Purchase_Orders", input.ID, po_data);
    }
    else
    {
        /* Above threshold — send for approval */
        /* Notification to approver would go here */
        po_data = Map();
        po_data.put("Approval_Status", "Pending Approval");
        zoho.creator.updateRecord("budget_tracking", "Purchase_Orders", input.ID, po_data);
    }
}

/* ── Approved by Approver ── */
if (status_val == "Approved" && input.Approval_Status == "Pending Approval")
{
    po_data = Map();
    po_data.put("Approval_Status", "Approved");
    po_data.put("Approver", zoho.currentuser);
    po_data.put("Approval_Date", now());
    po_data.put("Status", "Open");

    budget_ok = checkBudgetAvailability(project_id, po_total);
    if (budget_ok)
    {
        po_data.put("Budget_Check_Status", "Passed");
        commitBudget(project_id, po_total);
    }
    else
    {
        po_data.put("Budget_Check_Status", "Failed — Over Budget");
        alert "Warning: Project budget may be insufficient.";
    }

    zoho.creator.updateRecord("budget_tracking", "Purchase_Orders", input.ID, po_data);

    /* Email vendor with PO details (existing automation) */
}

/* ── Rejected ── */
if (status_val == "Rejected")
{
    po_data = Map();
    po_data.put("Approval_Status", "Rejected");
    po_data.put("Approver", zoho.currentuser);
    po_data.put("Approval_Date", now());
    zoho.creator.updateRecord("budget_tracking", "Purchase_Orders", input.ID, po_data);
}

/* ── Cancelled — release committed budget ── */
if (status_val == "Cancelled")
{
    releaseBudget(project_id, po_total);
}

/* ── Helper: checkBudgetAvailability ── */
/* Note: In actual Deluge, implement this as inline logic */
function checkBudgetAvailability(project, amount)
{
    /* Query Budget_Components where Project == project */
    /* Sum (Allocated_Amount − Spent_Amount − Committed_Amount) across components */
    /* Return true if total_remaining >= amount */
    return true; /* placeholder */
}

/* ── Helper: commitBudget ── */
function commitBudget(project, amount)
{
    /* Distribute PO total across Budget_Components proportionally */
    /* For each component: Committed_Amount += (component_allocated / total_allocated) × PO_total */
}

/* ── Helper: releaseBudget ── */
function releaseBudget(project, amount)
{
    /* Reverse the commitment: Committed_Amount -= previously committed portion */
}
```

---

## 2. Vendor Bills — Manual Approval Enhancement

### Modified Status Dropdown
Change to include: `Draft`, `Received`, `Matched`, `Pending Approval`, `Approved`, `Partially Paid`, `Paid`, `Cancelled`

### Deluge — Bill Approval Routing

Add to the On Submit workflow of Vendor_Bills:

```deluge
/* JUSTIFICATION: Bill approval requires finance manager review after 3-way match. Auto-approval would bypass financial control. This cannot be handled by form-level validation. */

status_val = ifnull(input.Status.toMap().get("display_value"), "");

/* ── Matched → Pending Approval (instead of auto-Approved) ── */
if (status_val == "Matched")
{
    /* 3-way match logic runs first (existing) */
    /* If match passes: set to Pending Approval instead of Approved */
    bill_data = Map();
    bill_data.put("Status", "Pending Approval");
    zoho.creator.updateRecord("budget_tracking", "Vendor_Bills", input.ID, bill_data);

    /* Send notification to Finance Manager for approval */
}

/* ── Pending Approval → Approved ── */
if (status_val == "Approved")
{
    /* Finance Manager manually approves */
    bill_data = Map();
    bill_data.put("Status", "Approved");

    /* Calculate and record PPV */
    /* ... existing PPV calculation logic ... */

    zoho.creator.updateRecord("budget_tracking", "Vendor_Bills", input.ID, bill_data);
}

/* ── Pending Approval → Rejected → back to Matched for revision ── */
if (status_val == "Rejected")
{
    bill_data = Map();
    bill_data.put("Status", "Matched");
    bill_data.put("Notes", ifnull(input.Notes, "") + " | Rejected: " + ifnull(input.Approval_Notes, "No reason given"));
    zoho.creator.updateRecord("budget_tracking", "Vendor_Bills", input.ID, bill_data);
}
```

---

## 3. Payments — Approval Workflow Enhancement

### Modified Status Dropdown
Change to include: `Draft`, `Pending Approval`, `Approved`, `Completed`, `Reversed`, `Failed`

### New Fields
| Label | Field Type | API Name | Required | Notes |
|---|---|---|---|---|
| Approval Threshold | Currency | `Approval_Threshold` | No | Read-only, defaults to $5,000 |
| Approver | User Picker | `Approver` | No | Who approved this payment |
| Approval Date | Date/Time | `Approval_Date` | No | When approved |

### Deluge — Payment Approval Routing

```deluge
/* JUSTIFICATION: Payment approval prevents unauthorized disbursements. Threshold-based routing ensures large payments get manager review. */

status_val = ifnull(input.Status.toMap().get("display_value"), "");
pmt_amt = ifnull(input.Amount, 0);
threshold = 5000; /* Configurable */

/* ── Draft → Pending Approval or auto-Approved ── */
if (status_val == "Pending Approval")
{
    if (pmt_amt <= threshold)
    {
        /* Below threshold — auto-approve */
        pmt_data = Map();
        pmt_data.put("Status", "Approved");
        pmt_data.put("Approver", zoho.currentuser);
        pmt_data.put("Approval_Date", now());
        zoho.creator.updateRecord("budget_tracking", "Payments", input.ID, pmt_data);
    }
    /* else: stays Pending Approval — Finance Manager reviews */
}

/* ── Approved → Completed (execute payment) ── */
if (status_val == "Completed")
{
    /* Execute payment logic (existing) */
    /* Update linked Bill/Invoice Amount_Paid + Balance_Due + Status */
    /* ... existing payment execution code ... */

    /* Record approval if not already set */
    if (input.Approver.isNull())
    {
        pmt_data = Map();
        pmt_data.put("Approver", zoho.currentuser);
        pmt_data.put("Approval_Date", now());
        zoho.creator.updateRecord("budget_tracking", "Payments", input.ID, pmt_data);
    }
}
```

---

## 4. Purchase Requisition — Budget Check

### Modified Deluge — Final Approval Step

Add to the existing PR approval workflow (when Approval_Stage = "Approved"):

```deluge
/* JUSTIFICATION: PR final approval should validate budget availability before auto-creating PO. Prevents procurement commitments without budget. */

/* ── Add this check before auto-creating PO ── */
project_id = input.Project;
pr_lines = input.PR_Line_Items;

if (!project_id.isNull() && !pr_lines.isNull())
{
    /* Calculate estimated total from PR line items */
    est_total = 0;
    for each li in pr_lines
    {
        est_total = est_total + ifnull(li.get("Estimated_Total"), 0);
    }

    /* Check available budget across all components for this project */
    components = zoho.creator.getRecords("budget_tracking", "Budget_Components", "Project == " + project_id.toString());
    available = 0;
    if (!components.isNull())
    {
        for each comp in components
        {
            allocated = ifnull(comp.get("Allocated_Amount"), 0);
            spent = ifnull(comp.get("Spent_Amount"), 0);
            committed = ifnull(comp.get("Committed_Amount"), 0);
            available = available + (allocated - spent - committed);
        }
    }

    if (est_total > available)
    {
        alert "Insufficient budget. Estimated total: " + est_total.toString() + ". Available budget: " + available.toString() + ". Cannot auto-create PO.";
        return;
    }
}

/* Continue with auto-PO creation (existing logic) ... */
```

---

## 5. Budget Components — Committed Amount Tracking

### Enhancement to Budget_Components

Add these fields to the existing form:

| Label | Field Type | API Name | Required | Notes |
|---|---|---|---|---|
| Committed Amount | Currency | `Committed_Amount` | No | Maintained by Deluge — sum of Open PO values allocated to this component |
| Available Budget | Currency (Formula) | `Available_Budget` | No | `Allocated_Amount − Spent_Amount − Committed_Amount` — true remaining budget |

### Deluge — On PO Status Changes

Add this to the PO On Submit workflow (already included in the PO section above):

```deluge
/* Committed amount logic for Budget_Components */

function commitBudget(project_id, po_total)
{
    components = zoho.creator.getRecords("budget_tracking", "Budget_Components", "Project == " + project_id.toString());
    if (!components.isNull() && components.size() > 0)
    {
        total_allocated = 0;
        for each comp in components
        {
            total_allocated = total_allocated + ifnull(comp.get("Allocated_Amount"), 0);
        }

        if (total_allocated > 0)
        {
            for each comp in components
            {
                comp_alloc = ifnull(comp.get("Allocated_Amount"), 0);
                comp_committed = ifnull(comp.get("Committed_Amount"), 0);
                share = (comp_alloc / total_allocated) * po_total;
                comp_data = Map();
                comp_data.put("Committed_Amount", comp_committed + share);
                zoho.creator.updateRecord("budget_tracking", "Budget_Components", comp.get("ID"), comp_data);
            }
        }
    }
}

function releaseBudget(project_id, po_total)
{
    components = zoho.creator.getRecords("budget_tracking", "Budget_Components", "Project == " + project_id.toString());
    if (!components.isNull() && components.size() > 0)
    {
        total_allocated = 0;
        for each comp in components
        {
            total_allocated = total_allocated + ifnull(comp.get("Allocated_Amount"), 0);
        }

        if (total_allocated > 0)
        {
            for each comp in components
            {
                comp_alloc = ifnull(comp.get("Allocated_Amount"), 0);
                comp_committed = ifnull(comp.get("Committed_Amount"), 0);
                share = (comp_alloc / total_allocated) * po_total;
                comp_data = Map();
                comp_data.put("Committed_Amount", max(comp_committed - share, 0));
                zoho.creator.updateRecord("budget_tracking", "Budget_Components", comp.get("ID"), comp_data);
            }
        }
    }
}
```

---

## 6. Segregation of Duties — Role Configuration

### New/Merged Roles

| Role | Permission | Forms |
|------|-----------|-------|
| AP Clerk | Create, Edit (own) | Vendor_Bills, Payments (Draft) |
| AP Manager | Approve, Full Access | Vendor_Bills (approve), Payments (approve), all AP reports |
| AR Clerk | Create, Edit (own) | Invoices, Customer_Credit_Notes, Payments (Draft) |
| AR Manager | Approve, Full Access | Customer_Credit_Notes (issue/apply), Payments (approve AR), all AR reports |
| Procurement Manager | Approve, Full Access | POs (approve), PRs (final approval), Vendor management |
| Procurement User | Create, Edit (own) | PRs, POs (Draft), Vendor viewing |

### Form-Level Permission Configuration

Configure in Zoho Creator:
1. **Purchase_Orders**: Procurement User = Create/Edit Draft only. Procurement Manager = Full + Approval
2. **Vendor_Bills**: AP Clerk = Create/Edit (not Approve). AP Manager = Approve
3. **Payments**: AP/AR Clerk = Create Draft. AP/AR Manager = Approve
4. **Budget_Components**: Only Finance Manager = Edit Allocated_Amount
5. **Audit_Log**: Administrator + Finance Manager = Read Only. No one can write directly

---

## 7. Reports

| Report | Type | Source | Audience |
|--------|------|--------|----------|
| POs Pending Approval | Tabular (filter: Status = Pending Approval) | Purchase_Orders | Procurement Manager |
| Bills Pending Approval | Tabular (filter: Status = Pending Approval) | Vendor_Bills | AP Manager |
| Payments Pending Approval | Tabular (filter: Status = Pending Approval) | Payments | AP Manager |
| Budget Commitment Report | Summary by Project | Budget_Components | PM, Finance |
| Available Budget vs PO Value | Comparison report | Budget_Components + POs | PM, Finance |
| User Activity by Role | Audit_Log filtered by role | Audit_Log | Admin |

---

## Verification Checklist

- [ ] PO approval workflow: Draft → Pending Approval → Approved → Open
- [ ] PO auto-approve works below threshold ($5,000)
- [ ] PO approval notification sent to approver for above-threshold
- [ ] PO budget check blocks Open when budget insufficient
- [ ] PO budget commitment increments Budget_Component.Committed_Amount
- [ ] PO cancellation releases committed budget
- [ ] Bill approval: Matched → Pending Approval (not auto-Approved)
- [ ] Bill approval notification sent to AP Manager
- [ ] Payment approval: Draft → Pending Approval → Approved → Completed
- [ ] Payment auto-approve works below threshold
- [ ] Payment above threshold requires explicit approval
- [ ] PR budget check blocks final approval when budget insufficient
- [ ] Available Budget formula shows: Allocated − Spent − Committed
- [ ] AP Clerk cannot approve Bills (view only)
- [ ] AP Manager can approve Bills and Payments
- [ ] Procurement User can only create Draft POs
- [ ] Procurement Manager can approve POs
