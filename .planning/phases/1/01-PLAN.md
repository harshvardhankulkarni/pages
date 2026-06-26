# Phase 1: Master Data & Admin — Plan

## Overview

Build 8 master-data forms in Zoho Creator (India datacenter, `.in` domain) plus 13 user profiles. No upstream dependencies. These forms are prerequisites for all subsequent phases (Sales, Purchase, Production, Project Management).

**Execution mode**: 100% Zoho Creator UI (form designer, field properties, report builder) + Deluge for auto-number generation, auto-fetch lookups, and validation. No external integrations.

**Total forms**: 8. **Total profiles**: 13. **Total reports**: 8 (one per form).

---

## Prerequisites

### 1. Create the Zoho Creator App

| Step | Action | Details |
|------|--------|---------|
| 1.1 | Log into Zoho Creator | Go to `https://creator.zoho.in` (India datacenter — critical) |
| 1.2 | Create new app | Name: **Chemsol** |
| 1.3 | Select datacenter | **India (`.in`)** — not changeable after creation |
| 1.4 | Verify region | App URL should be `https://creator.zoho.in/chemsol/...` |
| 1.5 | Enable audit fields | Settings > Form > Show Audit Fields (Created By, Created Time, Modified By, Modified Time) — enable ONCE at app level. All forms inherit. |

### 2. Create 13 User Profiles

Settings > Users & Permissions > Profiles > Create Profile. Create ALL 13 now even if some have no Phase 1 form access — later phases will add permissions.

| # | Profile Name | Description |
|---|-------------|-------------|
| 1 | Admin | System configuration, master data, user access |
| 2 | Purchase Manager | PR approval, PO creation, supplier management |
| 3 | Purchase Executive | PR initiation, rate comparison, GRN entry |
| 4 | Store Manager | Inventory oversight, material issues, FG receiving |
| 5 | Store Keeper | Daily store ops, material movement |
| 6 | Production Manager | Production planning, batch management |
| 7 | Production Executive | MR creation, RM consumption, packing |
| 8 | QC Inspector | Quality inspection, test results entry |
| 9 | Sales Executive | SO/WO creation, customer management |
| 10 | Project Manager | Project creation, tracking, task management |
| 11 | Project Coordinator | Daily project updates, coordination |
| 12 | Finance Executive | Payment tracking, financial reports |
| 13 | Viewer | Read-only access to assigned forms/reports |

**Profile creation steps per profile:**
- Click "Create Profile"
- Enter Profile Name (e.g., "Admin")
- Do NOT change any default form permissions yet (will configure per form in sections below)
- Save

After all 13 profiles exist, return to each form to set permissions.

### 3. App-Level Settings

| Setting | Value |
|---------|-------|
| App name | Chemsol |
| App URL slug | `chemsol` (auto-generated) |
| Time zone | Asia/Kolkata (IST) |
| Date format | DD/MM/YYYY |
| Currency | INR (₹) |
| Audit fields | Enabled (Created By, Created Time, Modified By, Modified Time) |

---

## Forms to Build (Ordered by Dependency)

---

### Form 1: Store Master

**Dependency**: None. Simplest form, establishes store lookup for Bin Location.

**Internal name**: `Store_Master`
**Form name displayed**: Store Master

#### Fields

| # | Field Label | Field Type | Required | Properties |
|---|-------------|-----------|----------|------------|
| 1 | Store Code | Auto Number | Yes (auto) | Format: `ST-{000}`. Read-only. Starts at 1. |
| 2 | Store Name | Text (Single) | Yes | Max length: 100. Unique (no duplicate store names). |
| 3 | Store Type | Dropdown | Yes | Options: **RM**, **FG**, **QC**, **Site** |
| 4 | Location | Text (Single) | No | Max length: 200 |

**Creator notes:**
- Store Code: Insert > Auto Number. Set custom format `ST-{000}`. Check "Read Only".
- Store Name: Insert > Text. Check "Required" and "Unique".
- Store Type: Insert > Dropdown. Manually enter 4 options. Check "Required".
- Location: Insert > Text.

**Audit fields**: Created By, Created Time, Modified By, Modified Time (auto-enabled at app level).

#### Reports

Create one List Report via Reports tab > New Report > List Report.

| Property | Value |
|----------|-------|
| Report name | Store Master List |
| Columns | Store Code, Store Name, Store Type, Location |
| Default sort | Store Code ascending |
| Filters | Optional: by Store Type |
| Search | Enable on Store Name, Store Code |
| Summary | Record count at footer |

#### Permissions

Set in Form > Permissions tab. For each profile below, set the checkboxes:

| Profile | Create | Read | Update | Delete |
|---------|--------|------|--------|--------|
| Admin | ✓ | ✓ | ✓ | ✓ |
| Purchase Manager | — | — | — | — |
| Purchase Executive | — | — | — | — |
| Store Manager | ✓ | ✓ | ✓ | ✓ |
| Store Keeper | ✓ | ✓ | ✓ | ✓ |
| Production Manager | — | ✓ | — | — |
| Production Executive | — | — | — | — |
| QC Inspector | — | — | — | — |
| Sales Executive | — | — | — | — |
| Project Manager | — | — | — | — |
| Project Coordinator | — | — | — | — |
| Finance Executive | — | — | — | — |
| Viewer | — | ✓ | — | — |

---

### Form 2: Supplier Master

**Dependency**: None. Item Master references this form via Preferred Supplier lookup.

**Internal name**: `Supplier_Master`
**Form name displayed**: Supplier Master

#### Fields

