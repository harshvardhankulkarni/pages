# BOM Master — Implementation Artifact

## 1. Form Configuration

| Property | Value |
|----------|-------|
| Form name (displayed) | BOM Master |
| Internal name | `BOM_Master` |
| App | Chemsol |
| Datacenter | India (`.in`) |
| Audit fields | Enabled (Created By, Created Time, Modified By, Modified Time) — inherited from app level |
| Architecture | Header + Subform (grid control) for line items. One System → many Items. |
| Key field | BOM Code — native auto-number field, format `BOM-{000}` |

**Dependencies**: System Master (for System Code lookup) + Item Master (for Item Code lookup in subform). Both must be built before BOM Master.

---

## 2. Header Field Configuration

| # | Field Label | Field Type | Required | Unique | Read-Only | Properties |
|---|-------------|-----------|----------|--------|-----------|------------|
| 1 | BOM Code | Auto Number | Yes (auto) | Auto | Yes | Format: `BOM-{000}`. Starts at 1. |
| 2 | System Code | Lookup | Yes | — | — | Target form: **System Master**. Display field: **System Code**. Autocomplete mode. Triggers auto-fetch of System Name. |
| 3 | System Name | Text (Single) | Yes | — | Yes | Max length: 200. Auto-fetched from System Master via Deluge On User Input. User cannot edit. |
| 4 | Description | Text (Multi-line) | No | — | — | 3 rows visible. |

**Creator notes:**
- BOM Code: Insert > Auto Number. Set custom format `BOM-{000}`. Check "Read Only".
- System Code: Insert > Lookup. Target form "System Master", Display field "System Code". Enable "Autocomplete". Check "Required".
- System Name: Insert > Text. Check "Required". Check "Read Only".
- Description: Insert > Text (Multi-line). Set Rows Visible = 3.

---

## 3. Subform (Grid Control) Configuration

### Create the Subform

1. In the BOM Master form designer, click "Create Subform".
2. Name: **BOM Items** (internal name: `BOM_Items`).
3. Enable "Add Row" button (users can add new line items).
4. Enable "Delete Row" per row (trash icon on each row).
5. Set row limit: **50**.
6. Column widths: Item Code (30%), Item Name (25%), Quantity (20%), UOM (15%), Delete (10%).

### Subform Fields

| # | Field Label | Field Type | Required | Read-Only | Properties |
|---|-------------|-----------|----------|-----------|------------|
| 1 | Item Code | Lookup | Yes | — | Target form: **Item Master**. Display field: **Purchase Item Code**. Autocomplete mode. Triggers auto-fetch of Item Name + UOM for the same row. |
| 2 | Item Name | Text (Single) | Yes | Yes | Max length: 200. Auto-fetched from Item Master. |
| 3 | Quantity | Decimal | Yes | — | 3 decimal places. Min value: **0.001**. |
| 4 | UOM | Text (Single) | Yes | Yes | Auto-fetched from Item Master. Read-only — user cannot edit. |

**Creator notes:**
- Item Code (inside subform): Insert > Lookup. Creator supports lookup fields inside subforms — same selector as header lookups. Target "Item Master", Display "Purchase Item Code". Autocomplete. Check "Required".
- Item Name: Insert > Text. Check "Required", "Read Only".
- Quantity: Insert > Decimal. Set Decimal Places = 3. Check "Required". Set Min Value = 0.001.
- UOM: Insert > Text. Check "Required", "Read Only".

---

## 4. Deluge Code — Auto-Fetch Workflows

### 4.1 Auto-Fetch System Name (Header Level)

**Trigger**: On User Input — System Code field (form-level lookup, header section)
**Purpose**: When user selects a System Code from the lookup, fetch and display the corresponding System Name.

**Workflow Name**: "Auto-Fetch System Name"

```deluge
// ─── Auto-Fetch System Name from System Master ─────────────────
// Fires when user selects a System Code in the header section.

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

**How to set up in Creator:**
1. Workflows tab > New Workflow > "On User Input".
2. Select trigger field: **System Code** (header level).
3. Name: "Auto-Fetch System Name".
4. Paste Deluge code.
5. Save & Enable.

### 4.2 Auto-Fetch Item Name + UOM (Subform Row Level)

**Trigger**: On User Input — Item Code field (inside BOM Items subform)
**Purpose**: When user selects an Item Code in any subform row, populate Item Name and UOM in the **same row**.

```deluge
// ─── Auto-Fetch Item Name + UOM from Item Master ──────────────
// Fires when user selects an Item Code in a subform row.
// In Creator, the `input` context inside a subform On User Input
// workflow refers to the CURRENT ROW's field values.
// Item_Code is a lookup field storing the Item Master record ID.

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

