# Phase 1B Build Guide — Budget Plans → Budget Components → Inventory Transactions

## Dependencies
Requires Phase 1A complete (Projects, Warehouses, Inventory_Items forms exist).

---

## 1.5 Budget Plans Form (`Budget_Plans`)

### Field Configuration
| Label | Field Type | API Name | Required | Notes |
|---|---|---|---|---|
| Budget Plan Name | Single Line | `Budget_Plan_Name` | Yes | |
| Budget Code | Auto Number | `Budget_Code` | Yes | Format: `BUD-{0000}` |
| Project | Lookup → Projects | `Project` | Yes | One budget plan per project |
| Total Budget | Currency | `Total_Budget` | Yes | Overall approved amount |
| Currency | Dropdown | `Currency` | No | `USD, EUR, INR, GBP, AED` |
| Budget Period Start | Date | `Budget_Period_Start` | No | |
| Budget Period End | Date | `Budget_Period_End` | No | |
| Status | Dropdown | `Status` | No | `Draft, Active, Closed, Cancelled` |
| Notes | Multi Line | `Notes` | No | |

### Validation Rules
1. **Unique active plan per project** — On Submit, if `Status == "Active"`, check no other Active plan exists for the same Project → `throw "An active budget plan already exists for this project."`

### Deluge Scripts

#### On Submit — Validate Budget Period
```deluge
/* Phase 1B — Budget_Plans: On Submit
   Validate budget period dates */
if (!input.Budget_Period_Start.isNull() && !input.Budget_Period_End.isNull())
{
    if (input.Budget_Period_End < input.Budget_Period_Start)
    {
        throw "Budget Period End must be after Budget Period Start.";
    }
}

/* Validate no duplicate active plans for same project */
status_val = ifnull(input.Status.toMap().get("display_value"), "");
if (status_val == "Active" && !input.Project.isNull())
{
    proj_id = input.Project;
    criteria = "Project == " + proj_id + " && Status == 'Active'";
    if (!input.ID.isNull())
    {
        criteria = criteria + " && ID != " + input.ID;
    }
    existing_active = zoho.creator.getRecords("budget_tracking", "Budget_Plans", criteria, 1, 10);
    if (!existing_active.isNull() && existing_active.size() > 0)
    {
        throw "An active budget plan already exists for this project. Close it before creating a new one.";
    }
}

/* Update project's Total Approved Budget when plan is approved */
if (status_val == "Active")
{
    proj_data = Map();
    proj_data.put("Total_Approved_Budget", input.Total_Budget);
    zoho.creator.updateRecord("budget_tracking", "Projects", input.Project, proj_data);
}
```

---

## 1.6 Budget Components Form (`Budget_Components`)

Separate form (not subform) linked via Add-as-Subform on Budget_Plans.

### Field Configuration
| Label | Field Type | API Name | Required | Notes |
|---|---|---|---|---|
| Budget Plan | Lookup → Budget_Plans | `Budget_Plan` | Yes | |
| Component Name | Single Line | `Component_Name` | Yes | e.g., "Materials", "Labor" |
| Category | Dropdown | `Category` | No | `Material, Labor, Equipment, Overhead, Contingency, Other` |
| Allocated Amount | Currency | `Allocated_Amount` | Yes | Budget for this component |
| Spent Amount | Currency | `Spent_Amount` | No | Updated by Expense/Stock Out |
| Remaining Amount | Formula | `Remaining_Amount` | — | `Allocated_Amount - Spent_Amount` |
| Utilization % | Formula | `Utilization_Pct` | — | `(Spent_Amount / Allocated_Amount) * 100` |

### Validation Rules
1. **Component sum ≤ Total Budget** — On Submit, check sum of all component Allocated_Amount ≤ parent Budget_Plan.Total_Budget.

### Deluge Scripts

#### On Submit — Validate Budget Component Total
```deluge
/* Phase 1B — Budget_Components: On Submit
   Validate component sum does not exceed plan total budget */
plan_id = input.Budget_Plan;

/* Get the parent budget plan */
plan = zoho.creator.getRecordById("budget_tracking", "Budget_Plans", plan_id);
if (!plan.isNull())
{
    total_budget = ifnull(plan.get("Total_Budget"), 0);

    /* Sum all components for this plan */
    criteria = "Budget_Plan == " + plan_id;
    if (!input.ID.isNull())
    {
        criteria = criteria + " && ID != " + input.ID;
    }
    components = zoho.creator.getRecords("budget_tracking", "Budget_Components", criteria, 1, 200);

    total_allocated = ifnull(input.Allocated_Amount, 0);
    if (!components.isNull())
    {
        for each comp in components
        {
            total_allocated = total_allocated + ifnull(comp.get("Allocated_Amount"), 0);
        }
    }

    if (total_allocated > total_budget)
    {
        remaining = total_budget - (total_allocated - ifnull(input.Allocated_Amount, 0));
        throw "Component total (" + total_allocated.toString() + ") exceeds Budget Plan total (" + total_budget.toString()
            + "). Remaining unallocated: " + remaining.toString();
    }
}
```