| # | Field Label | Field Type | Required | Properties |
|---|-------------|-----------|----------|------------|
| 1 | Supplier Code | Auto Number | Yes (auto) | Format: `SUP-{000}`. Read-only. Starts at 1. |
| 2 | Supplier Name | Text (Single) | Yes | Max 150 |
| 3 | Supplier Type | Dropdown | No | Options: **Manufacturer**, **Distributor**, **Trader**, **Service Provider** |
| 4 | GSTIN | Text (Single) | Yes | Max 15. Regex validation: `^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$` |
| 5 | PAN No | Text (Single) | Yes | Max 10. Regex: `^[A-Z]{5}[0-9]{4}[A-Z]{1}$` |
| 6 | Contact Person | Text (Single) | Yes | Max 100 |
| 7 | Mobile No | Text (Single) | Yes | Max 15. Min 10 digits. |
| 8 | Alternate Mobile | Text (Single) | No | Max 15 |
| 9 | Email ID | Text (Single) | Yes | Creator "Email" field type. |
| 10 | Address | Text (Multi-line) | Yes | 4-5 rows visible |
| 11 | Pincode | Text (Single) | No | Max 10. Regex: `^\d{6}$` |
| 12 | Bank Name | Text (Single) | Yes | Max 100 |
| 13 | Account No | Text (Single) | Yes | Max 20 |
| 14 | IFSC Code | Text (Single) | Yes | Max 11. Regex: `^[A-Z]{4}0[A-Z0-9]{6}$` |
| 15 | Payment Terms | Dropdown | Yes | Options: **Advance**, **7 Days**, **15 Days**, **30 Days**, **45 Days**, **60 Days**, **On Delivery** |
| 16 | Credit Days | Number (Integer) | Yes | Min 0 |

**Field-level security**: Account No and IFSC Code should be hidden from Viewer and non-Purchase profiles. Set in Field > Properties > Access:
- Profiles with View access: Admin, Purchase Manager, Finance Executive (View + Edit)
- All other profiles: No Access

#### UI Layout — 3 Sections

```
┌─ Section: Basic Details ─────────────────────────────────────┐
│ Supplier Code [Auto]    Supplier Name [____________________]  │
│ Supplier Type [▼]       GSTIN [___________________________]   │
│ PAN No [_______________]                                       │
└───────────────────────────────────────────────────────────────┘
┌─ Section: Contact ────────────────────────────────────────────┐
│ Contact Person [________]    Mobile No [________________]     │
│ Alternate Mobile [________]  Email ID [________________]      │
│ Address [Multi-line text area - 4 rows]                      │
│ Pincode [___________]                                         │
└───────────────────────────────────────────────────────────────┘
┌─ Section: Bank & Terms ──────────────────────────────────────┐
│ Bank Name [______________]   Account No [_________________]  │
│ IFSC Code [_______________]                                   │
│ Payment Terms [▼]           Credit Days [________]           │
└───────────────────────────────────────────────────────────────┘
```

#### Reports

| Property | Value |
|----------|-------|
| Report name | Supplier Master List |
| Columns | All 16 fields (excluding audit fields) |
| Default sort | Supplier Name ascending |
| Filters | Optional: by Supplier Type |
| Search | Enable on Supplier Name, GSTIN, PAN No, Contact Person |
| Summary | Record count |

#### Permissions

| Profile | Create | Read | Update | Delete |
|---------|--------|------|--------|--------|
| Admin | ✓ | ✓ | ✓ | ✓ |
| Purchase Manager | ✓ | ✓ | ✓ | ✓ |
| Purchase Executive | ✓ | ✓ | ✓ | ✓ |
| Store Manager | — | — | — | — |
| Store Keeper | — | — | — | — |
| Production Manager | — | — | — | — |
| Production Executive | — | — | — | — |
| QC Inspector | — | — | — | — |
| Sales Executive | — | — | — | — |
| Project Manager | — | — | — | — |
| Project Coordinator | — | — | — | — |
| Finance Executive | — | ✓ | — | — |
| Viewer | — | ✓ | — | — |

---

### Form 3: Customer Master

**Dependency**: None.

**Internal name**: `Customer_Master`
**Form name displayed**: Customer Master

#### Fields

| # | Field Label | Field Type | Required | Properties |
|---|-------------|-----------|----------|------------|
| 1 | Customer Code | Auto Number | Yes (auto) | Format: `CUS-{000}`. Read-only. Starts at 1. |
| 2 | Client Org Name | Text (Single) | Yes | Max 150 |
| 3 | Contact Person | Text (Single) | Yes | Max 100 |
| 4 | Contact No | Text (Single) | Yes | Max 15. Min 10 digits. |
| 5 | Alt Contact No | Text (Single) | No | Max 15 |
| 6 | Email | Text (Single) — Email | Yes | Creator "Email" field type |
| 7 | GST No | Text (Single) | Yes | Max 15. Regex: `^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$` |
| 8 | PAN | Text (Single) | Yes | Max 10. Regex: `^[A-Z]{5}[0-9]{4}[A-Z]{1}$` |
| 9 | Regd Address | Text (Multi-line) | Yes | 4 rows |
| 10 | Billing Address | Text (Multi-line) | No | 4 rows |
| 11 | Shipping Address | Text (Multi-line) | No | 4 rows |

#### UI Layout — 3 Sections

