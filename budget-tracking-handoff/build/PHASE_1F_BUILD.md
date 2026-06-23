# Phase 1F Build Guide — Reports & Dashboards

## Dependencies
Requires all prior phases complete (forms 1-16 exist with data).

---

## 1.18 Reports & Dashboards

### Overview
This phase creates all Zoho Creator Report and Dashboard widgets. No new forms — all reports are built on existing data.

---

### Report 1: Project P&L Statement
**Type:** Report on Projects with Lookup fields
**Purpose:** Show revenue (invoiced) − expenses per project

**Configuration:**
- **Source Form:** `Projects`
- **Fields:**
  - `Project_Name`
  - `Project_Code`
  - `Account` → Display Account Name
  - `Total_Approved_Budget`
  - Summary fields:
    - Total Invoiced (from Invoices where Status ≠ Cancelled)
    - Total Paid (from Invoices where Status = Paid)
    - Total Expenses (from Expenses where Status = Approved)
    - Net P&L = Total Invoiced − Total Expenses
    - Budget Utilization % = (Total Expenses / Total_Approved_Budget) × 100

**Deluge — Scheduled KPI Refresh (Daily)**
```deluge
/* JUSTIFICATION: Scheduled daily workflow that refreshes project P&L Currency fields (Total_Spent_Project, Total_Invoiced, Total_Paid) by querying related Expenses and Invoices. */
/* ===== PSEUDOCODE =====
   Trigger: Scheduled (Daily 1 AM) — refresh project P&L summary data
   
   1. Fetch all Projects (up to 200 records)
   2. If projects exist:
      For each project:
      a. Get the project ID
      b. Sum approved expenses:
         - Query Expenses where Project matches AND Status = "Approved"
         - For each expense found: add Amount to total_expenses
      c. Sum invoiced amounts:
         - Query Invoices where Project matches AND Status in
           ("Sent", "Partially Paid", "Paid")
         - For each invoice found:
           Add Total to total_invoiced
           Add Amount_Paid to total_paid
      d. Store calculated totals in the Projects form:
          - Update Total_Spent_Project with total_expenses
          - Update Total_Invoiced with total_invoiced
          - Update Total_Paid with total_paid
   3. If no projects exist: exit (nothing to refresh)
   ===== END PSEUDOCODE ===== */
active_projects = zoho.creator.getRecords("budget_tracking", "Projects", "", 1, 200);

if (!active_projects.isNull())
{
    for each proj in active_projects
    {
        proj_id = proj.get("ID");

        exp_criteria = "Project == " + proj_id + " && Status == 'Approved'";
        expenses = zoho.creator.getRecords("budget_tracking", "Expenses", exp_criteria, 1, 200);
        total_expenses = 0;
        if (!expenses.isNull())
        {
            for each exp in expenses
            {
                total_expenses = total_expenses + ifnull(exp.get("Amount"), 0);
            }
        }

        inv_criteria = "Project == " + proj_id + " && (Status == 'Sent' || Status == 'Partially Paid' || Status == 'Paid')";
        invoices = zoho.creator.getRecords("budget_tracking", "Invoices", inv_criteria, 1, 200);
        total_invoiced = 0;
        total_paid = 0;
        if (!invoices.isNull())
        {
            for each inv in invoices
            {
                total_invoiced = total_invoiced + ifnull(inv.get("Total"), 0);
                total_paid = total_paid + ifnull(inv.get("Amount_Paid"), 0);
            }
        }

        proj_data = Map();
        proj_data.put("Total_Spent_Project", total_expenses);
        proj_data.put("Total_Invoiced", total_invoiced);
        proj_data.put("Total_Paid", total_paid);
        zoho.creator.updateRecord("budget_tracking", "Projects", proj_id, proj_data);
    }
}
```

