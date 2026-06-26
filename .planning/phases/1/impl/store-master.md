# Store Master — Implementation Artifact

## 1. Form Config

| Property | Value |
|----------|-------|
| Zoho Creator URL | `https://creator.zoho.in` |
| App | Chemsol |
| UI Path | Forms → **+ Create Form** → Blank Form |
| Form Name (displayed) | **Store Master** |
| Internal Name | `Store_Master` |
| Audit Fields | Enabled at app level (Created By, Created Time, Modified By, Modified Time) |

## 2. Field Configuration Table

| # | Field Label | Type | Required | Properties |
|---|-------------|------|----------|------------|
| 1 | Store Code | Auto Number | Yes (auto) | Format: `ST-{000}`, Start: 1, Read Only: Yes |
| 2 | Store Name | Text (Single) | Yes | Max length: 100, **Unique**: Yes |
| 3 | Store Type | Dropdown | Yes | Options (manually entered): **RM**, **FG**, **QC**, **Site** |
| 4 | Location | Text (Single) | No | Max length: 200 |

### Creator Field Setup Steps

- **Store Code**: Insert → Auto Number → Custom Format `ST-{000}` → check "Read Only"
- **Store Name**: Insert → Text → check "Required" + "Unique" → set max length 100
- **Store Type**: Insert → Dropdown → add 4 options (one per line): `RM`, `FG`, `QC`, `Site` → check "Required"
- **Location**: Insert → Text → set max length 200

## 3. UI Layout

```
┌─ Section: Store Details ────────────────────────────────────────┐
│ Store Code [Auto]    Store Name [___________________________]    │
│ Store Type [▼]       Location [___________________________]     │
└─────────────────────────────────────────────────────────────────┘
```

- Single section "Store Details" containing all 4 fields in a 2-column layout.
- Store Code and Store Name on row 1 (left / right).
- Store Type and Location on row 2 (left / right).

## 4. Report Configuration

| Property | Value |
|----------|-------|
| Report Name | **Store Master List** |
| Report Type | List Report |
| Source | Reports tab → New Report → List Report → select Store Master |
| Columns Displayed | Store Code, Store Name, Store Type, Location |
| Default Sort | Store Code → Ascending |
| Filters | Optional filter by Store Type (dropdown facet) |
| Search Fields | Store Name, Store Code |
| Summary | Record count at footer |
| Permissions | Inherited from form-level CRUD (see section 5) |

## 5. Permissions

Set at Form → **Permissions** tab. For each profile, check the boxes below:

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

**Summary**: Full CRUD for **Admin**, **Store Manager**, and **Store Keeper**. Read-only for **Production Manager** and **Viewer**. All other profiles have no access.

## 6. Verification Checklist

After building, confirm each item:

| # | Check | Expected |
|---|-------|----------|
| 1 | Form exists in app | "Store Master" visible in Forms list |
| 2 | Store Code auto-generates | First record: `ST-001`, next: `ST-002` |
| 3 | Store Code is read-only | Cannot edit on form or in report inline edit |
| 4 | Store Name required | Submit fails if empty |
| 5 | Store Name unique | Duplicate name rejected (Creator validation error) |
| 6 | Store Type dropdown shows 4 options | RM, FG, QC, Site |
| 7 | Store Type required | Submit fails if empty |
| 8 | Location optional | Record saves with Location blank |
| 9 | Audit fields populated | Created By, Created Time, etc. auto-filled |
| 10 | Report "Store Master List" exists | Shows all records in list view |
| 11 | Report sorts by Store Code ASC | First row: `ST-001` |
| 12 | Report search works | Typing store name or code filters results |
| 13 | Store Manager can create/edit/delete | Login as Store Manager → full CRUD |
| 14 | Store Keeper can create/edit/delete | Login as Store Keeper → full CRUD |
| 15 | Production Manager read-only | Login as Production Manager → can view, no add/edit/delete buttons |
| 16 | Viewer read-only | Login as Viewer → can view, no add/edit/delete buttons |
| 17 | Purchase Manager no access | Login as Purchase Mgr → form not visible in forms list |