```
┌─ Section: Basic Details ──────────────────────────────────────┐
│ Customer Code [Auto]    Client Org Name [__________________]  │
│ Contact Person [_______] Contact No [____________________]    │
│ Alt Contact No [_______] Email [_________________________]    │
└───────────────────────────────────────────────────────────────┘
┌─ Section: GST/PAN ────────────────────────────────────────────┐
│ GST No [________________]    PAN [_________________________]  │
└───────────────────────────────────────────────────────────────┘
┌─ Section: Addresses ─────────────────────────────────────────┐
│ Regd Address [Multi-line text area - 4 rows]                  │
│ Billing Address [Multi-line text area - 4 rows]               │
│ Shipping Address [Multi-line text area - 4 rows]              │
└───────────────────────────────────────────────────────────────┘
```

#### Reports

| Property | Value |
|----------|-------|
| Report name | Customer Master List |
| Columns | Customer Code, Client Org Name, Contact Person, Contact No, Email, GST No, PAN, Regd Address, Billing Address, Shipping Address |
| Default sort | Client Org Name ascending |
| Search | Enable on Client Org Name, GST No, Contact Person |
| Summary | Record count |

#### Permissions

| Profile | Create | Read | Update | Delete |
|---------|--------|------|--------|--------|
| Admin | ✓ | ✓ | ✓ | ✓ |
| Purchase Manager | — | — | — | — |
| Purchase Executive | — | — | — | — |
| Store Manager | — | — | — | — |
| Store Keeper | — | — | — | — |
| Production Manager | — | — | — | — |
| Production Executive | — | — | — | — |
| QC Inspector | — | — | — | — |
| Sales Executive | ✓ | ✓ | ✓ | ✓ |
| Project Manager | ✓ | ✓ | ✓ | ✓ |
| Project Coordinator | ✓ | ✓ | ✓ | ✓ |
| Finance Executive | — | ✓ | — | — |
| Viewer | — | ✓ | — | — |

---

### Form 4: Item Master

**Dependency**: Supplier Master (Preferred Supplier is a Lookup). Build Supplier Master first.

**Internal name**: `Item_Master`
**Form name displayed**: Item Master

#### Fields

| # | Field Label | Field Type | Required | Properties |
|---|-------------|-----------|----------|------------|
| 1 | Category of Purchase Item | Dropdown | Yes | Options: **RM**, **PM**, **FG**, **CON**, **SVC** |
| 2 | Purchase Item Code | Text (Single) | Yes | Max 10. **Unique**. Read-only (auto-generated by Deluge). |
| 3 | Purchase Item Name | Text (Single) | Yes | Max 200. |
| 4 | UOM | Dropdown | Yes | Options: **Sq.Ft**, **Sq.Mtr**, **Kg**, **Litre**, **Nos**, **Meter**, **Roll**, **Packet**, **Bag**, **Drum**, **Set**, **Hour**, **Day** |
| 5 | HSN Code | Text (Single) | Yes | Max 10. Regex: `^\d{4,8}$` |
| 6 | GST % | Decimal | No | 2 decimal places. Range: 0–100 |
| 7 | Min Stock | Number (Integer) | Yes | Min 0 |
| 8 | Max Stock | Number (Integer) | No | Min 0 |
| 9 | Standard Rate | Currency | No | INR. 2 decimal places. |
| 10 | Preferred Supplier | Lookup | No | Target: **Supplier Master**. Display field: **Supplier Name**. Use Autocomplete mode. |
| 11 | Lead Time (Days) | Number (Integer) | No | Min 0 |

**Creator notes:**
- Preferred Supplier: Insert > Lookup. Select form "Supplier Master", display field "Supplier Name". Enable "Autocomplete" for large lists.
- Purchase Item Code: Mark as "Read Only" in field properties (users should not manually edit).
- Standard Rate: Insert > Currency. Set Currency = INR.

#### Deluge Workflow 1: Auto-Generate Item Code

**Trigger**: On Submit — Before record is added to the database
**Purpose**: Construct `{Category}-{3-digit seq}` code

```deluge
prefix = input.Category_of_Purchase_Item;
if(prefix != null && prefix != "")
{
    last_records = zoho.creator.getRecords("chemsol", "Item_Master",
        "Category_of_Purchase_Item == '" + prefix + "'",
        1, "Purchase_Item_Code desc");
    last_seq = 0;
    if(last_records.size() > 0 && last_records.get(0).get("Purchase_Item_Code") != null)
    {
        last_code = last_records.get(0).get("Purchase_Item_Code").toString();
        if(last_code.contains("-"))
        {
            last_seq = last_code.substringAfter("-").toLong();
        }
    }
    new_seq = last_seq + 1;
    formatted_seq = new_seq.toString().padLeft(3, "0");
    input.Purchase_Item_Code = prefix + "-" + formatted_seq;
}
else
{
    throw "Please select a Category before saving.";
}
```

**Test cases:**
- First RM item → RM-001
- Next RM item → RM-002
- After RM-009 → RM-010
- First FG item → FG-001

#### Deluge Workflow 2: Validation — On Submit (Before, combined with auto-number)

