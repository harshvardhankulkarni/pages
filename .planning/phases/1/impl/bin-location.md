# Bin Location Master — Implementation Artifact

> **Phase**: Phase 1 — Master Data & Admin
> **Form #**: 7 of 8
> **Dependency**: Store Master (must be built first)
> **Source spec**: `01-PLAN.md` §Form 7 + `BRD.md` §3.1.7

---

## 1. Form Configuration

| Property | Value |
|----------|-------|
| Display name | Bin Location Master |
| Internal name | `Bin_Location_Master` |
| Datacenter | India (`.in`) — inherit from app |
| Audit fields | Enabled at app level (Created By, Created Time, Modified By, Modified Time) |

---

## 2. Field Configuration Table

| # | Field Label | Field Type | Required | Properties |
|---|-------------|-----------|----------|------------|
| 1 | Bin Code | Auto Number | Yes (auto) | Format: `BIN-{000}`. Starts at 1. Read-only. |
| 2 | Store Name | Lookup | Yes | Target: **Store Master**. Display field: **Store Name**. Use Dropdown mode (few stores expected). |
| 3 | Store Type | Text (Single) | No | Read-only. Auto-fetched via Deluge On User Input. |
| 4 | Location | Text (Single) | No | Read-only. Auto-fetched via Deluge On User Input. |
| 5 | Rack No | Text (Single) | Yes | Max length: 50 |
| 6 | Shelf No | Text (Single) | Yes | Max length: 50 |
| 7 | Bin No | Text (Single) | Yes | Max length: 50 |

### Field-Level Security

No restrictions — all profiles with Read access see all fields.

---

## 3. Auto-Fetch Configuration (Deluge)

### Trigger: On User Input — Store Name field

**Purpose**: When user selects (or changes) a Store Name, fetch the corresponding Store Type and Location from Store Master and populate the read-only fields.

### Deluge Code

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

### Creator Configuration Steps

1. Open form designer for **Bin Location Master**
2. Select the **Store Name** field
3. Go to **Workflows** tab > **On User Input**
4. Create new workflow with name: `AutoFetch Store Details`
5. Paste the Deluge code above
6. Save workflow
7. **Test**: Create a Store Master record (e.g. Store Name="Main Warehouse", Store Type="RM", Location="Building A"). Then in Bin Location form, select this store — Store Type and Location should auto-populate as read-only text.

---

## 4. UI Layout — Single Section

```
┌─ Section: Bin Location Details ──────────────────────────────┐
│ Bin Code [Auto]               Store Name [Lookup ▼]         │
│ Store Type [Auto] (read-only) Location [Auto] (read-only)   │
│ Rack No [___________]         Shelf No [_______________]     │
│ Bin No [_____________]                                       │
└───────────────────────────────────────────────────────────────┘
```

**Field order** (top to bottom, left to right):
1. Row 1: Bin Code, Store Name
2. Row 2: Store Type, Location
3. Row 3: Rack No, Shelf No
4. Row 4: Bin No (spans full width, or left-aligned)

---

## 5. Report Configuration

### Report: Bin Location List

| Property | Value |
|----------|-------|
| Report name | Bin Location List |
| Type | List Report |
| Columns | Bin Code, Store Name, Store Type, Location, Rack No, Shelf No, Bin No |
| Default sort | Store Name ascending, then Rack No ascending, then Shelf No ascending, then Bin No ascending |
| Default filter | Optional: by Store Name (user can filter to view bins of a specific store) |
| Search fields | Store Name, Rack No, Shelf No, Bin No |
| Summary | Record count at footer |
| Permissions | Same as form Read access per profile |

### Creator Steps

1. Go to Reports tab within Bin Location Master form
2. Click "New Report" > "List Report"
3. Add columns: Bin Code, Store Name, Store Type, Location, Rack No, Shelf No, Bin No
4. Set default sort: Store Name ASC → Rack No ASC → Shelf No ASC → Bin No ASC
5. Enable search on: Store Name, Rack No, Shelf No, Bin No
6. Add Store Name as a filter dropdown
7. Enable record count summary
8. Set report sharing: same permissions as form Read (see §6)
9. Save as "Bin Location List"

---

## 6. Permissions

Set in Form > Permissions tab per the unified matrix:

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

No field-level or record-level security restrictions needed (all visible fields are appropriate for Store and Admin profiles).

---

## 7. Verification Checklist

- [ ] Form created with internal name `Bin_Location_Master`
- [ ] Bin Code is Auto Number with format `BIN-{000}`, starts at 1, read-only
- [ ] Store Name is Lookup to Store Master, display field = Store Name, dropdown mode
- [ ] Store Name field marked Required
- [ ] Store Type field is Text, read-only, not required
- [ ] Location field is Text, read-only, not required
- [ ] Rack No is Text, required, max 50 chars
- [ ] Shelf No is Text, required, max 50 chars
- [ ] Bin No is Text, required, max 50 chars
- [ ] Deluge On User Input workflow added to Store Name field with correct auto-fetch code
- [ ] Workflow tested: selecting a Store Name populates Store Type and Location correctly
- [ ] Workflow handles null Store Name gracefully (no error when field cleared)
- [ ] UI has single section "Bin Location Details" with 4 rows as specified
- [ ] Report "Bin Location List" created with all 7 columns
- [ ] Report sort: Store Name → Rack No → Shelf No → Bin No (all ascending)
- [ ] Report search enabled on Store Name, Rack No, Shelf No, Bin No
- [ ] Report filter by Store Name is available
- [ ] Permissions match the matrix (Admin + Store Manager + Store Keeper = CRUD, Viewer = Read only)
- [ ] No other profiles have any access
- [ ] Audit fields inherited from app-level setting
