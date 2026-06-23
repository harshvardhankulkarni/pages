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
         - Update Total_Expenses_Calc with total_expenses
         - Update Total_Invoiced_Calc with total_invoiced
         - Update Total_Paid_Calc with total_paid
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
        proj_data.put("Total_Expenses_Calc", total_expenses);
        proj_data.put("Total_Invoiced_Calc", total_invoiced);
        proj_data.put("Total_Paid_Calc", total_paid);
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
**Type:** Summary Report on Item_Warehouse_Stock
**Configuration:**
- **Group By:** Item.Item_Name
- **Values:** Sum of Current_Stock, Sum of Reserved_Qty, Sum of Available_Stock
- **Filter:** Current_Stock > 0
- **Display:** Table grouped by warehouse

---

### Report 4: Low Stock Alert
**Type:** Summary Report on Item_Warehouse_Stock
**Configuration:**
- **Filter:** `Current_Stock <= Reorder_Level AND Current_Stock > 0`
- **Group By:** Warehouse.Warehouse_Name
- **Values:** Item.Item_Name, Current_Stock, Reorder_Level

**Deluge — Scheduled Low Stock Notification**
```deluge
/* ===== PSEUDOCODE =====
   Trigger: Scheduled (Daily 8 AM) — send low stock notifications
   
   1. Query Item_Warehouse_Stock where Current_Stock > 0 AND
      Current_Stock <= Reorder_Level (items at or below reorder threshold)
   2. If low stock items exist:
      a. Initialize alert body with header listing item count
      b. For each low stock item:
         i.   Fetch the Inventory_Item record by ID to get Item_Name
         ii.  Fetch the Warehouse record by ID to get Warehouse_Name
         iii. Append formatted alert line: item name @ warehouse name
              (Stock: X, Reorder: Y)
      c. (Placeholder) Send email alert to inventory manager
   3. If no low stock items: exit (nothing to alert)
   ===== END PSEUDOCODE ===== */
low_stock = zoho.creator.getRecords("budget_tracking", "Item_Warehouse_Stock",
    "Current_Stock > 0 && Current_Stock <= Reorder_Level", 1, 200);

if (!low_stock.isNull() && low_stock.size() > 0)
{
    alert_body = "Low Stock Alert - " + low_stock.size().toString() + " item(s):\n\n";
    for each item in low_stock
    {
        item_name = "";
        item_id = item.get("Item");
        if (!item_id.isNull())
        {
            i = zoho.creator.getRecordById("budget_tracking", "Inventory_Items", item_id);
            if (!i.isNull()) { item_name = ifnull(i.get("Item_Name"), "Unknown"); }
        }

        wh_name = "";
        wh_id = item.get("Warehouse");
        if (!wh_id.isNull())
        {
            w = zoho.creator.getRecordById("budget_tracking", "Warehouses", wh_id);
            if (!w.isNull()) { wh_name = ifnull(w.get("Warehouse_Name"), "Unknown"); }
        }

        alert_body = alert_body + "- " + item_name + " @ " + wh_name
            + " (Stock: " + ifnull(item.get("Current_Stock"), 0).toString()
            + ", Reorder: " + ifnull(item.get("Reorder_Level"), 0).toString() + ")\n";
    }
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
- **Fields:** BOM_No, BOM_Name, Product_Item, Quantity, Total_Material_Cost, Labor_Cost, Overhead_Cost, Total_Mfg_Cost
- **Display:** Card view showing cost breakdown per BOM

---

### Report 8: Purchase Order Register
**Type:** Summary Report on Purchase_Orders
**Configuration:**
- **Group By:** Status
- **Values:** PO_Number, Vendor, PO_Date, Total, Delivery_Date
- **Filter:** Status != 'Cancelled'

---

### Report 9: Expense Analysis
**Type:** Summary Report on Expenses
**Configuration:**
- **Group By:** Expense_Type, Project.Project_Name
- **Values:** Sum of Amount, Count of expenses
- **Filter:** Status = 'Approved'
- **Display:** Pie chart by Expense_Type, bar chart by Project

---

### Report 10: Vendor Performance
**Type:** Summary Report on Vendors
**Configuration:**
- **Fields:** Vendor_Name, Category, Performance_Rating, Total PO Value (from POs)
- **Display:** Card view sorted by Performance_Rating desc

---

### Dashboard: Executive KPI Dashboard

**Widget 1 — KPI Cards Row:**
| KPI | Source | Formula |
|---|---|---|
| Total Active Projects | Projects | Count where Status = 'Active' or 'Planning' |
| Total Budget Allocated | Budget_Components | Sum of Allocated_Amount where Budget_Plan.Status = 'Active' |
| Total Spent | Budget_Components | Sum of Spent_Amount where Budget_Plan.Status = 'Active' |
| Budget Utilization % | Budget_Components | (Total Spent / Total Budget) × 100 |
| Open PO Value | Purchase_Orders | Sum of Total where Status = 'Open' |
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