```deluge
// --- Auto-number (same code as above) ---
prefix = input.Category_of_Purchase_Item;
if(prefix != null && prefix != "")
{
    last_records = zoho.creator.getRecords("chemsol", "Item_Master",
        "Category_of_Purchase_Item == '" + prefix + "'",
        1, "Purchase_Item_Code desc");
    last_seq = 0;
    if(last_records.size() > 0 && last_records.get(0).get("Purchase_Item_Code") != null)
    {
        last_code = last_records.get(0).get("Purchase_Item_Code").toString();
        if(last_code.contains("-"))
        {
            last_seq = last_code.substringAfter("-").toLong();
        }
    }
    new_seq = last_seq + 1;
    formatted_seq = new_seq.toString().padLeft(3, "0");
    input.Purchase_Item_Code = prefix + "-" + formatted_seq;
}
else
{
    throw "Please select a Category before saving.";
}

// --- GST % range check ---
if(input.GST_Percent != null)
{
    if(input.GST_Percent < 0 || input.GST_Percent > 100)
    {
        throw "GST % must be between 0 and 100.";
    }
}

// --- Min Stock <= Max Stock ---
if(input.Min_Stock != null && input.Max_Stock != null)
{
    if(input.Min_Stock > input.Max_Stock)
    {
        throw "Min Stock cannot be greater than Max Stock.";
    }
}

// --- Duplicate Item Name check ---
if(input.Purchase_Item_Name != null && input.Purchase_Item_Name != "")
{
    existing = zoho.creator.getRecords("chemsol", "Item_Master",
        "Purchase_Item_Name == '" + q(input.Purchase_Item_Name) + "'", 1, 0);
    if(existing.size() > 0)
    {
        throw "An item with this name already exists.";
    }
}
```

#### UI Layout — 2 Sections

```
┌─ Section: Basic Details ──────────────────────────────────────┐
│ Category of Purchase Item [▼]                                  │
│ Purchase Item Code [Auto]    Purchase Item Name [___________]  │
│ UOM [▼]                      HSN Code [___________________]    │
│ GST % [_________]                                              │
└───────────────────────────────────────────────────────────────┘
┌─ Section: Inventory & Purchase ───────────────────────────────┐
│ Min Stock [______]         Max Stock [__________________]      │
│ Standard Rate [______]     Preferred Supplier [Lookup ▼]      │
│ Lead Time (Days) [____]                                        │
└───────────────────────────────────────────────────────────────┘
```

#### Reports

| Property | Value |
|----------|-------|
| Report name | Purchase Item Master |
| Columns | Category, Item Code, Item Name, UOM, HSN Code, Min Stock, Max Stock, Standard Rate, Preferred Supplier, Lead Time |
| Default sort | Item Code ascending |
| Default filter | By Category (e.g., show RM by default — or remove default filter so all shown) |
| Grouping | By Category |
| Search | Enable on Item Name, Item Code, HSN Code |
| Summary | Record count, Sum of Min Stock/Max Stock |

#### Permissions

| Profile | Create | Read | Update | Delete |
|---------|--------|------|--------|--------|
| Admin | ✓ | ✓ | ✓ | ✓ |
| Purchase Manager | ✓ | ✓ | ✓ | ✓ |
| Purchase Executive | ✓ | ✓ | ✓ | ✓ |
| Store Manager | ✓ | ✓ | ✓ | ✓ |
| Store Keeper | ✓ | ✓ | ✓ | ✓ |
| Production Manager | ✓ | ✓ | ✓ | ✓ |
| Production Executive | ✓ | ✓ | ✓ | ✓ |
| QC Inspector | ✓ | ✓ | ✓ | ✓ |
| Sales Executive | — | ✓ | — | — |
| Project Manager | — | — | — | — |
| Project Coordinator | — | — | — | — |
| Finance Executive | — | — | — | — |
| Viewer | — | ✓ | — | — |

---

### Form 5: System Master

**Dependency**: None. Foundation for BOM Master.

**Internal name**: `System_Master`
**Form name displayed**: System Master

#### Fields

| # | Field Label | Field Type | Required | Properties |
|---|-------------|-----------|----------|------------|
| 1 | System Type | Dropdown | Yes | Options: **EP**, **PU**, **DEM**, **NUM**, **ARR**, **ANTI**, **ESD**, **FIL**, **COV** |
| 2 | System Code | Text (Single) | Yes | Max 10. **Unique**. Read-only (auto-generated by Deluge). |
| 3 | System Name | Text (Single) | Yes | Max 200. E.g., "3mm Epoxy Flooring" |
| 4 | Thickness | Text (Single) | No | Max 50. Free text e.g., "3mm", "4mm", "100 micron" |
| 5 | Description | Text (Multi-line) | No | 4 rows |
| 6 | UOM | Dropdown | Yes | Options: **Sq.Ft**, **Sq.Mtr** (system-level UOM is area-based) |

**Creator notes:**
- System Type dropdown: manually enter all 9 options.
- System Code: Mark Read-Only. Set Unique.

#### Deluge Workflow: Auto-Generate System Code

**Trigger**: On Submit — Before record is added to the database
**Purpose**: Construct `{System Type}-{3-digit seq}` code

```deluge
prefix = input.System_Type;
if(prefix != null && prefix != "")
{
    last_records = zoho.creator.getRecords("chemsol", "System_Master",
        "System_Type == '" + prefix + "'",
        1, "System_Code desc");
    last_seq = 0;
    if(last_records.size() > 0 && last_records.get(0).get("System_Code") != null)
    {
        last_code = last_records.get(0).get("System_Code").toString();
        if(last_code.contains("-"))
        {
            last_seq = last_code.substringAfter("-").toLong();
        }
    }
    new_seq = last_seq + 1;
    formatted_seq = new_seq.toString().padLeft(3, "0");
    input.System_Code = prefix + "-" + formatted_seq;
}
else
{
    throw "Please select a System Type before saving.";
}
```

#### UI Layout — 1 Section

```
┌─ Section: System Details ─────────────────────────────────────┐
│ System Type [▼]              System Code [Auto]               │
│ System Name [_______________________________________]        │
│ Thickness [________________] UOM [▼]                         │
│ Description [Multi-line text area - 4 rows]                  │
└───────────────────────────────────────────────────────────────┘
```