---

## 1.7 Inventory Transactions Form (`Inventory_Transactions`)

Core stock movement tracking — every stock change is logged here.

### Field Configuration
| Label | Field Type | API Name | Required | Notes |
|---|---|---|---|---|
| Transaction No | Auto Number | `Transaction_No` | Yes | Format: `TXN-{0000}` |
| Transaction Type | Dropdown | `Transaction_Type` | Yes | `Stock In, Stock Out, Transfer, Adjustment, Reservation, Release` |
| Item | Lookup → Inventory_Items | `Item` | Yes | |
| Warehouse | Lookup → Warehouses | `Warehouse` | Yes | Source or destination |
| To Warehouse | Lookup → Warehouses | `To_Warehouse` | No | Required for Transfer type |
| Quantity | Decimal | `Quantity` | Yes | Positive number |
| Unit Rate | Currency | `Unit_Rate` | No | Cost per unit |
| Total Value | Formula | `Total_Value` | — | `Quantity * Unit_Rate` |
| Project | Lookup → Projects | `Project` | No | For Stock Out tracking |
| Reference Type | Dropdown | `Reference_Type` | No | `PO, GRN, TO, Invoice, DC, Manual` |
| Reference ID | Single Line | `Reference_ID` | No | ID of source document |
| Notes | Multi Line | `Notes` | No | |
| Transaction Date | Date | `Transaction_Date` | No | Defaults to today |
| Created By | User Picker | `Created_By` | No | |

### Validation Rules
1. **Positive Quantity** — On Submit, if `Quantity <= 0` → `throw "Quantity must be positive."`
2. **Warehouse required** — On Submit, if `Transaction_Type != "Transfer"` and `Warehouse` is null → `throw "Warehouse is required."`
3. **To Warehouse for Transfer** — On Submit, if `Transaction_Type == "Transfer"` and `To_Warehouse` is null → `throw "To Warehouse is required for transfers."`
4. **Stock Out cannot exceed available** — On Submit, if `Transaction_Type` is `Stock Out, Transfer, Reservation` → check warehouse stock level.

### Deluge Scripts

#### On Submit — Validate Stock Availability
```deluge
/* Phase 1B — Inventory_Transactions: On Submit
   Validate stock availability before Stock Out / Transfer / Reservation */
txn_type = ifnull(input.Transaction_Type.toMap().get("display_value"), "");
qty = ifnull(input.Quantity, 0);
item_id = input.Item;
wh_id = input.Warehouse;

if (qty > 0 && !item_id.isNull() && !wh_id.isNull())
{
    if (txn_type == "Stock Out" || txn_type == "Transfer" || txn_type == "Reservation")
    {
        /* Get current stock for this item+warehouse */
        criteria = "Item == " + item_id + " && Warehouse == " + wh_id;
        stock_records = zoho.creator.getRecords("budget_tracking", "Item_Warehouse_Stock", criteria, 1, 1);

        available = 0;
        if (!stock_records.isNull() && stock_records.size() > 0)
        {
            stock = stock_records.get(0);
            current = ifnull(stock.get("Current_Stock"), 0);
            reserved = ifnull(stock.get("Reserved_Qty"), 0);
            available = current - reserved;

            if (txn_type == "Reservation")
            {
                available = current - reserved;
            }
            else
            {
                available = current; /* Stock Out checks total, not just unreserved */
            }
        }

        if (qty > available)
        {
            throw "Insufficient stock. Available: " + available.toString() + ", Requested: " + qty.toString();
        }
    }
}
```