**How to set up in Creator (subform):**
1. Workflows tab > New Workflow > "On User Input".
2. Select trigger field: **BOM Items > Item Code** (navigate into the subform, select the Item Code column).
3. Creator knows this workflow applies to the subform row context.
4. Name: "Auto-Fetch Item Name & UOM".
5. Paste Deluge code.
6. Save & Enable.

**Important:** The `input` variable in a subform On User Input workflow points to the **current subform row** being edited, not the form header. This is Creator's native behavior — the same workflow code runs for each row independently.

---

## 5. Deluge Code — Form Validation (On Submit)

**Trigger**: On Submit — Before record is added to the database
**Purpose**: Validate BOM data integrity before saving.

**Workflow Name**: "BOM Validation"

```deluge
// ============================================================
// BOM Master — On Submit (Before) Validation
// ============================================================
// 1. At least one BOM item must exist
// 2. All quantities must be > 0
// 3. No duplicate Item Codes within the same BOM
// ============================================================

// --- 1. Ensure at least one BOM item exists ---
if(input.BOM_Items == null || input.BOM_Items.size() == 0)
{
    throw "At least one BOM item is required.";
}

// --- 2 & 3. Validate each BOM item ---
// item_ids tracks seen Item Code record IDs to detect duplicates
item_ids = List();

foreach item in input.BOM_Items
{
    // --- 2. Validate quantity > 0 ---
    if(item.Quantity == null || item.Quantity <= 0)
    {
        throw "Quantity must be greater than zero for all BOM items. Please check item: "
            + item.Item_Code;
    }

    // --- 3. Check for duplicate Item Codes ---
    // Item_Code is a lookup field — Creator stores the record ID.
    // We compare by ID (not display value) to handle edge cases.
    if(item_ids.contains(item.Item_Code))
    {
        throw "Duplicate item found in BOM. Each item code can only appear once within a BOM.";
    }

    item_ids.add(item.Item_Code);
}
```

**How to set up validation in Creator:**
1. Workflows tab > New Workflow > "On Submit".
2. Select "Before record is added to the Database".
3. Name: "BOM Validation".
4. Paste Deluge code.
5. Save & Enable.

**Validation Rule Summary:**

| # | Rule | Layer | Error Message |
|---|------|-------|--------------|
| 1 | At least 1 BOM item | Deluge On Submit (Before) | "At least one BOM item is required." |
| 2 | Quantity > 0 per item | Deluge On Submit (Before) | "Quantity must be greater than zero for all BOM items. Please check item: {code}" |
| 3 | No duplicate Item Codes | Deluge On Submit (Before) | "Duplicate item found in BOM. Each item code can only appear once within a BOM." |
| 4 | Quantity min 0.001 | Field property: Min Value = 0.001 | Creator built-in min value error |

---

## 6. UI Layout

### Section: BOM Details (single section with embedded subform)