#### Reports

| Property | Value |
|----------|-------|
| Report name | System Master List |
| Columns | System Code, System Name, Thickness, UOM, Description |
| Default sort | System Code ascending |
| Search | Enable on System Code, System Name |
| Summary | Record count |

#### Permissions

| Profile | Create | Read | Update | Delete |
|---------|--------|------|--------|--------|
| Admin | ✓ | ✓ | ✓ | ✓ |
| Purchase Manager | — | — | — | — |
| Purchase Executive | — | — | — | — |
| Store Manager | — | — | — | — |
| Store Keeper | — | — | — | — |
| Production Manager | ✓ | ✓ | ✓ | ✓ |
| Production Executive | ✓ | ✓ | ✓ | ✓ |
| QC Inspector | — | — | — | — |
| Sales Executive | ✓ | ✓ | ✓ | ✓ |
| Project Manager | ✓ | ✓ | ✓ | ✓ |
| Project Coordinator | ✓ | ✓ | ✓ | ✓ |
| Finance Executive | — | — | — | — |
| Viewer | — | ✓ | — | — |

---

### Form 6: BOM Master

**Dependency**: System Master (System Code lookup) + Item Master (Item Code lookup). Both must be built first.

**Architecture decision**: Separate form (not subform of System Master) with a subform for line items. Single-level BOM (one System → multiple RM/PM items).

**Internal name**: `BOM_Master`
**Form name displayed**: BOM Master

#### Header Fields

| # | Field Label | Field Type | Required | Properties |
|---|-------------|-----------|----------|------------|
| 1 | BOM Code | Auto Number | Yes (auto) | Format: `BOM-{000}`. Read-only. Starts at 1. |
| 2 | System Code | Lookup | Yes | Target: **System Master**. Display field: **System Code**. Autocomplete mode. |
| 3 | System Name | Text (Single) | Yes | Read-only. Auto-fetched from System Code. |
| 4 | Description | Text (Multi-line) | No | 3 rows |

#### Subform: BOM Items

Create subform named **BOM Items** in the BOM Master form designer. Add these fields inside the subform:

| # | Field Label | Field Type | Required | Properties |
|---|-------------|-----------|----------|------------|
| 1 | Item Code | Lookup (inside subform) | Yes | Target: **Item Master**. Display field: **Purchase Item Code**. Autocomplete mode. |
| 2 | Item Name | Text (Single) | Yes | Read-only. Auto-fetched from Item Code. |
| 3 | Quantity | Decimal | Yes | 3 decimal places. Min value: 0.001 |
| 4 | UOM | Text (Single) | Yes | Read-only. Auto-fetched from Item Master. |

**Subform settings:**
- Enable "Add Row" button
- Enable "Delete Row" for each row
- Limit: 50 rows (default max is fine)
- Column widths: Item Code (30%), Item Name (25%), Quantity (20%), UOM (15%), Delete (10%)

#### Deluge Workflow 1: Auto-Fetch System Name

**Trigger**: On User Input — System Code field (header level)
**Purpose**: Fetch System Name from System Master when user selects a System Code

```deluge
sys_id = input.System_Code;
if(sys_id != null)
{
    sys_data = zoho.creator.getRecordById("chemsol", "System_Master", sys_id);
    if(sys_data != null)
    {
        input.System_Name = sys_data.get("System_Name");
    }
}
```

#### Deluge Workflow 2: Auto-Fetch Item Name + UOM (subform)

**Trigger**: On User Input — Item Code field (inside BOM Items subform row)
**Purpose**: When user selects an item, populate Item Name and UOM in the same subform row

```deluge
item_id = input.Item_Code;
if(item_id != null)
{
    item_data = zoho.creator.getRecordById("chemsol", "Item_Master", item_id);
    if(item_data != null)
    {
        input.Item_Name = item_data.get("Purchase_Item_Name");
        input.UOM = item_data.get("UOM");
    }
}
```

**Configuration note**: In Creator, you add an "On User Input" workflow on the subform's Item Code field. The `input` context in a subform workflow refers to the current subform row's fields.

#### Deluge Workflow 3: BOM Validation

**Trigger**: On Submit — Before record is added to the database
**Purpose**: Validate quantity > 0 and no duplicate items

```deluge
// Validate each BOM item
item_codes = List();
foreach item in input.BOM_Items
{
    if(item.Quantity <= 0)
    {
        throw "Quantity must be greater than zero for all BOM items.";
    }

    if(item_codes.contains(item.Item_Code))
    {
        throw "Duplicate item found in BOM. Each item can only appear once.";
    }

    item_codes.add(item.Item_Code);
}

// Ensure at least one BOM item exists
if(input.BOM_Items.size() == 0)
{
    throw "At least one BOM item is required.";
}
```

#### UI Layout

```
┌─ Section: BOM Details ──────────────────────────────────────┐
│ BOM Code [Auto]          System Code [Lookup ▼]             │
│ System Name [Auto] (read-only)                               │
│ Description [Multi-line - 3 rows]                            │
│                                                               │
│ ┌─ BOM Items (Subform) ──────────────────────────────────────┐│
│ │ Item Code  | Item Name    | Quantity | UOM  |   Delete   ││
│ │ [Lookup ▼] | [Auto]       | [____]   |[Auto]| [X]        ││
│ │ [Lookup ▼] | [Auto]       | [____]   |[Auto]| [X]        ││
│ │ [ + Add Row ]                                              ││
│ └─────────────────────────────────────────────────────────────┘│
└───────────────────────────────────────────────────────────────┘
```

