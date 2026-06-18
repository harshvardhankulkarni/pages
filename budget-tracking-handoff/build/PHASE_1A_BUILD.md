# Phase 1A Build Guide — Vendors → Projects → Warehouses → Inventory Items

## Prerequisites
- Zoho Creator account with app "Project Budget Tracking" created
- Workspace API name: `budget_tracking`
- Follow this order to respect lookup dependencies

---

## 1.1 Vendors Form (`Vendors`)

### Field Configuration
| Label | Field Type | API Name | Required | Notes |
|---|---|---|---|---|
| Vendor Name | Single Line | `Vendor_Name` | Yes | |
| Company Name | Single Line | `Company_Name` | No | Legal entity name |
| Email | Email | `Email` | No | |
| Phone | Phone | `Phone` | No | |
| Mobile | Phone | `Mobile` | No | |
| Website | URL | `Website` | No | |
| Currency | Dropdown | `Currency` | No | `USD, EUR, INR, GBP, AED` |
| Payment Terms | Dropdown | `Payment_Terms` | No | `Due on Receipt, Net 15, Net 30, Net 45, Net 60` |
| Payment Options | Multi Select | `Payment_Options` | No | `Cheque, Cash, Bank Transfer, Credit Card, Online Payment` |
| Opening Balance | Currency | `Opening_Balance` | No | |
| Account Number | Single Line | `Account_Number` | No | |
| Tax ID | Single Line | `Tax_ID` | No | GSTIN / VAT |
| PAN | Single Line | `PAN` | No | India PAN |
| Billing Address | Address | `Billing_Address` | No | Zoho Creator Address type (composite) |
| Shipping Address | Address | `Shipping_Address` | No | Zoho Creator Address type (composite) |
| Vendor Category | Dropdown | `Vendor_Category` | No | `Materials, Services, Equipment, Labor, Logistics` |
| Performance Rating | Decimal | `Performance_Rating` | No | 1-5 scale |
| Status | Dropdown | `Status` | No | `Active, Inactive` — default Active |
| Portal Access | Checkbox | `Portal_Access` | No | |
| Remarks | Multi Line | `Remarks` | No | |
| Tags | Multi Select | `Tags` | No | |

### Subforms (Add-as-Subform)

**Vendor Contacts** — Form: `Vendor_Contacts`
| Label | Field Type | API Name |
|---|---|---|
| Vendor | Lookup → Vendors | `Vendor` |
| Salutation | Dropdown | `Salutation` — `Mr, Ms, Mrs, Dr` |
| First Name | Single Line | `First_Name` |
| Last Name | Single Line | `Last_Name` |
| Email | Email | `Email` |
| Phone | Phone | `Phone` |
| Mobile | Phone | `Mobile` |
| Designation | Single Line | `Designation` |
| Department | Single Line | `Department` |
| Is Primary | Checkbox | `Is_Primary` |

**Vendor Documents** — Form: `Vendor_Documents`
| Label | Field Type | API Name |
|---|---|---|
| Vendor | Lookup → Vendors | `Vendor` |
| Document Name | Single Line | `Document_Name` |
| File | Upload | `File` |
| Expiry Date | Date | `Expiry_Date` |
| Notes | Single Line | `Notes` |

### Validation Rules
1. **Vendor Name required** — On Submit, if `Vendor_Name` is blank → `throw "Vendor Name is required."`
2. **Performance Rating range** — On Submit, if `Performance_Rating` is not null and (`Performance_Rating < 1` or `Performance_Rating > 5`) → `throw "Performance Rating must be between 1 and 5."`

### Deluge Scripts



---

## 1.2 Projects Form (`Projects`)

### Field Configuration
| Label | Field Type | API Name | Required | Notes |
|---|---|---|---|---|
| Project Name | Single Line | `Project_Name` | Yes | |
| Project Code | Auto Number | `Project_Code` | Yes | Format: `PROJ-{0000}` |
| Account | Lookup → Vendors | `Account` | No | Client/company |
| Start Date | Date | `Start_Date` | No | |
| End Date | Date | `End_Date` | No | |
| Project Manager | User Picker | `Project_Manager` | No | |
| Total Approved Budget | Currency | `Total_Approved_Budget` | No | |
| Status | Dropdown | `Status` | No | `Planning, Active, On Hold, Completed, Closed` |

### Custom Actions (Form Buttons)
Create two buttons in Form Settings → Custom Actions:

1. **Create Invoice**
   - Label: "Create Invoice"
   - Action: Open form `Invoices` with `Project` pre-filled = current record ID

2. **Request Part Repair**
   - Label: "Request Part Repair"  
   - Action: Open form `Purchase_Requisitions` with `Project` pre-filled = current record ID, `Request_Type` = "Part Repair"

### Validation Rules
1. **End Date after Start Date** — On Submit, if `End_Date` is not null and `Start_Date` is not null and `End_Date < Start_Date` → `throw "End Date must be after Start Date."`

### Deluge Scripts

#### On Submit — Validate Project Completion
```deluge
/* Phase 1A — Projects: On Submit
   When Status changes to "Completed", check for open dependencies */
status_val = ifnull(input.Status.toMap().get("display_value"), "");

if (status_val == "Completed" && !input.ID.isNull())
{
    /* Check for open Expenses */
    exp_criteria = "Project == " + input.ID + " && Status == 'Submitted'";
    open_expenses = zoho.creator.getRecords("budget_tracking", "Expenses", exp_criteria, 1, 200);
    if (!open_expenses.isNull() && open_expenses.size() > 0)
    {
        throw "Cannot complete project: " + open_expenses.size().toString() + " expense(s) are still open.";
    }

    /* Check for open Purchase Orders */
    po_criteria = "Project == " + input.ID + " && Status == 'Open'";
    open_pos = zoho.creator.getRecords("budget_tracking", "Purchase_Orders", po_criteria, 1, 200);
    if (!open_pos.isNull() && open_pos.size() > 0)
    {
        throw "Cannot complete project: " + open_pos.size().toString() + " PO(s) are still open.";
    }

    /* Check for open Purchase Requisitions */
    pr_criteria = "Project == " + input.ID + " && Status == 'Open'";
    open_prs = zoho.creator.getRecords("budget_tracking", "Purchase_Requisitions", pr_criteria, 1, 200);
    if (!open_prs.isNull() && open_prs.size() > 0)
    {
        throw "Cannot complete project: " + open_prs.size().toString() + " PR(s) are still open.";
    }
}
```

---

## 1.3 Warehouses Form (`Warehouses`)

### Field Configuration
| Label | Field Type | API Name | Required | Notes |
|---|---|---|---|---|
| Warehouse Name | Single Line | `Warehouse_Name` | Yes | |
| Warehouse Code | Auto Number | `Warehouse_Code` | Yes | Format: `WH-{0000}` |
| Address | Multi Line | `Address` | No | |
| City | Single Line | `City` | No | |
| State | Single Line | `State` | No | |
| Country | Single Line | `Country` | No | |
| Contact Person | Single Line | `Contact_Person` | No | |
| Phone | Phone | `Phone` | No | |
| Status | Dropdown | `Status` | No | `Active, Inactive` — default Active |

### Validation Rules
1. **Warehouse Name required** — On Submit, if `Warehouse_Name` is blank → `throw "Warehouse Name is required."`

### Deluge Scripts
No Deluge scripts required for Phase 1A Warehouses. Auto-number handled by field type.

### Seeding
After form creation, manually create one default record:
- Warehouse Name: "Main Warehouse"
- Status: "Active"

---

## 1.4 Inventory Items Form (`Inventory_Items`)

### Field Configuration
| Label | Field Type | API Name | Required | Notes |
|---|---|---|---|---|
| Item Name | Single Line | `Item_Name` | Yes | |
| SKU | Auto Number | `SKU` | Yes | Format: `SKU-{0000}` |
| Item Type | Dropdown | `Item_Type` | No | `Goods, Services` |
| Category | Dropdown | `Category` | No | `Raw Material, Component, Consumable, Equipment, Service, Subcontract` |
| Unit | Dropdown | `Unit` | No | `Pcs, Kg, Ltr, Box, Meter, Hour, Day, Set, Pair, Nos` |
| Length | Decimal | `Length` | No | cm |
| Width | Decimal | `Width` | No | cm |
| Height | Decimal | `Height` | No | cm |
| Weight | Decimal | `Weight` | No | kg |
| Brand | Single Line | `Brand` | No | |
| Manufacturer | Single Line | `Manufacturer` | No | |
| HSN/SAC Code | Single Line | `HSN_SAC_Code` | No | Tax classification |
| Taxability | Dropdown | `Taxability` | No | `Taxable, Non-Taxable, Zero-Rated` |
| Tax Rate | Decimal | `Tax_Rate` | No | Default tax % |
| Purchase Price | Currency | `Purchase_Price` | No | Default unit cost |
| Sales Price | Currency | `Sales_Price` | No | For reference |
| Reorder Level | Decimal | `Reorder_Level` | No | Min stock alert |
| Preferred Vendor | Lookup → Vendors | `Preferred_Vendor` | No | Default vendor for POs |
| Current Stock | Decimal | `Current_Stock` | No | Maintained by Deluge — aggregated across warehouses |
| Stock Value | Formula | `Stock_Value` | — | `Current_Stock * Purchase_Price` |
| Description | Multi Line | `Description` | No | |
| Image | Upload | `Image` | No | |
| Status | Dropdown | `Status` | No | `Active, Inactive` — default Active |

