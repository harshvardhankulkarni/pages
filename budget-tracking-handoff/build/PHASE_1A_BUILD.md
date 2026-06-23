# Phase 1A Build Guide — Vendors → Accounts → Projects → Warehouses → Inventory Items

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
| Tax ID | Single Line | `Tax_ID` | No | GSTIN / VAT |
| PAN | Single Line | `PAN` | No | India PAN |
| Billing Address | Address | `Billing_Address` | No | Zoho Creator Address type (composite) |
| Shipping Address | Address | `Shipping_Address` | No | Zoho Creator Address type (composite) |
| Status | Dropdown | `Status` | No | `Active, Inactive` — default Active |
| Remarks | Multi Line | `Remarks` | No | |

### Subform: Vendor Contacts
| Label | Field Type | Notes |
| Salutation | Dropdown | `Mr, Ms, Mrs, Dr` |
| First Name | Single Line | |
| Last Name | Single Line | |
| Email | Email | |
| Phone | Phone | |
| Mobile | Phone | |
| Designation | Single Line | |
| Department | Single Line | |
| Is Primary | Checkbox | |

### Subform: Vendor Documents
| Label | Field Type | Notes |
| Document Name | Single Line | |
| File | Upload | |
| Expiry Date | Date | |
| Notes | Single Line | |

### Validation Rules
1. **Vendor Name required** — On Submit, if `Vendor_Name` is blank → `alert "Vendor Name is required."`

### Deluge Scripts



---

## 1.2 Accounts Form (`Accounts`)

### Field Configuration
| Label | Field Type | API Name | Required | Notes |
|---|---|---|---|---|
| Account Name | Single Line | `Account_Name` | Yes | Display name |
| Company Name | Single Line | `Company_Name` | No | Legal entity name |
| Email | Email | `Email` | No | |
| Phone | Phone | `Phone` | No | |
| Mobile | Phone | `Mobile` | No | |
| Website | URL | `Website` | No | |
| Currency | Dropdown | `Currency` | No | `USD, EUR, INR, GBP, AED` |
| Payment Terms | Dropdown | `Payment_Terms` | No | `Due on Receipt, Net 15, Net 30, Net 45, Net 60` |
| Tax ID | Single Line | `Tax_ID` | No | GSTIN / VAT |
| PAN | Single Line | `PAN` | No | India PAN |
| Billing Address | Address | `Billing_Address` | No | Zoho Creator Address type (composite) |
| Shipping Address | Address | `Shipping_Address` | No | Zoho Creator Address type (composite) |
| Status | Dropdown | `Status` | No | `Active, Inactive` — default Active |
| Remarks | Multi Line | `Remarks` | No | |

### Subform: Account Contacts
| Label | Field Type | Notes |
| Salutation | Dropdown | `Mr, Ms, Mrs, Dr` |
| First Name | Single Line | |
| Last Name | Single Line | |
| Email | Email | |
| Phone | Phone | |
| Mobile | Phone | |
| Designation | Single Line | |
| Department | Single Line | |
| Is Primary | Checkbox | |

### Subform: Account Documents
| Label | Field Type | Notes |
| Document Name | Single Line | |
| File | Upload | |
| Expiry Date | Date | |
| Notes | Single Line | |

### Validation Rules
1. **Account Name required** — On Submit, if `Account_Name` is blank → `alert "Account Name is required."`

### Deluge Scripts

---

## 1.3 Projects Form (`Projects`)

### Field Configuration
| Label | Field Type | API Name | Required | Notes |
|---|---|---|---|---|
| Project Name | Single Line | `Project_Name` | Yes | |
| Project Code | Auto Number | `Project_Code` | Yes | Format: `PROJ-{0000}` |
| Account | Lookup → Accounts | `Account` | No | Client/company |
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
1. **End Date after Start Date** — On Submit, if `End_Date` is not null and `Start_Date` is not null and `End_Date < Start_Date` → `alert "End Date must be after Start Date."`

### Deluge Scripts