#### Reports

| Property | Value |
|----------|-------|
| Report name | BOM Master List |
| Columns | BOM Code, System Code, System Name, Item Code (from subform), Item Name (from subform), Quantity (from subform), UOM (from subform) |
| Grouping | By System Code |
| Default sort | System Code ascending, then Item Code ascending |
| Search | Enable on System Code, System Name, Item Code, Item Name |
| Summary | Count of systems, count of items per system |

**Note**: For subform fields in reports, Creator may require using a Summary Report with "Show subform data as rows" option, or create the report by referencing the subform's fields directly.

#### Permissions

| Profile | Create | Read | Update | Delete |
|---------|--------|------|--------|--------|
| Admin | ✓ | ✓ | ✓ | ✓ |
| Purchase Manager | — | — | — | — |
| Purchase Executive | — | — | — | — |
| Store Manager | — | — | — | — |
| Store Keeper | — | — | — | — |
| Production Manager | ✓ | ✓ | ✓ | ✓ |
| Production Executive | ✓ | ✓ | ✓ | ✓ |
| QC Inspector | ✓ | ✓ | ✓ | ✓ |
| Sales Executive | — | — | — | — |
| Project Manager | — | — | — | — |
| Project Coordinator | — | — | — | — |
| Finance Executive | — | ✓ | — | — |
| Viewer | — | ✓ | — | — |

---

### Form 7: Bin Location Master

**Dependency**: Store Master (Store Name lookup). Build Store Master first.

**Internal name**: `Bin_Location_Master`
**Form name displayed**: Bin Location Master

#### Fields

| # | Field Label | Field Type | Required | Properties |
|---|-------------|-----------|----------|------------|
| 1 | Bin Code | Auto Number | Yes (auto) | Format: `BIN-{000}`. Read-only. Starts at 1. |
| 2 | Store Name | Lookup | Yes | Target: **Store Master**. Display field: **Store Name**. Dropdown mode (few stores). |
| 3 | Store Type | Text (Single) | No | Read-only. Auto-fetched from Store Master. |
| 4 | Location | Text (Single) | No | Read-only. Auto-fetched from Store Master. |
| 5 | Rack No | Text (Single) | Yes | Max 50 |
| 6 | Shelf No | Text (Single) | Yes | Max 50 |
| 7 | Bin No | Text (Single) | Yes | Max 50 |

**Note on Store Type and Location**: These are convenience auto-fetch fields so users can see the store details without navigating away. They are read-only and not required.

#### Deluge Workflow: Auto-Fetch Store Details

**Trigger**: On User Input — Store Name field
**Purpose**: Fetch Store Type and Location from Store Master

```deluge
store_id = input.Store_Name;
if(store_id != null)
{
    store_data = zoho.creator.getRecordById("chemsol", "Store_Master", store_id);
    if(store_data != null)
    {
        input.Store_Type = store_data.get("Store_Type");
        input.Location = store_data.get("Location");
    }
}
```

#### UI Layout — 1 Section

```
┌─ Section: Bin Location Details ──────────────────────────────┐
│ Bin Code [Auto]               Store Name [Lookup ▼]         │
│ Store Type [Auto] (read-only) Location [Auto] (read-only)   │
│ Rack No [___________]         Shelf No [_______________]     │
│ Bin No [_____________]                                       │
└───────────────────────────────────────────────────────────────┘
```

#### Reports

| Property | Value |
|----------|-------|
| Report name | Bin Location List |
| Columns | Bin Code, Store Name, Store Type, Location, Rack No, Shelf No, Bin No |
| Default filter | By Store Name |
| Default sort | Store Name ascending, then Rack No ascending, then Shelf No ascending, then Bin No ascending |
| Search | Enable on Store Name, Rack No, Shelf No, Bin No |
| Summary | Record count |

#### Permissions

| Profile | Create | Read | Update | Delete |
|---------|--------|------|--------|--------|
| Admin | ✓ | ✓ | ✓ | ✓ |
| Purchase Manager | — | — | — | — |
| Purchase Executive | — | — | — | — |
| Store Manager | ✓ | ✓ | ✓ | ✓ |
| Store Keeper | ✓ | ✓ | ✓ | ✓ |
| Production Manager | — | — | — | — |
| Production Executive | — | — | — | — |
| QC Inspector | — | — | — | — |
| Sales Executive | — | — | — | — |
| Project Manager | — | — | — | — |
| Project Coordinator | — | — | — | — |
| Finance Executive | — | — | — | — |
| Viewer | — | ✓ | — | — |

---

### Form 8: User Access & Approval Matrix

**Dependency**: None. No lookup dependencies — User Name uses Creator's native User field type.

**Internal name**: `User_Access`
**Form name displayed**: User Access & Approval Matrix

#### Fields

| # | Field Label | Field Type | Required | Properties |
|---|-------------|-----------|----------|------------|
| 1 | User Code | Auto Number | Yes (auto) | Format: `USR-{000}`. Read-only. Starts at 1. |
| 2 | User Name | User | Yes | Creator "User" field type. Dropdown of all org users. |
| 3 | Department | Dropdown | Yes | Options: **Admin**, **Purchase**, **Store & Logistics**, **Production**, **QC**, **Sales**, **Project Management**, **Account & Finance** |
| 4 | Role | Dropdown | Yes | Options: **Admin**, **Purchase Manager**, **Purchase Executive**, **Store Manager**, **Store Keeper**, **Production Manager**, **Production Executive**, **QC Inspector**, **Sales Executive**, **Project Manager**, **Project Coordinator**, **Finance Executive**, **Viewer** |
| 5 | PR Approval Limit | Currency | No | INR. 2 decimal places. Default: 0 (user cannot approve PR). |
| 6 | PO Approval Limit | Currency | No | INR. 2 decimal places. Default: 0 (user cannot approve PO). |