```
┌─ Section: BOM Details ──────────────────────────────────────────────────┐
│                                                                            │
│    BOM Code  [BOM-001       ]   System Code  [Lookup ▼]                    │
│                                                                            │
│    System Name  [3mm Epoxy Flooring                             ]         │
│                                                                            │
│    Description                                                             │
│    [Multi-line text area — 3 rows visible]                                 │
│                                                                            │
│    ┌─ BOM Items (Subform — Grid Control) ───────────────────────────────┐ │
│    │                                                                    │ │
│    │  Item Code         | Item Name        | Quantity  | UOM  | Delete │ │
│    │  ──────────────────|──────────────────|───────────|──────|──────── │ │
│    │  [Lookup ▼]        | [Auto-fetched]   | [0.000]   |[Auto]| [X]    │ │
│    │  [Lookup ▼]        | [Auto-fetched]   | [0.000]   |[Auto]| [X]    │ │
│    │  [Lookup ▼]        | [Auto-fetched]   | [0.000]   |[Auto]| [X]    │ │
│    │                                                                    │ │
│    │  [ + Add Row ]                                                     │ │
│    │                                                                    │ │
│    └────────────────────────────────────────────────────────────────────┘ │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

### Field Placement

| Location | Fields (in order) |
|----------|------------------|
| Header row 1 | BOM Code (auto, read-only, gray background), System Code (lookup dropdown) |
| Header row 2 | System Name (full-width, read-only, gray background, auto-fetched) |
| Header row 3 | Description (full-width, multi-line, 3 rows) |
| Subform | Item Code (lookup), Item Name (auto-fetched, read-only), Quantity (decimal), UOM (auto-fetched, read-only), Delete (icon) |

**Layout notes:**
- BOM Code and System Code sit side-by-side in a 2-column layout.
- System Name is full-width below (users should see the fetched name clearly).
- Description is full-width below System Name.
- The subform grid is placed below Description, spanning the full section width.
- Enable "Add Row" button below the grid.
- Delete column shows a trash icon per row (Creator's default for subforms).

---

## 7. Report Configuration

### Main Report: BOM Master List

| Property | Value |
|----------|-------|
| Report name | BOM Master List |
| Report type | List Report (with subform data as rows) |
| Columns | BOM Code, System Code, System Name, Item Code, Item Name, Quantity, UOM |
| Default sort | System Code ascending, then Item Code ascending |
| Grouping | By System Code (expand/collapse per system, showing its items underneath) |
| Search fields | System Code, System Name, Item Code, Item Name |
| Summary | Record count at footer (count of systems) |

**Creator notes for subform reports:**
In Zoho Creator, displaying subform data in reports requires specific handling:

1. **Option A — Summary Report with "Show Subform Data as Rows"**:
   - Go to Reports tab > New Report > Summary Report.
   - Add BOM Code, System Code, System Name as "Group By" fields (or leave ungrouped).
   - Add subform fields (Item Code, Item Name, Quantity, UOM) as "Aggregated Fields" with "Show Subform Data as Rows" checked.
   - This option flattens the subform into individual rows.

2. **Option B — Use Creator's Form Reference in Pages**:
   - Create a Page (not a List Report) that uses `zoho.creator.getRecords("chemsol", "BOM_Master", ...)` to fetch header + subform data.
   - Render with a sub-table for each BOM. More flexible but requires Deluge.

3. **Option C — Default List Report (subform columns show as comma-separated)**:
   - Creator's default List Report shows subform data as comma-separated values in a single cell.
   - Useful for quick reference but less readable for multi-row BOMs.

**Recommended**: Use **Option A** (Summary Report with "Show Subform Data as Rows") for the BOM Master List. This produces the most readable output — each subform row becomes a separate line, grouped by System Code.

### Creator Steps (Option A)

1. Reports tab > New Report > Summary Report.
2. Report name: "BOM Master List".
3. In the "Select Columns" step:
   - Drag BOM Code, System Code, System Name into the "Group By" section (or leave header fields as Context fields — experiment to get best layout).
   - Drag Item Code, Item Name, Quantity, UOM (from the BOM_Items subform) as Aggregated Fields.
4. Enable **"Show Subform Data as Rows"** — this is the key setting that flattens subform rows.
5. Set Default Sort: System Code > Ascending, then Item Code > Ascending.
6. Enable Search on: System Code, System Name, Item Code, Item Name.
7. Enable Summary > Record Count.
8. Set report permissions (same as form Read access — see §8).
9. Save.

### Alternative: Page-Based Report (Advanced)

If the Summary Report layout is unsatisfactory, build a Deluge page:

```deluge
// Page: BOM Master List (Page Builder with Deluge data table)
bom_records = zoho.creator.getRecords("chemsol", "BOM_Master", null, 200, 0);

html = "<table border='1' cellpadding='5'>";
html += "<tr><th>BOM Code</th><th>System Code</th><th>System Name</th>"
     + "<th>Item Code</th><th>Item Name</th><th>Qty</th><th>UOM</th></tr>";

foreach bom in bom_records
{
    foreach item in bom.get("BOM_Items")
    {
        html += "<tr>";
        html += "<td>" + bom.get("BOM_Code") + "</td>";
        html += "<td>" + bom.get("System_Code") + "</td>";
        html += "<td>" + bom.get("System_Name") + "</td>";
        html += "<td>" + item.get("Item_Code") + "</td>";
        html += "<td>" + item.get("Item_Name") + "</td>";
        html += "<td>" + item.get("Quantity") + "</td>";
        html += "<td>" + item.get("UOM") + "</td>";
        html += "</tr>";
    }
}