**Report Fields (Add to Projects form):**
| Field | Type | API Name | Notes |
|---|---|---|---|
| Total Invoiced | Formula | `Total_Invoiced` | Aggregate from Invoices report |
| Total Paid | Formula | `Total_Paid` | Aggregate from Invoices report |
| Total Expenses | Formula | `Total_Expenses` | Aggregate from Expenses report |
| P&L | Formula | `PnL` | `Total_Invoiced - Total_Expenses` |

---

### Report 2: Budget vs Actual
**Type:** Summary Report on Budget_Components
**Configuration:**
- **Group By:** Budget_Plan.Project.Project_Name
- **Sub-group:** Category
- **Values:** Sum of Allocated_Amount, Sum of Spent_Amount, Sum of Remaining_Amount
- **Display:** Bar chart showing Allocated vs Spent by project

---

### Report 3: Stock Availability
**Type:** Summary Report on Inventory_Items
**Configuration:**
- **Fields:** Item_Name, Item_Warehouse_Stock.Current_Stock, Item_Warehouse_Stock.Reserved_Qty, Item_Warehouse_Stock.Available_Stock (via subform aggregate columns)

---

### Report 4: Low Stock Alert
**Type:** Summary Report on Inventory_Items
**Configuration:**
- **Fields:** Item_Name, Item_Warehouse_Stock.Current_Stock, Item_Warehouse_Stock.Reorder_Level
- **Filter:** Item_Warehouse_Stock.Current_Stock <= Item_Warehouse_Stock.Reorder_Level (via subform filter)

**Deluge — Scheduled Low Stock Notification**
```deluge
/* JUSTIFICATION: Scheduled daily workflow that checks stock levels across all Inventory_Items via the embedded Item_Warehouse_Stock subform and alerts when stock falls at or below reorder level. */
/* ===== PSEUDOCODE =====
   Trigger: Scheduled (Daily 8 AM) — send low stock notifications
   
   1. Fetch all active Inventory_Items (up to 200 records)
   2. For each item, access the embedded Item_Warehouse_Stock subform
   3. For each stock row where Current_Stock > 0 AND <= Reorder_Level:
      a. Build alert line with Item_Name, Warehouse_Name, Current_Stock, Reorder_Level
   4. If any low stock items found: (Placeholder) send email alert
   5. If no low stock items: exit (nothing to alert)
   ===== END PSEUDOCODE ===== */
active_items = zoho.creator.getRecords("budget_tracking", "Inventory_Items", "Status == 'Active'", 1, 200);
alert_body = "";

if (!active_items.isNull())
{
    for each item in active_items
    {
        item_name = ifnull(item.get("Item_Name"), "Unknown");
        stock_rows = item.get("Item_Warehouse_Stock");
        if (!stock_rows.isNull())
        {
            for each srow in stock_rows
            {
                current = ifnull(srow.get("Current_Stock"), 0);
                reorder = ifnull(srow.get("Reorder_Level"), 0);
                if (current > 0 && current <= reorder)
                {
                    wh_name = "Unknown";
                    wh_id = srow.get("Warehouse");
                    if (!wh_id.isNull())
                    {
                        w = zoho.creator.getRecordById("budget_tracking", "Warehouses", wh_id);
                        if (!w.isNull()) { wh_name = ifnull(w.get("Warehouse_Name"), "Unknown"); }
                    }
                    alert_body = alert_body + "- " + item_name + " @ " + wh_name
                        + " (Stock: " + current.toString()
                        + ", Reorder: " + reorder.toString() + ")\n";
                }
            }
        }
    }
}

if (alert_body != "")
{
    alert_body = "Low Stock Alert - items:\n\n" + alert_body;
}
```

---

### Report 5: Invoice Aging
**Type:** Summary Report on Invoices
**Configuration:**
- **Filter:** Status = 'Sent' OR Status = 'Overdue' OR Status = 'Partially Paid'
- **Aging Buckets:** 0-30 days, 31-60 days, 61-90 days, 90+ days
- **Group By:** Aging bucket (use formula)
- **Values:** Invoice_No, Account, Total, Balance_Due, Invoice_Date, Due_Date