#### On Post Submit — Update Item_Warehouse_Stock
```deluge
/* Phase 1B — Inventory_Transactions: On Post Submit
   Update Item_Warehouse_Stock based on transaction type */
txn_type = ifnull(input.Transaction_Type.toMap().get("display_value"), "");
qty = ifnull(input.Quantity, 0);
item_id = input.Item;
wh_id = input.Warehouse;
to_wh_id = input.To_Warehouse;

/* Helper function to get or create stock record function */
/* For readability we inline the logic */

if (!item_id.isNull() && qty > 0)
{
    /* --- Source Warehouse Updates --- */
    if (txn_type == "Stock In" && !wh_id.isNull())
    {
        /* Increase stock */
        criteria = "Item == " + item_id + " && Warehouse == " + wh_id;
        stock_records = zoho.creator.getRecords("budget_tracking", "Item_Warehouse_Stock", criteria, 1, 1);
        if (!stock_records.isNull() && stock_records.size() > 0)
        {
            srec = stock_records.get(0);
            current_qty = ifnull(srec.get("Current_Stock"), 0);
            data = Map();
            data.put("Current_Stock", current_qty + qty);
            zoho.creator.updateRecord("budget_tracking", "Item_Warehouse_Stock", srec.get("ID"), data);
        }
    }
    else if ((txn_type == "Stock Out" || txn_type == "Reservation") && !wh_id.isNull())
    {
        criteria = "Item == " + item_id + " && Warehouse == " + wh_id;
        stock_records = zoho.creator.getRecords("budget_tracking", "Item_Warehouse_Stock", criteria, 1, 1);
        if (!stock_records.isNull() && stock_records.size() > 0)
        {
            srec = stock_records.get(0);
            current_qty = ifnull(srec.get("Current_Stock"), 0);
            data = Map();

            if (txn_type == "Stock Out")
            {
                data.put("Current_Stock", current_qty - qty);
            }
            else if (txn_type == "Reservation")
            {
                reserved_qty = ifnull(srec.get("Reserved_Qty"), 0);
                data.put("Reserved_Qty", reserved_qty + qty);
            }

            zoho.creator.updateRecord("budget_tracking", "Item_Warehouse_Stock", srec.get("ID"), data);
        }
    }
    else if (txn_type == "Release" && !wh_id.isNull())
    {
        /* Decrease reserved quantity */
        criteria = "Item == " + item_id + " && Warehouse == " + wh_id;
        stock_records = zoho.creator.getRecords("budget_tracking", "Item_Warehouse_Stock", criteria, 1, 1);
        if (!stock_records.isNull() && stock_records.size() > 0)
        {
            srec = stock_records.get(0);
            reserved_qty = ifnull(srec.get("Reserved_Qty"), 0);
            new_reserved = reserved_qty - qty;
            if (new_reserved < 0) { new_reserved = 0; }
            data = Map();
            data.put("Reserved_Qty", new_reserved);
            zoho.creator.updateRecord("budget_tracking", "Item_Warehouse_Stock", srec.get("ID"), data);
        }
    }
    else if (txn_type == "Adjustment" && !wh_id.isNull())
    {
        /* Set stock to the quantity value (absolute adjustment) */
        criteria = "Item == " + item_id + " && Warehouse == " + wh_id;
        stock_records = zoho.creator.getRecords("budget_tracking", "Item_Warehouse_Stock", criteria, 1, 1);
        if (!stock_records.isNull() && stock_records.size() > 0)
        {
            srec = stock_records.get(0);
            data = Map();
            data.put("Current_Stock", qty); /* Quantity field holds the new stock level */
            zoho.creator.updateRecord("budget_tracking", "Item_Warehouse_Stock", srec.get("ID"), data);
        }
    }

    /* --- Transfer: Source Out + Destination In --- */
    if (txn_type == "Transfer" && !wh_id.isNull() && !to_wh_id.isNull())
    {
        /* Source: decrease stock */
        criteria = "Item == " + item_id + " && Warehouse == " + wh_id;
        src_records = zoho.creator.getRecords("budget_tracking", "Item_Warehouse_Stock", criteria, 1, 1);
        if (!src_records.isNull() && src_records.size() > 0)
        {
            srec = src_records.get(0);
            current_qty = ifnull(srec.get("Current_Stock"), 0);
            data = Map();
            data.put("Current_Stock", current_qty - qty);
            zoho.creator.updateRecord("budget_tracking", "Item_Warehouse_Stock", srec.get("ID"), data);
        }

        /* Destination: increase stock (create if not exists) */
        criteria2 = "Item == " + item_id + " && Warehouse == " + to_wh_id;
        dst_records = zoho.creator.getRecords("budget_tracking", "Item_Warehouse_Stock", criteria2, 1, 1);
        if (!dst_records.isNull() && dst_records.size() > 0)
        {
            drec = dst_records.get(0);
            current_qty = ifnull(drec.get("Current_Stock"), 0);
            data = Map();
            data.put("Current_Stock", current_qty + qty);
            zoho.creator.updateRecord("budget_tracking", "Item_Warehouse_Stock", drec.get("ID"), data);
        }
        else
        {
            /* Create new stock record at destination */
            data = Map();
            data.put("Item", item_id);
            data.put("Warehouse", to_wh_id);
            data.put("Current_Stock", qty);
            data.put("Reserved_Qty", 0);
            zoho.creator.createRecord("budget_tracking", "Item_Warehouse_Stock", data);
        }
    }

    /* --- Auto-create Stock In for Stock Out with Project (inventory deduction) --- */
    if (txn_type == "Stock Out" && !input.Project.isNull() && !wh_id.isNull())
    {
        /* Phase 2 — will auto-create Expense record here */
        /* For now, the transaction is logged and stock is updated above */
    }
}
```

---

## Build Verification Checklist
1. Budget Plans form creates with unique project constraint working
2. Budget Components subform validates total ≤ parent budget
3. Creating Budget Plan with Status=Active updates Project.Total_Approved_Budget
4. Inventory Transactions creates TXN-0001, TXN-0002...
5. Stock In increases Item_Warehouse_Stock.Current_Stock
6. Stock Out decreases Item_Warehouse_Stock.Current_Stock (with availability check)
7. Transfer creates paired movements (source -qty, destination +qty)
8. Reservation increases Reserved_Qty
9. Release decreases Reserved_Qty

## Next Phase
→ Proceed to `PHASE_1C_BUILD.md` when all above forms are verified.