### Formula: Stock_Value
```
Current_Stock * Purchase_Price
```

### Subforms (Add-as-Subform)

**Stock by Warehouse** — Form: `Item_Warehouse_Stock`
| Label | Field Type | API Name | Notes |
|---|---|---|---|
| Item | Lookup → Inventory_Items | `Item` | |
| Warehouse | Lookup → Warehouses | `Warehouse` | |
| Current Stock | Decimal | `Current_Stock` | Maintained by Deluge |
| Reserved Qty | Decimal | `Reserved_Qty` | Default 0 |
| Available Stock | Formula | `Available_Stock` | `Current_Stock - Reserved_Qty` |
| Reorder Level | Decimal | `Reorder_Level` | Override item default |

**Item Attributes** — Form: `Item_Attributes`
| Label | Field Type | API Name |
|---|---|---|
| Item | Lookup → Inventory_Items | `Item` |
| Attribute Name | Single Line | `Attribute_Name` |
| Value | Single Line | `Value` |

### Validation Rules
1. **Item Name required** — On Submit, if `Item_Name` is blank → `throw "Item Name is required."`
2. **Positive Purchase Price** — On Submit, if `Purchase_Price` is not null and `Purchase_Price < 0` → `throw "Purchase Price cannot be negative."`
3. **Goods require Unit** — On Submit, if `Item_Type == "Goods"` and `Unit` is blank → `throw "Unit is required for Goods items."`

### Deluge Scripts

No Deluge scripts for Vendors in Phase 1A — Zoho Creator Address type handles the composite address fields natively.

#### On Submit — Initialize Stock for All Warehouses
```deluge
/* Phase 1A — Inventory_Items: On Submit
   When a new item is created, create Item_Warehouse_Stock records
   for all active warehouses with 0 stock */

if (input.ID.isNull())
{
    /* This is a new record — will run after save */
    /* We use On Post Submit for this logic */
}
```

#### On Post Submit — Create Stock Records
```deluge
/* Phase 1A — Inventory_Items: On Post Submit
   Create Item_Warehouse_Stock for all active warehouses */
item_id = input.ID;
item_type = ifnull(input.Item_Type, "");

if (item_type == "Goods")
{
    /* Fetch all active warehouses */
    warehouses = zoho.creator.getRecords("budget_tracking", "Warehouses", "Status == 'Active'", 1, 200);

    if (!warehouses.isNull())
    {
        for each wh in warehouses
        {
            /* Check if stock record already exists */
            stock_criteria = "Item == " + item_id + " && Warehouse == " + wh.get("ID");
            existing = zoho.creator.getRecords("budget_tracking", "Item_Warehouse_Stock", stock_criteria, 1, 1);

            if (existing.isNull() || existing.size() == 0)
            {
                stock_data = Map();
                stock_data.put("Item", item_id);
                stock_data.put("Warehouse", wh.get("ID"));
                stock_data.put("Current_Stock", 0);
                stock_data.put("Reserved_Qty", 0);
                zoho.creator.createRecord("budget_tracking", "Item_Warehouse_Stock", stock_data);
            }
        }
    }
}
```

---

## Build Verification Checklist
After building Phase 1A, verify:
1. Vendors form creates records with all fields saving correctly
2. Vendor Contacts subform adds contact persons
3. Vendor Documents subform uploads files
4. Projects form generates PROJ-0001, PROJ-0002...
5. Account lookup in Projects shows Vendors list
6. Warehouses form generates WH-0001, WH-0002...
7. Inventory Items generates SKU-0001, SKU-0002...
8. Item_Warehouse_Stock auto-creates records for all active warehouses on new item

## Next Phase
→ Proceed to `PHASE_1B_BUILD.md` when all above forms are verified.