**Creator Report Widget:**
- Use formula field `Age_Days = Today() - Due_Date`
- Create aging groups via report criteria

---

### Report 6: DC Register
**Type:** Summary Report on Delivery_Challans
**Configuration:**
- **Group By:** Status
- **Sub-group:** Project.Project_Name
- **Values:** DC_No, DC_Date, Account, Count of line items
- **Display:** Table with status filter

---

### Report 7: BOM Cost Summary
**Type:** Summary Report on BOM
**Configuration:**
- **Fields:** BOM_No, BOM_Name, Finished_Item, Quantity, Total_Material_Cost, Labor_Cost, Overhead_Cost, Total_Mfg_Cost
- **Display:** Card view showing cost breakdown per BOM

---

### Report 8: Purchase Order Register
**Type:** Summary Report on Purchase_Orders
**Configuration:**
- **Group By:** Status
- **Values:** PO_Number, Vendor, PO_Date, Total, Delivery_Date
- **Filter:** Status != 'Cancelled'

---

| Expense Analysis | Summary | Expenses | Expense_Type, Amount, Status, Project |

---

| Vendor Performance | Summary | Vendors | Category, Performance_Rating, PO count |

---

### Dashboard: Executive KPI Dashboard

**Widget 1 — KPI Cards Row:**
| KPI | Source | Formula |
|---|---|---|
| Total Active Projects | Projects | Count where Status = 'Active' or 'Planning' |
| Total Budget Allocated | Budget_Components | Sum of Allocated_Amount where Budget_Plan.Status = 'Active' |
| Total Spent | Budget_Components | Sum of Spent_Amount where Budget_Plan.Status = 'Active' |
| Budget Utilization % | Budget_Components | (Total Spent / Total Budget) × 100 |
| Open PO Value | Purchase_Orders | Sum of PO_Total where Status='Open' |
| Pending GRNs | Purchase_Orders | Count of Open POs with any line not fully received |
| Inventory Value | Inventory_Items | Sum of Stock_Value where Status = 'Active' |

**Widget 2 — Budget vs Actual Chart**
- Bar chart grouped by Project
- Series: Budget, Spent

**Widget 3 — Project P&L Summary**
- Table: Project Name, Budget, Spent, Invoiced, Net P&L

**Widget 4 — Low Stock Alerts**
- List of items where Current_Stock ≤ Reorder_Level

**Widget 5 — Invoice Aging**
- Grouped bar or table by aging bucket

**Widget 6 — Recent Activity Feed**
- Latest 10 Inventory_Transactions sorted by Transaction_Date desc

**Widget 7 — Quick Actions**
- Buttons linking to: Create PO, Create Expense, Create Invoice, New Project

---

### Scheduled Workflow: KPI Refresh (Daily Midnight)
```deluge
/* ===== PSEUDOCODE =====
   Trigger: Scheduled (Daily Midnight) — refresh KPI summary data
   
   1. POs are manually closed only — no auto-close.
      PO lifecycle simplified: Open → Close (manual only).
      GRN tracks accepted quantities but does not auto-close POs.
   
   2. Mark overdue invoices — already handled in Phase 1E scheduled workflow
   
   3. Budget alerts — already handled in Phase 1C scheduled workflow
   ===== END PSEUDOCODE ===== */

```

---

## Build Verification Checklist
1. All 10+ report views created and rendering data correctly
2. Executive Dashboard displays all 7 KPI cards with live data
3. Budget vs Actual chart shows correct comparisons
4. Project P&L report shows correct revenue − expense per project
5. Low Stock Alert report triggers correctly
6. Invoice Aging report shows correct aging buckets
7. (POs are closed manually — no auto-close in schedule)
8. Scheduled KPI refresh runs without errors

---

## ✅ Phase 1F Complete — All 6 Phases Finished
The full application build is ready for testing and UAT.