html += "</table>";
return html;
```

> **Note**: The page-based approach is optional and should only be used if the Summary Report doesn't meet requirements. Start with the Summary Report (Option A) first.

---

## 8. Permissions

### Form-Level CRUD

Set in Form > Permissions tab. For each profile, check the appropriate boxes:

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

**Legend**: ✓ = granted, — = no access.

### Report Permissions

Same as form Read permission — profiles with Read access on the form also see the report:
- Admin, Production Manager, Production Executive, QC Inspector, Finance Executive, Viewer

### Field-Level Security

No field-level security restrictions are required for BOM Master (no sensitive fields).

---

## 9. Verification Checklist

### Form & Fields — Header
- [ ] Form created with internal name `BOM_Master`.
- [ ] App datacenter confirmed as India (`.in`).
- [ ] Audit fields visible (inherited from app level).
- [ ] **BOM Code**: Auto Number, format `BOM-{000}`, Read-only.
- [ ] **System Code**: Lookup to System Master, Display field: System Code, Autocomplete, Required.
- [ ] **System Name**: Text, Max 200, Required, Read-only.
- [ ] **Description**: Text (Multi-line), 3 rows, Optional.

### Form & Fields — Subform (BOM Items)
- [ ] Subform created with internal name `BOM_Items`.
- [ ] Add Row button enabled.
- [ ] Delete Row enabled per row.
- [ ] Row limit set to 50.
- [ ] Column widths set (30%, 25%, 20%, 15%, 10%).
- [ ] **Item Code**: Lookup to Item Master, Display field: Purchase Item Code, Autocomplete, Required.
- [ ] **Item Name**: Text, Required, Read-only.
- [ ] **Quantity**: Decimal, 3 decimal places, Required, Min value = 0.001.
- [ ] **UOM**: Text, Required, Read-only.

### Deluge Workflow — Auto-Fetch System Name
- [ ] On User Input workflow created on System Code field.
- [ ] Workflow name: "Auto-Fetch System Name".
- [ ] Uses `zoho.creator.getRecordById` to fetch System Master record.
- [ ] Sets `input.System_Name = sys_data.get("System_Name")`.
- [ ] Test: Select EP-001 → System Name auto-populates with "3mm Epoxy Flooring".
- [ ] Test: Change System Code selection → System Name updates.

### Deluge Workflow — Auto-Fetch Item Name + UOM
- [ ] On User Input workflow created on BOM Items > Item Code (subform column).
- [ ] Workflow name: "Auto-Fetch Item Name & UOM".
- [ ] Uses `zoho.creator.getRecordById` to fetch Item Master record.
- [ ] Sets `input.Item_Name = item_data.get("Purchase_Item_Name")`.
- [ ] Sets `input.UOM = item_data.get("UOM")`.
- [ ] Test: Select RM-001 in row 1 → Item Name and UOM populate in row 1.
- [ ] Test: Select RM-002 in row 2 → Item Name and UOM populate in row 2 independently.
- [ ] Test: Change Item Code in existing row → Item Name and UOM update.

### Deluge Workflow — BOM Validation (On Submit)
- [ ] On Submit (Before) workflow created.
- [ ] Workflow name: "BOM Validation".
- [ ] Validation 1: Submit with 0 items → error "At least one BOM item is required.".
- [ ] Validation 2: Submit with item having Quantity = 0 → error thrown.
- [ ] Validation 2: Submit with item having Quantity = -1 → error thrown.
- [ ] Validation 2: Submit with item having Quantity = 0.001 → passes.
- [ ] Validation 3: Add same Item Code twice → error "Duplicate item found in BOM.".
- [ ] Validation 3: Add different Item Codes → passes.
- [ ] Happy path: 3 valid items with unique codes, positive quantities → record saved.

### UI Layout
- [ ] Single section "BOM Details" with BOM Code + System Code side by side.
- [ ] System Name displayed below as full-width read-only text.
- [ ] Description as full-width multi-line (3 rows).
- [ ] BOM Items subform grid placed below Description.
- [ ] All fields positioned correctly per layout diagram.

### Report
- [ ] Report "BOM Master List" created (Summary Report with subform rows).
- [ ] Subform data displayed as rows (flattened).
- [ ] Columns: BOM Code, System Code, System Name, Item Code, Item Name, Quantity, UOM.
- [ ] Default sort: System Code ASC, then Item Code ASC.
- [ ] Search enabled on: System Code, System Name, Item Code, Item Name.
- [ ] Record count summary enabled.
- [ ] Report permissions match form Read access.

### Permissions
- [ ] Admin: CRUD
- [ ] Purchase Manager: No Access
- [ ] Purchase Executive: No Access
- [ ] Store Manager: No Access
- [ ] Store Keeper: No Access
- [ ] Production Manager: CRUD
- [ ] Production Executive: CRUD
- [ ] QC Inspector: CRUD
- [ ] Sales Executive: No Access
- [ ] Project Manager: No Access
- [ ] Project Coordinator: No Access
- [ ] Finance Executive: Read only
- [ ] Viewer: Read only