**Creator notes:**
- User Name: Insert > User. This gives a dropdown of all Zoho Creator users in the organization. Only one user can be selected per record (no multi-select).
- User Code serves as the record identifier since User Name is a reference to an external user record.
- Department dropdown values match BRD Section 6 exactly.
- Role dropdown values match USER-ROLES.md Section 1 exactly.
- PR Approval Limit and PO Approval Limit: Insert > Currency. Default value = 0.

**Record-level security**: Only Admin should access this form. Set form permissions so ONLY Admin has access.

#### UI Layout — 1 Section

```
┌─ Section: User Access & Approval Limits ─────────────────────┐
│ User Code [Auto]          User Name [User ▼]                │
│ Department [▼]            Role [▼]                          │
│ PR Approval Limit [₹___]  PO Approval Limit [₹_________]   │
└──────────────────────────────────────────────────────────────┘
```

#### Reports

| Property | Value |
|----------|-------|
| Report name | User Access List |
| Columns | User Code, User Name (display name), Department, Role, PR Approval Limit, PO Approval Limit |
| Default sort | Department ascending, then User Name ascending |
| Search | Enable on User Name, Department, Role |
| Summary | Record count, Sum of PR/PO limits |

#### Permissions

| Profile | Create | Read | Update | Delete |
|---------|--------|------|--------|--------|
| Admin | ✓ | ✓ | ✓ | ✓ |
| All other profiles | — | — | — | — |

**This form is Admin-only per USER-ROLES.md Section 2.1**. No other profile gets any access.

---

## Automation Patterns Summary

### Pattern 1: Auto-Number Generation (Deluge On Submit — Before)

| Form | Approach | Field Updated | Format |
|------|----------|--------------|--------|
| Store Master | Native auto-number field | Store Code | `ST-{000}` |
| Supplier Master | Native auto-number field | Supplier Code | `SUP-{000}` |
| Customer Master | Native auto-number field | Customer Code | `CUS-{000}` |
| Item Master | Deluge On Submit (before) | Purchase Item Code | `{Category}-{seq}` |
| System Master | Deluge On Submit (before) | System Code | `{Type}-{seq}` |
| BOM Master | Native auto-number field | BOM Code | `BOM-{000}` |
| Bin Location Master | Native auto-number field | Bin Code | `BIN-{000}` |
| User Access | Native auto-number field | User Code | `USR-{000}` |

**Native auto-number** → Set via Insert > Auto Number with custom format string (e.g., `ST-{000}`). Read-only.

**Deluge auto-number** → Text field (Unique, Read-only) + Deluge workflow On Submit (Before) that queries max existing code and constructs next value. Code snippet is identical in structure for Item and System Master — only the prefix source field and target field name differ.

### Pattern 2: Auto-Fetch via Lookups

| Form | Trigger Field | Source Form | Fields to Auto-Fetch | Mechanism |
|------|-------------|-------------|----------------------|-----------|
| BOM Master header | System Code | System Master | System Name | Deluge On User Input |
| BOM Items subform | Item Code | Item Master | Item Name, UOM | Deluge On User Input (subform row) |
| Item Master | Preferred Supplier | Supplier Master | Supplier Name | Creator built-in "Add Lookup Fields" |
| Bin Location | Store Name | Store Master | Store Type, Location | Deluge On User Input |

**Creator built-in method:** When adding a Lookup field, Creator offers "Add Lookup Fields" option — select which fields from the parent form to auto-populate. Use this for the Item Master's Preferred Supplier → Supplier Name fetch (no code needed).

**Deluge method:** For more complex scenarios (subform rows, multiple fields), add an On User Input workflow on the trigger field.

### Pattern 3: Form-Level Validation

| Form | Validation | Layer | Implementation |
|------|-----------|-------|----------------|
| Item Master | GST % 0–100 | Deluge On Submit | `if(GST < 0 or > 100) throw` |
| Item Master | Min Stock ≤ Max Stock | Deluge On Submit | `if(Min > Max) throw` |
| Item Master | Duplicate Item Name | Deluge On Submit | Query existing records by name |
| Supplier Master | GSTIN format | Field regex | Regex pattern on field |
| Supplier Master | PAN format | Field regex | Regex pattern on field |
| Supplier Master | IFSC format | Field regex | Regex pattern on field |
| Supplier Master | Email format | Field type | Creator Email field |
| Customer Master | GSTIN format | Field regex | Same regex as Supplier |
| Customer Master | PAN format | Field regex | Same regex as Supplier |
| Customer Master | Contact No min 10 | Field validation | Min length = 10 |
| BOM Master | Quantity > 0 | Deluge On Submit | `foreach item if(Qty <= 0) throw` |
| BOM Master | No duplicate items | Deluge On Submit | Track seen Item Codes |
| BOM Master | At least 1 item | Deluge On Submit | `if(size == 0) throw` |

**Field regex configuration**: In Creator field properties, set "Custom Validation" > Pattern with the regex string. Example for GSTIN: `^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$`

### Pattern 4: Field Validation Properties

