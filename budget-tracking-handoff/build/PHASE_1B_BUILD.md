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
2. **Component sum ≤ Total Budget** — On Submit, sum of all Budget_Components Allocated_Amount must not exceed Total_Budget. Validated via `input.Budget_Components` iteration.

### Deluge Scripts

#### On Submit — Validate Budget Period
```deluge
/* ===== PSEUDOCODE =====
   Trigger: On Submit — when Budget_Plan record is created or updated
   
   1. Check if both Budget_Period_Start and Budget_Period_End are filled
   2. If end date is before start date: throw validation error
   3. Get the display value of the Status field
   4. If Status is "Active" and a Project is linked:
      a. Build a criteria to find other Active plans for the same Project
      b. If editing an existing record, exclude the current record ID
      c. Query for duplicate active plans
      d. If another active plan exists: throw error — must close existing plan first
   5. Validate component totals: iterate input.Budget_Components (embedded subform)
      a. Sum all Allocated_Amount values
      b. If sum exceeds Total_Budget: throw validation error
   6. If Status is "Active":
      a. Create a data map with the Total_Budget value
      b. Update the linked Project record's Total_Approved_Budget field
   7. If Status is not "Active" or no Project linked: skip budget sync
   ===== END PSEUDOCODE ===== */
if (!input.Budget_Period_Start.isNull() && !input.Budget_Period_End.isNull())
{
    if (input.Budget_Period_End < input.Budget_Period_Start)
    {
        throw "Budget Period End must be after Budget Period Start.";
    }
}

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

/* Phase 1B — Validate component totals do not exceed plan budget
   Budget_Components is an embedded subform — data available via input */
total_budget = ifnull(input.Total_Budget, 0);
components = input.Budget_Components;
total_allocated = 0;
if (!components.isNull())
{
    for each comp in components
    {
        total_allocated = total_allocated + ifnull(comp.get("Allocated_Amount"), 0);
    }
}
if (total_allocated > total_budget)
{
    throw "Component total (" + total_allocated.toString() + ") exceeds Budget Plan total (" + total_budget.toString() + ").";
}

if (status_val == "Active")
{
    proj_data = Map();
    proj_data.put("Total_Approved_Budget", input.Total_Budget);
    zoho.creator.updateRecord("budget_tracking", "Projects", input.Project, proj_data);
}
```


### Subforms (Add-as-Subform)

**Budget Components** — embedded subform (no separate API name, no standalone CRUD)
| Label | Field Type | Required | Notes |
|---|---|---|---|
| Component Name | Single Line | Yes | e.g., "Materials", "Labor" |
| Category | Dropdown | No | `Material, Labor, Equipment, Overhead, Contingency, Other` |
| Allocated Amount | Currency | Yes | Budget for this component |
| Spent Amount | Currency | No | Updated by Expense/Stock Out |
| Remaining Amount | Formula | — | `Allocated_Amount - Spent_Amount` |
| Utilization % | Formula | — | `(Spent_Amount / Allocated_Amount) * 100` |

No separate Deluge scripts — validation occurs in parent Budget_Plans On Submit via `input.Budget_Components`.

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
/* ===== PSEUDOCODE =====
   Trigger: On Submit — before Inventory_Transaction record is saved
   
   1. Get the transaction type display value from the dropdown
   2. Get the quantity, item ID, and warehouse ID from the current record
   3. If quantity is positive AND item AND warehouse are both linked:
      a. Check if transaction type is "Stock Out", "Transfer", or "Reservation"
      b. If yes: query Item_Warehouse_Stock for this item+warehouse combination
      c. If stock record exists:
         - Get Current_Stock and Reserved_Qty
         - For "Reservation": available = Current_Stock - Reserved_Qty (unreserved)
         - For "Stock Out" and "Transfer": available = Current_Stock (total stock)
      d. If requested quantity exceeds available stock: throw insufficient stock error
   4. If transaction type is not a stock-consuming type (Stock In, Adjustment, Release):
      skip availability check
   ===== END PSEUDOCODE ===== */
txn_type = ifnull(input.Transaction_Type.toMap().get("display_value"), "");
qty = ifnull(input.Quantity, 0);
item_id = input.Item;
wh_id = input.Warehouse;

if (qty > 0 && !item_id.isNull() && !wh_id.isNull())
{
    if (txn_type == "Stock Out" || txn_type == "Transfer" || txn_type == "Reservation")
    {
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
                available = current;
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
/* ===== PSEUDOCODE =====
   Trigger: On Post Submit — after Inventory_Transaction record is saved
   
   1. Get the transaction type display value, quantity, item, warehouse, and destination warehouse
   2. If item is valid AND quantity is positive:
   
      CASE A — "Stock In":
         a. Query Item_Warehouse_Stock for this item+source warehouse
         b. If found: increment Current_Stock by the transaction quantity
      
      CASE B — "Stock Out" or "Reservation":
         a. Query Item_Warehouse_Stock for this item+source warehouse
         b. If found:
            - "Stock Out": decrement Current_Stock by the quantity
            - "Reservation": increment Reserved_Qty by the quantity
      
      CASE C — "Release":
         a. Query Item_Warehouse_Stock for this item+warehouse
         b. If found: decrement Reserved_Qty by the quantity (floor at 0)
      
      CASE D — "Adjustment":
         a. Query Item_Warehouse_Stock for this item+warehouse
         b. If found: set Current_Stock to the quantity value (absolute, not delta)
      
      CASE E — "Transfer" (both source and destination warehouses):
         a. Source: decrement Current_Stock by quantity
         b. Destination: increment Current_Stock by quantity
         c. If no stock record exists at destination: create one with the quantity
      
      CASE F — "Stock Out" with a Project linked:
         a. Placeholder for Phase 2 (auto-create Expense record)
         b. Currently: stock update handled above, no further action
   
   3. If item is null or quantity is 0 or negative: skip all updates
   ===== END PSEUDOCODE ===== */
txn_type = ifnull(input.Transaction_Type.toMap().get("display_value"), "");
qty = ifnull(input.Quantity, 0);
item_id = input.Item;
wh_id = input.Warehouse;
to_wh_id = input.To_Warehouse;

if (!item_id.isNull() && qty > 0)
{
    if (txn_type == "Stock In" && !wh_id.isNull())
    {
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
        criteria = "Item == " + item_id + " && Warehouse == " + wh_id;
        stock_records = zoho.creator.getRecords("budget_tracking", "Item_Warehouse_Stock", criteria, 1, 1);
        if (!stock_records.isNull() && stock_records.size() > 0)
        {
            srec = stock_records.get(0);
            data = Map();
            data.put("Current_Stock", qty);
            zoho.creator.updateRecord("budget_tracking", "Item_Warehouse_Stock", srec.get("ID"), data);
        }
    }

    if (txn_type == "Transfer" && !wh_id.isNull() && !to_wh_id.isNull())
    {
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
            data = Map();
            data.put("Item", item_id);
            data.put("Warehouse", to_wh_id);
            data.put("Current_Stock", qty);
            data.put("Reserved_Qty", 0);
            zoho.creator.createRecord("budget_tracking", "Item_Warehouse_Stock", data);
        }
    }

    if (txn_type == "Stock Out" && !input.Project.isNull() && !wh_id.isNull())
    {
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