#### On Submit — Validate Project Completion
```deluge
/* JUSTIFICATION: Completion validation requires cross-form queries across Expenses, POs, and PRs — cannot be handled by embedded subform submission alone */
/* ===== PSEUDOCODE =====
   Trigger: On Submit — when Project record is saved with Status = "Completed"
   
   1. Get the display value of the Status field from the current record
   2. Check if Status is "Completed" AND the record already exists (not a new insert)
   3. If condition met:
      a. Query all Expenses for this Project where Status = "Submitted"
      b. If any open expenses exist: alert error listing the count
      c. Query all Purchase Orders for this Project where Status = "Open"
      d. If any open POs exist: alert error listing the count
      e. Query all Purchase Requisitions for this Project where Status = "Open"
      f. If any open PRs exist: alert error listing the count
   4. If no open dependencies found: allow completion (no action needed)
   5. If Status is not "Completed": skip — no validation required
   ===== END PSEUDOCODE ===== */
status_val = ifnull(input.Status.toMap().get("display_value"), "");

if (status_val == "Completed" && !input.ID.isNull())
{
    exp_criteria = "Project == " + input.ID + " && Status == 'Submitted'";
    open_expenses = zoho.creator.getRecords("budget_tracking", "Expenses", exp_criteria, 1, 200);
    if (!open_expenses.isNull() && open_expenses.size() > 0)
    {
        alert "Cannot complete project: " + open_expenses.size().toString() + " expense(s) are still open.";
    }

    po_criteria = "Project == " + input.ID + " && Status == 'Open'";
    open_pos = zoho.creator.getRecords("budget_tracking", "Purchase_Orders", po_criteria, 1, 200);
    if (!open_pos.isNull() && open_pos.size() > 0)
    {
        alert "Cannot complete project: " + open_pos.size().toString() + " PO(s) are still open.";
    }

    pr_criteria = "Project == " + input.ID + " && Status == 'Open'";
    open_prs = zoho.creator.getRecords("budget_tracking", "Purchase_Requisitions", pr_criteria, 1, 200);
    if (!open_prs.isNull() && open_prs.size() > 0)
    {
        alert "Cannot complete project: " + open_prs.size().toString() + " PR(s) are still open.";
    }
}
```

---

## 1.4 Warehouses Form (`Warehouses`)

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
1. **Warehouse Name required** — On Submit, if `Warehouse_Name` is blank → `alert "Warehouse Name is required."`

### Deluge Scripts
No Deluge scripts required for Phase 1A Warehouses. Auto-number handled by field type.

### Seeding
After form creation, manually create one default record:
- Warehouse Name: "Main Warehouse"
- Status: "Active"

---

## 1.5 Inventory Items Form (`Inventory_Items`)

### Field Configuration
| Label | Field Type | API Name | Required | Notes |
|---|---|---|---|---|
| Item Name | Single Line | `Item_Name` | Yes | |
| SKU | Auto Number | `SKU` | Yes | Format: `SKU-{0000}` |
| Item Type | Dropdown | `Item_Type` | No | `Goods, Services` |
| Category | Dropdown | `Category` | No | `Raw Material, Component, Consumable, Equipment, Service, Subcontract` |
| Unit | Dropdown | `Unit` | No | `Pcs, Kg, Ltr, Box, Meter, Hour, Day, Set, Pair, Nos` |
| HSN/SAC Code | Single Line | `HSN_SAC_Code` | No | Tax classification |
| Taxability | Dropdown | `Taxability` | No | `Taxable, Non-Taxable, Zero-Rated` |
| Tax Rate | Decimal | `Tax_Rate` | No | Default tax % |
| Purchase Price | Currency | `Purchase_Price` | No | Default unit cost |
| Reorder Level | Decimal | `Reorder_Level` | No | Min stock alert |
| Preferred Vendor | Lookup → Vendors | `Preferred_Vendor` | No | Default vendor for POs |
| Current Stock | Decimal | `Current_Stock` | No | Maintained by Deluge |
| Stock Value | Formula | `Stock_Value` | — | `Current_Stock * Purchase_Price` |
| Description | Multi Line | `Description` | No | |
| Status | Dropdown | `Status` | No | `Active, Inactive` — default Active |

### Subform: Stock by Warehouse
| Label | Field Type | Notes |
| Warehouse | Lookup → Warehouses | |
| Current Stock | Decimal | Maintained by Deluge |
| Reserved Qty | Decimal | Default 0 |
| Available Stock | Formula | `Current_Stock - Reserved_Qty` |
| Reorder Level | Decimal | Override item default |

### Validation Rules
1. **Item Name required** — On Submit, if `Item_Name` is blank → `alert "Item Name is required."`
2. **Positive Purchase Price** — On Submit, if `Purchase_Price` is not null and `Purchase_Price < 0` → `alert "Purchase Price cannot be negative."`
3. **Goods require Unit** — On Submit, if `Item_Type == "Goods"` and `Unit` is blank → `alert "Unit is required for Goods items."`

### Deluge Scripts
```deluge
/* Embedded subform: Stock_by_Warehouse
   Users manually enter stock quantities per warehouse.
   No auto-creation — Deluge does not manage embedded subform records.
   Stock_Value is a Formula field: Current_Stock * Purchase_Price */
```

---

## Build Verification Checklist
After building Phase 1A, verify:
1. Vendors form creates records with all fields saving correctly
2. Vendor Contacts subform adds contact persons
3. Vendor Documents subform uploads files
4. Accounts form creates records with all fields saving correctly
5. Account Contacts subform adds contact persons
6. Account Documents subform uploads files
7. Projects form generates PROJ-0001, PROJ-0002...
8. Account lookup in Projects shows Accounts list
9. Warehouses form generates WH-0001, WH-0002...
10. Inventory Items generates SKU-0001, SKU-0002...
11. Stock_by_Warehouse subform accepts manual warehouse entries

## Next Phase
→ Proceed to `PHASE_1B_BUILD.md` when all above forms are verified.