| Field | Validation Type | Value |
|-------|---------------|-------|
| Supplier GSTIN | Pattern (Regex) | See Pattern 3 above |
| Supplier PAN | Pattern (Regex) | `^[A-Z]{5}[0-9]{4}[A-Z]{1}$` |
| Supplier IFSC | Pattern (Regex) | `^[A-Z]{4}0[A-Z0-9]{6}$` |
| Supplier Pincode | Pattern (Regex) | `^\d{6}$` |
| Supplier Email | Field type | Email |
| Customer GST No | Pattern (Regex) | Same as Supplier GSTIN |
| Customer PAN | Pattern (Regex) | Same as Supplier PAN |
| Customer Contact No | Min length | 10 |
| Item HSN Code | Pattern (Regex) | `^\d{4,8}$` |
| Item Min Stock | Min value | 0 |
| Supplier Credit Days | Min value | 0 |
| BOM Quantity (subform) | Min value | 0.001 |
| All Unique codes | Unique checkbox | Enabled |

---

## Permissions Configuration — Unified Matrix

For each form, set permissions via Form > Permissions tab. Select each profile and check the appropriate boxes.

| Form | Admin | Pur.Mgr | Pur.Exec | Sto.Mgr | Sto.Kpr | Prod.Mgr | Prod.Exec | QC | Sales | Proj.Mgr | Proj.Coord | Fin. | Viewer |
|------|-------|---------|----------|---------|---------|----------|-----------|----|-------|----------|------------|------|--------|
| Item Master | CRUD | CRUD | CRUD | CRUD | CRUD | CRUD | CRUD | CRUD | V | — | — | — | V |
| System Master | CRUD | — | — | — | — | CRUD | CRUD | — | CRUD | CRUD | CRUD | — | V |
| BOM Master | CRUD | — | — | — | — | CRUD | CRUD | CRUD | — | — | — | V | V |
| Supplier Master | CRUD | CRUD | CRUD | — | — | — | — | — | — | — | — | R | V |
| Customer Master | CRUD | — | — | — | — | — | — | — | CRUD | CRUD | CRUD | R | V |
| Store Master | CRUD | — | — | CRUD | CRUD | R | — | — | — | — | — | — | V |
| Bin Location | CRUD | — | — | CRUD | CRUD | — | — | — | — | — | — | — | V |
| User Access | CRUD | — | — | — | — | — | — | — | — | — | — | — | — |

**Legend:** CRUD = Full access, R = Read-only, V = View (no Create/Update/Delete), — = No Access

### Field-Level Security

| Form | Field | Restricted Access |
|------|-------|------------------|
| Supplier Master | Account No, IFSC Code | Only Admin, Purchase Manager, Finance Executive (View) |
| Item Master | Standard Rate | Only Admin, Purchase Manager, Store Manager, Finance (View) |

Set via: Field > Properties > Access tab > uncheck for restricted profiles.

### Record-Level Access

No record-level sharing rules are needed for Phase 1. All users with Read access see all records in these master data forms. Record-level restrictions (e.g., PR department scoping) belong to later phases.

---

## Reports Summary

All reports are standard List Reports using Creator's Report Builder (Reports tab > New Report > List Report).

| Form | Report Name | Key Columns | Default Sort | Special |
|------|------------|-------------|-------------|---------|
| Store Master | Store Master List | Code, Name, Type, Location | Code ASC | Filter by Type |
| Supplier Master | Supplier Master List | All 16 fields | Name ASC | Search on Name/GSTIN/PAN |
| Customer Master | Customer Master List | All 11 fields | Org Name ASC | Search on Name/GST |
| Item Master | Purchase Item Master | Category, Code, Name, UOM, HSN, Min/Max, Rate, Supplier, Lead Time | Code ASC | Group by Category |
| System Master | System Master List | Code, Name, Thickness, UOM, Description | Code ASC | — |
| BOM Master | BOM Master List | BOM Code, System Code, Item Code, Qty, UOM | System ASC, Item ASC | Group by System Code |
| Bin Location | Bin Location List | Bin Code, Store, Rack, Shelf, Bin | Store ASC, Rack ASC | Filter by Store |
| User Access | User Access List | User Code, User Name, Dept, Role, PR Limit, PO Limit | Dept ASC, Name ASC | — |

**Report configuration steps per form:**
1. Go to Reports tab (within the form designer)
2. Click "New Report"
3. Select "List Report"
4. Add columns from available fields
5. Set default sort order
6. Add any default filters
7. Enable search on specified fields
8. Set report sharing permissions (same as form Read permission)
9. Save

---

## Verification Checklist (Plan Quality Gate)

Before marking this plan as ready for execution, verify:

- [ ] All 8 forms listed with full field specs (name, type, required, properties, regex)
- [ ] All 13 profiles created with names matching USER-ROLES.md
- [ ] Permissions matrix complete — every form × every profile with correct C/R/U/D/V/—
- [ ] Auto-number format specified for all 8 forms (native or Deluge)
- [ ] Auto-fetch relationships documented for all lookup fields
- [ ] Deluge code written for: Item auto-number, System auto-number, BOM auto-fetch, BOM validation, Item validation, Bin Location auto-fetch
- [ ] Field-level regex patterns specified for GSTIN, PAN, IFSC, Pincode, HSN, Email
- [ ] UI layout (sections and field grouping) defined for all forms
- [ ] Report spec (columns, sort, filters, search, grouping) for all 8 forms
- [ ] Build order respects dependencies (Supplier before Item, Store before Bin, System+Item before BOM)
- [ ] India datacenter (.in) confirmed for app creation
- [ ] All forms have audit fields enabled (Created By, Created Time, Modified By, Modified Time)
